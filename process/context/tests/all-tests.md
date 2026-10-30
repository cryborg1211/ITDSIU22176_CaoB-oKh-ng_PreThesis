# wyckoff-thesis - All Tests

Last updated: 2026-10-30

Attach this file first when the task involves testing, verification, or test debugging.
Do not load the whole `process/context/tests/` folder by default. Start here, then drill down.

---

## What This Covers

- test runner selection and commands
- what must be tested in a research codebase (look-ahead, units, costs)
- current testing gaps

## Read This When

- running tests after implementation
- adding a detector rule, cost model, or data loader
- debugging failing tests

## Quick Routing

(No deeper test docs yet. Add routing entries here as they are created.)

## Quick Decision Guide

### Use `pytest` for everything Python

- unit tests for pure functions in `src/wyckoff/` (swings, ranges, event rules, cost model)
- small synthetic OHLCV fixtures built in code — never depend on `data/` or the parent's parquet
  in unit tests (they are git-ignored and machine-specific)

### Use MT5 Strategy Tester for MQL5

- no automated runner; verify the EA by reproducing a Python backtest on the same custom symbol
  and comparing trade lists. Record the comparison in `process/features/mt5/reports/`.

## Must-have test categories

1. **No look-ahead:** for every event detector, truncating the series at bar t must not change any
   event confirmed at or before t.
2. **Units:** prices in thousands of VND are scaled before tick-size / lot / cost math.
3. **VN constraints:** long-only, lot 100, ±7% band fill rule, T+2 minimum hold, fees + sell tax.
4. **Adjustment steps:** a synthetic corporate-action step must not be detected as a climax once
   the series is on one adjustment basis.

## Default Verification Order

1. run the narrowest test file
2. run the full suite
3. only then run backtests / notebooks

## Commands

| Scope | Runner | Command |
|---|---|---|
| all | pytest | `python -m pytest -q` |
| one file | pytest | `python -m pytest tests/test_<name>.py -q` |
| one test | pytest | `python -m pytest tests/test_<name>.py::test_<case> -q` |

Run from the `wyckoff-thesis/` root. No `pytest.ini` yet — add one with `testpaths = tests` and
`pythonpath = src` together with the first test.

## Debugging Quick Reference

- Shell: on this machine git-bash is unreliable — use PowerShell.
- `src/` layout: until `pythonpath = src` is configured, imports of `wyckoff` fail in tests.

## Known Gaps

- No tests and no source code yet (scaffold only).
- No automated MT5 verification.
