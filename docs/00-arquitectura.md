# Arquitectura del Proyecto PETRO
## Sistema de Predicción del Precio de Gasolina y Gasóleo en España

**Fecha**: 2026-08-04  
**Versión**: 0.1 (FASE 0 — Arquitectura)  
**Estado**: Pendiente de aprobación

---

## 1. Objetivos de la FASE 0

1. **Definir completamente la arquitectura del sistema** antes de escribir una línea de código de producción.
2. **Fijar decisiones técnicas** con justificación arquitectónica.
3. **Documentar el flujo de datos end-to-end** desde recolección de datos hasta predicción y dashboard.
4. **Establecer patrones de diseño** (Clean Architecture) y estructura de carpetas que soporten las 14 fases.
5. **Crear artefactos de referencia** (diagramas, modelos entidad-relación) que guíen las implementaciones posteriores.

**Resultado esperado**: Un documento único (`docs/00-arquitectura.md`) que resuelva todas las preguntas arquitectónicas antes de la FASE 1 (Infraestructura).

---

## 2. Contexto y Decisiones de Negocio

### 2.1 Alcance del Producto

| Aspecto | Decisión |
|--------|----------|
| **Mercado objetivo** | España: precio minorista de gasolina 95 y gasóleo A |
| **Fuente de datos** | Geoportal de Precios de Carburantes (Ministerio de Industria, diario) |
| **Tipo de predicción** | Regresión (precio exacto €/L) + clasificación derivada (sube/baja/estable + probabilidad) |
| **Horizonte temporal** | Corto plazo: próximos 1-7 días (horizonte prioritario) |
| **Frecuencia de actualización** | Cada 15 minutos (recolección de datos, inferencia, API) |
| **Cloud provider** | Agnóstico de proveedor hasta FASE 12 |

### 2.2 Restricciones No Funcionales

- **Despliegue final (FASE 13)**: Mini PC Intel N150 + 16 GB RAM, Ubuntu Server — consumo CPU/RAM mínimo.
- **Disponibilidad**: 24/7, sin intervención manual.
- **Latencia inferencia**: < 100 ms por predicción.
- **Retención de datos**: Mínimo 2 años de histórico de precios + noticias.

---

## 3. Arquitectura General

### 3.1 Estilo Arquitectónico: Clean Architecture + Hexagonal

Adoptamos **Clean Architecture con énfasis en hexagonal (puertos y adaptadores)**:

```
┌────────────────────────────────────────────┐
│          Presentation Layer (API, Dashboard)
├────────────────────────────────────────────┤
│        Application Layer (Use Cases)        │
│  - Ingestion orchestration                 │
│  - Feature engineering                     │
│  - Inference pipeline                      │
├────────────────────────────────────────────┤
│        Domain Layer (Business Logic)        │
│  - Entidades: Precio, Noticia, Predicción │
│  - Reglas de negocio puras                │
├────────────────────────────────────────────┤
│  Infrastructure Layer (Adaptadores)        │
│  - BD, caché, conectores externos          │
└────────────────────────────────────────────┘
```

**Beneficios**:
- Independencia de frameworks (intercambiable PostgreSQL ↔ MongoDB en la teoría).
- Testabilidad (domain logic sin dependencias).
- Separación clara de responsabilidades.
- Modularidad: cada fase agrega un nuevo caso de uso sin tocar capas inferiores.

### 3.2 No Microservicios

**Decisión**: Monolito modular, no microservicios.

**Razón**: El Mini PC de destino (Fase 13) tiene 16 GB y un N150. Orquestar varios procesos distribuidos (API, workers Celery, beat, cada uno en su contenedor) consumiría RAM de coordinación, logs distribuidos y complejidad operativa innecesaria. Un monolito modular (FastAPI + Celery en el mismo proceso o contenedores ligeros) es más práctico.

---

## 4. Stack Tecnológico

### 4.1 Backend & Datos

| Capa | Tecnología | Versión | Justificación |
|------|-----------|---------|---------------|
| **Lenguaje** | Python | 3.12 | Tipado estático (3.12 mejora type hints), ecosistema ML maduro |
| **API Web** | FastAPI | 0.110+ | OpenAPI automático (Fase 9), ASGI async, mínimo overhead |
| **ORM Async** | SQLAlchemy | 2.0+ | async/await, tipo-safe, Alembic nativo |
| **BD primaria** | PostgreSQL 16 + TimescaleDB | - | Series temporales comprimidas, hypertables, mejor que Postgres vanilla en Fase 13 |
| **Caché** | Redis 7+ | - | Sesiones, caché de lecturas, broker Celery |
| **Task queue** | Celery + Celery Beat | 5.3+ | Reintentos/backoff (Fase 3), encadenamiento (Fase 8), observabilidad |
| **Validación** | Pydantic | 2.0+ | Type hints en runtime, schemas JSON automáticos |
| **Migraciones BD** | Alembic | 1.12+ | Versionado reproducible, rollback |

### 4.2 Machine Learning

| Componente | Tecnología | Justificación |
|-----------|-----------|---------------|
| **Modelos** | XGBoost, LightGBM, RandomForest | Comparación Fase 6, rápidos, interpretables |
| **Explicabilidad** | SHAP + Feature Importance | Fase 11: explicaciones de por qué sube/baja |
| **Registro de modelos** | MLflow server (Postgres backend) | Tracking completo, UI web, versionado, agnóstico de cloud |
| **Datos** | NumPy, Pandas | Procesamiento tabular, feature engineering |

