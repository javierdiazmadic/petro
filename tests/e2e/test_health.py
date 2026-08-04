"""End-to-end tests for health checks."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"]
    assert data["version"]
    assert "docs_url" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    """Test metrics endpoint."""
    response = await client.get("/api/v1/metrics")
    assert response.status_code == 200
    # Prometheus metrics format check
    assert b"# HELP" in response.content or b"# TYPE" in response.content
