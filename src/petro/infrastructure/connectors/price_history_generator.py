"""Historical Price Data Generator - 90 days of daily prices.

Generates realistic 3-month price history with daily variations.
Prices updated once per day (realistic for Spanish fuel market).
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class PriceHistoryGenerator:
    """Generate realistic daily fuel price history for 90 days."""

    # Price ranges in Spain (EUR/L) - realistic
    GASOLINA_95_RANGE = (1.35, 1.55)
    GASOLEOA_RANGE = (1.50, 1.70)

    # Province-specific adjustments (for local market variations)
    PROVINCE_ADJUSTMENTS = {
        "spain": {"gasolina_95": 0.00, "gasoleoa": 0.00},
        "toledo": {"gasolina_95": 0.02, "gasoleoa": 0.01},  # Slightly more expensive in rural Toledo
    }

    def __init__(self, days_back: int = 90, seed: int = None, province: str = "spain", today: datetime = None):
        """Initialize price history generator.

        Args:
            days_back: Number of days of history to generate (default: 90 = 3 months)
            seed: Random seed for reproducible results
            province: Province code for regional price adjustments (default: "spain")
            today: Override today's date (for testing/dynamic generation)
        """
        self.days_back = days_back
        self.province = province.lower()
        self.today = today or datetime.utcnow()
        if seed is not None:
            random.seed(seed)

    def generate_daily_history(self) -> Tuple[List[str], List[float], List[float]]:
        """Generate 90 days of daily prices.

        Returns:
            Tuple of (dates, gasolina_95_prices, gasoleoa_prices)
        """
        dates = []
        gasolina_prices = []
        gasoleoa_prices = []

        # Start N days ago from today
        start_date = self.today - timedelta(days=self.days_back)

        # Get province adjustment
        adjustment = self.PROVINCE_ADJUSTMENTS.get(self.province, self.PROVINCE_ADJUSTMENTS["spain"])
        gasolina_adjustment = adjustment.get("gasolina_95", 0)
        gasoleoa_adjustment = adjustment.get("gasoleoa", 0)

        # Generate daily prices
        gasolina_price = random.uniform(*self.GASOLINA_95_RANGE) + gasolina_adjustment
        gasoleoa_price = random.uniform(*self.GASOLEOA_RANGE) + gasoleoa_adjustment

        for day in range(self.days_back):
            current_date = start_date + timedelta(days=day)
            dates.append(current_date.isoformat())

            # Daily price variation (realistic: ±0.02-0.05 EUR/L)
            # Sometimes larger swings (market movements)
            if random.random() < 0.1:  # 10% chance of larger swing
                swing = random.uniform(-0.08, 0.08)
            else:
                swing = random.uniform(-0.03, 0.03)

            gasolina_price = max(
                self.GASOLINA_95_RANGE[0] + gasolina_adjustment,
                min(
                    self.GASOLINA_95_RANGE[1] + gasolina_adjustment,
                    gasolina_price + swing,
                ),
            )
            gasoleoa_price = max(
                self.GASOLEOA_RANGE[0] + gasoleoa_adjustment,
                min(
                    self.GASOLEOA_RANGE[1] + gasoleoa_adjustment,
                    gasoleoa_price + swing * 0.9,  # Gasóleo usually moves less than gasolina
                ),
            )

            gasolina_prices.append(round(gasolina_price, 3))
            gasoleoa_prices.append(round(gasoleoa_price, 3))

        return dates, gasolina_prices, gasoleoa_prices

    def get_price_stats(
        self,
        prices: List[float],
    ) -> Dict[str, float]:
        """Calculate statistics for price history.

        Args:
            prices: List of prices

        Returns:
            Dictionary with min, max, avg, current
        """
        return {
            "min": round(min(prices), 3),
            "max": round(max(prices), 3),
            "avg": round(sum(prices) / len(prices), 3),
            "current": round(prices[-1], 3),
            "change": round(prices[-1] - prices[0], 3),
            "change_percent": round(
                ((prices[-1] - prices[0]) / prices[0]) * 100,
                2,
            ),
        }

    def generate_with_stats(
        self,
    ) -> Dict[str, any]:
        """Generate full price history with statistics.

        Returns:
            Dictionary with history and stats
        """
        dates, gasolina, gasoleoa = self.generate_daily_history()

        return {
            "days": self.days_back,
            "province": self.province,
            "data_type": "daily",
            "update_frequency": "once per day",
            "timestamps": dates,
            "gasolina_95": gasolina,
            "gasoleoa": gasoleoa,
            "gasolina_95_stats": self.get_price_stats(gasolina),
            "gasoleoa_stats": self.get_price_stats(gasoleoa),
            "start_date": dates[0],
            "end_date": dates[-1],
        }


# Singleton instances for consistent history by province
# seed=42 ASEGURA que SIEMPRE devuelve los MISMOS datos
_price_generator_spain = PriceHistoryGenerator(days_back=90, seed=42, province="spain")
_price_generator_toledo = PriceHistoryGenerator(days_back=90, seed=42, province="toledo")

# Cache para almacenar datos generados (evita regenerarlos)
_price_history_cache_spain = None
_price_history_cache_toledo = None


def get_price_history(days: int = 90, province: str = "spain") -> Dict:
    """Get price history for specified number of days and province.

    ⚠️ IMPORTANTE: Usa seed=42 para CONSISTENCIA TOTAL
    Cada llamada retorna los MISMOS datos (determinístico).

    NO devuelve datos aleatorios - siempre los MISMOS.

    Args:
        days: Number of days (max 90)
        province: Province code ("spain" for all Spain, "toledo" for Toledo province)

    Returns:
        Price history with daily data (SIEMPRE IGUAL)
    """
    global _price_history_cache_spain, _price_history_cache_toledo

    if days > 90:
        days = 90

    province = province.lower()

    # Si es 90 días, usar cache del singleton
    if days == 90:
        if province == "toledo":
            if _price_history_cache_toledo is None:
                _price_history_cache_toledo = _price_generator_toledo.generate_with_stats()
            return _price_history_cache_toledo
        else:  # spain by default
            if _price_history_cache_spain is None:
                _price_history_cache_spain = _price_generator_spain.generate_with_stats()
            return _price_history_cache_spain
    else:
        # Para otros días, generar con seed fijo SIEMPRE
        gen = PriceHistoryGenerator(days_back=days, seed=42, province=province)
        return gen.generate_with_stats()
