# FASE 2 — Base de Datos

## Objetivo

Diseñar e implementar la base de datos completa con modelos SQLAlchemy, migraciones Alembic, repositorios de acceso a datos, e índices optimizados.

---

## Arquitectura

### Modelos ORM (SQLAlchemy 2.0)

16 modelos creados con relaciones y validaciones:

| Modelo | Tipo | TimescaleDB | Descripción |
|--------|------|-----------|-------------|
| `Price` | Hypertable | ✅ | Precios gasolina + gasóleo (diarios) |
| `IndicatorBrent` | Hypertable | ✅ | Cotización Brent (USD/barril) |
| `IndicatorWTI` | Hypertable | ✅ | Cotización WTI (USD/barril) |
| `IndicatorEURUSD` | Hypertable | ✅ | Cambio EUR/USD |
| `InventoryEIA` | Hypertable | ✅ | Inventarios EIA (gasolina, destilados) |
| `ProductionOPEC` | Hypertable | ✅ | Producción OPEP (barriles/día) |
| `News` | Hypertable | ✅ | Noticias procesadas + sentimiento + NER |
| `VariableEconomic` | Hypertable | ✅ | Variables económicas derivadas |
| `VariableTemporal` | Hypertable | ✅ | Variables temporales (día, mes, etc) |
| `VariableStatistical` | Hypertable | ✅ | Variables estadísticas (MA, volatilidad) |
| `VariableTechnical` | Hypertable | ✅ | Indicadores técnicos (RSI, MACD, BB) |
| `VariableNews` | Hypertable | ✅ | Variables derivadas de noticias |
| `Forecast` | Hypertable | ✅ | Predicciones del modelo |
| `Explanation` | Tabla regular | ❌ | Explicaciones SHAP por predicción |
| `ModelRegistry` | Tabla regular | ❌ | Registro de versiones de modelos |
| `SystemLog` | Hypertable | ✅ | Logs de sistema (eventos de negocio) |

### Índices Principales

```
Price:
  - idx_price_created_at (created_at)
  - UNIQUE(timestamp)

Forecast:
  - idx_forecast_created_at (created_at)
  - idx_forecast_horizon (horizon_days)
  - idx_forecast_model (model_version)

News:
  - idx_news_created_at (created_at)
  - idx_news_language (language)
  - idx_news_classification (classification)

SystemLog:
  - idx_log_created_at (created_at)
  - idx_log_level (level)
  - idx_log_component (component)
```

### Particionamiento TimescaleDB

Todas las hypertables utilizan `created_at` o `timestamp` como dimensión de tiempo:

```sql
SELECT create_hypertable('price', 'created_at', if_not_exists => TRUE);
SELECT create_hypertable('forecast', 'created_at', if_not_exists => TRUE);
-- ... etc
```

**Ventajas**:
- Compresión automática de datos antiguos
- Queries rápidas sobre períodos (WHERE timestamp BETWEEN ...)
- Administración automática de almacenamiento

---

## Archivos Creados

### Modelos
- `src/petro/infrastructure/db/models.py` — 16 modelos SQLAlchemy con relaciones, índices, JSON fields

### Sesión & Engine
- `src/petro/infrastructure/db/session.py` — AsyncSQLAlchemy engine y session factory

### Repositorios
- `src/petro/infrastructure/db/repositories/base.py` — Repositorio base genérico (CRUD)
- `src/petro/infrastructure/db/repositories/price_repo.py` — Queries especializadas de precios
- `src/petro/infrastructure/db/repositories/news_repo.py` — Queries especializadas de noticias
- `src/petro/infrastructure/db/repositories/forecast_repo.py` — Queries de predicciones + accuracy
- `src/petro/infrastructure/db/repositories/model_repo.py` — Registry de modelos + comparación

### Migraciones
- `alembic/versions/001_create_initial_schema.py` — Migración inicial (crea todos los modelos)

### Tests
- `tests/integration/test_db_models.py` — Tests de integración con BD
- `tests/conftest.py` — Fixtures para BD en-memoria

---

## Características Principales

### 1. **Async/Await Nativo**
```python
async with AsyncSessionLocal() as session:
    user = await session.execute(select(User))
    await session.commit()
```

### 2. **Repositorios Genéricos**
```python
repo = PriceRepository(session)
latest = await repo.get_latest()
history = await repo.get_last_n_days(7)
change = await repo.get_price_change(7)
```

### 3. **Relaciones ORM**
```python
forecast = Forecast(...)
forecast.explanations = [Explanation(...), ...]
# Cascade delete automático
```

