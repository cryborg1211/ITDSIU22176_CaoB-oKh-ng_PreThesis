"""Build the thesis datasets into data/.

    python scripts/build_data.py              # layer A (fetch, resumable) + layer B + index
    python scripts/build_data.py --force      # refetch every window -> one adjustment basis
    python scripts/build_data.py --skip-fetch # rebuild outputs from cache only

Outputs (absolute VND, git-ignored):
    data/hose_daily_ssi.parquet     layer A, 2020-01 -> today, all HOSE instruments
    data/hose_daily_vci.parquet     layer B, 2013 -> 2026-10-18, adjusted only
    data/index_daily.parquet        VNINDEX / VN30 / VN100 (official DailyIndex)
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wyckoff.data import legacy_vci, ssi_fastconnect as ssi  # noqa: E402

PARENT = ROOT.parent
DATA = ROOT / "data"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=date.fromisoformat, default=ssi.HISTORY_START)
    ap.add_argument("--end", type=date.fromisoformat, default=date.today())
    ap.add_argument("--force", action="store_true", help="refetch all cached windows")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--allow-mixed-basis", action="store_true",
                    help="accept windows fetched on different days (only after verifying no "
                         "session -- hence no ex-right adjustment -- happened in between)")
    a = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger("build_data")
    # thesis .env first, then the parent's (read-only) -- credentials are never copied
    load_dotenv(ROOT / ".env")
    load_dotenv(PARENT / ".env")

    cache = DATA / "raw" / "ssi_dsp"
    if not a.skip_fetch:
        session = requests.Session()
        token = ssi.access_token(session)
        get_page = ssi.make_page_fetcher(session, token, ssi.RateLimiter())
        ssi.fetch_to_cache(a.start, a.end, cache, get_page, force=a.force)
    layer_a = ssi.build_layer_a(cache, DATA / "hose_daily_ssi.parquet",
                                allow_mixed_basis=a.allow_mixed_basis)
    log.info("layer A: %d rows, %d tickers, %s..%s", layer_a.height, layer_a["ticker"].n_unique(),
             layer_a["date"].min(), layer_a["date"].max())

    layer_b = legacy_vci.load_layer_b(PARENT / "data" / "_refetch")
    layer_b.write_parquet(DATA / "hose_daily_vci.parquet")
    log.info("layer B: %d rows, %d tickers, %s..%s", layer_b.height, layer_b["ticker"].n_unique(),
             layer_b["date"].min(), layer_b["date"].max())

    index = legacy_vci.load_index(PARENT / "data" / "market_breadth_daily.parquet")
    index.write_parquet(DATA / "index_daily.parquet")
    log.info("index: %d rows %s", index.height, sorted(index["index_id"].unique().to_list()))


if __name__ == "__main__":
    main()
