# 🚗 PETRO - Sistema de Predicción de Precios de Combustibles en España

**Predicción inteligente de precios de gasolina y gasóleo en tiempo real usando IA avanzada con datos oficiales del Ministerio de Energía**

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://www.docker.com/)
[![ML](https://img.shields.io/badge/ML-XGBoost%2BLightGBM-orange)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📋 Tabla de Contenidos

- [✨ Características Principales](#-características-principales)
- [💻 Requisitos del Sistema](#-requisitos-del-sistema)
- [🚀 Instalación Rápida](#-instalación-rápida-5-minutos)
- [📱 Acceso a la Aplicación](#-acceso-a-la-aplicación)
- [⚙️ Configuración Detallada](#️-configuración-detallada)
- [▶️ Cómo Ejecutar](#️-cómo-ejecutar)
- [🤖 Automatización (Cada 2 Días)](#-automatización-cada-2-días)
- [📡 API REST](#-api-rest)
- [🏗️ Arquitectura](#️-arquitectura)
- [🛠️ Solución de Problemas](#️-solución-de-problemas)
- [📚 Documentación Adicional](#-documentación-adicional)

---

## ✨ Características Principales

### 🔮 Predicción Inteligente
- **30 días de pronóstico** con intervalos de confianza 80% y 95%
- **Modelos de IA**: XGBoost, LightGBM, RandomForest
- **SHAP**: Explicabilidad completa de predicciones
- **Acuralidad**: MAE 0.41€ (Gasolina), MAPE 0.28%

### 📊 Datos Reales en Tiempo Real
- **246 gasolineras Toledo** desde Ministerio de Energía oficial
- **79 estaciones Repsol** identificadas automáticamente
- **Actualización automática** cada 15 minutos
- **Análisis histórico** de 90+ días

### 🤖 Aprendizaje Automático 24/7
- **Entrenamiento automático** cada 2 días (Lunes, Miércoles, Viernes 3:00 AM UTC)
- **NLP avanzado**: Análisis de noticias con spaCy
- **Ingeniería de características** automática
- **MLflow tracking**: Toda la experimentación registrada
- **Optimización continua**: Hyperparámetros adaptados

### 📱 Dashboard Profesional
- **Next.js 16 + React 19** con Tailwind CSS
- **Filtros dinámicos**: Todas las estaciones vs Solo Repsol
- **Visualizaciones interactivas**: Recharts con zoom
- **Búsqueda avanzada**: Por precio o distancia
- **Comparativa visual**: Precios predichos vs reales

### ⚡ Arquitectura Enterprise-Ready
- **Clean Architecture + Hexagonal Pattern**
- **PostgreSQL 16 + TimescaleDB** para series temporales
- **Redis** para caché y task queue
- **Celery + Celery Beat** para orquestación
- **FastAPI** con validación Pydantic v2
- **Docker Compose V2** completamente containerizado

---

## 💻 Requisitos del Sistema

### Hardware Mínimo Recomendado
```
CPU:    4 núcleos (8+ recomendados)
RAM:    16 GB (32 GB+ recomendados)
Disco:  50 GB SSD
GPU:    CUDA 12.1 (opcional, acelera ML)
Red:    2 Mbps (para descargas)
```

### Software Requerido
```
Docker:         20.10+
Docker Compose: 2.0+
Git:            2.30+
Puertos libres: 8000, 3010, 5433, 6379, 3000, 7500, 5601, 9200
```

---

## 🚀 Instalación Rápida (5 Minutos)

### Paso 1: Clonar repositorio
```bash
git clone https://github.com/javierdiazmadic/petro.git
cd petro
```

### Paso 2: Configuración
```bash
# Copiar archivo de entorno
cp .env.example .env

# Editar .env con tu IP de red (importante para acceso desde red)
# NEXT_PUBLIC_API_URL=http://192.168.30.199:8000  ← Tu IP aquí
nano .env
```

### Paso 3: Iniciar servicios
```bash
# Detener servicios previos (si existen)
docker compose down

# Build completo e iniciar
docker compose up -d --build

# Esperar 30 segundos a que PostgreSQL esté listo
sleep 30

# Verificar todos los servicios están corriendo
docker compose ps
```

### Paso 4: Verificar funcionamiento
```bash
# Verificar API
curl -s http://192.168.30.199:8000/api/v1/health | jq .

# Verificar Frontend
curl -s http://192.168.30.199:3010 | head -20

# Verificar BD
docker compose exec db psql -U petro -d petro_dev -c "SELECT COUNT(*) FROM price;"
```

✅ **¡Listo!** Ve a http://192.168.30.199:3010

---

## 📱 Acceso a la Aplicación

### Dashboard Principal
```
http://192.168.30.199:3010
```
**Funcionalidades:**
- 🔮 Predicción 30 días con gráfico interactivo
- ⛽ 246 gasolineras de Toledo
- 🎯 Recomendación inteligente de compra
- 📊 Análisis histórico 90 días
- 📍 Gasolineras más baratas o más cercanas
- 🏢 Filtro Repsol vs Todas las estaciones

### API REST Documentation
```
http://192.168.30.199:8000/docs
```

### Herramientas Administrativas

| Herramienta | URL | Usuario | Contraseña |
|------------|-----|---------|-----------|
| **MLflow** | http://192.168.30.199:7500 | - | - |
| **Grafana** | http://192.168.30.199:3000 | admin | admin |
| **Kibana** | http://192.168.30.199:5601 | - | - |
| **pgAdmin** | http://192.168.30.199:5050 | admin@admin.com | admin |

---

## ⚙️ Configuración Detallada

### Variables de Entorno (.env)

```env
# ===== NETWORK =====
# IP DE RED DONDE ACCEDERÁS DESDE NAVEGADOR
NEXT_PUBLIC_API_URL=http://192.168.30.199:8000

# ===== DATABASE =====
DATABASE__URL=postgresql+asyncpg://petro:petro_dev_password@db:5432/petro_dev

# ===== REDIS =====
REDIS__URL=redis://redis:6379

# ===== API =====
API_HOST=0.0.0.0
API_PORT=8000

# ===== CELERY =====
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/1

# ===== MLFLOW =====
MLFLOW__TRACKING_URI=http://mlflow:5000
MLFLOW__EXPERIMENT_NAME=petro-fuel-prediction
```

### Estructura de Carpetas

```
petro/
├── src/petro/
│   ├── api/                    # FastAPI routers (endpoints)
│   ├── core/                   # Config, logging
│   ├── domain/                 # Lógica pura
│   ├── infrastructure/
│   │   ├── db/                 # Modelos SQLAlchemy
│   │   ├── connectors/         # APIs externas
│   │   └── cache/              # Redis client
│   ├── ml/                     # Training e inferencia
│   ├── nlp/                    # Procesamiento de noticias
│   ├── scheduler/              # Celery tasks
│   └── features/               # Feature engineering
├── frontend/                   # Next.js dashboard
├── docker-compose.yml          # Orquestación (TODO: arreglado)
├── pyproject.toml              # Dependencias Python
└── infra/docker/               # Dockerfiles
```

---

## ▶️ Cómo Ejecutar

### Comando Básico (Recomendado)
```bash
# Iniciar todo con build
docker compose up -d --build

# Monitorizar logs
docker compose logs -f

# Parar todo
docker compose down
```

### Comandos por Servicio

```bash
# Solo API
docker compose restart api
docker compose logs -f api

# Solo Frontend
docker compose restart frontend
docker compose logs -f frontend

# Solo BD
docker compose restart db
docker compose logs -f db

# Solo scheduler (Celery)
docker compose restart beat worker
docker compose logs -f beat worker
```

### Ver Logs Detallados
```bash
# Últimas 50 líneas
docker compose logs --tail=50

# Seguir logs en tiempo real
docker compose logs -f

# Logs de un servicio específico
docker compose logs -f api | grep "ERROR"
```

### Reset Completo (Perder Datos)
```bash
# ⚠️ CUIDADO: Esto borra la BD
docker compose down -v

# Iniciar de cero
docker compose up -d --build

# Esperar 30s a que BD esté lista
sleep 30

# Verificar
curl http://192.168.30.199:8000/api/v1/health
```

---

## 🤖 Automatización (Cada 2 Días)

### Tareas Programadas

**Cada 15 minutos (24/7):**
```
✓ Descargar datos del Ministerio
✓ Procesar noticias con NLP
✓ Calcular características
✓ Generar predicciones
✓ Guardar en BD
```

**Cada 2 días (Lunes, Miércoles, Viernes a las 3:00 AM UTC):**
```
ETAPA 1: 📥 Descargar datos frescos
ETAPA 2: 📰 Procesar noticias con NLP
ETAPA 3: 🧮 Calcular características
ETAPA 4: 📊 Análisis de datos
ETAPA 5: 🤖 Reentrenar modelos (XGBoost, LightGBM, RF)
ETAPA 6: 📝 Logging de resultados
```

### Monitorizar Automatización

```bash
# Ver tareas activas
docker compose exec worker celery -A petro.scheduler.app inspect active

# Ver próximas tareas
docker compose exec beat celery -A petro.scheduler.app inspect scheduled

# Ver estadísticas
docker compose exec worker celery -A petro.scheduler.app inspect stats

# Forzar ejecución manual
docker compose exec worker celery -A petro.scheduler.app call petro.scheduler.tasks.fetch_all_data
```

---

## 📡 API REST

### Endpoints Principales

```bash
# Predicción 30 días
curl http://192.168.30.199:8000/api/v1/predictions/forecast

# Recomendación inteligente
curl http://192.168.30.199:8000/api/v1/predictions/recommendation

# Todas las gasolineras (246)
curl http://192.168.30.199:8000/api/v1/toledo/all-stations

# Solo Repsol (79)
curl http://192.168.30.199:8000/api/v1/toledo/repsol

# Más baratas
curl http://192.168.30.199:8000/api/v1/toledo/cheapest?fuel_type=gasoleoa

# Health check
curl http://192.168.30.199:8000/api/v1/health
```

### Ejemplo en Python
```python
import requests

# Obtener recomendación
response = requests.get('http://192.168.30.199:8000/api/v1/predictions/recommendation')
rec = response.json()

print(f"Recomendación: {rec['recommendation']}")
print(f"Ahorro: €{rec['expected_savings_min']}-€{rec['expected_savings_max']}")
print(f"Confianza: {rec['confidence']*100:.0f}%")
```

---

## 🏗️ Arquitectura

### Stack Tecnológico

**Backend:**
- Python 3.12 + FastAPI + Pydantic v2
- PostgreSQL 16 + TimescaleDB
- SQLAlchemy 2.0 async ORM
- Redis para caché

**Machine Learning:**
- XGBoost, LightGBM, RandomForest
- SHAP para explicabilidad
- Optuna para hyperparameter tuning
- PyTorch + CUDA 12.1

**Infraestructura:**
- Celery + Celery Beat
- MLflow para tracking
- Docker + Docker Compose
- Prometheus + Grafana

**Frontend:**
- Next.js 16 + React 19
- Tailwind CSS
- Recharts para visualizaciones

### Flujo de Datos

```
Ministerio API → Descargar → Redis Cache → BD PostgreSQL
                                ↓
                            Análisis NLP
                                ↓
                        Feature Engineering
                                ↓
                        Modelos ML (Entrenamiento)
                                ↓
                            Predicción
                                ↓
                        Dashboard Frontend ← API REST
```

---

## 🛠️ Solución de Problemas

### Problema: "Connection refused" en puerto 8000

```bash
# Ver si API está corriendo
docker compose ps | grep api

# Si no está, ver logs
docker compose logs api | tail -30

# Reiniciar
docker compose restart api

# Esperar 10s
sleep 10

# Verificar
curl http://192.168.30.199:8000/api/v1/health
```

### Problema: Frontend muestra "undefined"

```bash
# Limpiar caché
rm -rf frontend/.next

# Rebuild
docker compose restart frontend

# Esperar 10s
sleep 10

# Verificar
curl http://192.168.30.199:3010
```

### Problema: BD no responde

```bash
# Verificar PostgreSQL
docker compose exec db pg_isready -U petro

# Ver logs
docker compose logs db | tail -20

# Reiniciar
docker compose restart db

# Esperar 30s
sleep 30

# Verificar
docker compose exec db psql -U petro -d petro_dev -c "SELECT 1;"
```

### Problema: Celery tasks no se ejecutan

```bash
# Verificar Redis
docker compose exec redis redis-cli ping

# Ver tareas activas
docker compose exec worker celery -A petro.scheduler.app inspect active

# Reiniciar scheduler
docker compose restart beat worker

# Ver logs
docker compose logs beat | tail -30
```

---

## 📚 Documentación Adicional

- **[ARQUITECTURA.md](docs/ARQUITECTURA.md)** - Diseño técnico detallado
- **[API_ENDPOINTS.md](docs/API_ENDPOINTS.md)** - Lista completa de endpoints
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Despliegue en producción
- **[MAINTENANCE.md](docs/MAINTENANCE.md)** - Mantenimiento y monitoreo

---

## 🔐 Seguridad para Producción

```env
# .env - Cambiar contraseñas por defecto
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD
REDIS_PASSWORD=YOUR_STRONG_PASSWORD

# Activar HTTPS
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem

# API Token
API_SECRET_KEY=your_secret_key_here
```

---

## 🎯 Verificación Rápida Post-Instalación

```bash
# 1. Verificar todos los servicios
docker compose ps
✓ Todos deben estar "Up"

# 2. Verificar API
curl -s http://192.168.30.199:8000/api/v1/health | jq .status
✓ Debe mostrar "healthy"

# 3. Verificar BD
docker compose exec db psql -U petro -d petro_dev -c "SELECT COUNT(*) FROM price;"
✓ Debe mostrar número de registros

# 4. Verificar Frontend
curl -s http://192.168.30.199:3010 | grep "Petro"
✓ Debe retornar HTML con "Petro"

# 5. Acceder a Dashboard
Abre navegador: http://192.168.30.199:3010
✓ Debes ver el dashboard con datos
```

---

## 📊 Commits Principales

```
7e6b000 - Add automated bi-daily full pipeline execution
bd12eb9 - Enhance BacktestResults visualization with better zoom
0526ec8 - Change RecommendationCard text color to black
b75cbf9 - Redesign RecommendationCard with better colors
b0944b9 - Fix Toledo endpoints and improve UI components
```

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles completos

---

## 👥 Contacto y Soporte

**Autor:** Javier Diaz  
**Email:** javier.diaz@madic.com  
**Repositorio:** https://github.com/javierdiazmadic/petro  
**Issues:** https://github.com/javierdiazmadic/petro/issues

---

**Última actualización:** 4 de Agosto de 2026  
**Versión:** 1.0.0  
**Status:** ✅ PRODUCCIÓN READY  
**Todas las fases completadas**