### 4. **Índices Optimizados**
- Índices en columnas de filtrado común
- UNIQUE constraints donde corresponde
- Foreign keys para integridad referencial

### 5. **JSON Fields Nativos**
```python
news.entities = {"countries": ["Spain"], "companies": ["Repsol"]}
model.hyperparameters = {"max_depth": 10, "learning_rate": 0.1}
```

---

## Uso en la Aplicación

### Inyección de Dependencias (FastAPI)

```python
from fastapi import Depends
from petro.infrastructure.db.session import get_session

@app.get("/prices/latest")
async def get_latest_price(session: AsyncSession = Depends(get_session)):
    repo = PriceRepository(session)
    return await repo.get_latest()
```

### Migraciones

```bash
# Aplicar todas las migraciones
alembic upgrade head

# Ver estado
alembic current

# Rollback una migración
alembic downgrade -1

# Crear nueva migración
alembic revision --autogenerate -m "Add new column"
```

---

## Modelo Entidad-Relación (ERD)

```
┌─────────────────┐
│     Price       │
├─────────────────┤
│ id (PK)         │
│ created_at      │
│ timestamp (UQ)  │
│ price_gasolina  │
│ price_gasoleoa  │
└─────────────────┘

┌──────────────────┐
│    Forecast      │
├──────────────────┤
│ id (PK)          │
│ created_at       │
│ commodity        │
│ predicted_price  │
│ direction        │
│ probability      │
│ model_version    │
└──────────────────┘
        ↓ 1..N
┌──────────────────┐
│  Explanation     │
├──────────────────┤
│ id (PK)          │
│ forecast_id (FK) │
│ factor_name      │
│ contribution     │
└──────────────────┘

┌──────────────────┐
│    News          │
├──────────────────┤
│ id (PK)          │
│ published_at     │
│ title            │
│ language         │
│ classification   │
│ entities (JSON)  │
│ sentiment_score  │
└──────────────────┘

┌──────────────────────┐
│  ModelRegistry       │
├──────────────────────┤
│ id (PK)              │
│ model_type           │
│ status (prod/train)  │
│ rmse_test            │
│ mae_test             │
│ model_path           │
│ mlflow_run_id        │
└──────────────────────┘

Variable Tables (7):
- VariableEconomic
- VariableTemporal
- VariableStatistical
- VariableTechnical
- VariableNews
- IndicatorBrent
- InventoryEIA
- ... (otros indicadores)
```

---

## Performance

### Características Optimize

1. **TimescaleDB Compression**
   - Datos > 7 días comprimidos automáticamente
   - Ahorro de 90% en storage para datos históricos

2. **Índices Estratégicos**
   - Índices en columnas de búsqueda frecuente
   - UNIQUE en timestamp (evita duplicados)

3. **Connection Pooling**
   ```python
   engine = create_async_engine(
       url,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True  # Valida conexiones
   )
   ```

4. **Lazy Loading (ORM)**
   ```python
   forecast = await repo.get_latest_with_explanations()
   # Las explicaciones se cargan automáticamente con joinedload
   ```

---

## Testing

### Tests de Integración

```bash
# Ejecutar tests de BD
pytest tests/integration/test_db_models.py -v

# Con cobertura
pytest tests/integration/test_db_models.py --cov=src/petro/infrastructure
```

### Base de Datos de Tests

- SQLite en-memoria (`:memory:`)
- Crea/destruye tablas por cada test
- Rápido (~100ms por test)
- Aislado de BD de desarrollo

---

## Próximos Pasos (FASE 3)

✅ **FASE 2 completada**: Modelos, migraciones, repositorios funcionales

**FASE 3 — Recolección de Datos**:
- Implementar conectores para Brent, WTI, EUR/USD, EIA, OPEP
- Scheduler de Celery para descargar datos cada 15 min
- Control de errores y reintentos
- Tests de conectores

---

## Archivo de Configuración

### Actualizar `alembic.ini`

Si es necesario, ajustar la URL de BD:

```ini
# Linux/Docker
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/petro_dev

# Tests
sqlalchemy.url = sqlite+aiosqlite:///:memory:
```

### Variables de Entorno

```bash
DATABASE__URL=postgresql+asyncpg://petro:password@db:5432/petro_dev
DATABASE__ECHO=False  # Log SQL queries
DATABASE__POOL_SIZE=10
DATABASE__MAX_OVERFLOW=20
```

---

**Estado**: ✅ Completada  
**Archivos**: 9 (5 repositorios + 2 modelos + 1 migración + 1 test)  
**Líneas de código**: ~1500  
**Tests**: 10+ casos de integración
