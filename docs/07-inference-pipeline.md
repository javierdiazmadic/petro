# FASE 7: Pipeline de Inferencia

## Resumen

Inferencia de precios desde modelo entrenado con clasificación derivada de dirección (subida/bajada/estable) y cálculo de confianza. Objetivo: **< 100ms por predicción**.

## Componentes

### 1. ModelLoader (`src/petro/ml/inference/loader.py`)

Carga modelos entrenados desde MLflow.

**Métodos:**
- `load_production_model(experiment_name)` — Carga mejor modelo del experimento
- `load_model_by_run_id(run_id)` — Carga modelo específico por ID
- `load_scaler_from_file(filepath)` — Carga scaler desde pickle
- `get_model_info()` — Información del modelo cargado
- `is_loaded()` — Verifica si modelo está cargado

**Uso:**
```python
from petro.ml.inference import ModelLoader

loader = ModelLoader()
model, metadata = loader.load_production_model("petro-fuel-prediction")
print(f"RMSE: {metadata['rmse']:.6f}")
```

### 2. PricePredictor (`src/petro/ml/inference/predictor.py`)

Predice precios desde features.

**Métodos:**
- `predict(features)` — Predicción simple
- `predict_batch(features_list)` — Predicción múltiple
- `predict_with_bounds(features, uncertainty=0.05)` — Predicción con intervalo de confianza

**Ejemplo:**
```python
from petro.ml.inference import PricePredictor

predictor = PricePredictor(model, scaler=scaler)

# Predicción simple
price = predictor.predict(features)

# Predicción con bounds
result = predictor.predict_with_bounds(features, uncertainty=0.05)
# result = {
#   "prediction": 1.523,
#   "lower_bound": 1.447,  # 1.523 * (1 - 0.05)
#   "upper_bound": 1.599,  # 1.523 * (1 + 0.05)
# }
```

### 3. DirectionClassifier (`src/petro/ml/inference/classifier.py`)

Clasifica dirección (up/down/stable) desde predicción de precio.

**Enums:**
```python
class PriceDirection(Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
```

**Métodos:**
- `classify_single(predicted_price)` — Clasifica dirección
- `classify_with_confidence(predicted_price)` — Retorna probabilidades
- `classify_batch(predicted_prices)` — Clasifica múltiples precios
- `get_direction_string(direction)` — Texto legible con emoji

**Lógica de clasificación:**
- **UP**: Cambio > +0.5% (configurable)
- **DOWN**: Cambio < -0.5%
- **STABLE**: Cambio entre -0.5% y +0.5%

**Ejemplo:**
```python
from petro.ml.inference import DirectionClassifier, PriceDirection

classifier = DirectionClassifier(current_price=1.50, threshold_pct=0.5)

# Clasificación simple
direction = classifier.classify_single(1.515)
# direction = PriceDirection.UP

# Con confianza
confidence = classifier.classify_with_confidence(1.515)
# confidence = {
#   "up": 0.78,
#   "stable": 0.15,
#   "down": 0.07,
# }
```

### 4. InferencePipeline (`src/petro/ml/inference/pipeline.py`)

Orquestación completa: cargar → predecir → clasificar.

**Métodos:**
- `initialize(experiment_name, current_price)` — Inicializa con modelo y precio
- `predict_price(features, include_bounds=True)` — Predicción completa (precio + dirección + confianza)
- `predict_multiple(features_list, horizons)` — Predicción para múltiples horizontes
- `update_reference_price(new_price)` — Actualiza precio de referencia
- `is_ready()` — Verifica disponibilidad
- `get_model_info()` — Información del modelo

