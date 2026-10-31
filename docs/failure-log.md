# Failure log

Every failure, bug, rejected approach or broken run, recorded **when it is found**, with the
version it happened on. Source material for the thesis (methodology iterations, limitations,
"what did not work"). Never rewrite git history that removes a version listed here.

Entry format:

```
## YYYY-MM-DD — short title
- Version: <commit sha> (tag `fail/<slug>` if worth pinning)
- Area: data | detector | labeling | backtest | mt5 | report | tooling
- Tried: what was attempted
- Failed: exact error / numbers
- Root cause:
- Resolution: what replaced it (commit sha)
- Thesis use: where it may be cited (chapter/section), or "none"
```

---

## 2026-10-30 — winget has no Tectonic package
- Version: 3804b36
- Area: tooling
- Tried: `winget install --id TectonicTypesetting.Tectonic` to compile `report/`
- Failed: `No package found matching input criteria.`
- Root cause: Tectonic is not published on winget
- Resolution: official GitHub release binary 0.17.0 (msvc) into `%LOCALAPPDATA%\Programs\tectonic`
- Thesis use: none

## 2026-10-30 — Overleaf zip from PowerShell 5.1 had backslash paths
- Version: 3804b36
- Area: tooling
- Tried: `Compress-Archive` of `report/` for Overleaf upload
- Failed: zip entries stored as `chapters\01-introduction.tex` (backslash), which breaks
  `\input{chapters/...}` on Linux-based compilers
- Root cause: PS 5.1 `Compress-Archive` uses Windows separators in entry names
- Resolution: rebuilt with `System.IO.Compression` and `/` separators; Overleaf route later dropped
  in favour of local Tectonic
- Thesis use: none

## 2026-10-30 — first compile of the LaTeX template: 3 defects
- Version: 3804b36 (template as first committed, never compiled before)
- Area: report
- Tried: `tectonic -X compile main.tex` (Tectonic 0.17.0, XeTeX engine)
- Failed: (1) BibTeX error, empty `thebibliography` — no `\cite` yet; (2) xdvipdfmx
  `Object @page.i already defined` — cover and approval page both numbered i; (3) bibliography
  lower-cased titles ("The deflated sharpe ratio"); plus the List of Tables caption expanded the
  HOSE acronym on first use
- Root cause: (1) skeleton has citations only in comments; (2) `titlepage` resets the page
  counter; (3) `plainnat` changes title case unless braced; caption used `\gls`
- Resolution: `\nocite{*}` (template only), `pageanchor=false` around the cover, double-braced bib
  titles, short caption with `\acrshort`. Remaining harmless warning: overfull vbox in chapter 4
  from consecutive empty headings (disappears once sections have text)
- Thesis use: none

## 2026-10-31 — SSI layer-A build: empty page mid-window + run crossed midnight
- Version: uncommitted data pipeline (parent of the commit that adds `PagingError`)
- Area: data
- Tried: `python scripts/build_data.py`, full DailyStockPrice pull 2020-01 → 2026-10, 83 windows
- Failed: (1) after 79 windows, `2026-06-28..2026-07-27: page 40 empty with 39000/51674 rows`
  — earlier windows of up to 49,817 rows paged fine, so not a page cap; (2) at ~10 min per
  window the run took ~10 h and crossed midnight, so cached windows carry two fetch days and the
  mixed-adjustment-basis guard refuses to build
- Root cause: (1) transient server-side short page (FastConnect returns HTTP 200 with an empty
  page); (2) the guard keys on calendar day, but `ClosePriceAdjusted` only moves when a session
  (ex-right date) passes — 30-10 Fri evening → 31-10 Sat has none
- Resolution: window-level retry (`PagingError`, 3 attempts) + test; `--allow-mixed-basis` flag,
  used only after refetching a 30-10 window and diffing `close_adj` against the cache
- Thesis use: data-collection section — API reliability and why one adjustment basis matters

## 2026-10-31 — SSI paging silently duplicated rows: layer A was ~35% duplicates
- Version: uncommitted data pipeline, `PAGE_SIZE = 1000` (before the commit that sets 100_000)
- Area: data
- Tried: market-wide `DailyStockPrice` pull, 30-day windows, `pageSize=1000`, collect pages until
  `len(rows) == totalRecord`
- Failed: build "succeeded" but EDA showed HPG with 533 bars over 6.7 years (expected ~1,680) and
  ~5 bars per stock per month by 2023. Per cached window, unique (symbol, date) / rows averaged
  0.65 (worst 0.38): pages overlap, so rows repeat and others are never served. The row count
  still matched `totalRecord`, so the completeness check passed
- Root cause: server-side pagination is not a stable partition of the result set (order is stable
  only within a single page request). Counting rows is not a completeness check; counting
  unique keys is
- Resolution: one page per window (`pageSize=100000`; a 55,649-row window returns whole in ~55 s,
  measured) + guard raising `PagingError` when unique keys != `totalRecord`; regression test;
  full `--force` refetch. Earlier EDA numbers from the corrupt build are discarded
- Thesis use: data-collection section — an API that reports success can still return a wrong
  dataset; validate by key uniqueness and bar counts per ticker, not by HTTP status or row count

## 2026-10-31 — SSI rows that look fine but are not: placeholder bars and partial adjustment
- Version: layer A built 31-10-2026 (single basis), EDA in `scripts/eda_data_layers.py`
- Area: data
- Tried: use SSI `ClosePriceAdjusted` + raw OHLC directly as the detector input
- Failed: 2,479 opening gaps beyond −11% survived on the adjusted series (should be ~0 inside a
  ±7% band). 2,248 of them were zero-volume rows (7.9% of all stock rows) whose OHLC is
  placeholder data; the other 231 were real ex-rights the adjusted close never absorbed
  (SSI adjusts 195 of 350 large ex-rights, and no cash dividends). Also 2,685 rows with
  `ref_price = 0`
- Root cause: the API reports a row for every listed stock every session, traded or not, and its
  adjustment database covers only part of the corporate actions
- Resolution: decided to flag non-trading sessions and compute own back-adjustment from the
  exchange reference price (cleaning module, not yet built). Data choice written up in report §3.1
- Thesis use: data-quality subsection — every listed defect would print a fake climax
