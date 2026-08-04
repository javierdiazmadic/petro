# FASE 6: Entrenamiento de Modelos

## Resumen

Entrenamiento de tres algoritmos de ML (XGBoost, LightGBM, RandomForest) con optimización de hiperparámetros vía Optuna, evaluación de métricas, tracking con MLflow y cálculo de feature importance.

## Componentes

### 1. ModelTrainer (`src/petro/ml/training/trainer.py`)

Clase principal para entrenamiento de modelos.

**Métodos:**
- `prepare_data(X_train, X_test)` — Normaliza features con StandardScaler
- `train_xgboost(X_train, y_train, X_test, y_test, params=None)` — Entrena XGBoost
- `train_lightgbm(X_train, y_train, X_test, y_test, params=None)` — Entrena LightGBM
- `train_random_forest(X_train, y_train, params=None)` — Entrena RandomForest
- `train_all(X_train, y_train, X_test, y_test)` — Entrena los 3 modelos simultáneamente

**Uso:**
```python
from petro.ml.training import ModelTrainer

trainer = ModelTrainer()
results = trainer.train_all(X_train, y_train, X_test, y_test)

# results = {
#   "xgboost": {"model": ..., "model_type": "xgboost", "params": {...}},
#   "lightgbm": {...},
#   "random_forest": {...}
# }
```

### 2. ModelEvaluator (`src/petro/ml/training/evaluator.py`)

Evalúa modelos y calcula métricas.

**Métodos:**
- `calculate_metrics(y_true, y_pred)` — Calcula MSE, MAE, RMSE, R², MAPE
- `evaluate_model(model, X_test, y_test)` — Evalúa un modelo individual
- `get_feature_importance(model, feature_names=None, top_n=20)` — Extrae importancia de features
- `compare_models(results)` — Compara métricas entre modelos

**Ejemplo:**
```python
from petro.ml.training import ModelEvaluator

evaluator = ModelEvaluator()
eval_result = evaluator.evaluate_model(model, X_test, y_test)
print(eval_result["metrics"])  # RMSE, MAE, R², etc.

# Comparar todos los modelos
comparison = evaluator.compare_models({
    "xgboost": eval_result_xgb,
    "lightgbm": eval_result_lgb,
    "random_forest": eval_result_rf
})
print(f"Best model: {comparison['best_model']}")
```

### 3. HyperparameterTuner (`src/petro/ml/training/hyperparameter_tuner.py`)

Optimiza hiperparámetros con Optuna (TPE sampler).

**Métodos:**
- `optimize_xgboost(X_train, y_train, cv=5)` — Optimiza XGBoost
- `optimize_lightgbm(X_train, y_train, cv=5)` — Optimiza LightGBM
- `optimize_random_forest(X_train, y_train, cv=5)` — Optimiza RandomForest

**Usa cross-validation para evaluar cada trial, 5 folds por defecto.**

**Ejemplo:**
```python
from petro.ml.training import HyperparameterTuner

tuner = HyperparameterTuner(n_trials=50, n_jobs=-1)
result = tuner.optimize_xgboost(X_train, y_train, cv=5)

best_params = result["best_params"]
print(f"Best R²: {result['best_score']:.4f}")
```

### 4. ExperimentTracker (`src/petro/ml/training/experiment.py`)

Tracking con MLflow para reproducibilidad y versionado de modelos.

**Métodos:**
- `start_run(run_name, tags=None)` — Inicia un experimento
- `log_params(params)` — Registra hiperparámetros
- `log_metrics(metrics, step=0)` — Registra métricas
- `log_model(model, model_name, model_type, metrics=None)` — Registra modelo
- `log_feature_importance(feature_names, importances, model_name)` — Registra importancia
- `end_run(status='FINISHED')` — Finaliza el experimento
- `register_model(model_uri, model_name, description, tags)` — Registra en MLflow Model Registry
- `get_best_run(experiment_name, metric='rmse', mode='min')` — Recupera mejor run
- `compare_models(experiment_name)` — Compara todos los runs de un experimento

**Ejemplo completo:**
```python
from petro.ml.training import ExperimentTracker, ModelTrainer, ModelEvaluator

tracker = ExperimentTracker(experiment_name="petro-fuel-prediction")
tracker.start_run("baseline-xgb", tags={"phase": "phase6", "type": "baseline"})

trainer = ModelTrainer()
results = trainer.train_all(X_train, y_train, X_test, y_test)

xgb_result = results["xgboost"]
tracker.log_params(xgb_result["params"])

evaluator = ModelEvaluator()
eval_result = evaluator.evaluate_model(xgb_result["model"], X_test, y_test)
tracker.log_metrics(eval_result["metrics"])

tracker.log_model(xgb_result["model"], "xgboost-v1", "xgboost")
feature_imp = evaluator.get_feature_importance(xgb_result["model"], feature_names)
tracker.log_feature_importance(feature_imp["features"], feature_imp["importances"])

tracker.end_run()
```

## Pipeline Completo (Recomendado)