**Ejemplo completo:**
```python
from petro.ml.inference import InferencePipeline

pipeline = InferencePipeline()

# Inicializar
pipeline.initialize(
    experiment_name="petro-fuel-prediction",
    current_price=1.50
)

if not pipeline.is_ready():
    print("Pipeline not ready")
    exit()

# Predicción simple
result = pipeline.predict_price(features, include_bounds=True)
print(result)
# {
#   "timestamp": "2026-08-04T15:30:00.123456",
#   "prediction": 1.523,
#   "current_price": 1.50,
#   "change": 0.023,
#   "change_pct": 1.53,
#   "direction": "up",
#   "direction_label": "📈 Subida (esperado aumento de precio)",
#   "confidence": {"up": 0.78, "stable": 0.15, "down": 0.07},
#   "bounds": {"lower": 1.447, "upper": 1.599}
# }

# Multi-horizonte
results = pipeline.predict_multiple(
    [features_1d, features_3d, features_7d],
    horizons=["1d", "3d", "7d"]
)

for horizon, result in results.items():
    print(f"{horizon}: {result['prediction']:.4f} ({result['direction']})")
```

## Pipeline Completo

```
Features (PHASE 5)
      ↓
ModelLoader (MLflow)
      ↓
   model
      ↓
PricePredictor
      ↓
predicted_price
      ↓
DirectionClassifier
      ↓
   ┌─────┴─────┐
   ↓           ↓
direction   confidence
   ↓           ↓
InferencePipeline (resultado completo)
      ↓
API / Dashboard (PHASE 9)
```

## Estructura de Respuesta

```json
{
  "timestamp": "2026-08-04T15:30:00.123456",
  "prediction": 1.5230,
  "current_price": 1.5000,
  "change": 0.0230,
  "change_pct": 1.53,
  "direction": "up",
  "direction_label": "📈 Subida (esperado aumento de precio)",
  "confidence": {
    "up": 0.7850,
    "stable": 0.1500,
    "down": 0.0650
  },
  "bounds": {
    "lower": 1.4469,
    "upper": 1.5991
  }
}
```

## Performance Target

- **Latencia**: < 100ms
- **Throughput**: > 100 predicciones/segundo en servidor 16GB
- **Componentes**:
  - ModelLoader: < 10ms (cached)
  - PricePredictor: < 50ms
  - DirectionClassifier: < 10ms
  - Overhead: < 30ms

## Escalabilidad

### Servidor (125GB RAM, 42GB VRAM)
- Todas las predicciones < 50ms
- Model caching en memoria
- Thread-safe para concurrencia

### Edge (Mini PC, 16GB RAM)
- Modelo quantizado/lightweight
- Predicción < 100ms garantizada
- No requiere GPU

## Integración PHASE 8 (Celery)

El scheduler ejecutará:
```python
@app.task
def predict_prices():
    """Predecir precios cada 15 minutos."""
    pipeline = InferencePipeline()
    pipeline.initialize("petro-fuel-prediction", current_price=get_current_price())
    
    # Features de PHASE 5
    features = calculate_features(timestamp=now())
    
    # Predicción 1-7 días
    results = pipeline.predict_multiple(
        [features] * 7,  # Simplified: same features
        horizons=["1d", "3d", "7d"]
    )
    
    # Guardar predicción
    save_predictions(results)
```

## Integración PHASE 9 (API)

Endpoint `/api/v1/predict`:
```json
{
  "timestamp": "...",
  "predictions": {
    "gasolina_95": {...},
    "gasóleo_a": {...}
  }
}
```

## Tests

**14 pruebas unitarias** en `tests/unit/test_ml_inference.py`:
- PricePredictor (3 tests)
- DirectionClassifier (5 tests)
- InferencePipeline (3 tests)
- ModelLoader (3 tests)

Ejecutar con: `make test-inference`

## Mejoras Futuras (PHASE 11+)

- **SHAP**: Explicabilidad de predicciones
- **Ensemble**: Combinar predicciones de múltiples modelos
- **Uncertainty Quantification**: Estimación más sofisticada de confianza
- **Anomaly Detection**: Alertas si entrada fuera de distribución
- **Active Learning**: Feedback de usuarios para reentrenamiento

## Ejemplo de Uso

Ver `scripts/inference_example.py`:
```bash
python3 scripts/inference_example.py
```

## Próxima Fase: PHASE 8

PHASE 8 integrará este pipeline en Celery:
- Ejecutar cada 15 minutos
- Guardar predicciones en BD
- Comparar con actual para alertas

---

**Completado**: 2026-08-04  
**Status**: PHASE 7 READY FOR APPROVAL
