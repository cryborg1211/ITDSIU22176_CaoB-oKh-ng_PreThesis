# wyckoff-thesis - All Context

Last updated: 2026-10-30

This file is the root context entrypoint for the repo.

Use it for two things:

1. quick routing to the right context pack or root file
2. broad architecture and repository understanding

Start here before loading deeper context files.

---

## Project Description

Solo academic project: **pre-thesis → thesis**, topic *Wyckoff Pattern Detection for Market Phase
Identification* on the Vietnamese equity market (HOSE).

Goal: automatically detect Wyckoff accumulation / distribution events (SC, AR, ST, Spring, Test,
SOS, LPS, BU / PSY, BC, UTAD, SOW, LPSY) and phases A–E on HOSE daily bars, turn them into
**long-only** entry/exit rules that respect VN market constraints, and validate them with a Python
reference backtest (vectorbt) cross-checked against MetaTrader 5 Strategy Tester on custom symbols.

The full scope, research questions, strategy draft, indicator list, risk ("hệ số an toàn") table,
evaluation plan and open questions live in **`docs/00-scope-synthesis.md`** — read it before any
planning work. That doc is the source of truth for scope decisions; this file holds the durable
operating rules.

Audience: the author, the thesis supervisor, the defense committee. Every result must be
reproducible and defensible, not just profitable.

---

## Hard Rules (read before touching code or data)

These were the project-specific `CLAUDE.md` rules before the harness was installed; they are binding.

- **Parent repo is read-only.** This repo is nested inside `stock_price_v3/` but is an independent
  git repo (the parent ignores `wyckoff-thesis/`). Read `../data/ohlcv_*.parquet` and adapt ideas
  from `../src/` by copying, **never import parent modules and never write into `..`**.
- **Price units and adjustment.** Parent parquet prices are **thousands of VND** and
  **back-adjusted**. Shards that were only tail-appended carry fake level steps at every corporate
  action (878 measured across 362 shards, 18-10-26) — a fake −30% step looks exactly like a Selling
  Climax. Only trust ranges on series refetched onto one adjustment basis
  (`../scripts/refetch_adjusted_ohlcv.py`).
- **No look-ahead.** An event is "known" only at the bar where it is *confirmed*, not the bar where
  it starts. Swing points (zigzag) are confirmed late by construction — account for the lag.
- **`external/` is read-only.** Third-party reference repos as git submodules. Never edit them.
  Respect licenses: AGPL repos are study-only, never copy their code into `src/`.
- **Every claimed result states:** universe, date range, out-of-sample split, costs used.
- **VN market constraints are not optional in any backtest:** long-only, lot 100, HOSE tick sizes,
  ±7% daily band (limit-lock = order may not fill), T+2 settlement (min hold ~3 sessions),
  fees ~0.15–0.25%/side + 0.1% sell tax.
- **Statistics:** report Deflated Sharpe Ratio + PBO and use walk-forward / purged CV. The parent
  repo's lesson: a single good Sharpe means nothing (its own strategy fails DSR robustly).

## Lessons inherited from the parent repo

- Foreign flow is **same-day price impact** (+0.26 Spearman at lag 0, ~0 at t+1) — use as volume
  confirmation, not as a forward predictor. Always include a lag-0 arm in any flow/volume EDA and
  use Spearman on fat-tailed series.
- Existing labels in the parent are **triple-barrier outcome labels**, not Wyckoff phase labels.
  Wyckoff labels must be built here (rule-based weak labels + manual annotation sample).
- Any new OHLCV writer must keep numeric dtypes consistent (int64 vs float64 volume across shards
  crashed `pl.concat` in the parent).

---

## How This File Works (the `all-*.md` Convention)

Every `process/context/` directory has one `all-*.md` entrypoint that acts as an attachable quick
router for that domain. This root file is the top-level router.

