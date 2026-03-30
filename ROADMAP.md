# Edge Catcher — Roadmap

## Current State (v0.1 — Complete)
- [x] Kalshi REST adapter (markets + trades, paginated, resumable)
- [x] SQLite storage layer (WAL, incremental upserts, 90-day archive)
- [x] Hypothesis registry + Bonferroni correction
- [x] Statistical engine (proportions_ztest, clustered SEs, HLZ threshold)
- [x] 5-verdict system with fee-adjusted edge
- [x] AI workflow: formalize (English → config + stub) + interpret (JSON → English)
- [x] 60-test pytest suite

---

## Phase 1 — Web UI ✅ Complete
**Goal:** Browser dashboard wrapping existing CLI pipeline.
- [x] FastAPI backend (9 endpoints) + React/Vite frontend (4 views, dark mode, Tailwind)
- [x] Pre-built, served by FastAPI. 67 tests passing. Pushed to main.

---

## Phase 2 — Multi-Market Adapter
**Goal:** Prove the adapter pattern works cross-market. Sports is the target.

- [ ]  (or equivalent public odds API)
- [ ] Shared  /  dataclasses already handle cross-market data
- [ ] Reference hypothesis for sports (e.g., closing line value)
- [ ] Adapter docs + example for community contributions

---

## Phase 3 — AI Closes the Implement Gap
**Goal:** Full pipeline automation. User inputs hypothesis in English → AI generates + writes the stats module → human reviews → run.

- [ ] AI-generated hypothesis modules (AI writes the Python, not just the stub)
- [ ] Human review gate before execution (diff view in UI)
- [ ] Confidence scoring: AI flags low-confidence generated tests for manual review
- [ ] Fallback: revert to manual stub if AI confidence < threshold

---

## Phase 4 — Live Data & Agent Backtesting (In Progress)
**Goal:** Real-time edge monitoring + agent-driven backtesting.

- [x] WebSocket adapter (paper_trader.py — Kalshi WS, live ticker subscription)
- [x] Paper trader systemd service (edge-catcher-paper-trader)
- [x] Multi-strategy support: Strategy A (YES 70-99¢), Strategy B (contrarian NO on momentum drops)
- [x] Discord webhook notifications on every trade (buy/win/loss, tagged by strategy)
- [x] Daily P&L cron reporting
- [x] Hypothesis analysis against 16.7M historical trades (4 hypotheses validated)
- [ ] **Active trading (exit before expiry)** — the key scaling unlock. Track yes_bid from WS/orderbook, implement take-profit exits (e.g. buy at 85¢, sell at 92¢), stop-loss, and capital recycling within each contract's lifetime. Enables multiple round-trips per hour vs one hold-to-settlement. Requires: bid tracking, exit logic, P&L per round-trip. Build after hold-to-settlement edge is validated live.
- [ ] Live signal alerts beyond paper trades
- [ ] Agent backtesting: spawn AI agent against live DB pipeline to validate edge continuously
- [ ] Candlesticks table — wire up OHLCV aggregation

---

## Contributing
See  for the adapter interface.
See  for the hypothesis template.
All new adapters + hypotheses auto-discover via the registry — no core changes needed.
