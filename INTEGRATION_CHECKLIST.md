# ✅ Integración del Sistema de Carga de Modelos

Checklist de integración del sistema de carga de modelos en la aplicación PETRO.

---

## 📋 TAREAS DE INTEGRACIÓN

### 1. ✅ Backend - Registrar endpoint de modelos

**Archivo**: `src/petro/api/main.py` (o el archivo principal de FastAPI)

**Agregar esta línea** (después de otros imports de routers):

```python
from petro.api import models as models_router

# ...

# En la función setup de FastAPI
app.include_router(models_router.router)
```

**Resultado**: Los endpoints `/api/v1/models/*` estarán disponibles.

### 2. ✅ Backend - Inicializar ModelsRegistry al startup

**Archivo**: `src/petro/api/main.py`

**Agregar en evento startup**:

```python
from petro.ml.model_loader import models_registry

@app.on_event("startup")
async def startup_event():
    # ... otros inicios
    
    # Cargar modelos al startup
    print("🤖 Cargando modelos entrenados...")
    models_registry.load_models_from_cache()
    print("✅ Modelos cargados en memoria")
```

### 3. ✅ Frontend - Usar información de modelos

**Archivo**: `frontend/components/Dashboard.tsx`

**Agregar hook para obtener info de modelos**:

```typescript
import { predictionAPI } from '@/lib/api';

const Dashboard = () => {
  const [modelsInfo, setModelsInfo] = useState(null);

  useEffect(() => {
    const fetchModelsInfo = async () => {
      try {
        const response = await predictionAPI.getModelsInfo?.();
        setModelsInfo(response.data);
      } catch (error) {
        console.error("Error fetching models info:", error);
      }
    };

    fetchModelsInfo();
  }, []);

  return (
    <div>
      {/* Mostrar info de modelos */}
      {modelsInfo && (
        <div className="bg-blue-50 p-4 rounded">
          <p>Mejor modelo: {modelsInfo.best_model}</p>
          <p>Modelos cargados: {modelsInfo.loaded_models}/3</p>
        </div>
      )}
    </div>
  );
};
```

### 4. ✅ Frontend API - Agregar método de modelos

**Archivo**: `frontend/lib/api.ts`

**Agregar en predictionAPI**:

```typescript
getModelsInfo: () => api.get('/api/v1/models/info'),
getModelBest: () => api.get('/api/v1/models/best'),
getModel: (modelName: string) => api.get(`/api/v1/models/${modelName}`),
refreshModels: () => api.post('/api/v1/models/refresh'),
```

### 5. ✅ Docker - Volumen para modelos_export

**Archivo**: `docker-compose.yml`

**Asegurar que hay volumen compartido**:

```yaml
services:
  petro-api:
    volumes:
      - ./models_export:/home/app/models_export
      # ... otros volúmenes
```

**Resultado**: API puede acceder a archivos de modelos.

### 6. ✅ Docker - Volumen para reproducibilidad

**Archivo**: `docker-compose.yml`

**Agregar servicio de modelos** (opcional pero recomendado):

```yaml
services:
  models-loader:
    build:
      context: .
      dockerfile: Dockerfile
    command: python scripts/download_and_load_models.py
    volumes:
      - ./models_export:/home/app/models_export
      - ./scripts:/home/app/scripts
      - ./src:/home/app/src
    environment:
      - PYTHONUNBUFFERED=1
    depends_on:
      - petro-api
```

---

## 🧪 VERIFICACIÓN

### Paso 1: Verificar que endpoint está registrado

```bash
# Ver documentación de OpenAPI
curl http://localhost:8000/openapi.json | jq '.paths | keys' | grep models

# Debe incluir:
# "/api/v1/models/info"
# "/api/v1/models/best"
# "/api/v1/models/{model_name}"
```

### Paso 2: Verificar que modelos se cargaron

```bash
# Ver info de modelos
curl http://localhost:8000/api/v1/models/info | jq '.loaded_models'

# Debe retornar: 3 (si todo está cargado)
```

### Paso 3: Verificar en dashboard

```bash
# Abrir en navegador
http://localhost:3000

# Buscar info de modelos en consola del navegador
# console.log(await fetch('/api/v1/models/info').then(r => r.json()))
```

---

## 📝 NOTAS IMPORTANTES

### Para Docker Compose

Si usas Docker Compose, asegúrate de que:

1. **Volúmenes**: `models_export/` está montado en el contenedor
2. **Orden de startup**: API se inicia antes que se carguen modelos
3. **Permisos**: Archivos JSON son legibles

### Para Desarrollo Local

Si ejecutas localmente:

