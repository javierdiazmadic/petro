"""Load trained models from MLflow."""

from typing import Any, Optional, Tuple

import mlflow
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler

from petro.core import get_logger

logger = get_logger(__name__)


class ModelLoader:
    """Load trained models and scalers from MLflow."""

    def __init__(self):
        """Initialize loader."""
        self.model = None
        self.scaler = None
        self.model_metadata = None

    def load_production_model(
        self, experiment_name: str = "petro-fuel-prediction"
    ) -> Tuple[Optional[Any], Optional[StandardScaler]]:
        """Load the best model from experiment.

        Args:
            experiment_name: MLflow experiment name

        Returns:
            Tuple of (model, scaler) or (None, None) on failure
        """
        try:
            # Get best run
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if not experiment:
                logger.error(f"Experiment '{experiment_name}' not found")
                return None, None

            client = mlflow.tracking.MlflowClient()
            runs = client.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["metrics.rmse ASC"],
                max_results=1,
            )

            if not runs:
                logger.error(f"No runs found in experiment '{experiment_name}'")
                return None, None

            run = runs[0]
            run_id = run.info.run_id

            logger.info(f"Loading best model from run {run_id}")

            # Load model
            model_uri = f"runs:{run_id}/xgboost-v1"
            try:
                model = mlflow.xgboost.load_model(model_uri)
                logger.info("Loaded XGBoost model")
            except Exception:
                # Try LightGBM
                try:
                    model_uri = f"runs:{run_id}/lightgbm-v1"
                    model = mlflow.lightgbm.load_model(model_uri)
                    logger.info("Loaded LightGBM model")
                except Exception:
                    # Try RandomForest
                    model_uri = f"runs:{run_id}/random_forest-v1"
                    model = mlflow.sklearn.load_model(model_uri)
                    logger.info("Loaded RandomForest model")

            self.model = model
            self.model_metadata = {
                "run_id": run_id,
                "rmse": run.data.metrics.get("rmse"),
                "r2": run.data.metrics.get("r2"),
            }

            logger.info(f"Model loaded successfully. RMSE: {self.model_metadata['rmse']:.6f}")
            return model, None

        except Exception as e:
            logger.error(f"Error loading production model: {e}", exc_info=True)
            return None, None

    def load_model_by_run_id(self, run_id: str) -> Tuple[Optional[Any], Optional[dict]]:
        """Load a specific model by run ID.

        Args:
            run_id: MLflow run ID

        Returns:
            Tuple of (model, metadata) or (None, None) on failure
        """
        try:
            logger.info(f"Loading model from run {run_id}")

            client = mlflow.tracking.MlflowClient()
            run = client.get_run(run_id)

            # Try each model type
            model = None
            model_type = None

            for model_name, ml_type in [
                ("xgboost-v1", "xgboost"),
                ("lightgbm-v1", "lightgbm"),
                ("random_forest-v1", "sklearn"),
            ]:
                try:
                    model_uri = f"runs:{run_id}/{model_name}"
                    if ml_type == "xgboost":
                        model = mlflow.xgboost.load_model(model_uri)
                    elif ml_type == "lightgbm":
                        model = mlflow.lightgbm.load_model(model_uri)
                    else:
                        model = mlflow.sklearn.load_model(model_uri)
                    model_type = ml_type
                    logger.info(f"Loaded {ml_type} model")
                    break
                except Exception:
                    continue

            if model is None:
                logger.error(f"Could not load any model from run {run_id}")
                return None, None

            metadata = {
                "run_id": run_id,
                "model_type": model_type,
                "metrics": run.data.metrics,
                "params": run.data.params,
            }

            self.model = model
            self.model_metadata = metadata

            return model, metadata

        except Exception as e:
            logger.error(f"Error loading model by run ID: {e}", exc_info=True)
            return None, None

    def load_scaler_from_file(self, filepath: str) -> Optional[StandardScaler]:
        """Load scaler from pickle file.

        Args:
            filepath: Path to pickle file

        Returns:
            StandardScaler or None on failure
        """
        try:
            with open(filepath, "rb") as f:
                scaler = pickle.load(f)
            self.scaler = scaler
            logger.info(f"Scaler loaded from {filepath}")
            return scaler
        except Exception as e:
            logger.error(f"Error loading scaler: {e}")
            return None

    def get_model_info(self) -> Optional[dict]:
        """Get loaded model information.

        Returns:
            Dictionary with model metadata or None
        """
        if self.model_metadata:
            return self.model_metadata
        return None

    def is_loaded(self) -> bool:
        """Check if model is loaded.

        Returns:
            True if model is loaded
        """
        return self.model is not None
