# data

<!-- Part of wyckoff-thesis -->

## Scope

Datasets the whole thesis runs on. Two price layers plus the index series, all in absolute VND:

- **Layer A** `data/hose_daily_ssi.parquet` — SSI FastConnect `DailyStockPrice`, market-wide HOSE
  pull per <=30-day window, 2020-01 → today. Raw OHLC, reference/ceiling/floor, adjusted close
  (single basis per build), adjusted OHL + volume, limit flags, foreign flow. Survivorship-free.
- **Layer B** `data/hose_daily_vci.parquet` — parent repo's one-pass vnstock (VCI) refetch,
  2013 → 2026-10-18, adjusted OHLCV only, currently-listed tickers only.
- **Index** `data/index_daily.parquet` — official DailyIndex VNINDEX / VN30 / VN100 (close,
  volume, breadth counts; no OHLC).

Which start date the thesis uses is decided by the EDA in `docs/eda/data-layers.md`.

## Key Source Files

- `src/wyckoff/data/ssi_fastconnect.py` — layer A fetch, paging, rate limit, derived columns,
  mixed-basis guard
- `src/wyckoff/data/legacy_vci.py` — layer B + index loaders (read parent data read-only)
- `scripts/build_data.py` — build CLI (`--force` refetches every window onto one basis)
- `scripts/eda_data_layers.py` — layer comparison, writes `docs/eda/data-layers.md` + figures
- `tests/test_ssi_fastconnect.py`, `tests/test_legacy_vci.py`

## Source constraints (measured live 30-10-2026)

- `DailyStockPrice` history starts 2020-01 (`NoDataFound` before)
- window > 30 calendar days → status `Error`, zero rows
- market-wide pull includes covered warrants and funds → `instrument` column
- credentials: `Consumer_Key` / `ConsumerSecret_Key` from `.env`, falling back to `../.env`
- a rebuild that mixes windows fetched on different days may mix adjustment bases → refused
  unless `--force` refetches everything (`--allow-mixed-basis` only after `scripts/verify_basis.py`
  shows zero `close_adj` diffs)
- **paging is not a stable partition** (pages overlap, ~35% duplicates at pageSize 1000 while the
  row count still matches `totalRecord`) → one page per window (`pageSize=100000`) and a
  unique-key guard (`PagingError`)
- zero-volume rows (7.9%) carry placeholder OHLC → treat as non-trading, never as bars
- `ClosePriceAdjusted` is date-aligned but incomplete (195 of 350 large ex-rights; no cash
  dividends) → own back-adjustment from `ref_price` is the next step

## Decision (31-10-2026)

Main sample = layer A from 2020-02-26. Layer B pre-2020 = robustness check only, never spliced.
Write-up: `report/chapters/03-methodology.tex` §Data.

## Next

Cleaning module: non-trading flag, `ref_price = 0` repair, own ref-price back-adjustment
(investigate the ~4.7% of sessions where ref/previous close is neither 1 nor an ex-right).

## Related Context

- `process/context/all-context.md` — hard rules (read-only parent, no look-ahead)
- `docs/00-scope-synthesis.md` §5 — data scope
- `report/chapters/03-methodology.tex` §Data — where the data decisions are written up

## Current Status

Status: in-progress

## Folder Contents

```
process/features/data/
  active/       -- in-progress plans for this feature
  completed/    -- archived completed plans
  backlog/      -- deferred/future plans
  reports/      -- feature-specific operational reports
  references/   -- feature-specific research and reference docs
```
