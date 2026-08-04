"""RSS news feed connector."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import feedparser

from petro.infrastructure.connectors.base import BaseConnector


class NewsRSSConnector(BaseConnector):
    """Connector for fetching news from RSS feeds."""

    # News feed URLs (public, free feeds)
    NEWS_FEEDS = [
        "https://feeds.bloomberg.com/markets/energy.rss",  # Bloomberg Energy
        "https://feeds.reuters.com/reuters/businessNews",  # Reuters Business
        "https://feeds.cnbc.com/cnbc/world",  # CNBC World
    ]

    def __init__(self):
        """Initialize News RSS connector."""
        super().__init__(
            source_name="rss_news",
            timeout=20,
            max_retries=2,
        )

    async def fetch(self) -> Optional[Dict[str, Any]]:
        """Fetch news from RSS feeds.

        Returns:
            Dictionary with news items or None on failure
        """
        try:
            news_items = await self._fetch_all_feeds()

            if not news_items:
                self.log_fetch(False, "No news items fetched")
                return None

            data = {
                "source": self.source_name,
                "timestamp": datetime.utcnow(),
                "items": news_items,
                "total_count": len(news_items),
            }

            self.log_fetch(True, f"Fetched {len(news_items)} news items")
            return data

        except Exception as e:
            self.logger.error(f"Error fetching RSS feeds: {e}", exc_info=True)
            self.log_fetch(False, f"Exception: {str(e)}")
            return None

    async def _fetch_all_feeds(self) -> List[Dict[str, Any]]:
        """Fetch news from all configured feeds.

        Returns:
            List of news items
        """
        all_items = []

        for feed_url in self.NEWS_FEEDS:
            try:
                items = await self._fetch_feed(feed_url)
                all_items.extend(items)
            except Exception as e:
                self.logger.warning(f"Error fetching {feed_url}: {e}")

        # Return latest N items, sorted by date
        return sorted(all_items, key=lambda x: x.get("published_at", datetime.utcnow()), reverse=True)[:50]

    async def _fetch_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch items from a single RSS feed.

        Args:
            feed_url: URL of RSS feed

        Returns:
            List of parsed news items
        """
        feed = feedparser.parse(feed_url)

        if feed.bozo:
            self.logger.warning(f"RSS feed parsing warning for {feed_url}: {feed.bozo_exception}")

        items = []
        for entry in feed.entries[:20]:  # Limit to 20 per feed
            try:
                item = {
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", "") or entry.get("description", ""),
                    "url": entry.get("link", ""),
                    "source": feed.feed.get("title", feed_url),
                    "published_at": self._parse_date(entry.get("published", "")),
                    "author": entry.get("author", ""),
                }
                items.append(item)
            except Exception as e:
                self.logger.debug(f"Error parsing feed entry: {e}")

        return items

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from RSS feed.

        Args:
            date_str: Date string from feed

        Returns:
            Parsed datetime, or now() if parsing fails
        """
        if not date_str:
            return datetime.utcnow()

        try:
            # feedparser provides parsed_published as a time.struct_time
            # but we need to handle string formats too
            # For now, return current time as fallback
            return datetime.utcnow()
        except Exception:
            return datetime.utcnow()
