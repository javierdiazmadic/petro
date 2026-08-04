"""Repository for ModelRegistry data access."""

from typing import List, Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from petro.infrastructure.db.models import ModelRegistry
from petro.infrastructure.db.repositories.base import BaseRepository


class ModelRegistryRepository(BaseRepository[ModelRegistry]):
    """Repository for ModelRegistry with specialized queries."""

    def __init__(self, session: AsyncSession):
        """Initialize ModelRegistryRepository."""
        super().__init__(session, ModelRegistry)

    async def get_production_model(self, commodity: str = "all") -> Optional[ModelRegistry]:
        """Get current production model.

        Args:
            commodity: "gasolina_95", "gasoleoa", or "all"

        Returns:
            Current production ModelRegistry or None
        """
        stmt = (
            select(ModelRegistry)
            .where(
                and_(
                    ModelRegistry.commodity == commodity,
                    ModelRegistry.status == "production",
                )
            )
            .order_by(desc(ModelRegistry.created_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_type(
        self, model_type: str, commodity: str = "all", limit: int = 20
    ) -> List[ModelRegistry]:
        """Get models by type.

        Args:
            model_type: "xgboost", "lightgbm", or "rf"
            commodity: Commodity type
            limit: Maximum results

        Returns:
            List of ModelRegistry records
        """
        stmt = (
            select(ModelRegistry)
            .where(
                and_(
                    ModelRegistry.model_type == model_type,
                    ModelRegistry.commodity == commodity,
                )
            )
            .order_by(desc(ModelRegistry.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_best_model(
        self, commodity: str = "all", metric: str = "rmse_test"
    ) -> Optional[ModelRegistry]:
        """Get best model by metric.

        Args:
            commodity: Commodity type
            metric: Metric to sort by (rmse_test, mae_test, r2_test, mape_test)

        Returns:
            Best ModelRegistry or None
        """
        stmt = (
            select(ModelRegistry)
            .where(ModelRegistry.commodity == commodity)
            .order_by(getattr(ModelRegistry, metric))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_status(self, status: str = "production") -> List[ModelRegistry]:
        """Get models by status.

        Args:
            status: "training", "production", or "archived"

        Returns:
            List of ModelRegistry records
        """
        stmt = (
            select(ModelRegistry)
            .where(ModelRegistry.status == status)
            .order_by(desc(ModelRegistry.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_training_models(self) -> List[ModelRegistry]:
        """Get all models currently in training.

        Returns:
            List of training ModelRegistry records
        """
        return await self.get_by_status("training")

    async def get_archived_models(self) -> List[ModelRegistry]:
        """Get all archived models.

        Returns:
            List of archived ModelRegistry records
        """
        return await self.get_by_status("archived")

    async def compare_models(
        self, commodity: str = "all", limit: int = 5
    ) -> List[dict]:
        """Get models comparison data.

        Args:
            commodity: Commodity type
            limit: Maximum number of models

        Returns:
            List of model comparison dictionaries
        """
        models = await self.get_by_type("", commodity)[:limit]

        comparison = []
        for model in models:
            comparison.append({
                "id": model.id,
                "type": model.model_type,
                "created_at": model.created_at,
                "status": model.status,
                "rmse_test": model.rmse_test,
                "mae_test": model.mae_test,
                "r2_test": model.r2_test,
                "mape_test": model.mape_test,
            })

        return comparison

    async def set_production(self, model_id: int, commodity: str = "all") -> bool:
        """Set a model to production and archive others.

        Args:
            model_id: ID of model to promote
            commodity: Commodity type

        Returns:
            True if successful
        """
        # Get model
        model = await self.get(id=model_id)
        if not model:
            return False

        # Archive all current production models for this commodity
        current_prod = await self.get_production_model(commodity)
        if current_prod:
            await self.update(current_prod.id, {"status": "archived"})

        # Set new production
        await self.update(model_id, {"status": "production"})
        return True