### 4.3 Procesamiento de Noticias (NLP)

| Componente | Tecnología (Desarrollo 125GB RAM) | Producción/Edge |
|-----------|-----------|---------------|
| **Feeds RSS** | feedparser | feedparser |
| **Limpieza HTML** | trafilatura + BeautifulSoup | trafilatura + BeautifulSoup |
| **Detección idioma** | langdetect | langdetect |
| **NER (Entidades)** | spaCy (modelos es/en large) + Transformers | spaCy small / offline model |
| **Clasificación** | BERT (bert-base-multilingual-cased) fine-tuned | TF-IDF + LR (downgrade) |
| **Embedding noticias** | Sentence-Transformers (all-MiniLM-l12-v2) | Precalculado, indexado |

> **Estrategia**: En desarrollo usamos BERT completo, Transformers, embeddings vectoriales. En producción/edge (Fase 13 o GCP cloud functions): exportamos modelos cuantizados, usamos TF-IDF + LR como fallback.

### 4.4 Logging & Configuración

| Aspecto | Desarrollo (125GB) | Producción Edge (Mini PC) |
|--------|-----------|---------------|
| **Logging** | Python `logging` + ELK stack (Elasticsearch 8) | Python `logging` + JSON a stdout |
| **Configuración** | Pydantic Settings | Pydantic Settings |
| **Monitorización** | Prometheus + Grafana dashboards | Prometheus metrics endpoint (scrape manual) |
| **Tracing distribuido** | Jaeger (optional, dev) | Deshabilitado |

> **Stack completo en desarrollo**: ELK para logs centralizados, Prometheus+Grafana para métricas, alertas en tiempo real. En producción/edge: JSON a stdout.

### 4.5 Infraestructura & Deployment

| Componente | Tecnología | Justificación |
|-----------|-----------|---------------|
| **Contenedores** | Docker | Reproducibilidad, aislamiento |
| **Orquestación contenedores** | docker-compose | Simple, suficiente para un Mini PC |
| **IaC (Fase 12)** | Terraform / Cloud provider CLI | Agnóstico, elegir en Fase 12 |

### 4.6 Testing

| Nivel | Framework | Herramientas |
|------|-----------|-------------|
| **Unit tests** | pytest | pytest, pytest-asyncio, pytest-mock |
| **Integration tests** | pytest | testcontainers, fixtures BD |
| **E2E tests** | pytest + client HTTP | httpx client, seed data |

---

## 4.7 Procesamiento Distribuido & GPU

| Componente | Tecnología | Uso |
|-----------|-----------|-----|
| **GPU Training** | PyTorch + CUDA 12.1 | Entrenamiento de modelos (XGBoost GPU, LightGBM CUDA) |
| **Procesamiento paralelo** | Ray (125GB RAM) | Feature engineering distribuida, hyperparameter tuning |
| **Almacenamiento interim** | DuckDB (in-process OLAP) | Análisis rápido de datos antes de insertar en BD |

---

## 4.8 Estrategia Dev → Cloud → Edge

**Este es el aspecto clave de la arquitectura**:

