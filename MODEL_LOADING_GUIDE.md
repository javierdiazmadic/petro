# 🤖 Guía de Carga de Modelos Entrenados

Este documento explica cómo el sistema PETRO descarga y carga automáticamente los modelos entrenados desde GitHub cada noche.

---

## 🎯 ¿QUÉ ES?

Sistema automatizado que:
1. **Cada noche** (después del entrenamiento a las 3:00 AM UTC)
2. **Descarga** los nuevos modelos entrenados desde GitHub
3. **Carga** los modelos en la aplicación (API + frontend)
4. **Registra** metadata de los modelos para predicciones

---

## 📊 FLUJO COMPLETO

```
3:00 AM UTC - Se activa scheduler
    ↓
🤖 Etapa 1: Entrenamiento
├─ daily_training.py
└─ Genera nuevos modelos

    ↓
💾 Etapa 2: Exportación
├─ export_models.py (JSON)
├─ export_models_h5.py (H5 + metadata)
└─ Archivos listos para GitHub

    ↓
📝 Etapa 3: Reportes
└─ generate_report.py
    └─ Markdown con resultados

    ↓
📤 Etapa 4: GitHub
├─ git add -A
├─ git commit
└─ git push origin master

    ↓
📥 Etapa 5: CARGA DE MODELOS (NUEVA)
├─ download_and_load_models.py
├─ Descarga desde GitHub (git pull)
├─ Lee metadata (.h5 + JSON)
├─ Carga en memoria
└─ Genera cache para API

    ↓
✅ Modelos disponibles en API
    └─ GET /api/v1/models/info
    └─ GET /api/v1/models/best
    └─ GET /api/v1/models/xgboost (etc)
```

---

## 📁 ARCHIVOS CLAVE

### Exportación (Generados cada noche)

```
models_export/
├─ h5/
│  ├─ xgboost_model.h5
│  ├─ lightgbm_model.h5
│  └─ randomforest_model.h5
│
├─ json/
│  ├─ xgboost_metadata.json
│  ├─ lightgbm_metadata.json
│  ├─ randomforest_metadata.json
│
├─ models_api_cache.json  (← Cache para API)
└─ export_summary.json
```

### Scripts

```
scripts/
├─ daily_training.py           # Entrena modelos
├─ export_models.py            # Exporta JSON
├─ export_models_h5.py         # Exporta H5 + metadata (NUEVO)
├─ download_and_load_models.py # Descarga y carga (NUEVO)
└─ local_daily_scheduler.py    # Orquesta todo
```

### Backend (ML)

```
src/petro/ml/
├─ model_loader.py    # ModelsRegistry - gestor de modelos
└─ (más módulos ML)

src/petro/api/
├─ models.py          # API endpoints para modelos (NUEVO)
└─ (más endpoints)
```

---

## 🔄 CÓMO FUNCIONA LA CARGA

### 1. Exportación (.h5 + JSON)

```python
# scripts/export_models_h5.py

Crea:
├─ models_export/h5/xgboost_model.h5
├─ models_export/json/xgboost_metadata.json
└─ models_export/models_api_cache.json
```

**Contenido de metadata (JSON):**
```json
{
  "name": "XGBoost Gradient Boosting",
  "framework": "xgboost",
  "metrics": {
    "r2": 0.8645,
    "rmse": 0.0523,
    "mae": 0.0412,
    "accuracy": "95.2%"
  },
  "input_features": [
    "precio_gasolina_95_t1",
    "precio_gasoleoa_t1",
    "brent_price",
    "wti_price",
    "eurusd_rate"
  ],
  "training_date": "2026-08-14T03:00:00"
}
```

### 2. Descarga desde GitHub

```python
# scripts/download_and_load_models.py

1. git pull origin master
   ↓ Descarga archivos nuevos

2. Lee JSON metadata
   ↓ xgboost_metadata.json
   ↓ lightgbm_metadata.json
   ↓ randomforest_metadata.json

3. Carga en ModelsRegistry (singleton)
   ↓ Caché en memoria

4. Genera models_api_cache.json
   ↓ Listo para API
```

