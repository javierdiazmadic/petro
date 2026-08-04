"""Generic base repository for data access patterns."""

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from petro.core import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository for CRUD operations on ORM models.

    Usage:
        repo = BaseRepository(session, PriceModel)
        price = await repo.get(id=1)
        prices = await repo.list(limit=10)
        price = await repo.create({"timestamp": ..., "value": ...})
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        """Initialize repository with session and model.

        Args:
            session: AsyncSession instance
            model: SQLAlchemy model class
        """
        self.session = session
        self.model = model
        self.logger = get_logger(f"{__name__}.{model.__name__}")

    async def get(self, **filters) -> Optional[T]:
        """Get single record by filter conditions.

        Args:
            **filters: Column=value filters

        Returns:
            Single model instance or None
        """
        stmt = select(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list(self, limit: int = 100, offset: int = 0, **filters) -> List[T]:
        """List records with optional filters.

        Args:
            limit: Maximum number of records
            offset: Number of records to skip
            **filters: Column=value filters

        Returns:
            List of model instances
        """
        stmt = select(self.model)

        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: dict) -> T:
        """Create new record.

        Args:
            data: Dictionary of model attributes

        Returns:
            Created model instance
        """
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        self.logger.debug(f"Created {self.model.__name__}: {instance}")
        return instance

    async def update(self, id: int, data: dict) -> Optional[T]:
        """Update existing record.

        Args:
            id: Primary key
            data: Dictionary of attributes to update

        Returns:
            Updated model instance or None
        """
        instance = await self.get(id=id)
        if not instance:
            return None

        for key, value in data.items():
            setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        self.logger.debug(f"Updated {self.model.__name__}: {instance}")
        return instance

    async def delete(self, id: int) -> bool:
        """Delete record by id.

        Args:
            id: Primary key

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get(id=id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.commit()
        self.logger.debug(f"Deleted {self.model.__name__} id={id}")
        return True

    async def count(self, **filters) -> int:
        """Count records matching filters.

        Args:
            **filters: Column=value filters

        Returns:
            Number of matching records
        """
        stmt = select(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def exists(self, **filters) -> bool:
        """Check if record exists.

        Args:
            **filters: Column=value filters

        Returns:
            True if exists, False otherwise
        """
        count = await self.count(**filters)
        return count > 0
