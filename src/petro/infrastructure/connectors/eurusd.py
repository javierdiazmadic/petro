"""EUR/USD exchange rate connector."""

import random
from datetime import datetime
from typing import Any, Dict, Optional

from petro.infrastructure.connectors.base import BaseConnector


class EURUSDConnector(BaseConnector):
    """Connector for EUR/USD exchange rates."""

    def __init__(self):
        """Initialize EUR/USD connector."""
        super().__init__(
            source_name="eurusd",
            timeout=10,
            max_retries=3,
        )

    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch EUR/USD rates.

        Returns:
            Dictionary with EUR/USD data or None on failure
        """
        try:
            data = await self._fetch_simulated()

            if not await self.validate_response(data):
                self.log_fetch(False, "Invalid response format")
                return None

            self.log_fetch(True, "EUR/USD rates fetched", value=data.get("value"))
            return data

        except Exception as e:
            self.logger.error(f"Error fetching EUR/USD: {e}", exc_info=True)
            self.log_fetch(False, f"Exception: {str(e)}")
            return None

    async def _fetch_simulated(self) -> Dict[str, Any]:
        """Simulate EUR/USD data for development.

        Returns:
            Simulated EUR/USD data
        """
        base_rate = 1.0850  # Typical EUR/USD rate
        variation = random.uniform(-0.01, 0.01)
        rate = base_rate + variation

        return {
            "source": self.source_name,
            "timestamp": datetime.utcnow(),
            "value": round(rate, 4),
            "currency_pair": "EUR/USD",
            "bid": round(rate - 0.0001, 4),
            "ask": round(rate + 0.0001, 4),
            "change_pct": round(variation / base_rate * 100, 3),
        }
