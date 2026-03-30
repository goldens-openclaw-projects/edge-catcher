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

## Phase 1 — Web UI (Next)
**Goal:** Browser dashboard wrapping existing CLI pipeline. Zero new infrastructure — FastAPI serves the existing Python engine, React visualizes it.

### Backend (FastAPI)
- [ ]  — DB stats (market count, trade count, last download)
- [ ]  — trigger incremental download (background task)
- [ ]  — download progress (SSE stream)
- [ ]  — AI hypothesis formalization
- [ ]  — run backtest for hypothesis
- [ ]  — list analysis history
- [ ]  — single result detail
- [ ]  — AI interpretation of result
- [ ]  — list registered hypotheses
- [ ] Auth: single API key header (set in .env)

### Frontend (React + Vite)
- [ ] Dashboard: DB stats card, last-run verdicts, quick-action buttons
- [ ] Hypothesis panel: list hypotheses, show verdict badges
- [ ] Run panel: trigger download/analyze, stream progress log
- [ ] Results table: sortable by verdict, t-stat, edge, timestamp
- [ ] Result detail: bucket breakdown chart, AI interpretation panel
- [ ] Formalize flow: text input → AI output → editable config preview

### Constraints
- No new DB schema changes
- UI is optional — CLI must remain fully functional without it
- FastAPI wraps existing Python modules; no logic duplication

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

## Phase 4 — Live Data & Agent Backtesting
**Goal:** Real-time edge monitoring + agent-driven backtesting.

- [ ] WebSocket/polling adapter ( — stub exists in )
- [ ] Live signal alerts (Discord/webhook) when edge condition detected
- [ ] Agent backtesting: spawn AI agent against live DB pipeline to validate edge continuously
- [ ] Candlesticks table already in schema — wire up OHLCV aggregation

---

## Contributing
See  for the adapter interface.
See  for the hypothesis template.
All new adapters + hypotheses auto-discover via the registry — no core changes needed.
