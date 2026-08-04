"""Geoportal de Precios de Carburantes (Spain) connector."""

import random
from datetime import datetime
from typing import Any, Dict, Optional

from petro.infrastructure.connectors.base import BaseConnector


class GeoportalConnector(BaseConnector):
    """Connector for Spanish Ministry's Geoportal de Precios de Carburantes.

    Official source: https://sedeaplicaciones.minetur.gob.es/PortalConsumidor/
    """

    def __init__(self):
        """Initialize Geoportal connector."""
        super().__init__(
            source_name="geoportal",
            timeout=20,
            max_retries=3,
        )
        self.base_url = "https://sedeaplicaciones.minetur.gob.es/PortalConsumidor/api"

    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch Spanish fuel prices from Geoportal.

        Returns:
            Dictionary with price data or None on failure
        """
        try:
            data = await self._fetch_simulated()

            if not await self.validate_response(data):
                self.log_fetch(False, "Invalid response format")
                return None

            self.log_fetch(
                True,
                "Geoportal prices fetched",
                gasolina=data.get("price_gasolina_95"),
                gasoleoa=data.get("price_gasoleoa"),
            )
            return data

        except Exception as e:
            self.logger.error(f"Error fetching Geoportal data: {e}", exc_info=True)
            self.log_fetch(False, f"Exception: {str(e)}")
            return None

    async def _fetch_simulated(self) -> Dict[str, Any]:
        """Simulate Geoportal data for development.

        Returns:
            Simulated Spanish fuel price data
        """
        # Typical Spanish fuel prices (~1.40-1.60 EUR/L)
        gasolina_95_base = 1.495
        gasoleoa_base = 1.395

        gasolina_95 = gasolina_95_base + random.uniform(-0.05, 0.05)
        gasoleoa = gasoleoa_base + random.uniform(-0.05, 0.05)

        return {
            "source": self.source_name,
            "timestamp": datetime.utcnow(),
            "price_gasolina_95": round(gasolina_95, 3),
            "price_gasoleoa": round(gasoleoa, 3),
            "currency": "EUR",
            "unit": "liter",
            "country": "Spain",
            "update_frequency": "daily",
            "number_of_stations": 2400,  # Approximate
        }