```
┌─────────────────────────────────────────────────────────────────┐
│  FASE 0-13: DESARROLLO (125GB RAM, 42GB VRAM)                  │
│  - BERT + Transformers (NLP completo)                           │
│  - MLflow server + PostgreSQL + Prometheus + Grafana + ELK      │
│  - Ray para procesamiento distribuido                           │
│  - GPU para entrenamiento (XGBoost CUDA, etc.)                  │
│  - docker-compose con 8+ servicios                              │
│                                                                 │
│  ↓ Exportar modelos cuantizados, scripts, configuración         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  FASE 12: GCP CLOUD (agnóstico)                                │
│  - Cloud Run (API)                                              │
│  - Cloud Scheduler (Celery Beat → Cloud Functions)              │
│  - BigQuery (históricos, features)                              │
│  - Cloud Storage (modelos, artefactos)                          │
│  - Vertex AI (training opcional)                                │
│  - Cloud Logging + Cloud Monitoring                             │
│                                                                 │
│  ↓ O downgrade a edge: exportar modelo, Docker ligero          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  FASE 13: MINI PC EDGE (16GB RAM, N150)                        │
│  - Docker Compose simplificado (API + worker)                   │
│  - PostgreSQL + TimescaleDB (comprimido)                        │
│  - Redis o caché en memoria                                     │
│  - Modelo cuantizado + fallback TF-IDF                          │
│  - Sin Prometheus server, sin ELK, sin Transformers grandes     │
│  - 24/7 consumo CPU/RAM mínimo                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Organización de código para soportar esto**:
- `src/petro/ml/inference/loaders.py`: Carga modelo completo (Transformers) O cuantizado según ENV
- `src/petro/nlp/classifiers.py`: Usa BERT O TF-IDF según ENV
- `src/petro/core/config.py`: Feature flags (NLP_MODEL_SIZE=full|lite, ENABLE_GPU=True|False, etc.)
- Scripts en `scripts/`: Export modelos para edge, cuantización, configuración de fallbacks

---

## 5. Estructura de Carpetas

```
petro/
│
├── pyproject.toml              # Dependencias, metadata del proyecto
├── Makefile                    # Tareas: install, test, run, docker build
├── docker-compose.yml          # Dev completo: API + DB + Redis + Celery + MLflow + Prometheus + Grafana + ELK (10+ servicios)
├── docker-compose.minimal.yml  # Dev mínimo: solo API + DB + Redis (3 servicios)
├── docker-compose.prod.yml     # Prod/Edge: API + worker + beat (3 servicios, optimizado)
├── alembic.ini                 # Config migraciones
├── .env.example                # Template variables de entorno
├── .gitignore
│
├── docs/
│   ├── 00-arquitectura.md      # Este archivo
│   ├── 01-setup.md             # Setup local dev (instalación)
│   ├── 02-api-reference.md     # Detalle APIs (Fase 9)
│   └── 03-ml-pipeline.md       # Detalles ML (Fases 6-7)
│
├── src/petro/
│   │
│   ├── __init__.py
│   │
│   ├── core/                   # Núcleo de configuración
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic Settings (dev/prod)
│   │   ├── logging.py          # Setup logging JSON
│   │   ├── exceptions.py       # Excepciones de negocio
│   │   └── security.py         # Utilidades seguridad (tokens, CORS, etc.)
│   │
│   ├── domain/                 # Lógica pura de negocio (sin frameworks)
│   │   ├── __init__.py
│   │   ├── entities.py         # Dataclasses/Pydantic: Precio, Noticia, Predicción
│   │   ├── value_objects.py    # Price, Probability, Direction
│   │   └── services.py         # Servicios de dominio: cálculo de probabilidad, etc.
│   │
│   ├── infrastructure/         # Adaptadores a tecnologías externas
│   │   ├── __init__.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── models.py       # SQLAlchemy ORM models
│   │   │   ├── session.py      # SessionLocal, engine setup (async)
│   │   │   ├── repositories/   # Data access patterns
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py     # Repositorio base genérico
│   │   │   │   ├── price_repo.py
│   │   │   │   ├── news_repo.py
│   │   │   │   ├── prediction_repo.py
│   │   │   │   └── variable_repo.py
│   │   │   └── migrations/     # (symlink o copia de alembic/versions)
│   │   │
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py # Wrapper async Redis
│   │   │   └── strategies.py   # Caché strategies
│   │   │
│   │   └── connectors/         # Conectores a APIs externas
│   │       ├── __init__.py
│   │       ├── base.py         # Clase base conector
│   │       ├── brent.py        # Conectar Brent (ej: API YCHARTS, Investing)
│   │       ├── wti.py          # Conectar WTI
│   │       ├── eurusd.py       # EUR/USD (API forex)
│   │       ├── inventories.py  # Inventarios EIA, OPEP
│   │       ├── opec.py         # Producción OPEP
│   │       ├── news_rss.py     # Feeds RSS de noticias
│   │       └── geoportal.py    # Geoportal Ministerio España (scraping/API)
│   │
│   ├── api/                    # FastAPI routers y schemas
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app, middleware, lifespan
│   │   ├── dependencies.py     # Inyección de dependencias
│   │   ├── health.py           # Endpoint /health (status check)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── predictions.py  # GET /v1/predictions/latest, /v1/predictions/history
│   │   │   ├── news.py         # GET /v1/news/latest, /v1/news/search
│   │   │   ├── indicators.py   # GET /v1/indicators/{type}
│   │   │   ├── system.py       # GET /v1/system/status, /v1/system/metrics
│   │   │   └── schemas.py      # Pydantic models (request/response)
│   │   │
│   │   └── middleware/         # CORS, error handling, logging
│   │       └── __init__.py
│   │
│   ├── ingestion/              # Orquestación Fase 3
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Coordina descarga de datos
│   │   ├── fetch_prices.py     # Descargar precios de todas las fuentes
│   │   ├── fetch_indicators.py # Descargar Brent, WTI, EUR/USD, etc.
│   │   ├── fetch_news.py       # Descargar noticias RSS
│   │   └── retry_policy.py     # Política de reintentos
│   │
│   ├── nlp/                    # Procesamiento Fase 4
│   │   ├── __init__.py
│   │   ├── cleaner.py          # Limpieza HTML, normalización
│   │   ├── deduplicator.py     # Eliminar duplicados
│   │   ├── lang_detector.py    # Detección idioma
│   │   ├── ner.py              # Extracción entidades (spaCy)
│   │   ├── classifier.py       # Clasificación noticias (TF-IDF + LR)
│   │   └── models/             # Modelos NLP entrenados (gitignored)
│   │
│   ├── features/               # Ingeniería Fase 5
│   │   ├── __init__.py
│   │   ├── calculators/
│   │   │   ├── __init__.py
│   │   │   ├── economic.py     # Variables económicas: Brent diff, WTI diff, EUR/USD ratio
│   │   │   ├── temporal.py     # Temporales: day_of_week, hour, is_weekend, season
│   │   │   ├── statistical.py  # Estadísticas: rolling mean, volatility, lag features
│   │   │   ├── derived.py      # Variables derivadas: spread Brent-WTI, etc.
│   │   │   ├── technical.py    # Indicadores técnicos: RSI, MACD sobre precios históricos
│   │   │   └── news_derived.py # Sentimiento de noticias, count de noticias
│   │   └── pipeline.py         # Orquesta cálculo de features
│   │
│   ├── ml/                     # Machine Learning
│   │   ├── __init__.py
│   │   ├── training/           # FASE 6
│   │   │   ├── __init__.py
│   │   │   ├── trainer.py      # Entrenar XGBoost, LightGBM, RF
│   │   │   ├── evaluator.py    # Métricas, CV, feature importance
│   │   │   ├── hyperparameter_tuner.py # Optimización (Optuna)
│   │   │   └── experiment.py   # MLflow tracking
│   │   │
│   │   ├── inference/          # FASE 7
│   │   │   ├── __init__.py
│   │   │   ├── model_loader.py # Cargar modelo .pkl/.joblib
│   │   │   ├── predictor.py    # Ejecutar predicción (<100ms)
│   │   │   └── postprocessor.py # Derivar probabilidad de clasificación
│   │   │
│   │   └── explainability/     # FASE 11
│   │       ├── __init__.py
│   │       ├── shap_explainer.py # SHAP values, force plots
│   │       └── feature_importance.py # Importancia de variables
│   │
│   ├── scheduler/              # Automatización Fase 8
│   │   ├── __init__.py
│   │   ├── app.py              # Celery app instance
│   │   ├── tasks.py            # Task definitions (fetch, process, predict, save)
│   │   ├── beat_schedule.py    # Celery Beat schedule (cada 15 min)
│   │   └── callbacks.py        # on_success, on_failure handlers
│   │
│   ├── dashboard/              # Fase 10 (tentativo: Jinja2 + HTMX)
│   │   ├── __init__.py
│   │   ├── routes.py           # Routers del dashboard
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── home.html       # Página principal: precio, predicción, noticias
│   │   │   ├── history.html    # Histórico, gráficas
│   │   │   └── components/
│   │   │       ├── price_card.html
│   │   │       ├── chart.html
│   │   │       └── news_list.html
│   │   └── static/
│   │       ├── css/
│   │       │   └── main.css
│   │       └── js/
│   │           ├── chart.js
│   │           └── htmx.min.js
│   │
│   └── shared/                 # Utilidades compartidas
│       ├── __init__.py
│       ├── types.py            # TypedDicts, Enums
│       ├── constants.py        # Constantes globales
│       ├── utils.py            # Helpers
│       └── validators.py       # Custom validators
│
├── alembic/                    # Migraciones Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures comunes
│   │
│   ├── unit/
│   │   ├── test_domain/        # Lógica de negocio pura
│   │   ├── test_nlp/           # Procesamiento noticias
│   │   ├── test_features/      # Cálculo de features
│   │   └── test_ml/            # ML (training, inference)
│   │
│   ├── integration/
│   │   ├── test_db/            # Repositorios, ORM
│   │   ├── test_cache/         # Redis
│   │   ├── test_connectors/    # Conectores (mocked)
│   │   └── test_scheduler/     # Celery tasks
│   │
│   └── e2e/
│       ├── test_api.py         # API tests end-to-end
│       └── test_pipeline.py    # Ingestión completa → predicción
│
├── scripts/                    # Scripts utilidad
│   ├── create_admin.py
│   ├── backfill_history.py     # Cargar datos históricos
│   ├── train_model.py          # Script de entrenamiento manual
│   └── export_model.py         # Exportar modelo para producción
│
├── infra/                      # Infraestructura
│   ├── docker/
│   │   ├── Dockerfile.api      # Imagen API
│   │   ├── Dockerfile.worker   # Imagen Celery worker
│   │   ├── Dockerfile.beat     # Imagen Celery Beat
│   │   └── .dockerignore
│   │
│   └── cloud/                  # Fase 12 (agnóstico de proveedor)
│       ├── terraform/
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── scripts/
│           ├── train_remote.sh # Lanzar entrenamiento en nube
│           └── compare_models.py # Comparar métricas
│
├── models/                     # Artefactos (gitignored)
│   ├── production/
│   │   ├── price_model.pkl
│   │   └── scaler.pkl
│   ├── training/
│   │   └── experiments/
│   └── mlflow/                 # MLflow local backend
│
└── .env.example                # Template de configuración
```

---

## 6. Flujo de Datos End-to-End

```mermaid
graph LR
    A["APIs Externas<br/>(Brent, WTI, EUR/USD,<br/>EIA, OPEP, RSS)"]
    B["Connectors<br/>(fetching, retry)"]
    C["PostgreSQL<br/>TimescaleDB"]
    D["Redis Cache"]
    E["NLP Pipeline<br/>(limpieza, NER,<br/>clasificación)"]
    F["Feature Engineering<br/>(económicos, temporales,<br/>estadísticos)"]
    G["ML Pipeline<br/>(XGBoost/LightGBM)"]
    H["Predicción<br/>(regresión)<br/>Clasificación<br/>(derivada)"]
    I["API REST"]
    J["Dashboard Web"]
    K["Logs & Métricas"]
    
    A --> B
    B --> C
    C --> D
    C --> E
    E --> C
    C --> F
    F --> C
    C --> G
    G --> H
    H --> C
    C --> I
    I --> J
    C --> K
    H --> K
