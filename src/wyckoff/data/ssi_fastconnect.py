"""HOSE daily bars from SSI FastConnect Data `DailyStockPrice` (layer A).

One market-wide request per <=30-day window returns every instrument that traded on HOSE in
that window, so the dataset is survivorship-free by construction (delisted names are present
for the dates they traded). Each row carries the RAW session prices, the exchange's own
reference/ceiling/floor prices, and `ClosePriceAdjusted` -- the close back-adjusted onto the
adjustment basis current at fetch time.

Measured live 30-10-2026 (see docs/failure-log.md / process/features/data):
- history starts 2020-01; any window before that returns status "NoDataFound"
- a window longer than ~30 calendar days returns status "Error" with zero rows
- numbers arrive as strings, prices in absolute VND (kept in absolute VND here -- unlike the
  parent repo, which stores thousands of VND)
- the market-wide pull includes covered warrants, ETFs and fund certificates

Adjustment is retroactive upstream: a corporate action rewrites every earlier
`ClosePriceAdjusted`. Windows fetched on different days can therefore sit on different bases;
`build_layer_a` refuses to mix fetch days unless told to.
"""
from __future__ import annotations

import logging
import os
import re
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import polars as pl
import requests

LOGGER = logging.getLogger("wyckoff.data.ssi")

BASE_URL = "https://fc-data.ssi.com.vn/api/v2/Market"
TOKEN_URL = f"{BASE_URL}/AccessToken"
DAILY_STOCK_PRICE_URL = f"{BASE_URL}/DailyStockPrice"

HISTORY_START = date(2020, 1, 1)
MAX_WINDOW_DAYS = 30            # inclusive span; 31+ returns status "Error"
# Pages are NOT a stable partition: across pages of one query the server repeats rows and never
# serves others (measured 31-10-2026: ~35% duplicates per 30-day window at pageSize 1000, while
# the row count still matched totalRecord). One page per window avoids paging altogether --
# the largest HOSE window so far is ~56k rows and a 60k page returns it whole in ~55 s.
PAGE_SIZE = 100_000
REQUESTS_PER_MIN = 55           # community tier is 60/min; keep headroom
REQUEST_TIMEOUT_S = 300
MAX_ATTEMPTS = 4

_STOCK_RE = re.compile(r"^[A-Z]{3}$")
_CW_RE = re.compile(r"^C[A-Z0-9]{3}\d{4}$")

# FastConnect field -> output column (all parsed as float64)
_NUMERIC_FIELDS: dict[str, str] = {
    "RefPrice": "ref_price",
    "CeilingPrice": "ceiling_price",
    "FloorPrice": "floor_price",
    "OpenPrice": "open",
    "HighestPrice": "high",
    "LowestPrice": "low",
    "ClosePrice": "close",
    "AveragePrice": "avg_price",
    "ClosePriceAdjusted": "close_adj",
    "TotalMatchVol": "match_vol",
    "TotalMatchVal": "match_val",
    "TotalDealVol": "deal_vol",
    "TotalDealVal": "deal_val",
    "TotalTradedVol": "total_vol",
    "TotalTradedValue": "total_val",
    "ForeignBuyVolTotal": "foreign_buy_vol",
    "ForeignSellVolTotal": "foreign_sell_vol",
    "ForeignBuyValTotal": "foreign_buy_val",
    "ForeignSellValTotal": "foreign_sell_val",
    "ForeignCurrentRoom": "foreign_room",
    "TotalBuyTrade": "buy_trade_count",
    "TotalSellTrade": "sell_trade_count",
}

RAW_SCHEMA: dict[str, pl.DataType] = {
    "date": pl.Date,
    "ticker": pl.Utf8,
    **{col: pl.Float64 for col in _NUMERIC_FIELDS.values()},
}


# ---- pure helpers --------------------------------------------------------------------------

def chunk_windows(start: date, end: date, max_days: int = MAX_WINDOW_DAYS) -> list[tuple[date, date]]:
    """Split [start, end] into consecutive inclusive windows of at most `max_days` days."""
    if end < start:
        return []
    out: list[tuple[date, date]] = []
    cur = start
    while cur <= end:
        win_end = min(cur + timedelta(days=max_days - 1), end)
        out.append((cur, win_end))
        cur = win_end + timedelta(days=1)
    return out


def classify_instrument(ticker: str) -> str:
    """stock | cw (covered warrant) | fund (ETF / fund certificate)."""
    if _STOCK_RE.match(ticker):
        return "stock"
    if _CW_RE.match(ticker):
        return "cw"
    return "fund"