### 3. Acceso desde la API

```python
# src/petro/api/models.py

GET /api/v1/models/info
└─ Retorna info de todos los modelos

GET /api/v1/models/best
└─ Retorna mejor modelo (mayor R²)

GET /api/v1/models/xgboost
└─ Retorna info específica de XGBoost

POST /api/v1/models/refresh
└─ Recargar modelos (si es necesario)
```

---

## 🎯 ENDPOINTS DE LA API

### 1. Información general de modelos

```bash
curl http://localhost:8000/api/v1/models/info | jq .

Respuesta:
{
  "timestamp": "2026-08-14T03:00:00",
  "best_model": "xgboost",
  "models": {
    "xgboost": {
      "name": "XGBoost Gradient Boosting",
      "metrics": {"r2": 0.8645, "rmse": 0.0523},
      "available": true
    },
    "lightgbm": {...},
    "randomforest": {...}
  },
  "total_models": 3,
  "loaded_models": 3
}
```

### 2. Mejor modelo

```bash
curl http://localhost:8000/api/v1/models/best | jq .

Respuesta:
{
  "best_model": "xgboost",
  "name": "XGBoost Gradient Boosting",
  "metrics": {
    "r2": 0.8645,
    "rmse": 0.0523,
    "mae": 0.0412,
    "accuracy": "95.2%"
  },
  "training_date": "2026-08-14T03:00:00",
  "input_features": 7
}
```

### 3. Modelo específico

```bash
curl http://localhost:8000/api/v1/models/xgboost | jq .

Respuesta:
{
  "name": "XGBoost Gradient Boosting",
  "framework": "xgboost",
  "training_date": "2026-08-14T03:00:00",
  "metrics": {...},
  "input_features": ["precio_gasolina_95_t1", ...],
  "training_samples": 720
}
```

### 4. Recargar modelos (forzar update)

```bash
curl -X POST http://localhost:8000/api/v1/models/refresh | jq .

Respuesta:
{
  "status": "success",
  "message": "Modelos recargados exitosamente",
  "models_loaded": 3,
  "timestamp": "2026-08-14T15:30:45"
}
```

---

## 🚀 INICIO RÁPIDO

### Opción 1: Docker Compose (Automático)

```bash
docker compose up -d

# El scheduler de Celery Beat se encargará de:
# 1. Ejecutar entrenamiento a las 3:00 AM UTC
# 2. Exportar modelos
# 3. Cargar modelos
# 4. Todo automático
```

### Opción 2: Local - Ejecutar manualmente

```bash
# Entrenar
python scripts/daily_training.py

# Exportar (JSON + H5)
python scripts/export_models.py
python scripts/export_models_h5.py

# Descargar y cargar
python scripts/download_and_load_models.py

# Verificar en API
curl http://localhost:8000/api/v1/models/info
```

### Opción 3: Local - Con scheduler cron

```bash
# Editar crontab
crontab -e

# Agregar (ejecuta scheduler local a las 3:00 AM UTC)
0 3 * * * /path/to/venv/bin/python /path/to/petro/scripts/local_daily_scheduler.py

# El scheduler automáticamente:
# 1. Entrena
# 2. Exporta
# 3. Descarga y carga
# 4. Todo en el mismo proceso
```

---

## 📊 ESTRUCTURA DE DATOS

### ModelsRegistry (Singleton)

```python
class ModelsRegistry:
    # Caché en memoria
    _models_cache = {
        "xgboost": ModelMetadata(...),
        "lightgbm": ModelMetadata(...),
        "randomforest": ModelMetadata(...)
    }
    
    # Mejor modelo
    _best_model = "xgboost"
    
    # Última actualización
    _last_update = datetime(...)
    
    # Métodos
    get_model(name)          # Obtener uno
    get_all_models()         # Obtener todos
    get_best_model()         # El mejor
    get_models_info()        # Info para API
    refresh_models()         # Recargar
```

