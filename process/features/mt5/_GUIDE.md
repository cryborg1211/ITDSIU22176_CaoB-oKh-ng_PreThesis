# mt5

<!-- Part of wyckoff-thesis -->

## Scope

Independent confirmation engine. Create MT5 custom symbols for HOSE tickers from parquet daily bars, implement the strategy as an MQL5 EA that models VN constraints, and reconcile its trade list against the Python backtest on a representative subset of tickers.

## Key Source Files

- `mt5/Scripts/` -- custom-symbol creation + rates import (planned)
- `mt5/Experts/` -- EA (planned)

## Related Context

- `process/context/all-context.md` -- hard rules (read-only parent, price units, no look-ahead)
- `docs/00-scope-synthesis.md` -- scope and decisions
- `process/context/tests/all-tests.md` -- test commands and must-have test categories

## Current Status

Status: not-started

## Folder Contents

```
process/features/mt5/
  active/       -- in-progress plans for this feature
  completed/    -- archived completed plans
  backlog/      -- deferred/future plans
  reports/      -- feature-specific operational reports
  references/   -- feature-specific research and reference docs
```