def _to_float(raw: Any) -> float | None:
    if raw in (None, ""):
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def parse_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    """Raw DailyStockPrice rows -> RAW_SCHEMA frame. Malformed rows are dropped, not raised."""
    records: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("Symbol") or "").strip().upper()
        try:
            day = datetime.strptime(str(row.get("TradingDate") or ""), "%d/%m/%Y").date()
        except ValueError:
            continue
        if not symbol:
            continue
        rec: dict[str, Any] = {"date": day, "ticker": symbol}
        for field, col in _NUMERIC_FIELDS.items():
            rec[col] = _to_float(row.get(field))
        records.append(rec)
    if not records:
        return pl.DataFrame(schema=RAW_SCHEMA)
    return pl.DataFrame(records, schema=RAW_SCHEMA)


def derive_columns(raw: pl.DataFrame) -> pl.DataFrame:
    """Add instrument type, adjustment factor, adjusted OHLC/volume and limit flags.

    adj_factor = close_adj / close. Back-adjusted OHL use the same factor; volume is divided
    by it so share counts stay comparable across stock dividends / splits. A session whose
    close sits on the ceiling (floor) is flagged: a buy (sell) order there may not fill.
    """
    no_trade = (pl.col("close") <= 0) | pl.col("close").is_null()
    factor = pl.when(no_trade | pl.col("close_adj").is_null()).then(None).otherwise(
        pl.col("close_adj") / pl.col("close")
    )
    return (
        raw.with_columns(
            pl.col("ticker").map_elements(classify_instrument, return_dtype=pl.Utf8).alias("instrument"),
            factor.alias("adj_factor"),
        )
        .with_columns(
            (pl.col("open") * pl.col("adj_factor")).alias("open_adj"),
            (pl.col("high") * pl.col("adj_factor")).alias("high_adj"),
            (pl.col("low") * pl.col("adj_factor")).alias("low_adj"),
            (pl.col("match_vol") / pl.col("adj_factor")).alias("match_vol_adj"),
            ((pl.col("close") >= pl.col("ceiling_price")) & (pl.col("ceiling_price") > 0)).alias("at_ceiling"),
            ((pl.col("close") <= pl.col("floor_price")) & (pl.col("floor_price") > 0)).alias("at_floor"),
        )
        .sort(["ticker", "date"])
    )


# ---- network -------------------------------------------------------------------------------

class RateLimiter:
    """Sliding-window limiter shared by every request in a build."""

    def __init__(self, per_minute: int = REQUESTS_PER_MIN) -> None:
        self._per_minute = per_minute
        self._stamps: deque[float] = deque()
        self._lock = threading.Lock()

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            while self._stamps and now - self._stamps[0] >= 60.0:
                self._stamps.popleft()
            if len(self._stamps) >= self._per_minute:
                time.sleep(60.0 - (now - self._stamps[0]) + 0.05)
            self._stamps.append(time.monotonic())


def access_token(session: requests.Session) -> str:
    """POST consumer credentials -> JWT. Raises with a clear message; never logs secrets."""
    consumer_id = os.getenv("Consumer_Key")
    consumer_secret = os.getenv("ConsumerSecret_Key")
    if not consumer_id or not consumer_secret:
        raise RuntimeError("Consumer_Key / ConsumerSecret_Key not set (.env or ../.env)")
    r = session.post(
        TOKEN_URL,
        json={"consumerID": consumer_id, "consumerSecret": consumer_secret},
        timeout=REQUEST_TIMEOUT_S,
    )
    r.raise_for_status()
    token = (r.json().get("data") or {}).get("accessToken")
    if not token:
        raise RuntimeError("FastConnect AccessToken response had no token")
    return token


@dataclass
class WindowResult:
    start: date
    end: date
    status: str
    total_record: int
    frame: pl.DataFrame


PageFetcher = Callable[[date, date, int], dict[str, Any]]
WINDOW_ATTEMPTS = 3


class PagingError(RuntimeError):
    """A page came back empty before `totalRecord` rows were collected."""


