# Edge Catcher — Backlog

## In Progress
- [🔄] **Sports data download** — KXNBASPREAD + KXMLBSPREAD downloading to `data/kalshi_sports.db`. ~9,365 markets, est 10-12GB. Running in background (PID tracked, log at `/tmp/sports_download.log`). KXNBAGAME/KXMLBGAME skipped (18-50K trades/market, too large).
- [🔄] **Paper trader validation** — debut-fade on KXBTC15M running (PID 10449). Through Apr 7 before changes.

## Next Up — Retail Flow Score (Track A)
- [ ] **Design retail flow scoring from trade tape** — use `taker_side` field in existing BTC data to prototype. Count buy-side aggression, cluster by price level, flag imbalanced flow. Series-agnostic (works on any Kalshi data).
- [ ] **Backtest retail flow as entry filter** — add flow score as signal/filter to existing strategies. Does entering ONLY when retail flow is extreme improve win rate?
- [ ] **Apply to sports data** — once download completes, run same flow scoring on KXNBASPREAD

## Next Up — KXFED / Event Overreaction (Track C)
- [ ] **Download KXFED data** — 12K+ vol/market, monthly FOMC settlements. Pure retail-vs-institutional.
- [ ] **Backtest post-announcement mispricing** — do Kalshi KXFED prices overshoot after CPI/NFP/FOMC announcements? Compare to fed funds futures (the "correct" price).
- [ ] **Event overreaction hypothesis** — retail panic-buys "rate hike" contracts when CPI is hot, but bond market already priced it.

## Next Up — Sports Market Pivot (Track B)

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

## Next Up — Polymarket Multi-Venue (Track D)
- [ ] **Polymarket adapter** — add data adapter using CLOB API (public, no auth for reads). Historical timeseries + trades available.
- [ ] **Download Polymarket sports data** — sports markets have 3% taker fee (vs Kalshi 7%). Test flow score + debut-fade.
- [ ] **Polymarket geopolitics scan** — 0% fee category. Any signal = pure profit. Scan for retail flow patterns.
- [ ] **Maker execution prototype** — post limit orders (0% fee everywhere). Detect retail flow → post opposite limit → wait for fill → hold to settlement.
- [ ] **Cross-venue scanner** — same event on Kalshi AND Polymarket → flag price divergence > fee spread.

### Polymarket Fee Reference
| Category | Taker Fee | Maker Fee | Notes |
|----------|-----------|-----------|-------|
| Sports | 3.0% | 0% | Best venue for sports strategies |
| Crypto | 7.2% | 0% | WORSE than Kalshi for taker |
| Finance/Politics | 4.0% | 0% | Decent |
| Geopolitics | 0% | 0% | FREE — any edge = pure profit |
| Economics/Culture/Weather | 5.0% | 0% | Moderate |

## Future — Retail Bias Catalog
- [ ] **Round number anchoring** — retail clusters at 25¢/50¢/75¢. Test if fading round-number prices outperforms random entry.
- [ ] **Panic/FOMO filter (crypto)** — after >5% BTC move, are Kalshi prices systematically mispriced? Extend momentum filter to be a signal, not just a skip condition.
- [ ] **Public team bias (sports)** — popular teams (Lakers, Yankees, Cowboys) trade at premium. Fade public favorites.

## Parked
- [ ] **Maker execution design** — deprioritized, strategies are fundamentally taker
- [ ] **Active trading (exit before expiry)** — park until sports edge proven
- [ ] **Unified paper trader refactor** — architecture debt, after sports validation
- [ ] **Entry range optimization (BTC)** — BTC edge too thin after fees
- [ ] **Volume filter threshold sweep (BTC)** — same reason
- [ ] **Incremental `since` updates** — low priority, full download works
- [ ] **Backtest UI improvements** — park until sports strategies exist
