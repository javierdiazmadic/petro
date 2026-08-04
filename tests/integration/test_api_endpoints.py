"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from datetime import datetime

from petro.api.main import app


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestPredictionEndpoints:
    """Tests for prediction endpoints."""

    @pytest.mark.asyncio
    async def test_get_latest_prediction(self, client):
        """Test getting latest prediction."""
        response = await client.get("/api/v1/predict")

        assert response.status_code in [200, 503]  # 200=success, 503=service unavailable

        if response.status_code == 200:
            data = response.json()
            assert "timestamp" in data
            assert "forecast_valid_until" in data
            assert "predictions" in data

    @pytest.mark.asyncio
    async def test_predict_with_parameters(self, client):
        """Test prediction with query parameters."""
        response = await client.get(
            "/api/v1/predict",
            params={"product": "gasolina_95", "horizons": "1d,3d"}
        )

        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_get_prediction_history(self, client):
        """Test getting prediction history."""
        response = await client.get("/api/v1/history")

        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "product" in data
            assert "horizon" in data
            assert "predictions" in data
            assert "count" in data

    @pytest.mark.asyncio
    async def test_history_with_parameters(self, client):
        """Test history with custom parameters."""
        response = await client.get(
            "/api/v1/history",
            params={
                "product": "gasóleo_a",
                "horizon": "3d",
                "days": 60,
            }
        )

        assert response.status_code in [200, 503]


class TestMetricsEndpoints:
    """Tests for metrics endpoints."""

    @pytest.mark.asyncio
    async def test_get_model_metrics(self, client):
        """Test getting model metrics."""
        response = await client.get("/api/v1/metrics")

        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "best_model" in data
            assert "best_metrics" in data
            assert "all_models" in data
            assert "last_training" in data

    @pytest.mark.asyncio
    async def test_get_explainability(self, client):
        """Test getting explainability data."""
        response = await client.get("/api/v1/explainability")

        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "model_type" in data
            assert "feature_importance" in data
            assert "timestamp" in data

            # Check feature importance structure
            features = data["feature_importance"]
            if features:
                feature = features[0]
                assert "feature_name" in feature
                assert "importance" in feature
                assert "rank" in feature


class TestHealthEndpoints:
    """Tests for health and status endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/api/v1/health")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "database" in data
        assert "redis" in data
        assert "model_loaded" in data
        assert "version" in data

        # Status should be one of: healthy, degraded, unhealthy
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_get_status(self, client):
        """Test status endpoint."""
        response = await client.get("/api/v1/status")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "features" in data
        assert "pipeline" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = await client.get("/")

        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs_url" in data
        assert "health_url" in data


class TestAPIDocumentation:
    """Tests for API documentation."""

    @pytest.mark.asyncio
    async def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint."""
        response = await client.get("/openapi.json")

        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    @pytest.mark.asyncio
    async def test_swagger_docs(self, client):
        """Test Swagger UI endpoint."""
        response = await client.get("/docs")

        assert response.status_code == 200
        assert "html" in response.text.lower() or "swagger" in response.text.lower()

    @pytest.mark.asyncio
    async def test_redoc_docs(self, client):
        """Test ReDoc endpoint."""
        response = await client.get("/redoc")

        assert response.status_code == 200
        assert "html" in response.text.lower() or "redoc" in response.text.lower()


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_not_found_endpoint(self, client):
        """Test 404 error handling."""
        response = await client.get("/api/v1/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_query_parameters(self, client):
        """Test invalid query parameters."""
        response = await client.get(
            "/api/v1/history",
            params={"days": 1000}  # Out of range
        )

        # Should either accept or return validation error
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_prometheus_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = await client.get("/metrics/prometheus")

        # Should be available
        assert response.status_code == 200

        # Should contain Prometheus format text
        assert "# HELP" in response.text or "# TYPE" in response.text


class TestResponseFormats:
    """Tests for response format validation."""

    @pytest.mark.asyncio
    async def test_json_response_format(self, client):
        """Test that responses are valid JSON."""
        response = await client.get("/api/v1/status")

        assert response.headers["content-type"].startswith("application/json")
        data = response.json()
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_response_headers(self, client):
        """Test response headers."""
        response = await client.get("/api/v1/health")

        assert "content-type" in response.headers
        assert response.headers["content-type"].startswith("application/json")

    @pytest.mark.asyncio
    async def test_timestamp_format(self, client):
        """Test that timestamps are ISO 8601 format."""
        response = await client.get("/api/v1/status")

        assert response.status_code == 200

        data = response.json()
        timestamp = data.get("timestamp")

        # Should be valid ISO 8601
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pytest.fail(f"Invalid timestamp format: {timestamp}")
