"""Layer B and the index series, both copied read-only from the parent repo.

Layer B: `../data/_refetch/ohlcv_*.parquet` -- full-history vnstock (VCI) refetch made by the
parent repo on 2026-10-18 in one pass, so every shard sits on one back-adjustment basis.
It reaches back to 2013 but carries ONLY adjusted OHLCV: no raw prices, no reference /
ceiling / floor, and only the tickers still listed when it was fetched (survivorship bias).
Parent prices are thousands of VND; converted here to absolute VND to match layer A.

Index: `../data/market_breadth_daily.parquet` -- official SSI DailyIndex (VNINDEX, VN30 from
2016, VN100 from 2018-12): close value, volume/value and exchange breadth counts. No index
OHLC.
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

PARENT_PRICE_UNIT_VND = 1000.0
PRICE_COLS = ("open", "high", "low", "close")


def load_layer_b(refetch_dir: Path) -> pl.DataFrame:
    paths = sorted(refetch_dir.glob("ohlcv_*.parquet"))
    if not paths:
        raise FileNotFoundError(f"no shards in {refetch_dir}")
    frames = [
        pl.scan_parquet(p, cast_options=pl.ScanCastOptions(integer_cast="allow-float"))
        .select("ticker", "date", *PRICE_COLS, "volume")
        .collect()
        for p in paths
    ]
    return normalize_layer_b(pl.concat(frames, how="vertical_relaxed"))


def normalize_layer_b(df: pl.DataFrame) -> pl.DataFrame:
    """thousands VND -> VND, float64 everywhere, drop non-positive bars, one row per key."""
    return (
        df.with_columns(
            pl.col("date").cast(pl.Date),
            pl.col("ticker").cast(pl.Utf8).str.to_uppercase(),
            *[(pl.col(c).cast(pl.Float64) * PARENT_PRICE_UNIT_VND).alias(f"{c}_adj") for c in PRICE_COLS],
            pl.col("volume").cast(pl.Float64).alias("volume_adj"),
        )
        .drop(*PRICE_COLS, "volume")
        .filter((pl.col("close_adj") > 0) & (pl.col("open_adj") > 0))
        .unique(["ticker", "date"], keep="last")
        .sort(["ticker", "date"])
    )


def load_index(breadth_path: Path) -> pl.DataFrame:
    return (
        pl.read_parquet(breadth_path)
        .select("date", "index_id", "index_value", "total_match_vol", "total_match_val",
                "advances", "declines", "no_changes", "ceilings", "floors")
        .with_columns(pl.col("date").cast(pl.Date))
        .sort(["index_id", "date"])
    )
