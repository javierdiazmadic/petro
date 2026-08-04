"""EIA inventory data connector."""

import random
from datetime import datetime
from typing import Any, Dict, Optional

from petro.infrastructure.connectors.base import BaseConnector


class InventoryEIAConnector(BaseConnector):
    """Connector for EIA (U.S. Energy Information Administration) inventory data."""

    def __init__(self):
        """Initialize EIA connector."""
        super().__init__(
            source_name="eia",
            timeout=15,
            max_retries=3,
        )
        self.base_url = "https://api.eia.gov/series"  # Placeholder

    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch EIA inventory data.

        Returns:
            Dictionary with EIA inventory data or None on failure
        """
        try:
            data = await self._fetch_simulated()

            if not await self.validate_response(data):
                self.log_fetch(False, "Invalid response format")
                return None

            self.log_fetch(True, "EIA inventory fetched")
            return data

        except Exception as e:
            self.logger.error(f"Error fetching EIA data: {e}", exc_info=True)
            self.log_fetch(False, f"Exception: {str(e)}")
            return None

    async def _fetch_simulated(self) -> Dict[str, Any]:
        """Simulate EIA inventory data for development.

        Returns:
            Simulated EIA data
        """
        # Simulated inventory levels (millions of barrels)
        gasoline_base = 230.0
        distillate_base = 125.0
        crude_base = 410.0

        return {
            "source": self.source_name,
            "timestamp": datetime.utcnow(),
            "gasoline_inventory": round(gasoline_base + random.uniform(-10, 10), 1),
            "distillate_inventory": round(distillate_base + random.uniform(-5, 5), 1),
            "crude_inventory": round(crude_base + random.uniform(-20, 20), 1),
            "unit": "million barrels",
            "week": datetime.utcnow().isocalendar()[1],
            "year": datetime.utcnow().year,
        }
