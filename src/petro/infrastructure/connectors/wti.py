"""WTI crude oil price connector."""

import random
from datetime import datetime
from typing import Any, Dict, Optional

from petro.infrastructure.connectors.base import BaseConnector


class WTIConnector(BaseConnector):
    """Connector for WTI crude oil prices."""

    def __init__(self):
        """Initialize WTI connector."""
        super().__init__(
            source_name="wti",
            timeout=10,
            max_retries=3,
        )

    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch WTI prices.

        Returns:
            Dictionary with WTI data or None on failure
        """
        try:
            data = await self._fetch_simulated()

            if not await self.validate_response(data):
                self.log_fetch(False, "Invalid response format")
                return None

            self.log_fetch(True, "WTI prices fetched", value=data.get("value"))
            return data

        except Exception as e:
            self.logger.error(f"Error fetching WTI: {e}", exc_info=True)
            self.log_fetch(False, f"Exception: {str(e)}")
            return None

    async def _fetch_simulated(self) -> Dict[str, Any]:
        """Simulate WTI data for development.

        Returns:
            Simulated WTI data
        """
        base_price = 79.5  # WTI typically cheaper than Brent
        variation = random.uniform(-2, 2)
        price = base_price + variation

        return {
            "source": self.source_name,
            "timestamp": datetime.utcnow(),
            "value": round(price, 2),
            "currency": "USD",
            "unit": "barrel",
            "high": round(price + random.uniform(0, 1), 2),
            "low": round(price - random.uniform(0, 1), 2),
            "change_pct": round(variation / base_price * 100, 2),
        }
