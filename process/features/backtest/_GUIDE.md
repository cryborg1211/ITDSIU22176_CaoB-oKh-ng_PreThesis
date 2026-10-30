# backtest

<!-- Part of wyckoff-thesis -->

## Scope

Python reference backtest of the Wyckoff entry/exit rules with vectorbt: VN cost and constraint model (long-only, lot 100, tick sizes, +/-7% band, T+2, fees + sell tax), risk sizing (1% NAV risk, R:R floor, position and liquidity caps), walk-forward evaluation, baselines (buy-and-hold VNINDEX, N-day breakout), DSR + PBO reporting.

## Key Source Files

- `external/vectorbt/` -- reference copy (read-only)
- `src/wyckoff/` -- strategy + cost model (planned)
- `docs/00-scope-synthesis.md` sections 8 and 9 -- risk table and evaluation

## Related Context

- `process/context/all-context.md` -- hard rules (read-only parent, price units, no look-ahead)
- `docs/00-scope-synthesis.md` -- scope and decisions
- `process/context/tests/all-tests.md` -- test commands and must-have test categories

## Current Status

Status: not-started

## Folder Contents

```
process/features/backtest/
  active/       -- in-progress plans for this feature
  completed/    -- archived completed plans
  backlog/      -- deferred/future plans
  reports/      -- feature-specific operational reports
  references/   -- feature-specific research and reference docs
```
