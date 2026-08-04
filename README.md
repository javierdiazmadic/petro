# PETRO — Sistema de Predicción de Precios de Gasolina y Gasóleo en España

![Status](https://img.shields.io/badge/status-development-yellow)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Descripción

PETRO es un sistema de predicción de precios de gasolina (95) y gasóleo (A) en España basado en:

- **Datos oficiales**: Geoportal de Precios de Carburantes (Ministerio)
- **Machine Learning**: XGBoost + LightGBM + Random Forest
- **Variables económicas**: Brent, WTI, EUR/USD, inventarios, producción OPEP
- **NLP**: Procesamiento de noticias con BERT/Transformers
- **Predicción**: Regresión (precio exacto) + clasificación derivada (probabilidad de subida/bajada)

## 🚀 Características

✅ **Stack moderno y escalable**
- FastAPI + PostgreSQL + TimescaleDB
- Celery para automatización (cada 15 min)
- Redis para caché y task queue
- MLflow para tracking de experimentos

✅ **Machine Learning profesional**
- Comparación de 3 modelos (XGBoost, LightGBM, RF)
- SHAP para explicabilidad
- Hyperparameter tuning con Optuna
- Cross-validation y feature importance

✅ **Monitorización y observabilidad**
- Prometheus + Grafana (métricas)
- ELK Stack (logs centralizados)
- Endpoints `/health` y `/metrics`

✅ **Desarrollo en servidor potente**
- 125 GB RAM + 42 GB VRAM
- GPU CUDA 12.1 para training
- Modelos BERT/Transformers completos
- Ray para procesamiento distribuido

✅ **Preparado para producción**
- Dockerizado completamente
- IaC agnóstica de cloud (GCP, Azure, etc.)
- Downgrade automático para Mini PC (Fase 13)
- Clean Architecture + SOLID principles

## 📚 Documentación

- [**Arquitectura**](docs/00-arquitectura.md) — Diseño completo del sistema
- [**Phase 1: Infraestructura**](PHASE_1_SUMMARY.md) — Docker, FastAPI, Celery
- [**Phase 2: Base de Datos**](PHASE_2_SUMMARY.md) — SQLAlchemy, TimescaleDB
- [**Phase 3: Ingestion**](PHASE_3_SUMMARY.md) — Conectores, reintentos
- [**Phase 4: NLP**](PHASE_4_SUMMARY.md) — Procesamiento de noticias
- [**Phase 5: Feature Engineering**](PHASE_5_SUMMARY.md) — Calculadoras de variables
- [**Phase 6: Model Training**](docs/06-model-training.md) — Entrenamiento ML ([Summary](PHASE_6_SUMMARY.md))
- [**Phase 7: Inference Pipeline**](docs/07-inference-pipeline.md) — Predicción < 100ms ([Summary](PHASE_7_SUMMARY.md))
- [**Phase 8: Celery Automation**](docs/08-automation-celery.md) — Pipeline cada 15 min ([Summary](PHASE_8_SUMMARY.md))
- [**Phase 9: REST API**](docs/09-rest-api.md) — Endpoints con FastAPI ([Summary](PHASE_9_SUMMARY.md))

## ⚡ Inicio rápido

### Con Docker (recomendado)

```bash
# Clonar y configurar
git clone <repo>
cd petro
cp .env.example .env

# Iniciar servicios
make docker-build
make docker-up

# Verificar salud
curl http://localhost:8000/api/v1/health

# Acceder a servicios
# API: http://localhost:8000
# Grafana: http://localhost:3000 (admin/admin)
# MLflow: http://localhost:5000
# Kibana: http://localhost:5601
```

### Desarrollo local

```bash
# Setup
python3.12 -m venv venv
source venv/bin/activate
make install-dev

# Iniciar DB y Redis en Docker
docker-compose up db redis -d

# Iniciar aplicación
make api-dev      # Terminal 1
make celery-worker  # Terminal 2
make celery-beat    # Terminal 3
```

## 📊 Estructura del proyecto

```
petro/
├── src/petro/
│   ├── api/           # FastAPI routers y schemas
│   ├── core/          # Config, logging, excepciones
│   ├── domain/        # Lógica de negocio pura
│   ├── infrastructure/# BD, caché, conectores
│   ├── ingestion/     # Descarga de datos
│   ├── nlp/           # Procesamiento de noticias
│   ├── features/      # Feature engineering
│   ├── ml/            # Training e inferencia
│   └── scheduler/     # Celery tasks y Beat
├── tests/             # Unit, integration, E2E
├── docs/              # Documentación
└── infra/             # Docker, Terraform
```

## 🔄 Fases de desarrollo (Roadmap)

| Fase | Descripción | Estado |
|------|-------------|--------|
| **0** | Arquitectura | ✅ Completada |
| **1** | Infraestructura | ✅ Completada |
| **2** | Base de datos | ✅ Completada |
| **3** | Recolección de datos | ✅ Completada |
| **4** | Procesamiento de noticias | ✅ Completada |
| **5** | Ingeniería de variables | ✅ Completada |
| **6** | Entrenamiento de modelos | ✅ Completada |
| **7** | Inferencia | ✅ Completada |
| **8** | Automatización (15 min) | ✅ Completada |
| **9** | API REST | ✅ Completada |
| **10** | Dashboard Web | ✅ Completada |
| **11** | Sistema de explicaciones (SHAP) | ✅ Completada |
| **12** | Reentrenamiento en cloud (GCP) | ✅ Completada |
| **13** | Optimización para Mini PC | ✅ **Completada** |

## 🛠 Stack Tecnológico

### Backend
- **Python 3.12** — Lenguaje principal
- **FastAPI** — Framework web async
- **Pydantic** — Validación de datos
- **SQLAlchemy 2.0** — ORM async
- **PostgreSQL 16 + TimescaleDB** — Base de datos series temporales

### Machine Learning
- **scikit-learn** — Preprocesamiento
- **XGBoost** — Modelos boosting
- **LightGBM** — Modelos boosting
- **SHAP** — Explicabilidad
- **Optuna** — Hyperparameter tuning
- **PyTorch + CUDA** — GPU training
- **Transformers** — BERT/NLP

### Infraestructura
- **Docker & Docker Compose** — Contenedores
- **Celery** — Task queue distribuida
- **Redis** — Caché y broker
- **MLflow** — Tracking de experimentos
- **Prometheus + Grafana** — Monitorización
- **ELK Stack** — Logs centralizados
- **Terraform** — IaC (cloud)

### Testing
- **pytest** — Framework testing
- **pytest-asyncio** — Tests async
- **pytest-cov** — Cobertura

## 🤝 Contribuciones

Este proyecto está en desarrollo activo. Las contribuciones siguen los principios de **Clean Architecture** y **SOLID**.

## 📄 Licencia

MIT License — Ver [LICENSE](LICENSE) para detalles.

## 📧 Contacto

**Autor**: Javier Diaz  
**Email**: javier.diaz@madic.com

---

**Última actualización**: 2026-08-04  
**Versión**: 1.0.0 (TODAS LAS 14 FASES COMPLETADAS)  
**Status**: ✅ PROYECTO FINALIZADO Y LISTO PARA PRODUCCIÓN
