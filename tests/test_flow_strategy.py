"""Tests for StrategyFlowFade retail flow score strategy.

TDD: these tests were written BEFORE the implementation.
"""

from datetime import datetime, timezone

import pytest

from edge_catcher.runner.strategies import Signal
from edge_catcher.storage.models import Market, Trade


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_T0 = datetime(2025, 12, 1, tzinfo=timezone.utc)
_TICKER = 'KXBTCD-25DEC0100000-T100'


def make_trade(ticker=_TICKER, yes_price=50, no_price=50, count=1, taker_side='yes'):
    return Trade(
        trade_id='t',
        ticker=ticker,
        yes_price=yes_price,
        no_price=no_price,
        count=count,
        taker_side=taker_side,
        created_time=_T0,
    )


def make_market(ticker=_TICKER):
    return Market(
        ticker=ticker,
        event_ticker='KXBTCD-25DEC01',
        series_ticker='KXBTCD',
        title='BTC daily',
        status='open',
        result=None,
        yes_bid=49, yes_ask=51, last_price=50,
        open_interest=100, volume=500,
        expiration_time=None, close_time=None,
        created_time=None, settled_time=None,
        open_time=None, notional_value=None,
        floor_strike=None, cap_strike=None,
    )


class MockPortfolio:
    def has_position(self, ticker, strategy_name):
        return False


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFlowScoreComputation:
    """Flow score = (small_yes_vol - small_no_vol) / total_small_vol."""

    def test_strong_yes_flow_triggers_buy_no(self):
        """16 small YES + 4 small NO → flow=0.6 > 0.5 → BUY NO to fade retail."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(16):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)
        for i in range(4):
            signals = strategy.on_trade(make_trade(taker_side='no', count=1), market, portfolio)

        assert len(signals) == 1
        assert signals[0].side == 'no'
        assert signals[0].action == 'buy'

    def test_strong_no_flow_triggers_buy_yes(self):
        """4 small YES + 16 small NO → flow=-0.6 < -0.5 → BUY YES to fade retail."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(4):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)
        for i in range(16):
            signals = strategy.on_trade(make_trade(taker_side='no', count=1), market, portfolio)

        assert len(signals) == 1
        assert signals[0].side == 'yes'
        assert signals[0].action == 'buy'

    def test_flow_uses_contract_count_not_trade_count(self):
        """Large YES trade (count=5) + many NO trades (count=1): volume-weighted flow matters."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        # 4 YES trades of size 5 = 20 YES vol; 16 NO trades of size 1 = 16 NO vol
        # total = 36; flow = (20 - 16) / 36 ≈ 0.111 — below 0.5 threshold
        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(4):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=5), market, portfolio)
        for i in range(16):
            signals = strategy.on_trade(make_trade(taker_side='no', count=1), market, portfolio)

        assert signals == []  # flow too weak after volume-weighting


class TestLookbackEnforcement:
    """Entry should only fire at exactly the Nth trade."""

    def test_no_entry_before_lookback_complete(self):
        """First 19 trades with strong YES flow → no signal yet."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        all_signals = []
        for i in range(19):
            sigs = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)
            all_signals.extend(sigs)

        assert all_signals == []

    def test_entry_fires_at_exactly_nth_trade(self):
        """Signal emitted on the 20th trade with strong YES flow."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        signals = None
        for i in range(20):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)

        assert len(signals) == 1

    def test_no_second_entry_after_nth_trade(self):
        """After the lookback fires, subsequent trades for the same ticker produce no signals."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        for i in range(20):
            strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)

        # Trade 21+
        late_signals = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)
        assert late_signals == []