1. Agent reads `all-context.md` first (this file)
2. Finds the relevant context group or feature folder from the tables below
3. Reads that group's `all-{group}.md` / the feature's `_GUIDE.md`
4. Only then loads the specific deep doc needed

Never load the whole `process/context/` tree.

## Quick Start

1. read this file
2. read `docs/00-scope-synthesis.md` for scope
3. pick the feature folder for the work (table below)
4. only then load deeper files

## Current Root Entry Points

| File | Read when |
|---|---|
| `process/context/all-context.md` | any substantial planning, research, review, or implementation task |
| `docs/00-scope-synthesis.md` | any scope, strategy, methodology, or evaluation question |
| `process/context/tests/all-tests.md` | testing, verification, debugging test failures |
| `process/context/planning/all-planning.md` | plan-shape calibration, SIMPLE vs COMPLEX reference docs |

## Current Context Groups

| Group | Entry point | Scope |
|---|---|---|
| `planning/` | `process/context/planning/all-planning.md` | plan-shape calibration, planning examples |
| `tests/` | `process/context/tests/all-tests.md` | pytest runner, commands, debugging, gaps |

No domain groups yet — create one (e.g. `data/`, `wyckoff-domain/`) when a topic reaches 3+
durable docs.

## Current Features

| Feature | Folder | Status |
|---|---|---|
| Data layers (SSI 2020+, VCI refetch 2013+, index) | `process/features/data/` | in-progress |
| Wyckoff detector (rule-based → hybrid ML) | `process/features/detector/` | not-started |
| Labeling (guideline + manual annotation) | `process/features/labeling/` | not-started |
| Python backtest (vectorbt) | `process/features/backtest/` | not-started |
| MetaTrader 5 (custom symbols + EA) | `process/features/mt5/` | not-started |
| Thesis report | `process/features/report/` | not-started (template pending university) |

## Task Routing Table

| If the task involves... | Start with |
|---|---|
| scope, research questions, strategy | `docs/00-scope-synthesis.md` |
| architecture or stack questions | this file |
| datasets, SSI API, price adjustment | `process/features/data/_GUIDE.md` |
| detector / events / phases | `process/features/detector/_GUIDE.md` |
| ground-truth labels, annotation | `process/features/labeling/_GUIDE.md` |
| backtest, costs, metrics | `process/features/backtest/_GUIDE.md` |
| MT5, MQL5, custom symbols | `process/features/mt5/_GUIDE.md` |
| writing the thesis, figures, citations | `process/features/report/_GUIDE.md` |
| testing or verification | `process/context/tests/all-tests.md` |
| creating a new plan | `process/context/planning/all-planning.md` |

## Context Group Lifecycle

Context groups are durable knowledge domains, not feature folders.

Create a group when: a topic has 3+ durable docs; a single doc exceeds ~800 lines with separable
subtopics; agents repeatedly need one slice of a large file; the topic is a stable domain.

Do not create a group for temporary reports, plans, or feature-specific content (that belongs in
`process/features/...`). Move or split one group at a time. Run `vc-audit-context` after every
context organization change.

## Naming Convention

No `README.md` files inside `process/context/`. Entrypoints use `all-*.md`:
root `process/context/all-context.md`, group `process/context/{group}/all-{group}.md`.

## Context Update Protocol

1. update the smallest relevant context file
2. update this file if routing, ownership, naming, groups or features changed
3. update the owning `all-{group}.md` entrypoint when a group exists
4. run `vc-audit-context`

---

## Repository Structure

