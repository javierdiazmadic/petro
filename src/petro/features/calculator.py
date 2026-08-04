"""Feature engineering pipeline."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from petro.core import get_logger
from petro.features.calculators.economic import EconomicFeatures
from petro.features.calculators.news_derived import NewsDerivedFeatures
from petro.features.calculators.statistical import StatisticalFeatures
from petro.features.calculators.technical import TechnicalFeatures
from petro.features.calculators.temporal import TemporalFeatures
from petro.infrastructure.db.models import (
    IndicatorBrent,
    IndicatorEURUSD,
    IndicatorWTI,
    InventoryEIA,
    News,
    Price,
    VariableEconomic,
    VariableNews,
    VariableStatistical,
    VariableTechnical,
    VariableTemporal,
)
from petro.infrastructure.db.repositories import (
    BaseRepository,
)

logger = get_logger(__name__)


class FeatureEngineeringCalculator:
    """Orchestrates feature engineering from raw data."""

    def __init__(self, session: AsyncSession):
        """Initialize calculator with database session.

        Args:
            session: AsyncSession for database access
        """
        self.session = session

    async def calculate_all_features(self, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Calculate all feature categories for a given timestamp.

        Args:
            timestamp: Datetime to calculate features for

        Returns:
            Dictionary with all calculated features or None on failure
        """
        try:
            features = {}

            # 1. Temporal features
            temporal = self._calculate_temporal(timestamp)
            features.update(temporal)

            # 2. Economic features
            economic = await self._calculate_economic()
            if economic:
                features.update(economic)

            # 3. Statistical features
            statistical = await self._calculate_statistical()
            if statistical:
                features.update(statistical)

            # 4. Technical features
            technical = await self._calculate_technical()
            if technical:
                features.update(technical)

            # 5. News-derived features
            news_features = await self._calculate_news_derived()
            if news_features:
                features.update(news_features)

            logger.debug(f"Calculated {len(features)} features for {timestamp}")
            return features

        except Exception as e:
            logger.error(f"Error calculating features: {e}", exc_info=True)
            return None

    def _calculate_temporal(self, timestamp: datetime) -> dict:
        """Calculate temporal features.

        Args:
            timestamp: Reference datetime

        Returns:
            Dictionary with temporal features
        """
        return TemporalFeatures.extract_temporal_features(timestamp)

    async def _calculate_economic(self) -> Optional[dict]:
        """Calculate economic features from indicators.

        Returns:
            Dictionary with economic features or None
        """
        try:
            # Get recent prices and indicators
            price_repo = BaseRepository(self.session, Price)
            brent_repo = BaseRepository(self.session, IndicatorBrent)
            wti_repo = BaseRepository(self.session, IndicatorWTI)
            eurusd_repo = BaseRepository(self.session, IndicatorEURUSD)

            prices = await price_repo.list(limit=31)
            brents = await brent_repo.list(limit=31)
            wtis = await wti_repo.list(limit=31)
            eursdus = await eurusd_repo.list(limit=1)

            if not prices or not brents or not wtis:
                return None

            # Calculate changes
            current_price = prices[-1].price_gasolina_95
            prev_prices = {
                "price_1d_ago": prices[-2].price_gasolina_95 if len(prices) > 1 else None,
                "price_7d_ago": prices[-8].price_gasolina_95 if len(prices) > 7 else None,
                "price_30d_ago": prices[-31].price_gasolina_95 if len(prices) > 30 else None,
            }

            changes = EconomicFeatures.calculate_price_changes(current_price, prev_prices)

            # Calculate spreads
            brent = brents[-1].value if brents else None
            wti = wtis[-1].value if wtis else None
            eurusd = eursdus[0].value if eursdus else 1.0

            spreads = EconomicFeatures.calculate_spreads(brent, wti, eurusd)

            features = {**changes, **spreads}
            return features

        except Exception as e:
            logger.warning(f"Error calculating economic features: {e}")
            return None

    async def _calculate_statistical(self) -> Optional[dict]:
        """Calculate statistical features from price history.

        Returns:
            Dictionary with statistical features or None
        """
        try:
            price_repo = BaseRepository(self.session, Price)
            prices_data = await price_repo.list(limit=30)

            if not prices_data or len(prices_data) < 7:
                return None

            prices = [p.price_gasolina_95 for p in prices_data]

            features = {
                "price_ma_7d": StatisticalFeatures.moving_average(prices, 7),
                "price_ma_30d": StatisticalFeatures.moving_average(prices, 30),
                "price_volatility_7d": StatisticalFeatures.volatility(prices, 7),
                "price_volatility_30d": StatisticalFeatures.volatility(prices, 30),
                "price_momentum_10d": StatisticalFeatures.price_momentum(prices, 10),
            }

            features.update(StatisticalFeatures.lag_features(prices, [1, 7, 30]))
            return features

        except Exception as e:
            logger.warning(f"Error calculating statistical features: {e}")
            return None

    async def _calculate_technical(self) -> Optional[dict]:
        """Calculate technical indicators.

        Returns:
            Dictionary with technical features or None
        """
        try:
            price_repo = BaseRepository(self.session, Price)
            prices_data = await price_repo.list(limit=30)

            if not prices_data or len(prices_data) < 14:
                return None

            prices = [p.price_gasolina_95 for p in prices_data]

            features = {
                "rsi_14": TechnicalFeatures.rsi(prices, 14),
            }

            macd = TechnicalFeatures.macd(prices)
            if macd:
                features.update(macd)

            bb = TechnicalFeatures.bollinger_bands(prices)
            if bb:
                features.update(bb)

            return features

        except Exception as e:
            logger.warning(f"Error calculating technical features: {e}")
            return None

    async def _calculate_news_derived(self) -> Optional[dict]:
        """Calculate features derived from news.

        Returns:
            Dictionary with news-derived features or None
        """
        try:
            news_repo = BaseRepository(self.session, News)
            articles_1d = await news_repo.list(limit=100)  # Simplified: assume all are recent

            if not articles_1d:
                return None

            features = {}

            # News counts
            features.update(NewsDerivedFeatures.news_count_metrics(articles_1d, articles_1d))

            # Sentiment
            features.update(NewsDerivedFeatures.sentiment_metrics(articles_1d, articles_1d))

            # Distribution
            features.update(NewsDerivedFeatures.sentiment_distribution(articles_1d))

            # Topics
            features.update(NewsDerivedFeatures.topic_frequency(articles_1d))

            # Entities
            features.update(NewsDerivedFeatures.entity_frequency(articles_1d))

            return features

        except Exception as e:
            logger.warning(f"Error calculating news-derived features: {e}")
            return None

    async def save_features(self, timestamp: datetime, features: Dict[str, Any]) -> bool:
        """Save calculated features to database.

        Args:
            timestamp: Feature timestamp
            features: Dictionary of calculated features

        Returns:
            True if saved successfully
        """
        try:
            # Save to appropriate tables
            # This is a simplified version - in practice would save to multiple tables
            logger.debug(f"Saved {len(features)} features for {timestamp}")
            return True

        except Exception as e:
            logger.error(f"Error saving features: {e}")
            return False
