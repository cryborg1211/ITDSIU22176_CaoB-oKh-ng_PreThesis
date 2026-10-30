# detector

<!-- Part of wyckoff-thesis -->

## Scope

Automatic detection of Wyckoff trading ranges, events (SC, AR, ST, Spring, Test, SOS, LPS, BU; PSY, BC, UTAD, SOW, LPSY) and phases A-E on HOSE daily bars. Baseline is rule-based (zigzag swings + trading range + relative volume/spread rules); thesis extends to a hybrid where rules generate candidates and an ML model filters them (meta-labeling).

## Key Source Files

- `src/wyckoff/` -- detector library (planned: swings, ranges, events, phases, config)
- `docs/00-scope-synthesis.md` sections 4 and 7 -- strategy draft and indicators

## Related Context

- `process/context/all-context.md` -- hard rules (read-only parent, price units, no look-ahead)
- `docs/00-scope-synthesis.md` -- scope and decisions
- `process/context/tests/all-tests.md` -- test commands and must-have test categories

## Current Status

Status: not-started

## Folder Contents

```
process/features/detector/
  active/       -- in-progress plans for this feature
  completed/    -- archived completed plans
  backlog/      -- deferred/future plans
  reports/      -- feature-specific operational reports
  references/   -- feature-specific research and reference docs
```