```
wyckoff-thesis/
  CLAUDE.md, AGENTS.md    -- managed harness protocol (RIPER-5), do not adapt
  README.md               -- human overview
  docs/
    00-scope-synthesis.md -- scope + decisions + open questions (source of truth)
    literature/           -- papers, notes, annotated bibliography
  src/wyckoff/            -- detector library (swings, trading ranges, events, phases) -- empty
  mt5/
    Experts/              -- MQL5 EA (VN constraints modelled inside)
    Scripts/              -- custom-symbol creation / rates import
  notebooks/              -- EDA, labeling, report figures
  tests/                  -- pytest
  data/                   -- local cache, git-ignored
  external/
    vectorbt/             -- shallow submodule, reference only
  process/                -- agent harness workspace (context, plans, features)
  .claude/                -- agents (12), skills (31), hooks
```

`report/` -- LaTeX thesis (IU SCSE format, `iuthesis.sty`, `main.tex`, 7 chapter skeletons).
MT5 is both the confirmation engine and the GUI/demo (phase indicator + Strategy Tester visual
mode); no Streamlit.

## Technology Stack

- **Language:** Python 3.11 (strict type hints), MQL5 for the MT5 EA/scripts
- **Data:** Polars (preferred) + PyArrow parquet; source = parent repo shards + SSI FastConnect API
- **Backtest (primary):** vectorbt (reference copy in `external/vectorbt`; install via pip)
- **Backtest (confirmation):** MetaTrader 5 Strategy Tester on custom symbols; Python
  `MetaTrader5` package (Windows-only) — **not installed yet**
- **Indicators:** TA-Lib (planned), own implementations for VSA spread/volume, Weis Wave, P&F count
- **Testing:** pytest
- **Report:** LaTeX template TBD (university-dependent)
- **Not used:** vnstock (useful features are premium; SSI covers the need)

No dependency manifest yet — create `requirements.txt` (pinned) with the first code.

## Key Patterns and Conventions

- Pure functions + procedural orchestration, no deep OOP. Polars-native pipelines.
- Detector output must be timestamped at **confirmation bar**; keep a `start_bar` and a
  `confirm_bar` separately for every event.
- Parameters of the detector (swing threshold, range min length, volume z-score cutoffs) live in
  one config object, never magic numbers scattered in code — they are what gets swept and must be
  counted as trials for DSR.
- Thresholds that depend on price band or tick size are per-exchange constants (HOSE only for now).
- Figures for the report are produced by code in `notebooks/` / `src/`, never edited by hand.

## Environment and Configuration

- `.env` (git-ignored) for secrets. SSI FastConnect uses the same key names as the parent:
  `Consumer_Key`, `ConsumerSecret_Key`.
- Parent data path (read-only): `../data/ohlcv_*.parquet`.

## Institution and report format

- International University – VNU-HCM, School of Computer Science and Engineering, Bachelor of
  Data Science (student ID prefix `ITDSIU`). Thesis is written in **English**.
- Both LaTeX and Word are accepted (past theses: Phan Manh Son 2025 = LaTeX/pdfTeX; Pham Dong Quan
  2025 = Word). Front matter used by both: cover (VNU-HCM / IU / SCSE, title, name + ID,
  supervisor, "A thesis submitted to the School of Computer Science and Engineering in partial
  fulfillment of the requirements for the degree of Bachelor of Data Science"), committee approval
  page, acknowledgements, TOC, lists of tables/figures/abbreviations, abstract.
- Typical chapters: Introduction → Related Work/Literature Review → Methodology → Implementation /
  Experiments & Results → Discussion & Future Work → Conclusion → References. ~55–80 pages.
- Bar to clear vs past IU trading theses: they used free/US data or vnstock, a single train/test
  split, **no transaction costs**, and no VN market mechanics. This thesis's differentiators are
  exactly those: VN costs + constraints, walk-forward, DSR/PBO, labeled ground truth, two engines.

## Open Questions

See `docs/00-scope-synthesis.md` §12 — whether MT5 is mandatory, intraday or not, second annotator.

## Scan Metadata

- Generated: 2026-10-30
- HEAD: 3179ee1 (before harness commit)
- Mode: fresh (Flow B — pre-existing CLAUDE.md content migrated here)
- Package manager: pip (no manifest yet)
