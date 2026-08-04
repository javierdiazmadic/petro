"""Unit tests for feature calculators."""

from datetime import datetime

import pytest

from petro.features.calculators.economic import EconomicFeatures
from petro.features.calculators.news_derived import NewsDerivedFeatures
from petro.features.calculators.statistical import StatisticalFeatures
from petro.features.calculators.technical import TechnicalFeatures
from petro.features.calculators.temporal import TemporalFeatures


class TestEconomicFeatures:
    """Tests for economic feature calculations."""

    def test_price_changes(self):
        """Test price change calculations."""
        current = 1.50
        prev_prices = {
            "price_1d_ago": 1.48,
            "price_7d_ago": 1.45,
            "price_30d_ago": 1.40,
        }

        result = EconomicFeatures.calculate_price_changes(current, prev_prices)

        assert result["price_1d_ago_change"] == pytest.approx(0.02, abs=0.01)
        assert result["price_1d_ago_change_pct"] > 0
        assert result["price_30d_ago_change"] > 0

    def test_spreads(self):
        """Test spread calculations."""
        result = EconomicFeatures.calculate_spreads(
            brent=85.0,
            wti=82.0,
            eurusd=1.08,
        )

        assert result["brent_wti_spread"] == 3.0
        assert result["eurusd_ratio"] == 1.08


class TestTemporalFeatures:
    """Tests for temporal features."""

    def test_extract_temporal(self):
        """Test temporal feature extraction."""
        dt = datetime(2026, 8, 4, 14, 30, 0)  # Tuesday, summer

        result = TemporalFeatures.extract_temporal_features(dt)

        assert result["day_of_week"] == 1  # Tuesday
        assert result["month"] == 8
        assert result["hour"] == 14
        assert result["is_weekend"] == 0
        assert result["season"] == "summer"

    def test_weekend_detection(self):
        """Test weekend detection."""
        saturday = datetime(2026, 8, 1, 12, 0, 0)
        result = TemporalFeatures.extract_temporal_features(saturday)
        assert result["is_weekend"] == 1

    def test_trading_hours(self):
        """Test trading hours detection."""
        trading_time = datetime(2026, 8, 4, 14, 0, 0)  # 2 PM, Tuesday
        result = TemporalFeatures.is_trading_hours(trading_time)
        assert result == 1

        after_hours = datetime(2026, 8, 4, 18, 0, 0)  # 6 PM
        result = TemporalFeatures.is_trading_hours(after_hours)
        assert result == 0


class TestStatisticalFeatures:
    """Tests for statistical features."""

    def test_moving_average(self):
        """Test moving average calculation."""
        prices = [1.40, 1.42, 1.44, 1.43, 1.45, 1.47, 1.46, 1.48, 1.50]
        ma = StatisticalFeatures.moving_average(prices, 3)

        # Last 3: [1.50, 1.48, 1.46]
        expected = (1.50 + 1.48 + 1.46) / 3
        assert ma == pytest.approx(expected, abs=0.01)

    def test_volatility(self):
        """Test volatility calculation."""
        prices = [1.40, 1.42, 1.44, 1.40, 1.35, 1.38, 1.42, 1.45, 1.48, 1.50]
        vol = StatisticalFeatures.volatility(prices, 5)

        assert vol is not None
        assert vol > 0

    def test_momentum(self):
        """Test momentum calculation."""
        prices = [1.40] * 10 + [1.50]  # Last 10 are baseline, current is higher
        momentum = StatisticalFeatures.price_momentum(prices, 10)

        # (1.50 - 1.40) / 1.40 * 100 ≈ 7.14%
        assert momentum == pytest.approx(7.14, abs=0.1)

    def test_lag_features(self):
        """Test lag feature creation."""
        prices = list(range(100, 110))  # [100, 101, ..., 109]
        result = StatisticalFeatures.lag_features(prices, [1, 5])

        assert result["price_lag_1d"] == 108
        assert result["price_lag_5d"] == 104


class TestTechnicalFeatures:
    """Tests for technical indicators."""

    def test_rsi_oversold(self):
        """Test RSI in oversold condition."""
        prices = [100] * 20 + [90, 85, 80, 75, 70]  # Downtrend
        rsi = TechnicalFeatures.rsi(prices, 14)

        assert rsi is not None
        assert rsi < 30  # Oversold < 30

    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        prices = [1.45 + (i * 0.01) for i in range(20)]
        bb = TechnicalFeatures.bollinger_bands(prices, period=10)

        assert bb is not None
        assert bb["bb_lower"] < bb["bb_middle"] < bb["bb_upper"]
        assert 0 <= bb["bb_position"] <= 1


class TestNewsDerivedFeatures:
    """Tests for news-derived features."""

    def test_news_count_metrics(self):
        """Test news count calculations."""
        articles_7d = [{"sentiment_score": 0.5}] * 14

        result = NewsDerivedFeatures.news_count_metrics(articles_7d, articles_7d)

        assert result["news_count_7d"] == 14
        assert result["news_avg_per_day_7d"] == 2.0

    def test_sentiment_distribution(self):
        """Test sentiment distribution."""
        articles = [
            {"sentiment_score": 0.8},
            {"sentiment_score": -0.7},
            {"sentiment_score": 0.1},
        ]

        result = NewsDerivedFeatures.sentiment_distribution(articles)

        assert result["positive_news_count"] >= 1
        assert result["negative_news_count"] >= 1