### ModelMetadata

```python
class ModelMetadata(BaseModel):
    name: str                    # "XGBoost Gradient Boosting"
    type: str                    # "regression"
    version: str                 # "2.0.0"
    training_date: str           # "2026-08-14T03:00:00"
    framework: str               # "xgboost"
    input_features: list[str]    # ["precio_gasolina_95_t1", ...]
    output_feature: str          # "gasolina_95_prediction"
    metrics: Dict[str, float]    # {"r2": 0.8645, "rmse": 0.0523}
    training_samples: int        # 720
    hyperparameters: Dict        # {...}
    file_format: str             # "joblib"
    file_path: str               # "models_export/h5/xgboost_model.h5"
```

---

## 🔍 MONITOREO

### Ver logs del scheduler

```bash
# En tiempo real
tail -f training_scheduler.log | grep "ETAPA\|✅\|❌"

# Buscar carga de modelos
grep "ETAPA 5\|download_and_load" training_scheduler.log
```

### Verificar que se descargó de GitHub

```bash
# Ver últimos cambios en git
git log --oneline | head -5

# Verificar que modelos existen localmente
ls -lh models_export/json/
ls -lh models_export/h5/

# Verificar cache de API
cat models_export/models_api_cache.json | jq .
```

### Verificar que API tiene modelos

```bash
# Conectarse a API
curl http://localhost:8000/api/v1/models/info | jq '.loaded_models'

# Debe retornar: 3 (xgboost, lightgbm, randomforest)
```

---

## 🐛 TROUBLESHOOTING

### Problema: Modelos no cargan

```bash
# 1. Verificar que el archivo existe
ls -la models_export/json/xgboost_metadata.json

# 2. Verificar contenido JSON
cat models_export/json/xgboost_metadata.json | jq .

# 3. Ver logs del script
grep "download_and_load" training_scheduler.log

# 4. Ejecutar manualmente para debug
python scripts/download_and_load_models.py
```

### Problema: Git pull falla

```bash
# Verificar credenciales
git config --global user.name
git config --global user.email

# Verificar conexión
git remote -v

# Intentar pull manual
git pull origin master
```

### Problema: API retorna 404 para /models

```bash
# 1. Verificar que endpoint está registrado
curl http://localhost:8000/openapi.json | jq '.paths | keys' | grep models

# 2. Recargar modelos manualmente
curl -X POST http://localhost:8000/api/v1/models/refresh

# 3. Reiniciar API
docker compose restart petro-api
```

---

## 📈 PRÓXIMO CICLO

Cada noche a las 3:00 AM UTC:

```
1. ENTRENA con 90 días de data → 3 modelos nuevos
2. EXPORTA como .h5 + JSON → GitHub ready
3. PUSHEA a GitHub → Available for download
4. DESCARGA latest → git pull
5. CARGA en memoria → ModelsRegistry
6. CACHE genera → models_api_cache.json
7. API obtiene → /api/v1/models/info retorna datos frescos
8. DASHBOARD usa → Predicciones con mejor modelo
```

---

## ✅ CHECKLIST DIARIO

Después de las 3:00 AM UTC, verifica:

- [ ] Nuevo commit en GitHub: `git log --oneline | head -1 | grep "🤖 Auto"`
- [ ] Archivos exportados: `ls models_export/h5/ | wc -l` (debe ser 3)
- [ ] Metadata generado: `cat models_export/models_api_cache.json | jq '.best_model'`
- [ ] API responde: `curl http://localhost:8000/api/v1/models/best | jq '.best_model'`
- [ ] Dashboard usa: Nuevos valores en predicciones y gráficos

Si todo ✅, sistema está funcionando correctamente.

---

*Última actualización: 2026-08-14*  
*Sistema de carga de modelos automático*
