"""Download and Load Trained Models - Descarga modelos de GitHub y los carga en la aplicación."""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class ModelDownloader:
    """Descargador de modelos entrenados desde GitHub."""

    GITHUB_REPO = "https://github.com/javierdiazmadic/petro.git"
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com/javierdiazmadic/petro/master"
    LOCAL_REPO_PATH = Path("/home/administrador/Desktop/petro")
    MODELS_EXPORT_DIR = LOCAL_REPO_PATH / "models_export"
    H5_DIR = MODELS_EXPORT_DIR / "h5"
    JSON_DIR = MODELS_EXPORT_DIR / "json"

    @staticmethod
    def ensure_directories():
        """Crear directorios necesarios."""
        for directory in [ModelDownloader.H5_DIR, ModelDownloader.JSON_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def download_from_github_via_git() -> bool:
        """Descargar modelos usando git pull (la forma más confiable en un servidor local)."""
        print("\n🔄 Actualizando repositorio local desde GitHub...")

        try:
            os.chdir(str(ModelDownloader.LOCAL_REPO_PATH))

            # Hacer pull del repositorio
            result = subprocess.run(
                ["git", "pull", "origin", "master"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("  ✅ Repositorio actualizado correctamente")
                return True
            else:
                print(f"  ⚠️ Git pull retornó error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("  ❌ Timeout esperando git pull")
            return False
        except Exception as e:
            print(f"  ❌ Error en git pull: {e}")
            return False

    @staticmethod
    def load_model_metadata(model_name: str) -> Optional[Dict]:
        """Cargar metadata de un modelo desde JSON."""
        try:
            metadata_path = ModelDownloader.JSON_DIR / f"{model_name}_metadata.json"

            if not metadata_path.exists():
                print(f"  ⚠️ Metadata no encontrada: {metadata_path}")
                return None

            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            print(f"  ✅ Metadata cargado: {model_name}")
            return metadata

        except Exception as e:
            print(f"  ❌ Error cargando metadata {model_name}: {e}")
            return None

    @staticmethod
    def verify_models_exist() -> Dict[str, bool]:
        """Verificar que los archivos de modelos existan."""
        models_status = {
            "xgboost": (ModelDownloader.JSON_DIR / "xgboost_metadata.json").exists(),
            "lightgbm": (ModelDownloader.JSON_DIR / "lightgbm_metadata.json").exists(),
            "randomforest": (ModelDownloader.JSON_DIR / "randomforest_metadata.json").exists(),
        }

        print("\n📊 Estado de modelos:")
        for model_name, exists in models_status.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {model_name.capitalize()}: {'presente' if exists else 'faltante'}")

        return models_status

    @staticmethod
    def load_all_models() -> Dict[str, Optional[Dict]]:
        """Cargar metadata de todos los modelos."""
        print("\n" + "=" * 80)
        print(f"📥 DESCARGANDO Y CARGANDO MODELOS - {datetime.utcnow().isoformat()}")
        print("=" * 80)

        # Crear directorios
        ModelDownloader.ensure_directories()

        # Descargar desde GitHub
        if not ModelDownloader.download_from_github_via_git():
            print("\n⚠️ Fallo al descargar desde GitHub - usando modelos en caché local")

        # Verificar que los modelos existan
        models_status = ModelDownloader.verify_models_exist()

        # Cargar metadata de todos los modelos
        print("\n🔄 Cargando metadata de modelos...")
        loaded_models = {}

        for model_name in ["xgboost", "lightgbm", "randomforest"]:
            metadata = ModelDownloader.load_model_metadata(model_name)
            loaded_models[model_name] = metadata

        # Resumen
        loaded_count = sum(1 for m in loaded_models.values() if m is not None)
        print("\n" + "=" * 80)
        print(f"✅ MODELOS CARGADOS: {loaded_count}/3")
        print("=" * 80)

        if loaded_count > 0:
            print("\n📊 Información de modelos cargados:")
            for model_name, metadata in loaded_models.items():
                if metadata:
                    print(f"\n  {model_name.upper()}:")
                    print(f"    • R²: {metadata['metrics']['r2']}")
                    print(f"    • RMSE: {metadata['metrics']['rmse']}")
                    print(f"    • Accuracy: {metadata['metrics']['accuracy']}")
                    print(f"    • Features: {len(metadata['input_features'])} variables")

        return loaded_models

    @staticmethod
    def get_best_model(loaded_models: Dict[str, Optional[Dict]]) -> Optional[str]:
        """Obtener el nombre del mejor modelo basado en R²."""
        best_model = None
        best_r2 = -1

        for model_name, metadata in loaded_models.items():
            if metadata and metadata['metrics']['r2'] > best_r2:
                best_r2 = metadata['metrics']['r2']
                best_model = model_name

        if best_model:
            print(f"\n🏆 MEJOR MODELO: {best_model.upper()} (R² = {best_r2})")

        return best_model

    @staticmethod
    def export_models_to_api_cache() -> Dict:
        """Exportar metadata de modelos a un archivo que la API pueda usar."""
        try:
            loaded_models = ModelDownloader.load_all_models()
            best_model = ModelDownloader.get_best_model(loaded_models)

            # Crear estructura para la API
            api_cache = {
                "timestamp": datetime.utcnow().isoformat(),
                "best_model": best_model,
                "models": {}
            }

            for model_name, metadata in loaded_models.items():
                if metadata:
                    api_cache["models"][model_name] = {
                        "name": metadata["name"],
                        "metrics": metadata["metrics"],
                        "input_features": metadata["input_features"],
                        "output_feature": metadata["output_feature"],
                        "training_date": metadata["training_date"]
                    }

            # Guardar para que la API lo use
            cache_path = ModelDownloader.MODELS_EXPORT_DIR / "models_api_cache.json"
            with open(cache_path, 'w') as f:
                json.dump(api_cache, f, indent=2)

            print(f"\n✅ Cache de API guardado: {cache_path}")
            return api_cache

        except Exception as e:
            print(f"\n❌ Error exportando cache: {e}")
            return {}


def main():
    """Función principal."""
    try:
        # Descargar y cargar todos los modelos
        downloader = ModelDownloader()
        loaded_models = downloader.load_all_models()

        # Obtener mejor modelo
        best_model = downloader.get_best_model(loaded_models)

        # Exportar para la API
        downloader.export_models_to_api_cache()

        print("\n" + "=" * 80)
        print("✅ PROCESO COMPLETADO")
        print("=" * 80)
        print(f"\n📍 Modelos listos para usar en:")
        print(f"  • API: /api/v1/predictions/models")
        print(f"  • Dashboard: /predictions")
        print(f"  • Backend: src/petro/ml/")

        return True

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