1. **Ruta**: `scripts/download_and_load_models.py` debe tener ruta correcta a `models_export/`
2. **Git**: Asegurar que git está configurado correctamente
3. **Permisos**: Archivos deben ser legibles/escribibles

### Para Producción

En producción:

1. **Caché**: Modelos se cachean en memoria (singleton)
2. **Refresh**: Usar `POST /api/v1/models/refresh` para actualizar si es necesario
3. **Logs**: Monitorear `training_scheduler.log` para ver si se cargaron correctamente

---

## 🔄 FLUJO DE DATOS

```
1. Scheduler ejecuta a las 3:00 AM UTC
   └─ local_daily_scheduler.py

2. Entrena modelos
   └─ daily_training.py

3. Exporta en .h5 + JSON
   └─ export_models_h5.py

4. Sube a GitHub
   └─ git push origin master

5. Descarga y carga modelos
   └─ download_and_load_models.py
      └─ ModelsRegistry.load_models_from_cache()
         └─ Lee JSON metadata
         └─ Carga en memoria

6. API sirve información
   └─ GET /api/v1/models/info
   └─ Retorna datos del registry en memoria

7. Frontend consume
   └─ predictionAPI.getModelsInfo()
   └─ Muestra información
```

---

## 📊 ARCHIVOS Y DEPENDENCIAS

```
scripts/
├─ local_daily_scheduler.py  ← Orquestador
├─ daily_training.py         ← Entrenamientos
├─ export_models_h5.py       ← Exporta .h5 + JSON
└─ download_and_load_models.py ← Descarga y carga (ETAPA 5)

src/petro/
├─ ml/
│  └─ model_loader.py        ← ModelsRegistry (singleton)
│
├─ api/
│  ├─ main.py                ← Registrar router
│  ├─ models.py              ← Endpoints (NUEVO)
│  └─ (otros endpoints)
│
└─ (resto de la app)

frontend/
├─ lib/
│  └─ api.ts                 ← Agregar métodos
│
├─ components/
│  └─ Dashboard.tsx          ← Usar información
│
└─ (resto del frontend)

models_export/
├─ h5/
│  ├─ xgboost_model.h5
│  ├─ lightgbm_model.h5
│  └─ randomforest_model.h5
│
├─ json/
│  ├─ xgboost_metadata.json
│  ├─ lightgbm_metadata.json
│  └─ randomforest_metadata.json
│
└─ models_api_cache.json      ← Lee aquí
```

---

## 🐛 TROUBLESHOOTING

### Error: ModuleNotFoundError: No module named 'petro.ml.model_loader'

**Solución**: Asegurar que la ruta está correcta en `PYTHONPATH`

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/petro/src"
```

### Error: File not found: models_export/json/xgboost_metadata.json

**Solución**: Ejecutar manualmente para generar archivos

```bash
python scripts/export_models_h5.py
python scripts/download_and_load_models.py
```

### Error: API returns 404 for /api/v1/models/info

**Solución**: Verificar que router está registrado en main.py

```python
# En src/petro/api/main.py
from petro.api import models as models_router
app.include_router(models_router.router)
```

### Error: 0 modelos cargados en API

**Solución**: Verificar logs

```bash
# Ver logs del scheduler
tail -f training_scheduler.log | grep "ETAPA 5\|download_and_load"

# Ver si archivos existen
ls -lh models_export/json/

# Ejecutar manualmente con debug
python scripts/download_and_load_models.py -v
```

---

## ✅ CHECKLIST FINAL

- [ ] Router de modelos importado en `main.py`
- [ ] Inicialización de ModelsRegistry en startup
- [ ] Volúmenes Docker configurados
- [ ] Archivos JSON exportados en `models_export/json/`
- [ ] API endpoint `/api/v1/models/info` retorna datos
- [ ] Frontend método `getModelsInfo()` funciona
- [ ] Dashboard muestra información de modelos
- [ ] Scheduler ejecuta `download_and_load_models.py` en Etapa 5
- [ ] Logs muestran "✅ Nuevos modelos cargados" cada noche

---

## 📞 SOPORTE

Si algo no funciona, revisar en este orden:

1. **Verificar logs**: `tail -f training_scheduler.log`
2. **Ejecutar manual**: `python scripts/download_and_load_models.py`
3. **Verificar archivos**: `ls -lh models_export/`
4. **API endpoint**: `curl http://localhost:8000/api/v1/models/info`
5. **Docker logs**: `docker compose logs petro-api | grep -i "model"`

---

*Última actualización: 2026-08-14*  
*Sistema de carga de modelos - Guía de integración*
