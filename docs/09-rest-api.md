# FASE 9: REST API

## Resumen

REST API con FastAPI que expone predicciones, métricas e información de sistema:

- **6 endpoints principales** para predicciones, histórico y métricas
- **OpenAPI/Swagger** auto-documentación
- **Pydantic v2** validación de request/response
- **Async/await** para máximo rendimiento
- **Error handling** consistente y detallado
- **Prometheus metrics** integradas

## Stack

- **FastAPI** — Framework web async
- **Pydantic v2** — Validación y serialización
- **SQLAlchemy async** — Acceso a BD no-bloqueante
- **Prometheus** — Métricas de performance
- **uvicorn** — ASGI server

## Endpoints

### 1. Predicciones

#### `GET /api/v1/predict`
**Descripción**: Obtener predicción más reciente para múltiples horizontes

**Query Parameters:**
```
product: str (default: gasolina_95) — Producto a predecir
horizons: str (default: 1d,3d,7d) — Horizontes separados por coma
include_bounds: bool (default: true) — Incluir intervalos de confianza
```

**Response** (200 OK):
```json
{
  "timestamp": "2026-08-04T15:30:00Z",
  "forecast_valid_until": "2026-08-04T15:45:00Z",
  "predictions": {
    "gasolina_95": [
      {
        "timestamp": "2026-08-04T15:30:00Z",
        "horizon": "1d",
        "product": "gasolina_95",
        "current_price": 1.50,
        "predicted_price": 1.523,
        "change": 0.023,
        "change_pct": 1.53,
        "direction": "up",
        "confidence": {
          "up": 0.79,
          "stable": 0.15,
          "down": 0.06
        },
        "bounds": {
          "lower": 1.447,
          "upper": 1.599,
          "uncertainty_pct": 5.0
        }
      }
    ]
  },
  "model_info": {
    "run_id": "abc-123",
    "rmse": 0.0523,
    "r2": 0.8645
  }
}
```

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/api/v1/predict?product=gasolina_95&horizons=1d,3d,7d"
```

**Cache**: Actualizado cada 15 minutos por pipeline Celery

#### `GET /api/v1/history`
**Descripción**: Obtener histórico de predicciones

**Query Parameters:**
```
product: str (default: gasolina_95) — Producto
horizon: str (default: 1d) — Horizonte (1d, 3d, 7d)
days: int (default: 30, min: 1, max: 365) — Días de histórico
include_accuracy: bool (default: true) — Incluir métricas de precisión
```

**Response** (200 OK):
```json
{
  "product": "gasolina_95",
  "horizon": "1d",
  "count": 10,
  "total_count": 450,
  "predictions": [
    {
      "timestamp": "2026-08-04T15:30:00Z",
      "actual_price": 1.525,
      "predicted_price": 1.523,
      "error": 0.002,
      "direction": "up",
      "confidence": {
        "up": 0.79,
        "stable": 0.15,
        "down": 0.06
      }
    }
  ],
  "accuracy_metrics": {
    "mae": 0.0412,
    "rmse": 0.0523,
    "mape": 2.75
  }
}
```

**Uso**: Backtesting, evaluación de modelo, validación de predicciones

### 2. Métricas

#### `GET /api/v1/metrics`
**Descripción**: Comparación de modelos entrenados

**Response** (200 OK):
```json
{
  "best_model": "xgboost",
  "best_metrics": {
    "rmse": 0.0523,
    "mae": 0.0412,
    "r2": 0.8645,
    "mape": 2.75
  },
  "all_models": {
    "xgboost": {...},
    "lightgbm": {...},
    "random_forest": {...}
  },
  "last_training": "2026-08-04T02:00:00Z"
}
```

**Métricas:**
- **RMSE** — Error cuadrático medio (penaliza grandes errores)
- **MAE** — Error absoluto medio (interpretable, en €/L)
- **R²** — Proporción de varianza explicada (0-1)
- **MAPE** — Error porcentual medio (%)

**Uso**: Monitoreo de model drift, auditoría, alertas

#### `GET /api/v1/explainability`
**Descripción**: Feature importance y explicabilidad del modelo

**Query Parameters:**
```
top_n: int (default: 10, min: 1, max: 50) — Top N features
```

**Response** (200 OK):
```json
{
  "model_type": "xgboost",
  "feature_importance": [
    {
      "feature_name": "price_momentum_10d",
      "importance": 0.245,
      "rank": 1
    },
    {
      "feature_name": "brent_price",
      "importance": 0.198,
      "rank": 2
    }
  ],
  "timestamp": "2026-08-04T15:30:00Z"
}
```

**Implementación:**
- PHASE 6: Feature importance de modelos (XGBoost, LightGBM, RandomForest)
- PHASE 11 (futuro): SHAP para explicaciones por predicción

### 3. Sistema

#### `GET /api/v1/health`
**Descripción**: Chequeo de salud del sistema

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-08-04T15:30:00Z",
  "database": "connected",
  "redis": "connected",
  "model_loaded": true,
  "last_cycle": "2026-08-04T15:30:00Z",
  "version": "0.9.0"
}
```

**Estados:**
- `healthy` — Sistema operacional
- `degraded` — Función limitada (BD conectada, modelo falla)
- `unhealthy` — Fallos críticos

**Uso**: Load balancers, k8s probes, monitoring

#### `GET /api/v1/status`
**Descripción**: Estado detallado del sistema