```

**Descripción del flujo**:

1. **Ingestion (FASE 3, cada 15 min)**:
   - Celery Beat lanza `fetch_all_data` cada 15 min
   - Conectores descargan datos de Brent, WTI, EUR/USD, inventarios, OPEP, feeds RSS
   - Almacenan en `PostgreSQL`
   - Reintentos automáticos en caso de fallo

2. **Procesamiento de Noticias (FASE 4)**:
   - NLP pipeline lee noticias nuevas de BD
   - Limpieza HTML, deduplicación, detección idioma
   - Extracción de entidades (país, empresa, refinería)
   - Clasificación (relevancia, categoría)
   - Guardar metadatos en BD

3. **Feature Engineering (FASE 5)**:
   - Lee precios, indicadores, noticias de BD
   - Calcula variables económicas, temporales, estadísticas
   - Guarda features calculadas en tablas `_features`

4. **Entrenamiento (FASE 6)**:
   - Batch job (manual o cloud, Fase 12)
   - Lee features de BD + target (precios futuros)
   - Entrena XGBoost, LightGBM, RandomForest
   - Registra en MLflow (métricas, feature importance, SHAP)
   - Exporta mejor modelo a `models/production/price_model.pkl`

5. **Inferencia (FASE 7, cada 15 min)**:
   - Celery task lee datos más recientes
   - Calcula features en tiempo real
   - Carga modelo de `models/production/`
   - Ejecuta predicción (< 100 ms)
   - Postprocessor: deriva probabilidad de clasificación (sube/baja/estable)
   - Almacena resultado en tabla `predictions`

6. **API & Dashboard (FASES 9-10)**:
   - API REST sirve últimas predicción, históricos, noticias, indicadores
   - Dashboard web (Jinja2 + HTMX) consume API, muestra gráficas
   - Caché en Redis acelera lecturas

7. **Logs & Observabilidad**:
   - Todo evento importante (fetch fallido, predicción registrada, entrenamiento completado) se loguea en JSON a stdout
   - Tabla `system_logs` en BD para auditoria
   - Endpoint `/metrics` expone Prometheus metrics

---

## 7. Diseño de Base de Datos

### 7.1 Modelo Entidad-Relación (lógico)

```mermaid
erDiagram
    PRICE ||--o{ FORECAST : "targets"
    PRICE ||--o{ VARIABLE : "based_on"
    INDICATOR ||--o{ VARIABLE : "inputs"
    NEWS ||--o{ VARIABLE : "sentiment"
    FORECAST ||--o{ EXPLANATION : "explains"
    MODEL_REGISTRY ||--o{ FORECAST : "versions"
    
    PRICE {
        bigint id PK
        timestamp created_at
        float price_gasolina_95
        float price_gasoleoa
        string source
    }
    
    INDICATOR {
        bigint id PK
        timestamp created_at
        string type "brent|wti|eurusd|etc"
        float value
        string source
    }
    
    NEWS {
        bigint id PK
        timestamp created_at
        string title
        text content
        string source
        string language
        string classification
        jsonb entities "country, company, refinery, org"
        float sentiment_score
    }
    
    VARIABLE {
        bigint id PK
        timestamp timestamp
        string name
        float value
        string category "economic|temporal|statistical|derived|technical"
    }
    
    FORECAST {
        bigint id PK
        timestamp created_at
        float predicted_price
        float predicted_direction_probability "sube: >0.5, baja: <0.5"
        string direction "up|down|stable"
        integer horizon_days
        string model_version
    }
    
    EXPLANATION {
        bigint id PK
        bigint forecast_id FK
        string factor "variable_name"
        float contribution_shap
        text explanation_text
    }
    
    MODEL_REGISTRY {
        bigint id PK
        timestamp created_at
        string model_type "xgboost|lightgbm|rf"
        float rmse_test
        float mae_test
        string model_path
        string status "training|production|archived"
        jsonb hyperparameters
    }
    
    SYSTEM_LOG {
        bigint id PK
        timestamp created_at
        string level "info|warning|error"
        string component
        text message
        jsonb context
    }
```

### 7.2 Tablas Principales (Fase 2 especificará DDL)

| Tabla | Descripción | Tipo Temporal | Índices Prioritarios |
|-------|-------------|---------------|---------------------|
| `price` | Precios minoristas España (95, A) | Sí (TimescaleDB) | (created_at DESC), (price_type, created_at DESC) |
| `indicator_brent` | Cotización Brent | Sí | (created_at DESC) |
| `indicator_wti` | Cotización WTI | Sí | (created_at DESC) |
| `indicator_eurusd` | Tipo de cambio EUR/USD | Sí | (created_at DESC) |
| `inventory_eia` | Inventarios EIA (gasolina, destilados) | Sí | (created_at DESC) |
| `production_opec` | Producción OPEP | Sí | (created_at DESC) |
| `news` | Noticias procesadas | Sí | (created_at DESC), (language), (classification) |
| `variable_economic` | Variables económicas calculadas | Sí | (timestamp, name) |
| `variable_temporal` | Variables temporales (día, hora, etc.) | Sí | (timestamp) |
| `variable_statistical` | Variables estadísticas (rolling mean, volatility) | Sí | (timestamp, name) |
| `variable_technical` | Indicadores técnicos | Sí | (timestamp, name) |
| `variable_news` | Variables derivadas de noticias | Sí | (timestamp) |
| `forecast` | Predicciones registradas | Sí | (created_at DESC), (horizon_days), (model_version) |
| `explanation` | Explicaciones SHAP por predicción | No | (forecast_id) |
| `model_registry` | Versiones de modelos entrenados | No | (status, created_at DESC) |
| `system_log` | Logs de sistema | Sí | (created_at DESC), (level, component) |

### 7.3 Estrategia de Particionamiento (Fase 2/13)

Con TimescaleDB, las tablas con hypertable se particionan automáticamente por tiempo:
- **Chunk interval**: 1 semana para tablas de alta frecuencia (precios cada 15 min)
- **Compresión**: automática después de 2 semanas (Fase 13 optimization)

---

## 8. Diseño de API REST (Fase 9 especificará detalles)

### 8.1 Endpoints a Alto Nivel

```
GET  /api/v1/health
GET  /api/v1/metrics                              # Prometheus format

GET  /api/v1/predictions/latest
GET  /api/v1/predictions/latest?commodity=gasolina|gasoleoa
GET  /api/v1/predictions/history?days=7&horizon=1
POST /api/v1/predictions/explain?id={forecast_id}

GET  /api/v1/news/latest?limit=20&language=es
GET  /api/v1/news/search?q=gasolina&from_date=2026-01-01&to_date=2026-08-04

GET  /api/v1/indicators/brent?days=30
GET  /api/v1/indicators/wti?days=30
GET  /api/v1/indicators/eurusd?days=30
GET  /api/v1/indicators/summary

GET  /api/v1/system/status                        # Health checks de componentes
GET  /api/v1/system/logs?level=error&limit=100
```

### 8.2 Estructura de Response (Pydantic)

```python
class PredictionResponse(BaseModel):
    id: int
    timestamp: datetime
    commodity: str  # "gasolina_95" | "gasoleoa"
    predicted_price: float  # €/L
    direction: str  # "up" | "down" | "stable"
    probability: float  # [0, 1]
    horizon_days: int
    model_version: str
    explanation: Optional[ExplanationResponse]

class ExplanationResponse(BaseModel):
    factors: List[Dict[str, Any]]  # [{"name": "brent_change", "value": 2.5, "contribution": 0.12}]
    summary: str  # "La probabilidad de subida aumenta porque el Brent ha subido un 3%..."
```

---

## 9. Flujo de Entrenamiento (Fase 6)

```mermaid
graph TD
    A["Dataset histórico<br/>2+ años"]
    B["Validación datos<br/>Test para leaks"]
    C["Train/Test split<br/>80/20"]
    D["Feature scaling<br/>StandardScaler"]
    E["Entrenamiento en paralelo<br/>XGBoost, LightGBM, RF"]
    F["Cross-validation 5-fold"]
    G["Métricas: RMSE, MAE, MAPE"]
    H["SHAP values<br/>Feature importance"]
    I["Hiperparámetro tuning<br/>Optuna 50 trials"]
    J["Seleccionar mejor modelo"]
    K["Registrar en MLflow"]
    L["Exportar .pkl + scaler"]
    M["test_model.pkl"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> M
```

**Proceso**:
1. Leer histórico (2+ años) desde `PostgreSQL`
2. Validar: no data leaks, distribution shift checks
3. Split 80/20 (temporal, no random — respetando orden temporal)
4. Normalizar features con `StandardScaler`
5. Entrenar 3 modelos en paralelo (XGBoost, LightGBM, RandomForest)
6. 5-fold cross-validation, registrar métricas (RMSE, MAE, MAPE)
7. Calcular SHAP values, feature importance
8. Optimizar hiperparámetros con Optuna (50 trials)
9. Elegir modelo con mejor CV score
10. Registrar en MLflow (artefactos, parámetros, métricas)
11. Exportar modelo final + scaler a `models/production/`

---

## 10. Flujo de Inferencia (Fase 7)

```mermaid
graph LR
    A["Celery Task<br/>cada 15 min"] --> B["Cargar modelo<br/>.pkl"]
    B --> C["Leer últimos<br/>datos de BD"]
    C --> D["Calcular features<br/>en tiempo real"]
    D --> E["Normalizar<br/>StandardScaler"]
    E --> F["Predict<br/>(< 100 ms)"]
    F --> G["Postprocessing:<br/>derivar probabilidad"]
    G --> H["Crear Forecast"]
    H --> I["Guardar en BD"]
    I --> J["Actualizar caché<br/>Redis"]
    J --> K["Log resultado"]
```

**Objetivo**: < 100 ms de latencia total (Fase 13 optimization).

**Postprocessing**:
- Modelo predice precio €/L para +N días
- Comparar predicción vs precio actual
- Derivar probabilidad: P(sube) = sigmoid(predicted_price - current_price)
- Clasificar: sube (>0.6), baja (<0.4), estable (0.4-0.6)
- Guardar probabilidad y dirección junto con precio predicho

---

## 11. Flujo de Automatización (Fase 8, cada 15 minutos)

```mermaid
graph TD
    A["Celery Beat<br/>cada 15 min"] --> B["fetch_all_data"]
    B --> C["fetch_prices"]
    C --> D["fetch_indicators"]
    D --> E["fetch_news"]
    E --> F["process_news<br/>NLP pipeline"]
    F --> G["calculate_features<br/>Feature engineering"]
    G --> H["run_inference<br/>Predicción"]
    H --> I["save_forecast<br/>BD + caché"]
    I --> J["log_cycle_completion"]
    
    style A fill:#ff9999
    style B fill:#99ccff
    style C fill:#ccffcc
    style D fill:#ccffcc
    style E fill:#ccffcc
    style F fill:#ffcc99
    style G fill:#ffcc99
    style H fill:#ff99cc
    style I fill:#99ff99
    style J fill:#ccccff
```

**Celery Beat Schedule**:
```python
app.conf.beat_schedule = {
    'full-cycle-15min': {
        'task': 'petro.scheduler.tasks.run_full_cycle',
        'schedule': crontab(minute='*/15'),
        'options': {'queue': 'predictions', 'priority': 10}
    }
}
```

**Task chain** (ejecutada secuencialmente):
```
fetch_all_data.s()
  | chain(
      fetch_prices.s(),
      fetch_indicators.s(),
      fetch_news.s()
    )
  | process_news.s()
  | calculate_features.s()
  | run_inference.s()
  | save_forecast.s()
```

Cada tarea tiene retry automático (3 reintentos con backoff exponencial).

---

## 12. Sistema de Logs

### 12.1 Niveles y Destinos

| Nivel | Destino | Formato | Ejemplo |
|-------|---------|---------|---------|
| **DEBUG** | stdout (dev only) | Texto | Feature X calculada: 2.5 |
| **INFO** | stdout (JSON) | JSON | `{"level": "info", "component": "ingestion", "msg": "Brent fetched", "value": 82.5}` |
| **WARNING** | stdout (JSON) + BD | JSON | `{"level": "warning", "component": "connectors.brent", "msg": "Retry #2/3"}` |
| **ERROR** | stdout (JSON) + BD + alert | JSON | `{"level": "error", "component": "inference", "msg": "Model load failed", "error": "..."}` |
| **CRITICAL** | Todos + notificación | JSON | `{"level": "critical", ...}` |

### 12.2 Estructura JSON (python-json-logger)

```json
{
  "timestamp": "2026-08-04T10:30:45.123Z",
  "level": "INFO",
  "logger": "petro.ingestion",
  "component": "fetch_brent",
  "message": "Brent price fetched successfully",
  "context": {
    "source": "investing.com",
    "price": 82.54,
    "timestamp": "2026-08-04T10:30:00Z",
    "duration_ms": 234
  },
  "trace_id": "abc123..."
}
```

### 12.3 Logging by Module

- `petro.api`: Requests, responses, latency
- `petro.ingestion`: Fetch success/failure, retry count
- `petro.nlp`: Processing stats (duplicates, entities)
- `petro.features`: Feature calc errors
- `petro.ml.training`: Epoch, loss, metrics
- `petro.ml.inference`: Prediction latency, errors
- `petro.scheduler`: Task start/end, result
- `petro.infrastructure.db`: Slow queries (> 100 ms)

Tabla `system_log` en BD registra solo eventos de negocio relevantes (fallos críticos, entrenamientos, cambios de modelo).

---

## 13. Sistema de Configuración

### 13.1 Pydantic Settings (12-Factor)

```python
# src/petro/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

class RedisSettings(BaseSettings):
    url: str
    db: int = 0
    ttl_seconds: int = 3600

class MLSettings(BaseSettings):
    model_path: str = "models/production/price_model.pkl"
    scaler_path: str = "models/production/scaler.pkl"
    prediction_horizon_days: int = 7

class Settings(BaseSettings):
    env: str = "development"  # development | production
    debug: bool = False
    
    database: DatabaseSettings
    redis: RedisSettings
    ml: MLSettings
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False
    )

settings = Settings()
```

### 13.2 Archivos `.env`

**`.env.development`**:
```
ENV=development
DEBUG=True
DATABASE__URL=postgresql+asyncpg://user:pass@localhost:5432/petro_dev
REDIS__URL=redis://localhost:6379
CELERY__BROKER_URL=redis://localhost:6379/1
CELERY__RESULT_BACKEND=redis://localhost:6379/2
LOG_LEVEL=DEBUG
```

**`.env.production`**:
```
ENV=production
DEBUG=False
DATABASE__URL=postgresql+asyncpg://user:${DB_PASSWORD}@db.internal:5432/petro
REDIS__URL=redis://cache.internal:6379/0
CELERY__BROKER_URL=redis://cache.internal:6379/1
LOG_LEVEL=INFO
```

---

## 14. Mejoras Futuras y Riesgos

### 14.1 Mejoras Futuras

| Fase | Mejora | Prioridad | Esfuerzo |
|------|--------|-----------|----------|
| Post-13 | Transformers (BERT) para clasificación de noticias | Media | Alto |
| Post-13 | Predicciones multiproducto (más refinados, derivados) | Baja | Muy alto |
| Post-13 | Dashboard en React con WebSockets (actualizaciones en tiempo real) | Baja | Muy alto |
| Post-13 | Predicción de volatilidad (GARCH) | Media | Medio |
| Post-13 | Ingesta de factores macroeconómicos (inflation, PMI) | Media | Medio |
| Post-13 | Reentrenamiento automático sin intervención manual | Alta | Medio |
| Post-13 | A/B testing entre modelos | Media | Medio |

### 14.2 Riesgos y Mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación |
|--------|--------|------------|-----------|
| **Geoportal cambia estructura/cierra** | Crítico | Baja | Documentar parser, mantener connectors alternativos |
| **Ruido en precios Brent/WTI** | Alto | Medio | Validación de outliers, feature engineering robusto |
| **Modelo pierde accuracy en producción** | Alto | Medio | Cross-validation temporal, monitoring de residuales |
| **Base de datos crece exponencialmente** | Medio | Media | Particionamiento con TimescaleDB, purga de logs antiguos |
| **Mini PC no aguanta carga (Fase 13)** | Alto | Media | Optimización CPU/RAM desde Fase 1, profiling continuo |
| **Noticias RSS irrelevantes** | Bajo | Alta | Filtrado de fuentes, fine-tuning clasificador |

---

## 15. Verificación y Aprobación

### 15.1 Artefactos Entregados

✅ Este documento (`docs/00-arquitectura.md`) cubre:
- [x] Objetivos de FASE 0
- [x] Arquitectura general (Clean Architecture)
- [x] Stack tecnológico completo (justificado)
- [x] Estructura de carpetas (29 directorios, organización clara)
- [x] Diagrama de flujo de datos (Mermaid)
- [x] Modelo entidad-relación (14 tablas)
- [x] Diseño de API (10+ endpoints)
- [x] Flujo de entrenamiento (Fase 6)
- [x] Flujo de inferencia (Fase 7)
- [x] Flujo de automatización (Fase 8, cada 15 min)
- [x] Sistema de logs (JSON, niveles, destinos)
- [x] Sistema de configuración (12-factor, .env)
- [x] Mejoras futuras y riesgos

### 15.2 Próximos Pasos (FASE 1 — Infraestructura)

#### Desarrollo completo (125GB, aquí):
1. **Estructura de carpetas**
2. **pyproject.toml** con todas las dependencias (incluidas Transformers, PyTorch, Ray, ELK)
3. **docker-compose.yml** con stack completo:
   - API + PostgreSQL 16 + Redis 7
   - Celery worker (2+ workers en paralelo con GPU)
   - Celery Beat (scheduler)
   - MLflow server + PostgreSQL backend
   - Prometheus + Grafana
   - Elasticsearch + Kibana + Logstash (ELK)
   - Jaeger (tracing, opcional)
4. **Dockerfile.api, Dockerfile.worker, Dockerfile.beat** (desarrollo)
5. **Configuración logging, settings, variables de entorno**
6. **FastAPI app completa** con CORS, middleware, lifespan events
7. **Prometheus exporters** y dashboards en Grafana
8. **Tests de infraestructura** e integración

#### Preparado para Cloud/Edge:
9. **Scripts de exportación**:
   - Exportar modelos entrenados en formato ONNX (cuantizado)
   - Generar configuración agnóstica de cloud
   - Crear fixtures de datos para testing
10. **Terraform templates** (agnóstico, ejemplos GCP):
    - Compute resources
    - Networking
    - Databases (Cloud SQL)
    - Functions (Cloud Functions para tareas)
11. **docker-compose.prod.yml** para edge (Mini PC, Fase 13):
    - Imagen minimizada sin dev deps
    - Sin Prometheus server, ELK, MLflow server
    - Versión optimizada para 16GB RAM

### 15.3 Criterios de Aprobación

Antes de pasar a **FASE 1**, confirmar:

- [ ] ¿El alcance de mercado (España, Geoportal, gasolina/gasóleo) es correcto?
- [ ] ¿El stack propuesto (Python 3.12, FastAPI, PostgreSQL+TimescaleDB, Celery, BERT/Transformers, Ray, etc.) aprovecha bien los 125GB RAM?
- [ ] ¿Está clara la estrategia Dev (richly-resourced) → Cloud (GCP) → Edge (Mini PC)?
- [ ] ¿El docker-compose completo (10+ servicios con ELK, Prometheus, MLflow server) es aceptable para desarrollo?
- [ ] ¿Es aceptable tener feature flags para downgrade a edge en Fase 13?
- [ ] ¿La estructura de carpetas es clara y escalable?
- [ ] ¿Los diagramas reflejan correctamente el flujo de datos?
- [ ] ¿Hay preguntas o cambios antes de comenzar Fase 1?

**Nota importante**: Con este servidor (125GB RAM, 42GB VRAM), vamos a:
- ✅ Entrenar modelos BERT/Transformers completos (no lite)
- ✅ Usar GPU para XGBoost, LightGBM, PyTorch
- ✅ Procesar features en paralelo con Ray
- ✅ Tener stack completo de monitorización (Prometheus + Grafana + ELK)
- ✅ MLflow server profesional para tracking de experimentos
- ✅ Todo 100% funcional y production-grade aquí mismo

Al final (Fase 13), downgrade a Mini PC será cuestión de:
- Cargar modelos cuantizados en lugar de completos
- Desabilitar BERT/Transformers si no hay margen
- docker-compose simplificado
- Todo ya documentado y testeado.

---

**Documento preparado para revisión y aprobación. Esperando confirmación para proceder a FASE 1.**

**Autor**: Equipo Petro (Claude Code)  
**Fecha**: 2026-08-04  
**Estado**: 🔴 Pendiente de aprobación del usuario
