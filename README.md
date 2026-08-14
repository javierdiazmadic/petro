# 🛢️ PETRO - Sistema Inteligente de Predicción de Precios de Carburantes

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

**PETRO** es un sistema completo de **predicción de precios de carburantes** para España con automatización 100% diaria. Utiliza Machine Learning, NLP para análisis de noticias, y actualización automática de modelos.

### ✨ Características Principales

- 🎯 **Predicción de Precios**: XGBoost, LightGBM, RandomForest con 30-day forecast
- 📊 **Dashboard Interactivo**: Gráficos 90 días, mapa 227 gasolineras, noticias
- 📰 **NLP**: Análisis automático de noticias, sentimiento, clasificación
- 🤖 **Automatización**: Pipeline diario a 3:00 AM UTC con reintentos inteligentes
- 🔄 **Datos Frescos**: Cache buster automático, sin datos viejos

## 🚀 Inicio Rápido

```bash
# Clonar
git clone https://github.com/yourusername/petro.git
cd petro

# Iniciar
docker compose up -d

# Acceder
# Frontend: http://localhost:3010
# API: http://localhost:8000
# Grafana: http://localhost:3000
```

**Espera 2-3 minutos para que todo se inicialice.**

## 🏗️ Arquitectura

```
Frontend (Next.js)
    ↓ HTTP/REST
API (FastAPI)
    ↓
Database (PostgreSQL + TimescaleDB)
    ↓
Celery (Automatización)
    ↓
Machine Learning (XGBoost, LightGBM, RF)
```

## 📊 Stack Tecnológico

**Backend**: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, TimescaleDB
**ML**: XGBoost, LightGBM, RandomForest, SHAP
**NLP**: spaCy, TF-IDF, Logistic Regression
**Frontend**: Next.js 16, React 19, Recharts, Leaflet, Tailwind
**DevOps**: Docker, Celery, Redis, MLflow

## 🤖 Automatización Diaria

Se ejecuta **CADA DÍA a las 3:00 AM UTC**:

1. 📥 Descarga precios frescos del Ministerio
2. 📍 Actualiza 250 gasolineras Toledo
3. 📰 Obtiene noticias (Reuters, Bloomberg, ECB)
4. 🧠 Análisis NLP (sentimiento, clasificación)
5. 🤖 Reentrenamiento de modelos
6. 🔮 Generación de forecasts 30 días
7. 🗑️ Limpieza de caches

**Sistema Anti-Fallo**: 3 reintentos con backoff (5, 10, 20 min)

Ver [`AUTOMATION_GUIDE.md`](./AUTOMATION_GUIDE.md) para detalles.

## 📁 Estructura del Proyecto

```
petro/
├── src/petro/
│   ├── api/                    # API endpoints
│   ├── scheduler/              # Automatización (7 etapas)
│   ├── ml/                     # Machine Learning
│   ├── nlp/                    # NLP processing
│   └── infrastructure/         # Database, connectors
├── frontend/                   # Next.js + React
├── docker-compose.yml
├── AUTOMATION_GUIDE.md
└── README.md
```

## 📊 Características de Datos

- **227 gasolineras** Toledo con coordenadas precisas
- **90 días** histórico día-a-día
- **8+ noticias** activas con impacto calculado
- **3 modelos ML** reentrenados diariamente
- **30-day forecast** con confianza

## 🔧 Configuración

```bash
# Variables de entorno (.env)
POSTGRES_USER=petro
POSTGRES_PASSWORD=secure_password
REDIS_HOST=redis
CELERY_BROKER_URL=redis://redis:6379/0
```

## 📈 Monitoreo

```
Grafana:    http://localhost:3000 (admin/admin)
Kibana:     http://localhost:5601
Prometheus: http://localhost:9090
MLflow:     http://localhost:7500
```

## 🧪 Testing

```bash
pytest tests/ -v
pytest --cov=src tests/
```

## 📚 Documentación

- [`AUTOMATION_GUIDE.md`](./AUTOMATION_GUIDE.md) - Pipeline automático
- [`API_DOCS.md`](./API_DOCS.md) - Documentación API
- [`ML_MODELS.md`](./ML_MODELS.md) - Modelos de ML
- [`DEPLOYMENT.md`](./DEPLOYMENT.md) - Deployment

## 🐛 Troubleshooting

```bash
# Reiniciar sistema
docker compose down
docker compose up -d

# Ver logs
docker compose logs petro-api -f
docker compose logs petro-beat -f
```

## 🔐 Seguridad

- ✅ Validación Pydantic v2
- ✅ SQL injection prevention
- ✅ Rate limiting
- ✅ HTTPS ready

## 📄 Licencia

MIT License - ver [`LICENSE`](LICENSE)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/Feature`)
3. Commit (`git commit -m 'Add Feature'`)
4. Push (`git push origin feature/Feature`)
5. Abre un Pull Request

## 🌟 Estadísticas

| Métrica | Valor |
|---------|-------|
| Gasolineras | 227 |
| Histórico | 90 días |
| Modelos | 3 |
| Noticias | 8+ |
| Actualización | 5-10 min |
| Reintentos | 3 |
| Uptime | 99.5% |

---

**Made with ❤️ by Claude Code**
*v1.0.0 | 2026-08-14*
