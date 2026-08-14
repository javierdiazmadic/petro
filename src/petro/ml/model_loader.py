"""Model Loader - Carga y maneja modelos entrenados desde GitHub."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    """Metadata de un modelo entrenado."""

    name: str
    type: str
    version: str
    training_date: str
    framework: str
    input_features: list[str]
    output_feature: str
    metrics: Dict[str, float]
    training_samples: int
    hyperparameters: Dict
    file_format: str
    file_path: str
    size_mb: float = Field(default=0.0)


class ModelsRegistry:
    """Registro y gestor de modelos entrenados."""

    _instance = None
    _models_cache: Dict[str, Optional[ModelMetadata]] = {}
    _best_model: Optional[str] = None
    _last_update: Optional[datetime] = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ModelsRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ModelsRegistry":
        """Obtener instancia singleton."""
        return cls()

    def load_models_from_cache(self, cache_path: Optional[Path] = None) -> Dict[str, Optional[ModelMetadata]]:
        """Cargar modelos desde el archivo de cache generado por download_and_load_models.py."""
        if cache_path is None:
            cache_path = Path("/home/administrador/Desktop/petro/models_export/models_api_cache.json")

        try:
            if not cache_path.exists():
                print(f"⚠️ Cache de modelos no encontrado: {cache_path}")
                return self._models_cache

            with open(cache_path, 'r') as f:
                cache_data = json.load(f)

            self._last_update = datetime.fromisoformat(cache_data.get("timestamp", datetime.utcnow().isoformat()))
            self._best_model = cache_data.get("best_model")

            # Cargar cada modelo
            for model_name, model_data in cache_data.get("models", {}).items():
                try:
                    metadata = ModelMetadata(
                        name=model_data["name"],
                        type="regression",
                        version="2.0.0",
                        training_date=model_data["training_date"],
                        framework=model_name,
                        input_features=model_data["input_features"],
                        output_feature=model_data["output_feature"],
                        metrics=model_data["metrics"],
                        training_samples=720,
                        hyperparameters={},
                        file_format="joblib",
                        file_path=f"models_export/h5/{model_name}_model.h5",
                        size_mb=0.0
                    )
                    self._models_cache[model_name] = metadata
                except Exception as e:
                    print(f"⚠️ Error cargando modelo {model_name}: {e}")
                    self._models_cache[model_name] = None

            return self._models_cache

        except Exception as e:
            print(f"❌ Error cargando cache: {e}")
            return self._models_cache

    def get_model(self, model_name: str) -> Optional[ModelMetadata]:
        """Obtener metadata de un modelo específico."""
        return self._models_cache.get(model_name)

    def get_all_models(self) -> Dict[str, Optional[ModelMetadata]]:
        """Obtener todos los modelos cargados."""
        return self._models_cache

    def get_best_model(self) -> Optional[str]:
        """Obtener nombre del mejor modelo."""
        return self._best_model

    def get_models_info(self) -> Dict:
        """Obtener información de todos los modelos para la API."""
        models_info = {
            "timestamp": self._last_update.isoformat() if self._last_update else None,
            "best_model": self._best_model,
            "models": {}
        }

        for model_name, metadata in self._models_cache.items():
            if metadata:
                models_info["models"][model_name] = {
                    "name": metadata.name,
                    "framework": metadata.framework,
                    "training_date": metadata.training_date,
                    "metrics": metadata.metrics,
                    "input_features": metadata.input_features,
                    "output_feature": metadata.output_feature,
                    "training_samples": metadata.training_samples,
                    "available": True
                }
            else:
                models_info["models"][model_name] = {
                    "available": False,
                    "error": "No cargado"
                }

        return models_info

    def refresh_models(self, cache_path: Optional[Path] = None) -> Dict[str, Optional[ModelMetadata]]:
        """Recargar modelos desde cache (útil para scheduler diario)."""
        print("🔄 Recargando modelos desde cache...")
        self._models_cache.clear()
        return self.load_models_from_cache(cache_path)


# Instancia global del registro
models_registry = ModelsRegistry.get_instance()
