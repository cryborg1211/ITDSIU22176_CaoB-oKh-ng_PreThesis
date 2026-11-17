# An AI-Driven Decision Support System for Intelligent Stock Trading

*Nghiên cứu và phát triển hệ thống hỗ trợ ra quyết định giao dịch chứng khoán thông minh dựa trên
trí tuệ nhân tạo* (official title since 04-11-2026; earlier working title: Wyckoff Pattern Detection
for Market Phase Identification). The text below describes the Wyckoff scope and is pending the
scope decision in `docs/01-qtradex-assessment.md`.

Pre-thesis → thesis workspace. Target market: Vietnam equities (HOSE).

Goal: detect Wyckoff accumulation / distribution phases and events on HOSE stocks,
turn them into long-only entry/exit rules that respect VN market constraints
(T+2 settlement, ±7% price band, lot 100, no retail shorting), and validate them
with a Python reference backtest cross-checked against MetaTrader 5 Strategy Tester
on custom symbols.

## Layout

| Path | Purpose |
|---|---|
| `docs/00-scope-synthesis.md` | Scope, decisions, open questions — **start here** |
| `docs/literature/` | Papers, notes, annotated bibliography |
| `src/wyckoff/` | Detector library (swings, trading ranges, events, phases) |
| `mt5/Experts/`, `mt5/Scripts/` | MQL5 EA + custom-symbol import script |
| `notebooks/` | EDA, labeling, figures for the report |
| `tests/` | pytest |
| `data/` | Local data cache (git-ignored) |
| `external/` | Reference repos (git submodules, read-only) |

## Relationship to the parent repo

This folder lives inside `stock_price_v3/` but is an **independent git repo**
(ignored by the parent). It reads the parent's OHLCV parquet shards read-only
(`../data/ohlcv_*.parquet`) and never writes back into the parent.
