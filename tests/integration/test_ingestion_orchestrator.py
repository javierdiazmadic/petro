"""Integration tests for data ingestion orchestrator."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from petro.ingestion.orchestrator import DataIngestionOrchestrator
from petro.infrastructure.db.models import (
    IndicatorBrent,
    IndicatorWTI,
    Price,
    SystemLog,
)


@pytest.mark.asyncio
async def test_orchestrator_full_cycle(session: AsyncSession):
    """Test full data ingestion cycle."""
    orchestrator = DataIngestionOrchestrator(session)

    results = await orchestrator.run_full_cycle()

    assert results is not None
    assert "sources" in results
    assert "timestamp" in results
    assert "duration_seconds" in results


@pytest.mark.asyncio
async def test_orchestrator_ingest_prices(session: AsyncSession):
    """Test price ingestion."""
    orchestrator = DataIngestionOrchestrator(session)

    await orchestrator._ingest_prices()

    # Verify price was inserted
    from sqlalchemy import select
    stmt = select(Price)
    result = await session.execute(stmt)
    prices = result.scalars().all()

    assert len(prices) > 0
    assert prices[0].price_gasolina_95 > 0
    assert prices[0].price_gasoleoa > 0


@pytest.mark.asyncio
async def test_orchestrator_ingest_indicators(session: AsyncSession):
    """Test indicator ingestion."""
    orchestrator = DataIngestionOrchestrator(session)

    await orchestrator._ingest_indicators()

    # Verify indicators were inserted
    from sqlalchemy import select

    brent_stmt = select(IndicatorBrent)
    brent_result = await session.execute(brent_stmt)
    brents = brent_result.scalars().all()

    wti_stmt = select(IndicatorWTI)
    wti_result = await session.execute(wti_stmt)
    wtis = wti_result.scalars().all()

    assert len(brents) > 0
    assert len(wtis) > 0
    assert brents[0].value > 0
    assert wtis[0].value > 0


@pytest.mark.asyncio
async def test_orchestrator_log_cycle(session: AsyncSession):
    """Test cycle logging."""
    orchestrator = DataIngestionOrchestrator(session)

    results = {
        "timestamp": None,
        "sources": {"prices": "success"},
        "total_records_inserted": 5,
        "errors": [],
    }

    await orchestrator._log_cycle(results)

    # Verify log was inserted
    from sqlalchemy import select

    stmt = select(SystemLog)
    result = await session.execute(stmt)
    logs = result.scalars().all()

    assert len(logs) > 0
    assert logs[0].component == "ingestion.orchestrator"
    assert logs[0].level == "info"
