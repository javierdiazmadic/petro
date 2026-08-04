"""Repository for Price data access."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from petro.infrastructure.db.models import Price
from petro.infrastructure.db.repositories.base import BaseRepository


class PriceRepository(BaseRepository[Price]):
    """Repository for Price model with specialized queries."""

    def __init__(self, session: AsyncSession):
        """Initialize PriceRepository."""
        super().__init__(session, Price)

    async def get_latest(self, commodity: str = "gasolina_95") -> Optional[Price]:
        """Get latest price by commodity.

        Args:
            commodity: "gasolina_95" or "gasoleoa"

        Returns:
            Latest Price record or None
        """
        stmt = select(Price).order_by(desc(Price.timestamp)).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_last_n_days(self, days: int = 7) -> List[Price]:
        """Get prices from last N days.

        Args:
            days: Number of days to retrieve

        Returns:
            List of Price records
        """
        since = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(Price)
            .where(Price.timestamp >= since)
            .order_by(Price.timestamp)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_date_range(self, start: datetime, end: datetime) -> List[Price]:
        """Get prices within date range.

        Args:
            start: Start datetime
            end: End datetime

        Returns:
            List of Price records
        """
        stmt = (
            select(Price)
            .where(Price.timestamp.between(start, end))
            .order_by(Price.timestamp)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_average_price(self, days: int = 7) -> Optional[dict]:
        """Calculate average prices for last N days.

        Args:
            days: Number of days

        Returns:
            Dictionary with avg gasolina_95 and avg gasoleoa, or None
        """
        prices = await self.get_last_n_days(days)
        if not prices:
            return None

        avg_gasolina = sum(p.price_gasolina_95 for p in prices) / len(prices)
        avg_gasoleoa = sum(p.price_gasoleoa for p in prices) / len(prices)

        return {
            "avg_gasolina_95": avg_gasolina,
            "avg_gasoleoa": avg_gasoleoa,
            "count": len(prices),
        }

    async def get_price_change(self, days: int = 7) -> Optional[dict]:
        """Calculate price change over N days.

        Args:
            days: Number of days

        Returns:
            Dictionary with percentage changes, or None
        """
        prices = await self.get_last_n_days(days)
        if len(prices) < 2:
            return None

        first = prices[0]
        last = prices[-1]

        gasolina_change = ((last.price_gasolina_95 - first.price_gasolina_95) / first.price_gasolina_95) * 100
        gasoleoa_change = ((last.price_gasoleoa - first.price_gasoleoa) / first.price_gasoleoa) * 100

        return {
            "gasolina_95_change_pct": gasolina_change,
            "gasoleoa_change_pct": gasoleoa_change,
            "period_days": days,
        }
