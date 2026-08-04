"""OpenStreetMap Gas Stations connector using Overpass API.

Fetches real gas station locations from OpenStreetMap.
Free, open-source, no authentication required.
"""

import math
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    httpx = None

from petro.infrastructure.connectors.base import BaseConnector


class OSMGasStationsConnector(BaseConnector):
    """Connector for OpenStreetMap gas stations via Overpass API.

    Uses Overpass API to fetch real gas station locations.
    Completely free and open-source.
    """

    def __init__(self):
        """Initialize OSM connector."""
        super().__init__(
            source_name="osm_gas_stations",
            timeout=30,
            max_retries=3,
        )
        self.overpass_url = "https://overpass-api.de/api/interpreter"

    async def fetch_by_province(
        self, province: str, bbox: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch gas stations for a specific province.

        Args:
            province: Province name (e.g., 'Toledo')
            bbox: Bounding box (south, west, north, east) for province

        Returns:
            List of gas stations or None on failure
        """
        if province.lower() == "toledo":
            # Toledo province bounding box (approximate)
            bbox = "39.4, -4.5, 40.3, -3.2"

        try:
            if httpx is None:
                return None

            # Overpass query for gas stations
            overpass_query = f"""
            [out:json];
            (
              node["amenity"="fuel"](bbox:{bbox});
              way["amenity"="fuel"](bbox:{bbox});
              relation["amenity"="fuel"](bbox:{bbox});
            );
            out geom;
            """

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.overpass_url,
                    data=overpass_query,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_osm_data(data, province)

            return None

        except Exception as e:
            self.logger.error(f"Error fetching OSM data: {e}")
            return None

    def _parse_osm_data(
        self, data: Dict[str, Any], province: str
    ) -> List[Dict[str, Any]]:
        """Parse Overpass API response.

        Args:
            data: Response from Overpass API
            province: Province name

        Returns:
            List of normalized gas station data
        """
        stations = []

        try:
            if "elements" not in data:
                return stations

            for element in data["elements"]:
                if "lat" not in element or "lon" not in element:
                    continue

                station = {
                    "id": element.get("id"),
                    "name": element.get("tags", {}).get("name", "Unknown"),
                    "latitude": element["lat"],
                    "longitude": element["lon"],
                    "province": province,
                    "operator": element.get("tags", {}).get("operator", "Unknown"),
                    "brand": element.get("tags", {}).get("brand", "Unknown"),
                    "source": "osm",
                }

                stations.append(station)

        except Exception as e:
            self.logger.error(f"Parse error: {e}")

        return stations

    def calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula.

        Args:
            lat1, lon1: Starting point (Los Yébenes)
            lat2, lon2: Ending point (gas station)

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch gas stations (not implemented for base fetch).

        This connector is used via fetch_by_province() instead.

        Returns:
            None
        """
        return None
