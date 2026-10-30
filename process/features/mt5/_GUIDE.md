# mt5

<!-- Part of wyckoff-thesis -->

## Scope

Two roles. (1) Independent confirmation engine: create MT5 custom symbols for HOSE tickers from parquet daily bars, implement the strategy as an MQL5 EA that models VN constraints, and reconcile its trade list against the Python backtest on a representative subset of tickers. (2) GUI / defense demo (replaces Streamlit): an MQL5 indicator that draws trading ranges, event labels and phase A-E shading on the chart; Strategy Tester visual mode for live walkthroughs. The hybrid detector's ML filter is trained in Python and run inside MT5 via ONNX. The MQL5 detector is a second implementation of the Python one; event-list agreement between the two is part of RQ3.

## Key Source Files

- `mt5/Scripts/` -- custom-symbol creation + rates import (planned)
- `mt5/Experts/` -- EA (planned)
- `mt5/Indicators/` -- Wyckoff phase indicator (planned)
- `mt5/Files/` -- ONNX model exported from Python (planned)

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
