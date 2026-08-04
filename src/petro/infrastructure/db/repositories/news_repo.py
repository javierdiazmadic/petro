"""Repository for News data access."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from petro.infrastructure.db.models import News
from petro.infrastructure.db.repositories.base import BaseRepository


class NewsRepository(BaseRepository[News]):
    """Repository for News model with specialized queries."""

    def __init__(self, session: AsyncSession):
        """Initialize NewsRepository."""
        super().__init__(session, News)

    async def get_latest(self, limit: int = 20, language: str = "es") -> List[News]:
        """Get latest news.

        Args:
            limit: Maximum number of articles
            language: Language code (es, en, etc)

        Returns:
            List of News records
        """
        stmt = (
            select(News)
            .where(News.language == language)
            .order_by(desc(News.published_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent_by_language(self, days: int = 7, language: str = "es") -> List[News]:
        """Get news from last N days by language.

        Args:
            days: Number of days
            language: Language code

        Returns:
            List of News records
        """
        since = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(News)
            .where(and_(News.published_at >= since, News.language == language))
            .order_by(desc(News.published_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search(self, query: str, language: str = "es", limit: int = 50) -> List[News]:
        """Search news by title or content.

        Args:
            query: Search query
            language: Language code
            limit: Maximum results

        Returns:
            List of matching News records
        """
        search_query = f"%{query}%"
        stmt = (
            select(News)
            .where(
                and_(
                    News.language == language,
                    (News.title.ilike(search_query) | News.content.ilike(search_query)),
                )
            )
            .order_by(desc(News.published_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_date_range(self, start: datetime, end: datetime, language: str = "es") -> List[News]:
        """Get news within date range.

        Args:
            start: Start datetime
            end: End datetime
            language: Language code

        Returns:
            List of News records
        """
        stmt = (
            select(News)
            .where(
                and_(
                    News.published_at.between(start, end),
                    News.language == language,
                )
            )
            .order_by(desc(News.published_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_classification(self, classification: str, limit: int = 20) -> List[News]:
        """Get news by classification.

        Args:
            classification: News classification/category
            limit: Maximum results

        Returns:
            List of News records
        """
        stmt = (
            select(News)
            .where(News.classification == classification)
            .order_by(desc(News.published_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_duplicates(self, limit: int = 100) -> List[News]:
        """Get marked duplicate news.

        Args:
            limit: Maximum results

        Returns:
            List of duplicate News records
        """
        stmt = (
            select(News)
            .where(News.is_duplicate == 1)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_average_sentiment(self, days: int = 7) -> Optional[float]:
        """Get average sentiment score for last N days.

        Args:
            days: Number of days

        Returns:
            Average sentiment score or None
        """
        since = datetime.utcnow() - timedelta(days=days)
        news = await self.get_recent_by_language(days)

        if not news:
            return None

        sentiments = [n.sentiment_score for n in news if n.sentiment_score is not None]
        if not sentiments:
            return None

        return sum(sentiments) / len(sentiments)
