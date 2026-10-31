"""Check that cached SSI windows fetched on an earlier day share today's adjustment basis.

Refetches the given cached windows into a temp dir and diffs `close_adj` row by row.
Zero differences => no ex-right adjustment happened between the two fetches, so the cache
can be built with `build_data.py --allow-mixed-basis`.

    python scripts/verify_basis.py dsp_20200101_20200130 dsp_20210425_20210524
"""
from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from pathlib import Path

import polars as pl
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wyckoff.data import ssi_fastconnect as ssi  # noqa: E402

CACHE = ROOT / "data" / "raw" / "ssi_dsp"


def main(names: list[str]) -> None:
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT.parent / ".env")
    session = requests.Session()
    get_page = ssi.make_page_fetcher(session, ssi.access_token(session), ssi.RateLimiter())
    worst = 0.0
    for name in names:
        cached = pl.read_parquet(CACHE / f"{name}.parquet")
        _, s, e = name.split("_")
        start, end = (datetime.strptime(x, "%Y%m%d").date() for x in (s, e))
        with tempfile.TemporaryDirectory() as tmp:
            fresh = pl.read_parquet(ssi.fetch_to_cache(start, end, Path(tmp), get_page, force=True)[0])
        j = cached.join(fresh, on=["ticker", "date"], suffix="_new", how="full", coalesce=True)
        diff = j.filter(pl.col("close_adj").ne_missing(pl.col("close_adj_new")))
        rel = (diff["close_adj_new"] / diff["close_adj"] - 1).abs().max() if diff.height else 0.0
        worst = max(worst, float(rel or 0.0))
        print(f"{name}: cached={cached.height} fresh={fresh.height} "
              f"fetched_at={cached['fetched_at'][0]} close_adj differs on {diff.height} rows "
              f"(max rel {float(rel or 0.0):.4%})")
        if diff.height:
            print(diff.select("ticker", "date", "close_adj", "close_adj_new").head(10))
    print("BASIS IDENTICAL" if worst == 0.0 else "BASIS DIFFERS -> rebuild with --force")


if __name__ == "__main__":
    main(sys.argv[1:])
