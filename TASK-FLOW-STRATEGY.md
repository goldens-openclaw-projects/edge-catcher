# Task: Build Retail Flow Score Strategy for Backtester

## Context
We discovered that retail flow (small trades ≤10 contracts, taker_side field) predicts settlement outcomes on Kalshi KXBTCD markets. When retail aggressively buys YES (flow > 0.5), YES only settles 43.5% of the time. Fading retail = ~6.5pp edge.

Analysis script: `scripts/retail_flow_analysis.py`

## What to Build

### 1. New Strategy: `StrategyFlowFade` in `edge_catcher/runner/strategies_local.py`

**Logic:**
- Track the first N trades per market (configurable, default 20)
- Compute retail flow score: `(small_yes_vol - small_no_vol) / small_total_vol` where "small" = count ≤ 10
- When flow score crosses threshold (configurable, default ±0.5):
  - Strong retail YES flow (>threshold) → BUY NO (fade retail)
  - Strong retail NO flow (<-threshold) → BUY YES (fade retail)
- Entry price = current market price at the Nth trade
- Hold to settlement (no TP/SL)

**Key parameters (all configurable via __init__):**
- `lookback_trades`: int = 20 (how many trades to score before entering)
- `flow_threshold`: float = 0.5 (minimum |flow| to trigger entry)
- `max_count`: int = 10 (max trade count to be considered "retail")
- `size`: int = 1

**Implementation notes:**
- Must track per-ticker state: trade count, running yes/no volumes for small trades
- Only enter once per ticker (after lookback_trades reached + threshold met)
- Inherits from Strategy base class in `edge_catcher/runner/strategies.py`
- The `on_trade` method receives Trade objects with: ticker, yes_price, no_price, count, taker_side, created_time

### 2. Register in `edge_catcher/__main__.py`

Add alias `Fflow` to the strategy map so it can be invoked via:
```
python -m edge_catcher backtest --series KXBTCD --strategy Fflow --fee-pct 1.0 --start 2025-01-01 --end 2025-12-31
```

### 3. Add variant: `StrategyFlowFade_VolumeFiltered`

Same as StrategyFlowFade but with the VolumeMixin (skip markets with >20 observed trades). Alias: `Ffvol`

### 4. Tests

Add tests in `tests/test_flow_strategy.py`:
- Test that flow score is computed correctly from mock trades
- Test that entry only happens after lookback_trades reached
- Test that threshold filtering works (no entry when |flow| < threshold)
- Test YES and NO entry directions are correct (fade = opposite of flow)

## Files to Modify
- `edge_catcher/runner/strategies_local.py` — add StrategyFlowFade, StrategyFlowFade_VolumeFiltered
- `edge_catcher/__main__.py` — add Fflow, Ffvol to strategy_map
- `tests/test_flow_strategy.py` — new test file

## Trade dataclass reference
Check `edge_catcher/runner/strategies.py` for the Trade NamedTuple/dataclass and Signal format. The Trade object has: ticker, yes_price, no_price (or computed), count, taker_side, created_time. Check the actual field names in the code.

## DO NOT modify
- `edge_catcher/runner/event_backtest.py` (backtester engine)
- `edge_catcher/runner/strategies.py` (base classes)
- Any config files
- The running download process

## After building, run:
```
python -m pytest tests/test_flow_strategy.py -v
python -m edge_catcher backtest --series KXBTCD --strategy Fflow --fee-pct 1.0 --start 2025-10-01 --end 2025-12-31 --output reports/flow_fade_q4_2025.json
```
Note: use Q4 only (3 months) to keep backtest fast — full year takes too long on the Pi.
