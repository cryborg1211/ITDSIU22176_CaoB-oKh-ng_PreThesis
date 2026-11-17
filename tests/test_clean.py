from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import polars as pl
import pytest

from wyckoff.data.clean import CleanConfig, clean_layer_a

# one session = one row; liquid_top_n=1 with a filler makes "liquid" a per-test choice
CFG = CleanConfig(start="2024-01-01", adv_window=2, adv_min_samples=1, liquid_top_n=1)


def _bars(ticker: str, closes: list[float], refs: list[float] | None = None, **cols: list[Any]) -> pl.DataFrame:
    n = len(closes)
    refs = refs if refs is not None else [closes[max(i - 1, 0)] for i in range(n)]
    base: dict[str, Any] = {
        "date": [date(2024, 1, 1) + timedelta(days=i) for i in range(n)],
        "ticker": [ticker] * n,
        "instrument": ["stock"] * n,
        "open": closes, "high": closes, "low": closes, "close": closes,
        "ref_price": refs,
        "ceiling_price": [r * 1.07 for r in refs],
        "floor_price": [r * 0.93 for r in refs],
        "match_vol": [1000.0] * n,
        "match_val": [1e9] * n,
        "close_adj": closes,
        "adj_factor": [1.0] * n,
    }
    base.update(cols)
    return pl.DataFrame(base).with_columns(
        pl.col("date").cast(pl.Date), *[pl.col(c).cast(pl.Float64) for c in base
                                        if c not in ("date", "ticker", "instrument")])


def _filler(n: int, value: float) -> pl.DataFrame:
    """A name that takes the single liquid slot, or leaves it free when its value is low."""
    return _bars("ZZZ", [50000.0] * n, match_val=[value] * n)


def test_back_adjustment_scales_only_bars_before_the_ex_date() -> None:
    df = pl.concat([_bars("HPG", [30000, 30000, 20000, 20100], refs=[30000, 30000, 20000, 20000]), _filler(4, 1.0)])
    out = clean_layer_a(df, CFG).filter(pl.col("ticker") == "HPG")
    assert out["ex_source"].to_list() == [None, None, "band", None]
    assert out["adj_factor"].to_list() == pytest.approx([2 / 3, 2 / 3, 1.0, 1.0])
    assert out["close_adj"].to_list() == pytest.approx([20000, 20000, 20000, 20100])
    assert out["volume_adj"].to_list() == pytest.approx([1500, 1500, 1000, 1000])


def test_small_drop_is_an_ex_right_on_a_liquid_name_only() -> None:
    closes, refs = [30000.0, 30000.0, 29000.0], [30000.0, 30000.0, 29000.0]
    liquid = clean_layer_a(pl.concat([_bars("HPG", closes, refs), _filler(3, 1.0)]), CFG)
    thin = clean_layer_a(pl.concat([_bars("HPG", closes, refs), _filler(3, 1e12)]), CFG)
    assert liquid.filter(pl.col("ticker") == "HPG")["ex_source"][2] == "liquid"
    assert thin.filter(pl.col("ticker") == "HPG")["ex_source"][2] is None
    assert thin.filter(pl.col("ticker") == "HPG")["adj_factor"][0] == 1.0


def test_thin_name_small_drop_accepted_when_ssi_factor_steps() -> None:
    df = pl.concat([_bars("HPG", [30000, 30000, 29000], refs=[30000, 30000, 29000], adj_factor=[0.97, 0.97, 1.0]),
                    _filler(3, 1e12)])
    assert clean_layer_a(df, CFG).filter(pl.col("ticker") == "HPG")["ex_source"][2] == "ssi"


def test_reference_above_previous_close_is_never_an_event() -> None:
    df = pl.concat([_bars("HPG", [30000, 30000, 31000], refs=[30000, 30000, 31000]), _filler(3, 1.0)])
    out = clean_layer_a(df, CFG).filter(pl.col("ticker") == "HPG")
    assert out["ex_ratio"].to_list() == [1.0, 1.0, 1.0]


def test_zero_volume_session_keeps_the_row_but_loses_its_prices() -> None:
    df = _bars("HPG", [30000, 30000, 30000], match_vol=[1000, 0, 1000])
    out = clean_layer_a(df, CFG)
    assert out["is_traded"].to_list() == [True, False, True]
    assert out["close"][1] is None and out["close_adj"][1] is None and out["volume_adj"][1] == 0.0


def test_non_tick_prices_are_suspect_and_never_produce_an_event() -> None:
    df = pl.concat([_bars("ELC", [20815.64, 20474.4], refs=[25800, 24400]), _filler(2, 1.0)])
    out = clean_layer_a(df, CFG).filter(pl.col("ticker") == "ELC")
    assert out["price_suspect"].all() and out["close"].null_count() == 2
    assert out["ex_ratio"].to_list() == [1.0, 1.0]


def test_rows_never_traded_and_other_instruments_are_dropped() -> None:
    df = pl.concat([
        _bars("AGD", [0.0, 0.0], refs=[0.0, 0.0]),
        _bars("CHPG2401", [1000.0, 1000.0]).with_columns(pl.lit("cw").alias("instrument")),
        _bars("HPG", [30000.0, 30000.0]),
    ])
    assert clean_layer_a(df, CFG)["ticker"].unique().to_list() == ["HPG"]


def test_missing_reference_price_means_limits_unknown_not_a_lock() -> None:
    df = _bars("HPG", [30000, 30000], refs=[30000, 0], ceiling_price=[32100, 0], floor_price=[27900, 0])
    out = clean_layer_a(df, CFG)
    assert out["limit_known"].to_list() == [True, False]
    assert not out["at_floor"][1] and not out["at_ceiling"][1] and out["ex_ratio"][1] == 1.0


def test_stale_ref_price_falls_back_to_band_midpoint() -> None:
    # ref still 30000 on the ex-date, but the limits were set around 20000
    df = pl.concat([_bars("HPG", [30000, 30000, 20000], refs=[30000, 30000, 30000],
                          ceiling_price=[32100, 32100, 21400], floor_price=[27900, 27900, 18600]), _filler(3, 1.0)])
    out = clean_layer_a(df, CFG).filter(pl.col("ticker") == "HPG")
    assert out["ex_ratio"][2] == pytest.approx(2 / 3)
    assert out["close_adj"][1] == pytest.approx(20000)


def test_inconsistent_bar_is_repaired_around_the_close() -> None:
    df = _bars("HPG", [30000, 30000], open=[30000, 31000], high=[30000, 30500], low=[30000, 30200])
    bar = clean_layer_a(df, CFG).row(1, named=True)
    assert bar["ohlc_repaired"] and bar["close"] == 30000
    assert bar["low"] == 30000 and bar["high"] == 30500 and bar["open"] == 30500


def test_zero_open_is_replaced_by_the_close() -> None:
    df = _bars("HPG", [30000, 30000], open=[30000, 0], high=[30000, 30000], low=[30000, 30000])
    bar = clean_layer_a(df, CFG).row(1, named=True)
    assert bar["ohlc_repaired"] and bar["open"] == 30000


def test_liquidity_rank_uses_only_earlier_sessions() -> None:
    # HPG turns huge on the last day: its rank that same day must not know it
    df = pl.concat([_bars("HPG", [30000] * 3, match_val=[1.0, 1.0, 1e15]), _filler(3, 1e9)])
    out = clean_layer_a(df, CFG).filter(pl.col("ticker") == "HPG")
    assert out["is_liquid"].to_list() == [False, False, False]