class TestThresholdFiltering:
    """Weak flow (|flow| < threshold) should produce no signal."""

    def test_no_entry_when_flow_below_threshold(self):
        """12 YES + 8 NO → flow=0.2 — below default 0.5 threshold → no signal."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(12):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)
        for i in range(8):
            signals = strategy.on_trade(make_trade(taker_side='no', count=1), market, portfolio)

        assert signals == []

    def test_entry_at_exact_threshold(self):
        """15 YES + 5 NO → flow = 0.5 exactly — equals threshold → no signal (strict >)."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(15):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)
        for i in range(5):
            signals = strategy.on_trade(make_trade(taker_side='no', count=1), market, portfolio)

        assert signals == []

    def test_custom_threshold(self):
        """With threshold=0.1, even weak flow (12 YES / 8 NO = 0.2) triggers entry."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.1)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(12):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)
        for i in range(8):
            signals = strategy.on_trade(make_trade(taker_side='no', count=1), market, portfolio)

        assert len(signals) == 1


class TestMaxCountFilter:
    """Only trades with count <= max_count are 'retail'."""

    def test_large_trades_ignored_in_flow(self):
        """Trades with count > max_count (10) should NOT contribute to flow score."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        # 10 large YES trades (count=100, ignored) + 10 tiny NO trades (count=1)
        # Only the 10 NO trades count → flow = (0 - 10) / 10 = -1.0 → BUY YES
        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5, max_count=10)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(10):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=100), market, portfolio)
        for i in range(10):
            signals = strategy.on_trade(make_trade(taker_side='no', count=1), market, portfolio)

        assert len(signals) == 1
        assert signals[0].side == 'yes'  # retail selling → fade by buying YES


class TestEntryPrice:
    """Entry price should be current market price at the Nth trade."""

    def test_entry_price_is_no_price_when_buying_no(self):
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(19):
            strategy.on_trade(make_trade(taker_side='yes', count=1, yes_price=60, no_price=40), market, portfolio)
        signals = strategy.on_trade(make_trade(taker_side='yes', count=1, yes_price=62, no_price=38), market, portfolio)

        assert len(signals) == 1
        assert signals[0].price == 38  # no_price from the 20th trade

    def test_entry_price_is_yes_price_when_buying_yes(self):
        from edge_catcher.runner.strategies_local import StrategyFlowFade

        strategy = StrategyFlowFade(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        for i in range(19):
            strategy.on_trade(make_trade(taker_side='no', count=1, yes_price=60, no_price=40), market, portfolio)
        signals = strategy.on_trade(make_trade(taker_side='no', count=1, yes_price=62, no_price=38), market, portfolio)

        assert len(signals) == 1
        assert signals[0].price == 62  # yes_price from the 20th trade


class TestVolumeFilteredVariant:
    """StrategyFlowFade_VolumeFiltered skips markets with >20 observed trades."""

    def test_enters_at_20_trades_within_limit(self):
        from edge_catcher.runner.strategies_local import StrategyFlowFade_VolumeFiltered

        strategy = StrategyFlowFade_VolumeFiltered(lookback_trades=20, flow_threshold=0.5)
        market = make_market()
        portfolio = MockPortfolio()

        signals = []
        for i in range(20):
            signals = strategy.on_trade(make_trade(taker_side='yes', count=1), market, portfolio)

        assert len(signals) == 1

    def test_no_entry_after_volume_limit_exceeded(self):
        """With lookback=10 and volume max=20, entering at trade 10 works; trade 21+ is blocked."""
        from edge_catcher.runner.strategies_local import StrategyFlowFade_VolumeFiltered

        # Use lookback=10 so signal fires at trade 10 (well within volume limit of 20)
        # Then simulate a fresh ticker hitting trade 21 — should be blocked
        TICKER2 = 'KXBTCD-25DEC0200000-T100'
        strategy = StrategyFlowFade_VolumeFiltered(lookback_trades=10, flow_threshold=0.5)
        market2 = make_market(ticker=TICKER2)
        portfolio = MockPortfolio()

        # Feed 21 trades — signal should not fire because volume filter blocks after 20
        signals = []
        for i in range(21):
            signals = strategy.on_trade(
                make_trade(ticker=TICKER2, taker_side='yes', count=1),
                market2, portfolio
            )
        # Trade 21 is blocked by volume filter; entry was at trade 10 (within limit)
        # so there should have been a signal at trade 10, not at trade 21
        # Last call (trade 21) returns [] due to volume filter
        assert signals == []
