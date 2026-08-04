"""Technical indicator feature calculations."""

from typing import List, Optional, Tuple

import numpy as np


class TechnicalFeatures:
    """Calculate technical indicators."""

    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index (RSI).

        RSI = 100 - (100 / (1 + RS))
        where RS = average gain / average loss

        Args:
            prices: List of prices (oldest first)
            period: Period for RSI calculation

        Returns:
            RSI value (0-100) or None
        """
        if not prices or len(prices) < period + 1:
            return None

        deltas = np.diff(prices)
        seed = deltas[:period]

        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0

        rsi = 100 - (100 / (1 + rs))

        for delta in deltas[period:]:
            if delta > 0:
                up = (up * (period - 1) + delta) / period
                down = down * (period - 1) / period
            else:
                up = up * (period - 1) / period
                down = (down * (period - 1) - delta) / period

            rs = up / down if down != 0 else 0
            rsi = 100 - (100 / (1 + rs))

        return round(float(rsi), 2)

    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26) -> Optional[dict]:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            prices: List of prices (oldest first)
            fast: Fast EMA period
            slow: Slow EMA period

        Returns:
            Dictionary with MACD, signal, histogram or None
        """
        if not prices or len(prices) < slow + 1:
            return None

        ema_fast = TechnicalFeatures._ema(prices, fast)
        ema_slow = TechnicalFeatures._ema(prices, slow)

        if ema_fast is None or ema_slow is None:
            return None

        macd = ema_fast - ema_slow
        signal = TechnicalFeatures._ema([macd], 9)  # MACD signal line
        histogram = macd - (signal or 0)

        return {
            "macd": round(float(macd), 3),
            "macd_signal": round(float(signal), 3) if signal else None,
            "macd_histogram": round(float(histogram), 3),
        }

    @staticmethod
    def bollinger_bands(
        prices: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Optional[dict]:
        """Calculate Bollinger Bands.

        Args:
            prices: List of prices
            period: Period for moving average
            std_dev: Number of standard deviations

        Returns:
            Dictionary with upper, middle, lower bands and position
        """
        if not prices or len(prices) < period:
            return None

        recent = prices[-period:]
        middle = np.mean(recent)
        std = np.std(recent)

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        # Position within bands: 0 = lower, 1 = upper
        current_price = prices[-1]
        if upper != lower:
            position = (current_price - lower) / (upper - lower)
            position = max(0, min(1, position))  # Clamp to [0, 1]
        else:
            position = 0.5

        return {
            "bb_upper": round(float(upper), 3),
            "bb_middle": round(float(middle), 3),
            "bb_lower": round(float(lower), 3),
            "bb_width": round(float(upper - lower), 3),
            "bb_position": round(float(position), 3),
        }

    @staticmethod
    def stochastic(prices: List[float], period: int = 14) -> Optional[dict]:
        """Calculate Stochastic Oscillator.

        Args:
            prices: List of prices
            period: Period for stochastic

        Returns:
            Dictionary with K and D values or None
        """
        if not prices or len(prices) < period:
            return None

        recent = prices[-period:]
        low = min(recent)
        high = max(recent)
        current = prices[-1]

        if high == low:
            k = 50
        else:
            k = ((current - low) / (high - low)) * 100

        return {
            "stochastic_k": round(float(k), 2),
            "stochastic_high": round(float(high), 3),
            "stochastic_low": round(float(low), 3),
        }

    @staticmethod
    def _ema(prices: List[float], period: int) -> Optional[float]:
        """Calculate exponential moving average (helper).

        Args:
            prices: List of prices
            period: EMA period

        Returns:
            EMA value or None
        """
        if not prices or len(prices) < period:
            return None

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = price * multiplier + ema * (1 - multiplier)

        return ema
