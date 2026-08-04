"""Integration tests for data connectors."""

import pytest

from petro.infrastructure.connectors import (
    BrentConnector,
    EURUSDConnector,
    GeoportalConnector,
    InventoryEIAConnector,
    NewsRSSConnector,
    OPECConnector,
    WTIConnector,
)


@pytest.mark.asyncio
async def test_brent_connector():
    """Test Brent connector."""
    connector = BrentConnector()
    data = await connector.fetch()

    assert data is not None
    assert data["source"] == "brent"
    assert "value" in data
    assert "timestamp" in data
    assert data["currency"] == "USD"
    assert data["unit"] == "barrel"


@pytest.mark.asyncio
async def test_wti_connector():
    """Test WTI connector."""
    connector = WTIConnector()
    data = await connector.fetch()

    assert data is not None
    assert data["source"] == "wti"
    assert "value" in data
    assert isinstance(data["value"], float)


@pytest.mark.asyncio
async def test_eurusd_connector():
    """Test EUR/USD connector."""
    connector = EURUSDConnector()
    data = await connector.fetch()

    assert data is not None
    assert data["source"] == "eurusd"
    assert "value" in data
    assert isinstance(data["value"], float)
    assert 0.8 < data["value"] < 1.3  # Realistic EUR/USD range


@pytest.mark.asyncio
async def test_eia_connector():
    """Test EIA inventory connector."""
    connector = InventoryEIAConnector()
    data = await connector.fetch()

    assert data is not None
    assert data["source"] == "eia"
    assert "gasoline_inventory" in data
    assert "distillate_inventory" in data
    assert "crude_inventory" in data


@pytest.mark.asyncio
async def test_opec_connector():
    """Test OPEC connector."""
    connector = OPECConnector()
    data = await connector.fetch()

    assert data is not None
    assert data["source"] == "opec"
    assert "total_production" in data
    assert 25 < data["total_production"] < 35  # Realistic OPEC production range


@pytest.mark.asyncio
async def test_geoportal_connector():
    """Test Geoportal connector."""
    connector = GeoportalConnector()
    data = await connector.fetch()

    assert data is not None
    assert data["source"] == "geoportal"
    assert "price_gasolina_95" in data
    assert "price_gasoleoa" in data
    assert data["currency"] == "EUR"
    assert data["unit"] == "liter"
    assert 1.3 < data["price_gasolina_95"] < 1.7  # Realistic Spanish prices


@pytest.mark.asyncio
async def test_news_rss_connector():
    """Test News RSS connector."""
    connector = NewsRSSConnector()
    data = await connector.fetch()

    assert data is not None
    assert data["source"] == "rss_news"
    assert "items" in data
    assert "total_count" in data
    # RSS feeds may or may not return items depending on connectivity
    # Just check structure
    assert isinstance(data["items"], list)
    assert isinstance(data["total_count"], int)