def fetch_window(start: date, end: date, get_page: PageFetcher, page_size: int = PAGE_SIZE) -> WindowResult:
    """All pages of one window. `get_page(start, end, page_index)` returns the raw JSON."""
    first = get_page(start, end, 1)
    status = str(first.get("status") or "")
    total = int(first.get("totalRecord") or 0)
    if status != "Success":
        return WindowResult(start, end, status, 0, pl.DataFrame(schema=RAW_SCHEMA))
    rows: list[dict[str, Any]] = list(first.get("data") or [])
    page = 2
    while len(rows) < total:
        batch = list(get_page(start, end, page).get("data") or [])
        if not batch:
            raise PagingError(f"{start}..{end}: page {page} empty with {len(rows)}/{total} rows")
        rows.extend(batch)
        page += 1
    keys = {(r.get("Symbol"), r.get("TradingDate")) for r in rows}
    if len(keys) != total:
        raise PagingError(f"{start}..{end}: {len(keys)} unique (symbol, date) of {total} rows "
                          f"over {page - 1} page(s) -- server paging overlapped")
    frame = parse_rows(rows)
    if frame.height != total:
        LOGGER.warning("%s..%s: parsed %d of %d rows", start, end, frame.height, total)
    return WindowResult(start, end, status, total, frame)


def make_page_fetcher(session: requests.Session, token: str, limiter: RateLimiter,
                      market: str = "HOSE") -> PageFetcher:
    def get_page(start: date, end: date, page_index: int) -> dict[str, Any]:
        params = {
            "fromDate": start.strftime("%d/%m/%Y"),
            "toDate": end.strftime("%d/%m/%Y"),
            "market": market,
            "pageIndex": page_index,
            "pageSize": PAGE_SIZE,
        }
        for attempt in range(1, MAX_ATTEMPTS + 1):
            limiter.wait()
            try:
                r = session.get(DAILY_STOCK_PRICE_URL, params=params,
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=REQUEST_TIMEOUT_S)
                if r.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(f"HTTP {r.status_code}")
                r.raise_for_status()
                return r.json()
            except (requests.RequestException, ValueError) as exc:
                if attempt == MAX_ATTEMPTS:
                    raise
                LOGGER.warning("%s..%s p%d attempt %d failed: %s", start, end, page_index, attempt, exc)
                time.sleep(2 ** attempt)
        raise AssertionError("unreachable")
    return get_page


# ---- build ---------------------------------------------------------------------------------

def window_path(cache_dir: Path, start: date, end: date) -> Path:
    return cache_dir / f"dsp_{start:%Y%m%d}_{end:%Y%m%d}.parquet"


def fetch_to_cache(start: date, end: date, cache_dir: Path, get_page: PageFetcher,
                   force: bool = False, today: date | None = None) -> list[Path]:
    """Fetch every window into its own parquet (resumable). The window containing `today`
    is always refetched because its session data is still growing."""
    today = today or date.today()
    cache_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for win_start, win_end in chunk_windows(max(start, HISTORY_START), end):
        path = window_path(cache_dir, win_start, win_end)
        if path.exists() and not force and win_end < today:
            written.append(path)
            continue
        # A page can come back empty mid-window (seen live 31-10-2026 at page 40 of 52);
        # refetching the whole window is the only safe recovery.
        for attempt in range(1, WINDOW_ATTEMPTS + 1):
            try:
                res = fetch_window(win_start, win_end, get_page)
                break
            except PagingError as exc:
                if attempt == WINDOW_ATTEMPTS:
                    raise
                LOGGER.warning("window attempt %d failed, refetching: %s", attempt, exc)
        if res.status not in ("Success", "NoDataFound"):
            raise RuntimeError(f"{win_start}..{win_end}: status {res.status!r}")
        res.frame.with_columns(pl.lit(datetime.now().isoformat(timespec="seconds")).alias("fetched_at")) \
            .write_parquet(path)
        LOGGER.info("%s..%s %s rows=%d", win_start, win_end, res.status, res.frame.height)
        written.append(path)
    return written


def build_layer_a(cache_dir: Path, out_path: Path, allow_mixed_basis: bool = False) -> pl.DataFrame:
    """Concatenate cached windows into one frame with derived columns."""
    paths = sorted(cache_dir.glob("dsp_*.parquet"))
    if not paths:
        raise FileNotFoundError(f"no cached windows in {cache_dir}")
    frames = [pl.read_parquet(p) for p in paths]
    raw = pl.concat([f for f in frames if f.height], how="vertical_relaxed")
    fetch_days = raw.select(pl.col("fetched_at").str.slice(0, 10).unique()).to_series().to_list()
    if len(fetch_days) > 1 and not allow_mixed_basis:
        raise RuntimeError(
            f"windows fetched on {sorted(fetch_days)}: ClosePriceAdjusted may sit on different "
            "adjustment bases -- rerun with --force, or pass allow_mixed_basis=True knowingly"
        )
    out = derive_columns(raw.drop("fetched_at").unique(["ticker", "date"], keep="last")) \
        .with_columns(pl.lit(min(fetch_days)).alias("basis_date"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(out_path)
    return out
