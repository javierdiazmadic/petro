"""Alembic migration environment."""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get SQLAlchemy URL from environment
from petro.core.config import settings

# Convert async URL to sync for Alembic (replace postgresql+asyncpg with postgresql)
db_url = settings.database.url.replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", db_url)

# Set target metadata (if using declarative base)
# from petro.infrastructure.db.models import Base
# target_metadata = Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # Get the database URL and convert from async to sync
    from sqlalchemy import create_engine

    db_url = config.get_main_option("sqlalchemy.url")
    if "asyncpg" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    # Create engine directly without config options to avoid track_migrations issue
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