```python
from petro.ml.training import (
    ModelTrainer,
    ModelEvaluator,
    HyperparameterTuner,
    ExperimentTracker,
)

# 1. Preparar datos (de FeatureEngineeringCalculator o similar)
# X_train, y_train, X_test, y_test = ...

# 2. Iniciar experiment tracking
tracker = ExperimentTracker("petro-fuel-prediction")

# 3. Para cada modelo a entrenar:
for model_type in ["xgboost", "lightgbm", "random_forest"]:
    tracker.start_run(f"{model_type}-optimized", tags={"type": model_type})

    # Optimizar hiperparámetros
    tuner = HyperparameterTuner(n_trials=50)
    if model_type == "xgboost":
        tuner_result = tuner.optimize_xgboost(X_train, y_train)
    elif model_type == "lightgbm":
        tuner_result = tuner.optimize_lightgbm(X_train, y_train)
    else:
        tuner_result = tuner.optimize_random_forest(X_train, y_train)

    best_params = tuner_result["best_params"]
    tracker.log_params(best_params)

    # Entrenar con mejores hiperparámetros
    trainer = ModelTrainer()
    if model_type == "xgboost":
        train_result = trainer.train_xgboost(X_train, y_train, X_test, y_test, best_params)
    # ... etc

    # Evaluar
    evaluator = ModelEvaluator()
    eval_result = evaluator.evaluate_model(train_result["model"], X_test, y_test)
    tracker.log_metrics(eval_result["metrics"])

    # Feature importance
    feat_imp = evaluator.get_feature_importance(train_result["model"], feature_names)
    tracker.log_feature_importance(feat_imp["features"], feat_imp["importances"])

    # Registrar modelo
    tracker.log_model(train_result["model"], f"{model_type}-v1", model_type)

    tracker.end_run()

# 4. Comparar todos los modelos
best_run = ExperimentTracker.get_best_run("petro-fuel-prediction")
print(f"Best model metrics: {best_run['metrics']}")

comparison = ExperimentTracker.compare_models("petro-fuel-prediction")
print(comparison["runs"])
```

## Flujo de Datos

```
FeatureEngineeringCalculator (FASE 5)
          ↓
      X_train, y_train, X_test, y_test
          ↓
   ┌──────┴──────┐
   │ HyperparameterTuner (Optuna)
   │  - 50 trials per model
   │  - Cross-validation (5 folds)
   └──────┬──────┘
          ↓
    best_params
          ↓
   ┌──────┴──────┐
   │ ModelTrainer
   │  - XGBoost
   │  - LightGBM
   │  - RandomForest
   └──────┬──────┘
          ↓
      models
          ↓
   ┌──────┴──────┐
   │ ModelEvaluator
   │  - MSE, MAE, RMSE, R², MAPE
   │  - Feature Importance
   └──────┬──────┘
          ↓
    metrics, importances
          ↓
   ┌──────┴──────┐
   │ ExperimentTracker (MLflow)
   │  - Log params, metrics, models
   │  - Model Registry
   └──────┬──────┘
          ↓
   MLflow artifacts
          ↓
    FASE 7: Inference Pipeline
```

## Métricas Calculadas

- **MSE** (Mean Squared Error) — Error cuadrático medio
- **MAE** (Mean Absolute Error) — Error absoluto medio
- **RMSE** (Root Mean Squared Error) — Raíz del MSE
- **R²** (Coefficient of Determination) — Proporción de varianza explicada (-1 a 1)
- **MAPE** (Mean Absolute Percentage Error) — Error porcentual medio

## Hiperparámetros Optimizados

### XGBoost
- `max_depth`: 3-15
- `learning_rate`: 0.001-0.3 (log scale)
- `subsample`: 0.5-1.0
- `colsample_bytree`: 0.5-1.0
- `n_estimators`: 50-300

### LightGBM
- `max_depth`: 3-15
- `num_leaves`: 20-100
- `learning_rate`: 0.001-0.3 (log scale)
- `feature_fraction`: 0.5-1.0
- `bagging_fraction`: 0.5-1.0

### RandomForest
- `n_estimators`: 50-500
- `max_depth`: 5-30
- `min_samples_split`: 2-20
- `min_samples_leaf`: 1-10

## Tests

Todos los componentes tiene pruebas unitarias en `tests/unit/test_ml_training.py`:
- Preparación de datos
- Entrenamiento de cada modelo
- Evaluación y métricas
- Optimización de hiperparámetros
- Tracking con MLflow
- Comparación de modelos
- Feature importance

Ejecutar con: `make test-ml`

## Integración con Celery (FASE 8)

La tarea `train_models` en `scheduler/tasks.py` integrará este pipeline:

```python
@app.task(bind=True, max_retries=3)
def train_models(self):
    """Reentrenar modelos con nuevos datos."""
    try:
        # 1. Obtener datos más recientes
        # 2. Calcular features
        # 3. Entrenar (con HyperparameterTuner si es día de reentrenamiento)
        # 4. Evaluar
        # 5. Registrar en MLflow
        # 6. Si mejora métrica, actualizar modelo de producción
        pass
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

## Próximas Fases

- **FASE 7**: Inference Pipeline — Cargar modelo, predicción < 100ms, clasificación derivada
- **FASE 8**: Automatización Celery — Ejecutar pipeline cada 15 minutos
- **FASE 9**: API REST — Endpoint /predict con resultados y explicabilidad
- **FASE 11**: Explainability — SHAP para interpretabilidad
