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

## Phase 2 — Sports Markets & Multi-Market Adapter
**Goal:** Pivot from BTC binaries to sports event contracts on Kalshi + external odds benchmarking.

### Phase 2a — Kalshi Sports Data Download
- [ ] Download historical trades for KXNBASPREAD, KXMLBSPREAD, KXNBAGAME, KXMLBGAME
- [ ] Scope: 2025 season only (Oct 2024–Jun 2025 for NBA, Mar–Oct 2025 for MLB) — est ~1-2GB
- [ ] Reuse existing Kalshi adapter (same API, different series tickers)
- [ ] Store in same `kalshi.db` or separate `kalshi_sports.db` to keep BTC data isolated

### Phase 2b — External Closing Line Data
- [ ] Evaluate odds API providers for historical closing lines (see cost analysis below)
- [ ] **Best option for research:** OddsPapi free tier (250 req/mo, includes Pinnacle, no multiplier on historical) or The Odds API $30/mo (20K credits, historical costs 10× = ~2K calls)
- [ ] Download closing lines for same games as Kalshi sports data (NBA/MLB 2025)
- [ ] Build cross-reference: Kalshi opening price vs sportsbook consensus closing line
- [ ] **BLOCKER:** Need to validate closing line data actually exists + is accessible before committing

### Phase 2c — Sports Hypothesis Testing
- [ ] Debut-fade on KXNBASPREAD/KXMLBSPREAD (first trade mispricing)
- [ ] Closing Line Value (CLV) strategy: Kalshi price vs Pinnacle/consensus closing line
- [ ] Volume filter transfer test: does low-volume filter work on sports markets too?
- [ ] Fee-adjusted backtests for all sports strategies

### Phase 2d — Adapter Generalization
- [ ] Shared dataclasses already handle cross-market data
- [ ] Reference hypothesis for sports (e.g., closing line value)
- [ ] Adapter docs + example for community contributions

### Cost Analysis — Odds Data Providers
| Provider | Free Tier | Historical Cost | Sharp Lines | Monthly for Research |
|----------|-----------|-----------------|-------------|---------------------|
| **OddsPapi** | 250 req/mo | Same as live (no multiplier) | ✅ Pinnacle, Singbet | $0–$49/mo |
| **The Odds API** | 500 credits/mo | 10× credit multiplier (~50 calls) | ❌ No Pinnacle | $30–$59/mo |
| **SportsGameOdds** | Limited free | Closing odds included | ✅ Pinnacle | $99–$499/mo |
| **Sports-Reference** | Free (web) | Basic closing lines, scrapeable | ❌ Not sharp-specific | $0 |

**Recommendation:** Start with OddsPapi free tier or Sports-Reference scraping for research phase. Upgrade to paid only after validating the cross-reference edge exists.

**Live data cost concern:** For live trading, we'd need real-time odds (~$49-119/mo). Only worth it AFTER research proves the edge is real. The Kalshi side is free (API included with account).

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
