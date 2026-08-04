"""Integration tests for database models."""

from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from petro.infrastructure.db.models import (
    Forecast,
    IndicatorBrent,
    News,
    Price,
    VariableEconomic,
)
from petro.infrastructure.db.repositories import PriceRepository


@pytest.mark.asyncio
async def test_create_price(session: AsyncSession):
    """Test creating a price record."""
    price = Price(
        timestamp=datetime.utcnow(),
        price_gasolina_95=1.50,
        price_gasoleoa=1.40,
        source="geoportal",
    )
    session.add(price)
    await session.commit()

    assert price.id is not None
    assert price.price_gasolina_95 == 1.50


@pytest.mark.asyncio
async def test_create_indicator_brent(session: AsyncSession):
    """Test creating a Brent indicator record."""
    brent = IndicatorBrent(
        timestamp=datetime.utcnow(),
        value=82.50,
        currency="USD",
        unit="barrel",
        source="investing.com",
    )
    session.add(brent)
    await session.commit()

    assert brent.id is not None
    assert brent.value == 82.50


@pytest.mark.asyncio
async def test_create_news(session: AsyncSession):
    """Test creating a news record."""
    news = News(
        published_at=datetime.utcnow(),
        title="Precios bajan por reducción OPEP",
        content="El cartel OPEP anunció una reducción de producción...",
        source="Reuters",
        language="es",
        classification="opec",
        sentiment_score=0.5,
        is_duplicate=0,
    )
    session.add(news)
    await session.commit()

    assert news.id is not None
    assert news.title == "Precios bajan por reducción OPEP"


@pytest.mark.asyncio
async def test_create_forecast(session: AsyncSession):
    """Test creating a forecast record."""
    forecast = Forecast(
        timestamp=datetime.utcnow(),
        commodity="gasolina_95",
        predicted_price=1.55,
        direction="up",
        direction_probability=0.75,
        horizon_days=7,
        model_version="xgboost-v1",
    )
    session.add(forecast)
    await session.commit()

    assert forecast.id is not None
    assert forecast.predicted_price == 1.55


@pytest.mark.asyncio
async def test_price_repository_get_latest(session: AsyncSession):
    """Test PriceRepository.get_latest()."""
    # Create prices
    for i in range(3):
        price = Price(
            timestamp=datetime.utcnow(),
            price_gasolina_95=1.50 + i * 0.01,
            price_gasoleoa=1.40 + i * 0.01,
            source="geoportal",
        )
        session.add(price)

    await session.commit()

    # Get latest
    repo = PriceRepository(session)
    latest = await repo.get_latest()

    assert latest is not None
    assert latest.price_gasolina_95 > 1.50


@pytest.mark.asyncio
async def test_price_repository_list(session: AsyncSession):
    """Test PriceRepository.list()."""
    # Create prices
    for i in range(5):
        price = Price(
            timestamp=datetime.utcnow(),
            price_gasolina_95=1.50 + i * 0.01,
            price_gasoleoa=1.40 + i * 0.01,
            source="geoportal",
        )
        session.add(price)

    await session.commit()

    # List
    repo = PriceRepository(session)
    prices = await repo.list(limit=10)

    assert len(prices) >= 5


@pytest.mark.asyncio
async def test_variable_economic_create(session: AsyncSession):
    """Test creating economic variable."""
    var = VariableEconomic(
        timestamp=datetime.utcnow(),
        brent_change_1d=2.5,
        brent_change_7d=5.0,
        wti_change_1d=2.3,
        brent_wti_spread=1.2,
        eurusd_ratio=1.08,
    )
    session.add(var)
    await session.commit()

    assert var.id is not None
    assert var.brent_change_1d == 2.5


@pytest.mark.asyncio
async def test_relationship_forecast_explanations(session: AsyncSession):
    """Test relationship between Forecast and Explanations."""
    from petro.infrastructure.db.models import Explanation

    # Create forecast
    forecast = Forecast(
        timestamp=datetime.utcnow(),
        commodity="gasolina_95",
        predicted_price=1.55,
        direction="up",
        direction_probability=0.75,
        horizon_days=7,
        model_version="xgboost-v1",
    )
    session.add(forecast)
    await session.commit()

    # Create explanations
    for i, factor in enumerate(["brent_change_1d", "eurusd_ratio", "news_sentiment"]):
        explanation = Explanation(
            forecast_id=forecast.id,
            factor_name=factor,
            contribution_shap=0.25 - i * 0.05,
            contribution_rank=i + 1,
        )
        session.add(explanation)

    await session.commit()

    # Verify relationship
    assert len(forecast.explanations) == 3
    assert forecast.explanations[0].factor_name == "brent_change_1d"
