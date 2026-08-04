"""Statistical feature calculations."""

from typing import List, Optional

import numpy as np


class StatisticalFeatures:
    """Calculate statistical features from price history."""

    @staticmethod
    def moving_average(prices: List[float], period: int) -> Optional[float]:
        """Calculate simple moving average.

        Args:
            prices: List of prices (oldest first)
            period: Number of periods for MA

        Returns:
            Moving average or None if not enough data
        """
        if not prices or len(prices) < period:
            return None

        ma = np.mean(prices[-period:])
        return round(float(ma), 3)

    @staticmethod
    def exponential_moving_average(
        prices: List[float], period: int, smoothing: float = 2.0
    ) -> Optional[float]:
        """Calculate exponential moving average.

        Args:
            prices: List of prices (oldest first)
            period: Number of periods for EMA
            smoothing: Smoothing factor (default 2.0 for EMA)

        Returns:
            Exponential moving average or None
        """
        if not prices or len(prices) < period:
            return None

        multiplier = smoothing / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = price * multiplier + ema * (1 - multiplier)

        return round(float(ema), 3)

    @staticmethod
    def volatility(prices: List[float], period: int = 20) -> Optional[float]:
        """Calculate price volatility (standard deviation).

        Args:
            prices: List of prices (oldest first)
            period: Number of periods for volatility

        Returns:
            Volatility (standard deviation) or None
        """
        if not prices or len(prices) < period:
            return None

        recent_prices = prices[-period:]
        volatility = np.std(recent_prices)
        return round(float(volatility), 3)

    @staticmethod
    def price_momentum(prices: List[float], period: int = 10) -> Optional[float]:
        """Calculate momentum: current vs N periods ago.

        Args:
            prices: List of prices (oldest first)
            period: Number of periods for momentum

        Returns:
            Momentum percentage or None
        """
        if not prices or len(prices) < period + 1:
            return None

        current = prices[-1]
        past = prices[-(period + 1)]

        if past == 0:
            return None

        momentum = ((current - past) / past) * 100
        return round(momentum, 3)

    @staticmethod
    def lag_features(prices: List[float], lags: List[int]) -> dict:
        """Create lag features (previous prices).

        Args:
            prices: List of prices (oldest first)
            lags: List of lag periods (e.g., [1, 7, 30])

        Returns:
            Dictionary with lag features
        """
        features = {}

        for lag in lags:
            if len(prices) > lag:
                features[f"price_lag_{lag}d"] = round(float(prices[-lag - 1]), 3)
            else:
                features[f"price_lag_{lag}d"] = None

        return features

    @staticmethod
    def price_range(prices: List[float], period: int = 20) -> Optional[float]:
        """Calculate price range (high - low) over period.

        Args:
            prices: List of prices
            period: Number of periods

        Returns:
            Price range or None
        """
        if not prices or len(prices) < period:
            return None

        recent = prices[-period:]
        price_range = max(recent) - min(recent)
        return round(float(price_range), 3)

    @staticmethod
    def returns_skewness(prices: List[float], period: int = 20) -> Optional[float]:
        """Calculate skewness of returns.

        Args:
            prices: List of prices
            period: Number of periods

        Returns:
            Skewness or None
        """
        if not prices or len(prices) < period + 1:
            return None

        recent_prices = prices[-period - 1 :]
        returns = np.diff(recent_prices) / recent_prices[:-1] * 100

        try:
            skewness = float(np.mean(np.power((returns - np.mean(returns)) / np.std(returns), 3)))
            return round(skewness, 3)
        except Exception:
            return None
