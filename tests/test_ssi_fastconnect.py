from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from wyckoff.data import ssi_fastconnect as ssi


def _row(symbol: str, day: str, close: str = "21200", adj: str = "21200", **kw: str) -> dict[str, Any]:
    base = {
        "Symbol": symbol, "TradingDate": day, "RefPrice": "20750", "CeilingPrice": "22200",
        "FloorPrice": "19300", "OpenPrice": "20800", "HighestPrice": "21600",
        "LowestPrice": "20750", "ClosePrice": close, "ClosePriceAdjusted": adj,
        "TotalMatchVol": "1000", "AveragePrice": "21000",
    }
    base.update(kw)
    return base


def test_chunk_windows_respects_cap_and_covers_range() -> None:
    wins = ssi.chunk_windows(date(2020, 1, 1), date(2020, 3, 15))
    assert wins[0][0] == date(2020, 1, 1) and wins[-1][1] == date(2020, 3, 15)
    assert all((e - s).days + 1 <= ssi.MAX_WINDOW_DAYS for s, e in wins)
    assert all(wins[i][1] + timedelta(days=1) == wins[i + 1][0] for i in range(len(wins) - 1))
    assert ssi.chunk_windows(date(2020, 2, 1), date(2020, 1, 1)) == []


@pytest.mark.parametrize("ticker,kind", [("HPG", "stock"), ("CHPG2401", "cw"),
                                         ("E1VFVN30", "fund"), ("FUEVFVND", "fund")])
def test_classify_instrument(ticker: str, kind: str) -> None:
    assert ssi.classify_instrument(ticker) == kind


def test_parse_rows_keeps_absolute_vnd_and_drops_malformed() -> None:
    df = ssi.parse_rows([_row("HPG", "29/10/2026"), _row("", "29/10/2026"), _row("HPG", "bad")])
    assert df.height == 1
    assert df["close"][0] == 21200.0 and df["date"][0] == date(2026, 10, 29)


def test_derive_columns_adjustment_and_limit_flags() -> None:
    raw = ssi.parse_rows([
        # 30% stock dividend later: adjusted close = close / 1.3
        _row("HDB", "01/10/2026", close="26000", adj="20000", TotalMatchVol="1300",
             RefPrice="25800", CeilingPrice="27600", FloorPrice="24000"),
        _row("HPG", "02/10/2026", close="22200", adj="22200"),          # closes on ceiling
        _row("VNM", "02/10/2026", close="19300", adj="19300"),          # closes on floor
    ])
    out = ssi.derive_columns(raw).sort("ticker")
    hdb = out.filter(pl.col("ticker") == "HDB").row(0, named=True)
    assert hdb["adj_factor"] == pytest.approx(20000 / 26000)
    assert hdb["open_adj"] == pytest.approx(20800 * 20000 / 26000)
    assert hdb["match_vol_adj"] == pytest.approx(1300 * 26000 / 20000)
    assert out.filter(pl.col("ticker") == "HPG")["at_ceiling"][0]
    assert out.filter(pl.col("ticker") == "VNM")["at_floor"][0]
    assert not hdb["at_ceiling"] and not hdb["at_floor"]


def _pager(total_rows: list[dict[str, Any]], page_size: int) -> ssi.PageFetcher:
    def get_page(start: date, end: date, page_index: int) -> dict[str, Any]:
        chunk = total_rows[(page_index - 1) * page_size: page_index * page_size]
        return {"status": "Success", "totalRecord": len(total_rows), "data": chunk}
    return get_page


def test_fetch_window_collects_all_pages() -> None:
    rows = [_row(f"A{i:02d}"[:3] if i < 10 else "ZZZ", f"{(i % 28) + 1:02d}/01/2024") for i in range(25)]
    res = ssi.fetch_window(date(2024, 1, 1), date(2024, 1, 30), _pager(rows, 10))
    assert res.status == "Success" and res.total_record == 25 and res.frame.height == 25


def test_fetch_window_no_data_is_empty_not_error() -> None:
    res = ssi.fetch_window(date(2016, 1, 1), date(2016, 1, 30),
                           lambda s, e, p: {"status": "NoDataFound", "totalRecord": 0, "data": None})
    assert res.status == "NoDataFound" and res.frame.height == 0


def test_fetch_window_raises_on_short_paging() -> None:
    def get_page(start: date, end: date, page_index: int) -> dict[str, Any]:
        data = [_row("HPG", "02/01/2024")] if page_index == 1 else []
        return {"status": "Success", "totalRecord": 5, "data": data}
    with pytest.raises(RuntimeError, match="page 2 empty"):
        ssi.fetch_window(date(2024, 1, 1), date(2024, 1, 30), get_page)


def test_fetch_window_raises_on_overlapping_pages() -> None:
    # the live failure: row count matches totalRecord but page 2 repeats page 1
    def get_page(start: date, end: date, page_index: int) -> dict[str, Any]:
        return {"status": "Success", "totalRecord": 2, "data": [_row("HPG", "02/01/2024")]}
    with pytest.raises(ssi.PagingError, match="1 unique"):
        ssi.fetch_window(date(2024, 1, 1), date(2024, 1, 30), get_page)


def test_fetch_to_cache_refetches_window_after_short_paging(tmp_path: Path) -> None:
    rows = [_row("HPG", "02/01/2024"), _row("VNM", "02/01/2024")]
    calls = {"n": 0}

    def flaky(start: date, end: date, page_index: int) -> dict[str, Any]:
        calls["n"] += 1
        if calls["n"] == 2:                     # first window attempt: page 2 empty
            return {"status": "Success", "totalRecord": 2, "data": []}
        return {"status": "Success", "totalRecord": 2, "data": rows[page_index - 1: page_index]}

    paths = ssi.fetch_to_cache(date(2024, 1, 1), date(2024, 1, 20), tmp_path, flaky, today=date(2026, 1, 1))
    assert pl.read_parquet(paths[0]).height == 2


def test_build_layer_a_refuses_mixed_adjustment_basis(tmp_path: Path) -> None:
    for i, stamp in enumerate(["2026-10-01T10:00:00", "2026-10-29T10:00:00"]):
        ssi.parse_rows([_row("HPG", f"0{i + 1}/10/2026")]) \
            .with_columns(pl.lit(stamp).alias("fetched_at")) \
            .write_parquet(tmp_path / f"dsp_2026100{i + 1}_2026100{i + 1}.parquet")
    with pytest.raises(RuntimeError, match="adjustment bases"):
        ssi.build_layer_a(tmp_path, tmp_path / "out.parquet")
    out = ssi.build_layer_a(tmp_path, tmp_path / "out.parquet", allow_mixed_basis=True)
    assert out.height == 2 and out["basis_date"][0] == "2026-10-01"
