#!/usr/bin/env python3
"""Script to insert Repsol real price data into database.

Inserts the real Repsol Toledo data:
- 79 gasolineras
- Gasolina 95: €1.805 (media)
- Gasóleo A: €1.938 (media)
- €0.070 más cara que media Toledo para gasolina
- €0.077 más cara que media Toledo para diesel
"""

import asyncio
import sys
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.insert(0, '/home/administrador/Desktop/petro/src')

from petro.core import get_logger
from petro.core.config import settings
from petro.infrastructure.db.models import Price

logger = get_logger(__name__)


async def init_db_session():
    """Initialize async database session."""
    engine = create_async_engine(
        settings.database.url,
        echo=False,
        pool_pre_ping=True,
    )

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    return async_session, engine


async def insert_repsol_prices():
    """Insert Repsol prices into database."""

    async_session, engine = await init_db_session()

    try:
        logger.info("Starting Repsol prices insertion...")

        # Real Repsol Toledo prices (as provided)
        repsol_data = {
            'timestamp': datetime(2026, 8, 4, 10, 0, 0),
            'price_gasolina_95': 1.805,
            'price_gasoleoa': 1.938,
            'source': 'repsol_toledo',
            'region': 'Toledo - Repsol',
            'meta_data': {
                'total_estaciones': 79,
                'estaciones_gasolina_95': 79,
                'estaciones_gasoleoa': 79,
                'min_gasolina_95': 1.729,
                'max_gasolina_95': 1.836,
                'min_gasoleoa': 1.799,
                'max_gasoleoa': 1.979,
                'media_toledo_gasolina_95': 1.735,
                'media_toledo_gasoleoa': 1.861,
                'diferencia_gasolina_95': 0.070,
                'diferencia_gasoleoa': 0.077,
            }
        }

        # Toledo all brands average
        toledo_data = {
            'timestamp': datetime(2026, 8, 4, 10, 0, 0),
            'price_gasolina_95': 1.735,
            'price_gasoleoa': 1.861,
            'source': 'ministerio_toledo',
            'region': 'Toledo - Todas',
            'meta_data': {
                'total_estaciones': 246,
                'estaciones_gasolina_95': 246,
                'estaciones_gasoleoa': 246,
                'marcas': ['Repsol', 'CEPSA', 'Petronas', 'AVIA', 'BP'],
            }
        }

        # Save to database
        async with async_session() as session:
            try:
                # Save Toledo all brands data
                toledo_record = Price(**toledo_data)
                session.add(toledo_record)
                logger.info(f"Created Toledo (Todas) record: €{toledo_data['price_gasolina_95']:.3f} / €{toledo_data['price_gasoleoa']:.3f}")

                # Save Repsol data
                repsol_record = Price(**repsol_data)
                session.add(repsol_record)
                logger.info(f"Created Repsol record: €{repsol_data['price_gasolina_95']:.3f} / €{repsol_data['price_gasoleoa']:.3f}")

                await session.commit()
                logger.info("Database records saved successfully")
                logger.info(f"Repsol is €{repsol_data['price_gasolina_95'] - toledo_data['price_gasolina_95']:.3f}/L more expensive in Gasolina 95")
                logger.info(f"Repsol is €{repsol_data['price_gasoleoa'] - toledo_data['price_gasoleoa']:.3f}/L more expensive in Gasóleo A")
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving to database: {e}", exc_info=True)
                return False

    finally:
        await engine.dispose()


async def main():
    """Main entry point."""
    success = await insert_repsol_prices()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
