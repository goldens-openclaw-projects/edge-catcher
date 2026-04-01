# Edge Catcher — Backlog

## In Progress
- [🔄] **Sports data download** — KXNBASPREAD + KXMLBSPREAD downloading to `data/kalshi_sports.db`. ~9,365 markets, est 10-12GB. Running in background (PID tracked, log at `/tmp/sports_download.log`). KXNBAGAME/KXMLBGAME skipped (18-50K trades/market, too large).
- [🔄] **Paper trader validation** — debut-fade on KXBTC15M running (PID 10449). Through Apr 7 before changes.

## Next Up — Sports Market Pivot

### Phase 2a — Data & Research (current focus)
- [x] Download Kalshi sports data (KXNBASPREAD, KXMLBSPREAD) — in progress
- [ ] **Sign up for OddsPapi free tier** — 250 req/mo, includes Pinnacle historical, no multiplier
- [ ] **Pull sample closing lines** — 20-30 NBA/MLB games that overlap with our Kalshi data
- [ ] **Eyeball test** — manually compare Kalshi opening prices vs Pinnacle closing lines for 10+ games
- [ ] **Debut-fade on KXNBASPREAD** — backtest first-trade mispricing on sports spreads

### Phase 2b — Cross-Reference Strategy
- [ ] Build CLV (Closing Line Value) hypothesis module
- [ ] Automated Kalshi ↔ Pinnacle price cross-reference
- [ ] Fee-adjusted backtests for all sports strategies
- [ ] Volume filter transfer test — does low-volume filter work on sports?

### Phase 2c — Live Trading ($49/mo OddsPapi Pro)
- [ ] Only if research shows >5¢ avg mispricing after fees
- [ ] OddsPapi WebSocket → Pinnacle real-time lines
- [ ] Live monitor: Pinnacle implied price vs Kalshi orderbook → signal
- [ ] Paper trade 2 weeks before any real capital

## BTC Strategies (Maintenance Mode)
- [x] Debut-fade paper trading live (KXBTC15M) — Sharpe 4.23 after 7% taker fee, +$10.95/yr
- [x] Cstack validated but marginal (+$9.97/yr taker, Sharpe 0.24)
- [x] Sweet-spot killed (79% WR, needs 85%)
- [x] TP/SL exits all negative — hold-to-settlement is correct
- [x] Filter stacking validated (Cstack = best combo)
- [x] Fee bug fixed (commit 2adb652)

## Completed
- [x] Paper trader Discord logging fix (Golden fixed .env space, restarted)
- [x] Fee model added to backtester (--fee-pct flag)
- [x] Fee bug fixed — PnL now accounts for entry fees
- [x] Strategy findings documented (reports/strategy-findings-2026-03-31.md)
- [x] Research agenda documented (reports/research-agenda-2026-04-01.md)
- [x] Kalshi BTC data download complete (16.7M trades, 23GB)
- [x] ROADMAP.md + BACKLOG.md created

## Parked
- [ ] **Maker execution design** — deprioritized, strategies are fundamentally taker
- [ ] **Active trading (exit before expiry)** — park until sports edge proven
- [ ] **Unified paper trader refactor** — architecture debt, after sports validation
- [ ] **Entry range optimization (BTC)** — BTC edge too thin after fees
- [ ] **Volume filter threshold sweep (BTC)** — same reason
- [ ] **Incremental `since` updates** — low priority, full download works
- [ ] **Backtest UI improvements** — park until sports strategies exist
