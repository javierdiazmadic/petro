"""OPEC production data connector."""

import random
from datetime import datetime
from typing import Any, Dict, Optional

from petro.infrastructure.connectors.base import BaseConnector


class OPECConnector(BaseConnector):
    """Connector for OPEC production data."""

    def __init__(self):
        """Initialize OPEC connector."""
        super().__init__(
            source_name="opec",
            timeout=15,
            max_retries=3,
        )

    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch OPEC production data.

        Returns:
            Dictionary with OPEC data or None on failure
        """
        try:
            data = await self._fetch_simulated()

            if not await self.validate_response(data):
                self.log_fetch(False, "Invalid response format")
                return None

            self.log_fetch(True, "OPEC production fetched", value=data.get("total_production"))
            return data

        except Exception as e:
            self.logger.error(f"Error fetching OPEC data: {e}", exc_info=True)
            self.log_fetch(False, f"Exception: {str(e)}")
            return None

    async def _fetch_simulated(self) -> Dict[str, Any]:
        """Simulate OPEC production data for development.

        Returns:
            Simulated OPEC data
        """
        # OPEC total production ~28-30 million barrels/day
        base_production = 29.0
        variation = random.uniform(-0.5, 0.5)
        production = base_production + variation

        return {
            "source": self.source_name,
            "timestamp": datetime.utcnow(),
            "total_production": round(production, 2),
            "unit": "million barrels per day",
            "member_count": 13,
            "month": datetime.utcnow().month,
            "year": datetime.utcnow().year,
            "change_from_previous": round(variation, 2),
        }
