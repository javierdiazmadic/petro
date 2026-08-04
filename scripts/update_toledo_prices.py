#!/usr/bin/env python3
"""Script to update Toledo gas station prices in database.

Fetches real data from Ministerio de Energía and stores it in the price table.
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
from petro.infrastructure.connectors.minetur_carburantes import MineturCarburantesConnector

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


async def save_toledo_prices():
    """Fetch Toledo prices from Ministerio and save to database."""

    async_session, engine = await init_db_session()

    try:
        logger.info("Starting Toledo prices update...")

        # Fetch from Ministerio
        logger.info("Fetching data from Ministerio de Energía...")
        ministerio_data = MineturCarburantesConnector.fetch_toledo_stations()

        if not ministerio_data:
            logger.error("Failed to fetch Ministerio data")
            return False

        # Calculate average prices
        stats = ministerio_data.get('estadisticas', {})

        # Data for TODAS (all brands)
        todas_data = {
            'timestamp': datetime.now(),
            'price_gasolina_95': stats.get('gasolina_95', {}).get('media', 0),
            'price_gasoleoa': stats.get('gasoleoa', {}).get('media', 0),
            'source': 'ministerio',
            'region': 'Toledo - Todas',
            'meta_data': {
                'total_estaciones': ministerio_data.get('total_estaciones'),
                'estaciones_gasolina_95': stats.get('gasolina_95', {}).get('estaciones_con_precio'),
                'estaciones_gasoleoa': stats.get('gasoleoa', {}).get('estaciones_con_precio'),
                'min_gasolina_95': stats.get('gasolina_95', {}).get('min'),
                'max_gasolina_95': stats.get('gasolina_95', {}).get('max'),
                'min_gasoleoa': stats.get('gasoleoa', {}).get('min'),
                'max_gasoleoa': stats.get('gasoleoa', {}).get('max'),
            }
        }

        # Filter Repsol stations
        repsol_stations = [
            s for s in ministerio_data.get('estaciones', [])
            if 'REPSOL' in s.get('nombre', '').upper()
        ]

        # Calculate Repsol averages
        repsol_95_prices = [
            s['precios'].get('gasolina_95')
            for s in repsol_stations
            if s['precios'].get('gasolina_95') is not None
        ]
        repsol_diesel_prices = [
            s['precios'].get('gasoleoa')
            for s in repsol_stations
            if s['precios'].get('gasoleoa') is not None
        ]

        repsol_data = {
            'timestamp': datetime.now(),
            'price_gasolina_95': (
                sum(repsol_95_prices) / len(repsol_95_prices)
                if repsol_95_prices else 0
            ),
            'price_gasoleoa': (
                sum(repsol_diesel_prices) / len(repsol_diesel_prices)
                if repsol_diesel_prices else 0
            ),
            'source': 'ministerio',
            'region': 'Toledo - Repsol',
            'meta_data': {
                'total_estaciones': len(repsol_stations),
                'estaciones_gasolina_95': len(repsol_95_prices),
                'estaciones_gasoleoa': len(repsol_diesel_prices),
                'min_gasolina_95': min(repsol_95_prices) if repsol_95_prices else None,
                'max_gasolina_95': max(repsol_95_prices) if repsol_95_prices else None,
                'min_gasoleoa': min(repsol_diesel_prices) if repsol_diesel_prices else None,
                'max_gasoleoa': max(repsol_diesel_prices) if repsol_diesel_prices else None,
            }
        }

        # Save to database
        async with async_session() as session:
            try:
                # Save TODAS data
                todas_record = Price(**todas_data)
                session.add(todas_record)
                logger.info(f"Created TODAS record: {todas_data['price_gasolina_95']:.3f} / {todas_data['price_gasoleoa']:.3f}")

                # Save REPSOL data
                repsol_record = Price(**repsol_data)
                session.add(repsol_record)
                logger.info(f"Created REPSOL record: {repsol_data['price_gasolina_95']:.3f} / {repsol_data['price_gasoleoa']:.3f}")

                await session.commit()
                logger.info("Database records saved successfully")
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving to database: {e}", exc_info=True)
                return False

    finally:
        await engine.dispose()


async def main():
    """Main entry point."""
    success = await save_toledo_prices()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
