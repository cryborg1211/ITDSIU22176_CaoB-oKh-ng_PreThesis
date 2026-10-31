from __future__ import annotations

from datetime import date

import polars as pl

from wyckoff.data import legacy_vci


def test_normalize_layer_b_scales_to_vnd_and_dedups() -> None:
    df = pl.DataFrame({
        "ticker": ["hpg", "HPG", "HPG"],
        "date": [date(2018, 1, 2), date(2018, 1, 2), date(2018, 1, 3)],
        "open": [30.5, 30.5, 0.0],
        "high": [31.0, 31.0, 31.0],
        "low": [30.0, 30.0, 30.0],
        "close": [30.8, 30.8, 30.9],
        "volume": [100, 100, 200],
    })
    out = legacy_vci.normalize_layer_b(df)
    assert out.height == 1                       # duplicate key collapsed, zero-open bar dropped
    assert out["close_adj"][0] == 30800.0
    assert out["volume_adj"].dtype == pl.Float64
    assert set(out.columns) == {"ticker", "date", "open_adj", "high_adj", "low_adj", "close_adj",
                                "volume_adj"}
