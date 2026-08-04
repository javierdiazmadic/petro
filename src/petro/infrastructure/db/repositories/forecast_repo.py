"""Repository for Forecast and Explanation data access."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from petro.infrastructure.db.models import Explanation, Forecast
from petro.infrastructure.db.repositories.base import BaseRepository


class ForecastRepository(BaseRepository[Forecast]):
    """Repository for Forecast model with specialized queries."""

    def __init__(self, session: AsyncSession):
        """Initialize ForecastRepository."""
        super().__init__(session, Forecast)

    async def get_latest(self, commodity: str = "gasolina_95") -> Optional[Forecast]:
        """Get latest forecast for commodity.

        Args:
            commodity: "gasolina_95" or "gasoleoa"

        Returns:
            Latest Forecast or None
        """
        stmt = (
            select(Forecast)
            .options(joinedload(Forecast.explanations))
            .where(Forecast.commodity == commodity)
            .order_by(desc(Forecast.created_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().first()

    async def get_latest_with_explanations(
        self, commodity: str = "gasolina_95"
    ) -> Optional[Forecast]:
        """Get latest forecast with all explanations eagerly loaded.

        Args:
            commodity: "gasolina_95" or "gasoleoa"

        Returns:
            Latest Forecast with explanations or None
        """
        return await self.get_latest(commodity)

    async def get_history(
        self, commodity: str = "gasolina_95", days: int = 30, horizon: int = 1
    ) -> List[Forecast]:
        """Get forecast history.

        Args:
            commodity: "gasolina_95" or "gasoleoa"
            days: Number of days of history
            horizon: Prediction horizon (1, 7, 30, etc)

        Returns:
            List of Forecast records
        """
        since = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(Forecast)
            .where(
                and_(
                    Forecast.commodity == commodity,
                    Forecast.created_at >= since,
                    Forecast.horizon_days == horizon,
                )
            )
            .order_by(desc(Forecast.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_accuracy(
        self, commodity: str = "gasolina_95", days: int = 30
    ) -> Optional[dict]:
        """Calculate forecast accuracy metrics.

        Args:
            commodity: "gasolina_95" or "gasoleoa"
            days: Number of days

        Returns:
            Dictionary with accuracy metrics or None
        """
        since = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(Forecast)
            .where(
                and_(
                    Forecast.commodity == commodity,
                    Forecast.created_at >= since,
                    Forecast.actual_price.isnot(None),
                )
            )
        )
        result = await self.session.execute(stmt)
        forecasts = result.scalars().all()

        if not forecasts:
            return None

        errors = [abs(f.error) for f in forecasts if f.error is not None]
        if not errors:
            return None

        mae = sum(errors) / len(errors)
        rmse = (sum(e ** 2 for e in errors) / len(errors)) ** 0.5

        # Direction accuracy
        correct_direction = sum(
            1
            for f in forecasts
            if (f.direction == "up" and f.actual_price > f.predicted_price)
            or (f.direction == "down" and f.actual_price < f.predicted_price)
            or (f.direction == "stable" and abs(f.actual_price - f.predicted_price) < 0.05)
        )
        direction_accuracy = (correct_direction / len(forecasts)) * 100 if forecasts else 0

        return {
            "mae": mae,
            "rmse": rmse,
            "direction_accuracy_pct": direction_accuracy,
            "count": len(forecasts),
            "period_days": days,
        }

    async def get_by_model(self, model_version: str, limit: int = 100) -> List[Forecast]:
        """Get forecasts by model version.

        Args:
            model_version: Model version string
            limit: Maximum results

        Returns:
            List of Forecast records
        """
        stmt = (
            select(Forecast)
            .where(Forecast.model_version == model_version)
            .order_by(desc(Forecast.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class ExplanationRepository(BaseRepository[Explanation]):
    """Repository for Explanation model with specialized queries."""

    def __init__(self, session: AsyncSession):
        """Initialize ExplanationRepository."""
        super().__init__(session, Explanation)

    async def get_by_forecast(self, forecast_id: int) -> List[Explanation]:
        """Get all explanations for a forecast.

        Args:
            forecast_id: Forecast ID

        Returns:
            List of Explanation records
        """
        stmt = (
            select(Explanation)
            .where(Explanation.forecast_id == forecast_id)
            .order_by(Explanation.contribution_rank)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_top_factors(self, forecast_id: int, top_n: int = 5) -> List[Explanation]:
        """Get top N factors by SHAP contribution.

        Args:
            forecast_id: Forecast ID
            top_n: Number of top factors

        Returns:
            List of top Explanation records
        """
        stmt = (
            select(Explanation)
            .where(Explanation.forecast_id == forecast_id)
            .order_by(desc(Explanation.contribution_shap))
            .limit(top_n)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
