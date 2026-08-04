# Setup Local Development

## Requisitos previos

- Docker & Docker Compose 2.0+
- Python 3.12+ (para desarrollo sin Docker)
- Git
- 125+ GB de RAM disponible (recomendado)
- GPU CUDA 12.1 (opcional, para training)

## Instalación rápida con Docker (RECOMENDADO)

### 1. Clonar repositorio

```bash
cd /path/to/petro
```

### 2. Crear archivo .env

```bash
cp .env.example .env
```

Revisar y ajustar variables según tu entorno.

### 3. Iniciar servicios

```bash
# Construir imágenes (primera vez)
make docker-build

# Iniciar todos los servicios
make docker-up

# Esperar a que todo esté healthy (~30s)
docker-compose ps
```

### 4. Verificar salud

```bash
# API
curl http://localhost:8000/api/v1/health

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health

# Elasticsearch
curl http://localhost:9200/

# MLflow
curl http://localhost:5000/
```

## Servicios disponibles

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **API FastAPI** | http://localhost:8000 | - |
| **Swagger UI** | http://localhost:8000/docs | - |
| **ReDoc** | http://localhost:8000/redoc | - |
| **MLflow** | http://localhost:5000 | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Kibana** | http://localhost:5601 | - |
| **PostgreSQL** | localhost:5432 | petro / petro_dev_password |
| **Redis** | localhost:6379 | - |

## Desarrollo local (sin Docker)

### 1. Crear virtual environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
make install-dev
```

### 3. Iniciar servicios principales (Docker)

```bash
# Solo servicios necesarios (DB, Redis, MLflow, etc.)
docker-compose up db redis mlflow elasticsearch kibana prometheus grafana -d
```

### 4. Ejecutar migraciones

```bash
make db-migrate
```

### 5. Iniciar aplicación

En terminales separadas:

```bash
# Terminal 1: API
make api-dev

# Terminal 2: Celery worker
make celery-worker

# Terminal 3: Celery beat
make celery-beat
```

## Ejecutar tests

```bash
# Todos los tests
make test

# Solo unit tests
make test-unit

# Solo integration tests
make test-integration

# Solo E2E tests
make test-e2e

# Con cobertura
pytest tests/ --cov=src/petro --cov-report=html
```

## Linting y formateo

```bash
# Verificar código
make lint

# Formatear código
make format
```

## Logs

```bash
# Ver logs de API
make docker-logs

# Ver logs de todos los servicios
make docker-logs-all

# Especifico de servicio
docker-compose logs -f worker
```

## Parar servicios

```bash
make docker-down
```

## Troubleshooting

### Puerto ya en uso

```bash
# Encontrar proceso en puerto
lsof -i :8000
kill -9 <PID>
```

### PostgreSQL no arranca

```bash
# Limpiar volumen
docker volume rm petro_postgres_data

# Reintentar
make docker-up
```

### Memoria insuficiente

```bash
# Reducir memoria de servicios en docker-compose.yml
# Reducir concurrency de Celery en Dockerfiles

# O ejecutar servicios seleccionados
docker-compose up db redis api -d
```

### Transformers/modelos no descargan

```bash
# Descargar modelos manualmente
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm

# En Docker:
docker-compose exec api python -m spacy download es_core_news_sm
```

## Estructua de carpetas del proyecto

```
petro/
├── src/petro/              # Código principal
├── tests/                  # Tests
├── docs/                   # Documentación
├── infra/                  # Configuración infraestructura
├── models/                 # Modelos ML
├── alembic/                # Migraciones BD
├── docker-compose.yml      # Orquestación contenedores
├── pyproject.toml          # Dependencias
├── Makefile                # Tareas útiles
└── .env.example            # Template variables
```

## Próximos pasos

1. Revisar `docs/00-arquitectura.md` para entender la arquitectura
2. Explorar endpoints en `http://localhost:8000/docs`
3. Empezar con **FASE 2 — Base de Datos**