**Response** (200 OK):
```json
{
  "status": "operational",
  "version": "0.9.0",
  "timestamp": "2026-08-04T15:30:00Z",
  "features": {
    "predictions": true,
    "explainability": true,
    "history": true,
    "metrics": true
  },
  "pipeline": {
    "frequency": "every 15 minutes",
    "last_run": "2026-08-04T15:30:00Z"
  }
}
```

#### `GET /`
**Descripción**: Información de la API

**Response**:
```json
{
  "name": "PETRO",
  "version": "0.9.0",
  "docs_url": "/docs",
  "redoc_url": "/redoc",
  "health_url": "/api/v1/health"
}
```

## Documentación Automática

### Swagger UI
```
http://localhost:8000/docs
```
- Interfaz interactiva
- Prueba endpoints
- Esquemas Pydantic visualizados

### ReDoc
```
http://localhost:8000/redoc
```
- Documentación en lectura

### OpenAPI JSON
```
http://localhost:8000/openapi.json
```
- Esquema completo en JSON
- Compatible con herramientas externas

## Schemas Pydantic

### Validación Automática

Todos los requests/responses validados con Pydantic v2:

```python
# Request
class PredictQuery(BaseModel):
    product: str = Field(default="gasolina_95")
    horizons: str = Field(default="1d,3d,7d")
    include_bounds: bool = Field(default=True)

# Response
class ForecastResponse(BaseModel):
    timestamp: datetime
    predictions: Dict[str, List[PricePredictor]]
    model_info: Optional[Dict]
```

**Beneficios:**
- Validación automática de tipos
- Documentación en OpenAPI
- Ejemplos en Swagger
- Serialización JSON segura

## Error Handling

### Errores Consistentes

```json
{
  "error": "Model not loaded",
  "error_code": "MODEL_NOT_AVAILABLE",
  "timestamp": "2026-08-04T15:30:00Z",
  "details": {
    "last_attempt": "2026-08-04T15:15:00Z",
    "retry_in_seconds": 300
  }
}
```

**Códigos Comunes:**
- `FORECAST_NOT_AVAILABLE` (404) — Sin datos
- `MODEL_NOT_AVAILABLE` (503) — Modelo no cargado
- `INTERNAL_ERROR` (500) — Error del servidor
- `VALIDATION_ERROR` (422) — Parámetros inválidos

## Performance

### Latency Targets
- `/api/v1/predict` — < 100ms (from Redis cache)
- `/api/v1/history` — < 500ms (DB query)
- `/api/v1/metrics` — < 100ms (cached)
- `/api/v1/health` — < 200ms (connection checks)

### Caching Strategy
- **Predictions**: Redis, actualizado cada 15 min
- **Metrics**: In-memory, actualizado diariamente
- **Features**: No cacheable (depende de hora actual)

### Concurrency
- Async/await por defecto
- uvicorn workers: `2 * CPU_COUNT + 1`
- Connection pool: PostgreSQL + Redis

## Testing

### Unit Tests (15 tests)
```bash
make test-api
pytest tests/integration/test_api_endpoints.py -v
```

Cubre:
- Endpoints accesibles (200/503)
- Response format (JSON válido)
- Query parameters
- Error handling
- Documentation endpoints (docs, redoc, openapi)

### Manual Testing

```bash
# Predicción
curl http://localhost:8000/api/v1/predict

# Histórico (últimos 30 días)
curl "http://localhost:8000/api/v1/history?days=30"

# Métricas
curl http://localhost:8000/api/v1/metrics

# Salud
curl http://localhost:8000/api/v1/health

# Swagger UI
open http://localhost:8000/docs
```

## Deployment

### Docker

```dockerfile
FROM python:3.12

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "petro.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
api:
  build: .
  ports:
    - "8000:8000"
  depends_on:
    - db
    - redis
  environment:
    SQLALCHEMY_DATABASE_URL: postgresql+asyncpg://user:pass@db:5432/petro
    REDIS_URL: redis://redis:6379
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: petro-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: petro-api
  template:
    metadata:
      labels:
        app: petro-api
    spec:
      containers:
      - name: api
        image: petro:0.9.0
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

## Monitoreo

### Prometheus Metrics

Endpoint: `/metrics/prometheus`

Métricas:
- `http_requests_total` — Total requests
- `http_request_duration_seconds` — Latencia por endpoint
- `http_requests_in_progress` — Requests activos
- `celery_task_executed_total` — Tasks completadas

### Alertas (Ejemplo)

```yaml
- alert: APILatencyHigh
  expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 0.5
  for: 5m

- alert: ModelNotLoaded
  expr: up{job="petro-api"} == 0
  for: 1m
```

## Mejoras Futuras (PHASES 10+)

- **PHASE 10**: Dashboard web (gráficos de predicciones + histórico)
- **PHASE 11**: Explicabilidad SHAP (por predicción individual)
- **PHASE 12**: WebSocket para actualizaciones en tiempo real
- **PHASE 13**: Edge API (modelo ligero en Mini PC)

## Integración

### Con PHASE 8
API consume predicciones cachadas por Celery:
- Celery actualiza cada 15 min
- Redis cache last prediction
- API lee desde cache (< 1ms latencia)

### Con PHASES 10+
- Dashboard consume `/api/v1/predict` y `/api/v1/history`
- SHAP usa `/api/v1/explainability`
- Monitoring usa `/api/v1/health` + `/metrics/prometheus`

---

**Completado**: 2026-08-04  
**Status**: PHASE 9 READY FOR APPROVAL
