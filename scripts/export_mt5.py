"""Export the cleaned HOSE series as files the MT5 import script reads.

    python scripts/export_mt5.py                # into MT5's shared folder (Terminal/Common/Files/hose)
    python scripts/export_mt5.py --out data/mt5 # anywhere else

Writes, under <out>:
    symbols.csv        ticker, description, first, last, bars, watch (1 = top-30 liquid on the last day)
    bars/<T>.csv       date, open, high, low, close, volume -- back-adjusted, traded sessions only
    limits/<T>.csv     date, ref, ceiling, floor, close_raw, at_ceiling, at_floor -- raw VND, for the EA

Charts use adjusted prices so corporate actions do not print fake gaps. Execution logic in the EA must
use limits/<T>.csv: the price band and limit-locks are defined on raw prices.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
MT5_COMMON = Path(os.environ.get("APPDATA", "")) / "MetaQuotes" / "Terminal" / "Common" / "Files" / "hose"
WATCH_N = 30
MT5_DATE = "%Y.%m.%d"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=MT5_COMMON)
    a = ap.parse_args()
    c = pl.read_parquet(ROOT / "data" / "hose_daily_clean.parquet")
    (a.out / "bars").mkdir(parents=True, exist_ok=True)
    (a.out / "limits").mkdir(parents=True, exist_ok=True)

    last = c["date"].max()
    watch = set(c.filter((pl.col("date") == last) & pl.col("adv_rank").is_not_null())
                .sort("adv_rank").head(WATCH_N)["ticker"].to_list())
    priced = c.filter(pl.col("close_adj").is_not_null())
    rows = []
    for ticker, g in priced.group_by("ticker", maintain_order=True):
        t = str(ticker[0])
        g = g.sort("date")
        g.select(pl.col("date").dt.strftime(MT5_DATE),
                 pl.col("open_adj").round(2).alias("open"), pl.col("high_adj").round(2).alias("high"),
                 pl.col("low_adj").round(2).alias("low"), pl.col("close_adj").round(2).alias("close"),
                 pl.col("volume_adj").round(0).cast(pl.Int64).alias("volume")
                 ).write_csv(a.out / "bars" / f"{t}.csv")
        g.select(pl.col("date").dt.strftime(MT5_DATE), pl.col("ref_price").alias("ref"),
                 pl.col("ceiling_price").alias("ceiling"), pl.col("floor_price").alias("floor"),
                 pl.col("close").alias("close_raw"), pl.col("at_ceiling").cast(pl.Int8),
                 pl.col("at_floor").cast(pl.Int8)).write_csv(a.out / "limits" / f"{t}.csv")
        # no commas: MQL5's CSV reader splits on them even inside quotes
        rows.append((t, f"HOSE {t} back-adjusted to {last}", g["date"].min().strftime(MT5_DATE),
                     g["date"].max().strftime(MT5_DATE), g.height, int(t in watch)))
    pl.DataFrame(rows, schema=["ticker", "description", "first", "last", "bars", "watch"], orient="row") \
        .sort("watch", "ticker", descending=[True, False]).write_csv(a.out / "symbols.csv")
    print(f"{len(rows)} symbols, {priced.height} bars -> {a.out} (watch list: {len(watch)})")


if __name__ == "__main__":
    main()
