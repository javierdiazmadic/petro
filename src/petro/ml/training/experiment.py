"""MLflow experiment tracking and model management."""

from typing import Any, Dict, Optional

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.lightgbm
import numpy as np

from petro.core import get_logger

logger = get_logger(__name__)


class ExperimentTracker:
    """Tracks ML experiments with MLflow."""

    def __init__(self, experiment_name: str = "petro-fuel-prediction"):
        """Initialize tracker.

        Args:
            experiment_name: MLflow experiment name
        """
        self.experiment_name = experiment_name
        self._setup_experiment()

    def _setup_experiment(self):
        """Setup or get MLflow experiment."""
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                mlflow.create_experiment(self.experiment_name)
            mlflow.set_experiment(self.experiment_name)
            logger.info(f"Experiment '{self.experiment_name}' initialized")
        except Exception as e:
            logger.error(f"Error setting up experiment: {e}")

    def start_run(
        self, run_name: str, tags: Optional[Dict[str, str]] = None
    ) -> str:
        """Start a new MLflow run.

        Args:
            run_name: Name of the run
            tags: Optional tags to attach to run

        Returns:
            Run ID
        """
        try:
            run = mlflow.start_run(run_name=run_name)
            run_id = run.info.run_id

            if tags:
                mlflow.set_tags(tags)

            logger.info(f"Started run '{run_name}' with ID {run_id}")
            return run_id

        except Exception as e:
            logger.error(f"Error starting run: {e}")
            return None

    def log_params(self, params: Dict[str, Any]):
        """Log hyperparameters.

        Args:
            params: Dictionary of parameters
        """
        try:
            # Filter out non-loggable types
            for key, value in params.items():
                if isinstance(value, (int, float, str, bool)):
                    mlflow.log_param(key, value)
        except Exception as e:
            logger.error(f"Error logging params: {e}")

    def log_metrics(self, metrics: Dict[str, float], step: int = 0):
        """Log metrics.

        Args:
            metrics: Dictionary of metrics
            step: Training step
        """
        try:
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value, step=step)
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")

    def log_model(
        self,
        model: Any,
        model_name: str,
        model_type: str,
        metrics: Optional[Dict] = None,
    ):
        """Log a trained model.

        Args:
            model: Trained model
            model_name: Name for the model
            model_type: Type (xgboost, lightgbm, random_forest)
            metrics: Optional metrics dict to log first
        """
        try:
            if metrics:
                self.log_metrics(metrics)

            # Log model with appropriate flavor
            if model_type == "xgboost":
                mlflow.xgboost.log_model(model, model_name)
            elif model_type == "lightgbm":
                mlflow.lightgbm.log_model(model, model_name)
            else:  # random_forest
                mlflow.sklearn.log_model(model, model_name)

            logger.info(f"Logged {model_type} model '{model_name}'")

        except Exception as e:
            logger.error(f"Error logging model: {e}")

    def log_feature_importance(
        self,
        feature_names: list,
        importances: list,
        model_name: str = "feature_importance",
    ):
        """Log feature importances as artifact.

        Args:
            feature_names: List of feature names
            importances: List of importance values
            model_name: Name to save under
        """
        try:
            # Create simple text artifact
            import tempfile
            import os

            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "feature_importance.txt")

                with open(filepath, "w") as f:
                    f.write("Feature,Importance\n")
                    for fname, imp in zip(feature_names, importances):
                        f.write(f"{fname},{imp}\n")

                mlflow.log_artifact(filepath, artifact_path=model_name)
                logger.info(f"Logged feature importance for {model_name}")

        except Exception as e:
            logger.error(f"Error logging feature importance: {e}")

    def end_run(self, status: str = "FINISHED"):
        """End the current run.

        Args:
            status: Run status (FINISHED, FAILED, SCHEDULED)
        """
        try:
            mlflow.end_run(status=status)
            logger.info(f"Run ended with status {status}")
        except Exception as e:
            logger.error(f"Error ending run: {e}")

    def register_model(
        self,
        model_uri: str,
        model_name: str,
        description: str = "",
        tags: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Register a model to MLflow Registry.

        Args:
            model_uri: Model URI from run (models/modelname)
            model_name: Name to register as
            description: Model description
            tags: Optional tags

        Returns:
            Model version or None
        """
        try:
            result = mlflow.register_model(model_uri, model_name)
            version = result.version

            # Update description
            if description:
                mlflow.models.update_model_version(
                    name=model_name, version=version, description=description
                )

            # Add tags if provided
            if tags:
                for key, value in tags.items():
                    mlflow.models.set_model_version_tag(
                        name=model_name, version=version, key=key, value=value
                    )

            logger.info(f"Registered {model_name} (v{version})")
            return version

        except Exception as e:
            logger.error(f"Error registering model: {e}")
            return None

    @staticmethod
    def get_best_run(
        experiment_name: str, metric: str = "rmse", mode: str = "min"
    ) -> Optional[Dict]:
        """Get best run from experiment.

        Args:
            experiment_name: Experiment name
            metric: Metric to optimize
            mode: 'min' or 'max'

        Returns:
            Dictionary with run info or None
        """
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if not experiment:
                return None

            client = mlflow.tracking.MlflowClient()
            runs = client.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=[f"metrics.{metric} {'ASC' if mode == 'min' else 'DESC'}"],
                max_results=1,
            )

            if not runs:
                return None

            run = runs[0]
            return {
                "run_id": run.info.run_id,
                "metrics": run.data.metrics,
                "params": run.data.params,
            }

        except Exception as e:
            logger.error(f"Error getting best run: {e}")
            return None

    @staticmethod
    def compare_models(experiment_name: str) -> Optional[Dict]:
        """Compare all models in an experiment.

        Args:
            experiment_name: Experiment name

        Returns:
            Dictionary with comparison results or None
        """
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if not experiment:
                return None

            client = mlflow.tracking.MlflowClient()
            runs = client.search_runs(experiment_ids=[experiment.experiment_id])

            comparison = {
                "runs": [],
            }

            for run in runs:
                comparison["runs"].append(
                    {
                        "run_id": run.info.run_id,
                        "status": run.info.status,
                        "metrics": run.data.metrics,
                        "params": run.data.params,
                    }
                )

            return comparison

        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            return None
