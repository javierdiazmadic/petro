"""Economic feature calculations."""

from typing import Optional

from petro.core import get_logger

logger = get_logger(__name__)


class EconomicFeatures:
    """Calculate economic indicators from price/indicator data."""

    @staticmethod
    def calculate_price_changes(current_price: float, previous_prices: dict) -> dict:
        """Calculate price changes over different periods.

        Args:
            current_price: Current price
            previous_prices: Dict with keys like 'price_1d_ago', 'price_7d_ago', 'price_30d_ago'

        Returns:
            Dictionary with change calculations
        """
        features = {}

        for period, price in previous_prices.items():
            if price is None or price == 0:
                features[f"{period}_change"] = None
                features[f"{period}_change_pct"] = None
            else:
                change = current_price - price
                change_pct = (change / price) * 100
                features[f"{period}_change"] = round(change, 3)
                features[f"{period}_change_pct"] = round(change_pct, 3)

        return features

    @staticmethod
    def calculate_spreads(brent: float, wti: float, eurusd: float) -> dict:
        """Calculate spreads between commodities.

        Args:
            brent: Brent price (USD/barrel)
            wti: WTI price (USD/barrel)
            eurusd: EUR/USD rate

        Returns:
            Dictionary with spreads
        """
        if not all([brent, wti, eurusd]):
            return {
                "brent_wti_spread": None,
                "brent_wti_spread_pct": None,
            }

        spread = brent - wti
        spread_pct = (spread / wti) * 100

        return {
            "brent_wti_spread": round(spread, 3),
            "brent_wti_spread_pct": round(spread_pct, 3),
            "eurusd_ratio": round(eurusd, 4),
        }

    @staticmethod
    def calculate_inventory_impact(
        current_inventory: float, previous_inventory: float, weekly: bool = True
    ) -> Optional[float]:
        """Calculate inventory change impact.

        Args:
            current_inventory: Current inventory level
            previous_inventory: Previous inventory level
            weekly: Whether this is weekly data

        Returns:
            Inventory change percentage or None
        """
        if not all([current_inventory, previous_inventory]) or previous_inventory == 0:
            return None

        change = (current_inventory - previous_inventory) / previous_inventory * 100
        return round(change, 3)

    @staticmethod
    def calculate_production_ratios(
        opec_production: float, total_global_production: float
    ) -> Optional[float]:
        """Calculate OPEC production ratio.

        Args:
            opec_production: OPEC production (million bbl/day)
            total_global_production: Global production (million bbl/day)

        Returns:
            OPEC share as percentage or None
        """
        if not all([opec_production, total_global_production]) or total_global_production == 0:
            return None

        ratio = (opec_production / total_global_production) * 100
        return round(ratio, 2)
