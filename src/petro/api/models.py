"""Models API - Endpoints para acceder a información de modelos entrenados."""

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from petro.ml.model_loader import models_registry

router = APIRouter(prefix="/api/v1/models", tags=["models"])


class ModelInfoResponse(BaseModel):
    """Información de un modelo."""

    name: str
    framework: str
    training_date: str
    metrics: Dict[str, float]
    input_features: List[str]
    output_feature: str
    training_samples: int
    available: bool


class ModelsResponse(BaseModel):
    """Respuesta con información de todos los modelos."""

    timestamp: str
    best_model: str
    models: Dict[str, ModelInfoResponse]
    total_models: int
    loaded_models: int


@router.get("/info", response_model=ModelsResponse)
async def get_models_info():
    """Obtener información de todos los modelos entrenados.

    Returns:
        Información de modelos cargados desde el último entrenamiento.

    Example:
        GET /api/v1/models/info
        Response:
        {
            "timestamp": "2026-08-14T03:00:00",
            "best_model": "xgboost",
            "models": {
                "xgboost": {
                    "name": "XGBoost Gradient Boosting",
                    "metrics": {"r2": 0.8645, "rmse": 0.0523},
                    ...
                }
            },
            "total_models": 3,
            "loaded_models": 3
        }
    """
    try:
        models_data = models_registry.get_models_info()

        # Contar modelos disponibles
        loaded_count = sum(
            1 for m in models_data.get("models", {}).values()
            if m.get("available", False)
        )

        return ModelsResponse(
            timestamp=models_data.get("timestamp") or datetime.utcnow().isoformat(),
            best_model=models_data.get("best_model", ""),
            models=models_data.get("models", {}),
            total_models=3,
            loaded_models=loaded_count
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener modelos: {str(e)}")


@router.get("/best")
async def get_best_model():
    """Obtener nombre del mejor modelo.

    Returns:
        Nombre del modelo con mejor rendimiento (mayor R²).

    Example:
        GET /api/v1/models/best
        Response:
        {
            "best_model": "xgboost",
            "r2": 0.8645,
            "rmse": 0.0523
        }
    """
    try:
        best_model_name = models_registry.get_best_model()

        if not best_model_name:
            raise HTTPException(status_code=404, detail="Ningún modelo disponible")

        best_model = models_registry.get_model(best_model_name)

        if not best_model:
            raise HTTPException(status_code=404, detail=f"Modelo {best_model_name} no encontrado")

        return {
            "best_model": best_model_name,
            "name": best_model.name,
            "metrics": best_model.metrics,
            "training_date": best_model.training_date,
            "input_features": len(best_model.input_features)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/{model_name}")
async def get_model(model_name: str):
    """Obtener información detallada de un modelo específico.

    Args:
        model_name: Nombre del modelo (xgboost, lightgbm, randomforest)

    Returns:
        Información detallada del modelo.

    Example:
        GET /api/v1/models/xgboost
        Response:
        {
            "name": "XGBoost Gradient Boosting",
            "metrics": {...},
            ...
        }
    """
    try:
        model = models_registry.get_model(model_name.lower())

        if not model:
            raise HTTPException(status_code=404, detail=f"Modelo {model_name} no encontrado")

        return {
            "name": model.name,
            "type": model.type,
            "framework": model.framework,
            "training_date": model.training_date,
            "metrics": model.metrics,
            "input_features": model.input_features,
            "output_feature": model.output_feature,
            "training_samples": model.training_samples,
            "hyperparameters": model.hyperparameters
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/refresh")
async def refresh_models():
    """Recargar modelos desde el archivo de cache.

    Útil para forzar una recarga después de un nuevo entrenamiento.

    Returns:
        Estado de la recarga.

    Example:
        POST /api/v1/models/refresh
        Response:
        {
            "status": "success",
            "message": "Modelos recargados",
            "models_loaded": 3
        }
    """
    try:
        models_registry.refresh_models()
        loaded_count = sum(1 for m in models_registry.get_all_models().values() if m is not None)

        return {
            "status": "success",
            "message": "Modelos recargados exitosamente",
            "models_loaded": loaded_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recargando modelos: {str(e)}")
