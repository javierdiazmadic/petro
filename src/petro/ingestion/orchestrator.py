"""Data ingestion orchestrator."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from petro.core import get_logger
from petro.infrastructure.connectors import (
    BrentConnector,
    EURUSDConnector,
    GeoportalConnector,
    InventoryEIAConnector,
    NewsRSSConnector,
    OPECConnector,
    WTIConnector,
)
from petro.infrastructure.db.models import (
    IndicatorBrent,
    IndicatorEURUSD,
    IndicatorWTI,
    InventoryEIA,
    News,
    Price,
    ProductionOPEC,
    SystemLog,
)
from petro.ingestion.retry_policy import DEFAULT_RETRY_POLICY

logger = get_logger(__name__)


class DataIngestionOrchestrator:
    """Orchestrates data collection from all sources."""

    def __init__(self, session: AsyncSession):
        """Initialize orchestrator.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

        # Initialize connectors
        self.connectors = {
            "brent": BrentConnector(),
            "wti": WTIConnector(),
            "eurusd": EURUSDConnector(),
            "eia": InventoryEIAConnector(),
            "opec": OPECConnector(),
            "geoportal": GeoportalConnector(),
            "news": NewsRSSConnector(),
        }

        self.retry_policy = DEFAULT_RETRY_POLICY

    async def run_full_cycle(self) -> Dict[str, Any]:
        """Run full data ingestion cycle.

        Returns:
            Dictionary with results and statistics
        """
        logger.info("Starting data ingestion cycle")
        cycle_start = datetime.utcnow()

        results = {
            "timestamp": cycle_start,
            "sources": {},
            "total_records_inserted": 0,
            "errors": [],
        }

        # Fetch prices (Geoportal)
        try:
            await self._ingest_prices()
            results["sources"]["prices"] = "success"
        except Exception as e:
            logger.error(f"Error ingesting prices: {e}", exc_info=True)
            results["sources"]["prices"] = f"failed: {str(e)}"
            results["errors"].append({"source": "prices", "error": str(e)})

        # Fetch indicators
        try:
            await self._ingest_indicators()
            results["sources"]["indicators"] = "success"
        except Exception as e:
            logger.error(f"Error ingesting indicators: {e}", exc_info=True)
            results["sources"]["indicators"] = f"failed: {str(e)}"
            results["errors"].append({"source": "indicators", "error": str(e)})

        # Fetch news
        try:
            await self._ingest_news()
            results["sources"]["news"] = "success"
        except Exception as e:
            logger.error(f"Error ingesting news: {e}", exc_info=True)
            results["sources"]["news"] = f"failed: {str(e)}"
            results["errors"].append({"source": "news", "error": str(e)})

        # Log cycle completion
        duration = (datetime.utcnow() - cycle_start).total_seconds()
        logger.info(f"Data ingestion cycle completed in {duration:.2f}s")

        results["duration_seconds"] = duration

        # Save cycle log
        await self._log_cycle(results)

        return results

    async def _ingest_prices(self) -> None:
        """Ingest price data from Geoportal."""
        logger.info("Ingesting prices from Geoportal")

        data = await self.retry_policy.execute(self.connectors["geoportal"].fetch)
        if not data:
            raise Exception("Failed to fetch Geoportal data")

        price = Price(
            timestamp=data["timestamp"],
            price_gasolina_95=data["price_gasolina_95"],
            price_gasoleoa=data["price_gasoleoa"],
            source=data["source"],
        )
        self.session.add(price)
        await self.session.commit()
        logger.info(f"Inserted price: {price}")

    async def _ingest_indicators(self) -> None:
        """Ingest all indicators (Brent, WTI, EUR/USD, EIA, OPEC)."""
        logger.info("Ingesting indicators")

        # Brent
        brent_data = await self.retry_policy.execute(self.connectors["brent"].fetch)
        if brent_data:
            brent = IndicatorBrent(
                timestamp=brent_data["timestamp"],
                value=brent_data["value"],
                currency=brent_data["currency"],
                unit=brent_data["unit"],
                source=brent_data["source"],
            )
            self.session.add(brent)
            logger.info(f"Inserted Brent: {brent_data['value']}")

        # WTI
        wti_data = await self.retry_policy.execute(self.connectors["wti"].fetch)
        if wti_data:
            wti = IndicatorWTI(
                timestamp=wti_data["timestamp"],
                value=wti_data["value"],
                currency=wti_data["currency"],
                unit=wti_data["unit"],
                source=wti_data["source"],
            )
            self.session.add(wti)
            logger.info(f"Inserted WTI: {wti_data['value']}")

        # EUR/USD
        eurusd_data = await self.retry_policy.execute(self.connectors["eurusd"].fetch)
        if eurusd_data:
            eurusd = IndicatorEURUSD(
                timestamp=eurusd_data["timestamp"],
                value=eurusd_data["value"],
                source=eurusd_data["source"],
            )
            self.session.add(eurusd)
            logger.info(f"Inserted EUR/USD: {eurusd_data['value']}")

        # EIA Inventories
        eia_data = await self.retry_policy.execute(self.connectors["eia"].fetch)
        if eia_data:
            inventory = InventoryEIA(
                timestamp=eia_data["timestamp"],
                gasoline_inventory=eia_data["gasoline_inventory"],
                distillate_inventory=eia_data["distillate_inventory"],
                crude_inventory=eia_data["crude_inventory"],
                unit=eia_data["unit"],
                source=eia_data["source"],
            )
            self.session.add(inventory)
            logger.info(f"Inserted EIA inventory")

        # OPEC Production
        opec_data = await self.retry_policy.execute(self.connectors["opec"].fetch)
        if opec_data:
            production = ProductionOPEC(
                timestamp=opec_data["timestamp"],
                total_production=opec_data["total_production"],
                unit=opec_data["unit"],
                source=opec_data["source"],
            )
            self.session.add(production)
            logger.info(f"Inserted OPEC production: {opec_data['total_production']}")

        await self.session.commit()

    async def _ingest_news(self) -> None:
        """Ingest news from RSS feeds."""
        logger.info("Ingesting news from RSS")

        data = await self.retry_policy.execute(self.connectors["news"].fetch)
        if not data:
            logger.warning("No news data fetched")
            return

        for item in data.get("items", []):
            news = News(
                published_at=item.get("published_at", datetime.utcnow()),
                title=item.get("title", ""),
                content=item.get("content", ""),
                source=item.get("source", ""),
                source_url=item.get("url", ""),
                language="en",  # TODO: detect language
                is_duplicate=0,
            )
            self.session.add(news)

        await self.session.commit()
        logger.info(f"Inserted {len(data.get('items', []))} news articles")

    async def _log_cycle(self, results: Dict[str, Any]) -> None:
        """Log cycle completion to database.

        Args:
            results: Cycle results dictionary
        """
        log_entry = SystemLog(
            level="info",
            component="ingestion.orchestrator",
            message=f"Data ingestion cycle completed",
            context=results,
        )
        self.session.add(log_entry)
        await self.session.commit()
