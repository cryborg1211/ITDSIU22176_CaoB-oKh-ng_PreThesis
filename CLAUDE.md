# CLAUDE.md — wyckoff-thesis

Independent repo nested in `stock_price_v3/`. Academic project (pre-thesis → thesis).

## Rules for agents

- Read `docs/00-scope-synthesis.md` first — it holds the scope and the decisions already made.
- Parent repo (`..`) is **read-only** from here: read `../data/ohlcv_*.parquet` and reuse ideas
  from `../src/` by copying/adapting, never import parent modules and never write into `..`.
- Prices in parent parquet are **thousands of VND** and **back-adjusted**; check for
  corporate-action level steps before trusting any trading range (see
  `../scripts/refetch_adjusted_ohlcv.py`).
- `external/` = third-party reference repos. Read them, never edit them, respect their licenses
  (AGPL repos: study only, do not copy code into `src/`).
- Python 3.11, strict type hints, pure functions, Polars preferred.
- Every claimed result must come with: universe, date range, out-of-sample split, costs used.
- No look-ahead: an event is only "known" at the bar where it is confirmed, not where it starts.
