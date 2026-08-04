"""Data connectors for external sources."""

from petro.infrastructure.connectors.base import BaseConnector
from petro.infrastructure.connectors.brent import BrentConnector
from petro.infrastructure.connectors.eurusd import EURUSDConnector
from petro.infrastructure.connectors.geoportal import GeoportalConnector
from petro.infrastructure.connectors.inventory_eia import InventoryEIAConnector
from petro.infrastructure.connectors.news_rss import NewsRSSConnector
from petro.infrastructure.connectors.opec import OPECConnector
from petro.infrastructure.connectors.wti import WTIConnector

__all__ = [
    "BaseConnector",
    "BrentConnector",
    "WTIConnector",
    "EURUSDConnector",
    "InventoryEIAConnector",
    "OPECConnector",
    "GeoportalConnector",
    "NewsRSSConnector",
]
