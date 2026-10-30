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
