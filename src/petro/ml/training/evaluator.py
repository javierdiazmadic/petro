"""Model evaluation and metrics calculation."""

from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from petro.core import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """Evaluates model performance using standard metrics."""

    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate standard regression metrics.

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            Dictionary with metrics
        """
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)

        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

        return {
            "mse": round(mse, 6),
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "r2": round(r2, 6),
            "mape": round(mape, 3),
        }

    @staticmethod
    def evaluate_model(model: Any, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate a single model.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target

        Returns:
            Dictionary with predictions and metrics
        """
        try:
            y_pred = model.predict(X_test)
            metrics = ModelEvaluator.calculate_metrics(y_test, y_pred)

            return {
                "predictions": y_pred,
                "metrics": metrics,
                "y_true": y_test,
            }

        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return None

    @staticmethod
    def get_feature_importance(
        model: Any, feature_names: Optional[List[str]] = None, top_n: int = 20
    ) -> Optional[Dict]:
        """Extract feature importance from model.

        Args:
            model: Trained model
            feature_names: Names of features
            top_n: Top N features to return

        Returns:
            Dictionary with feature importance or None
        """
        try:
            # Get importance based on model type
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
            elif hasattr(model, "get_score"):
                # LightGBM
                importances_dict = model.get_score(importance_type="gain")
                # Convert to array (assumes feature indices as keys)
                importances = np.zeros(len(importances_dict))
                for idx, imp in importances_dict.items():
                    importances[int(idx)] = imp
            else:
                return None

            # Get top features
            top_indices = np.argsort(importances)[-top_n:][::-1]

            if feature_names:
                top_features = [feature_names[i] for i in top_indices]
            else:
                top_features = [f"feature_{i}" for i in top_indices]

            top_importances = [float(importances[i]) for i in top_indices]

            return {
                "features": top_features,
                "importances": top_importances,
                "all_importances": {
                    (feature_names[i] if feature_names else f"feature_{i}"): float(importances[i])
                    for i in range(len(importances))
                },
            }

        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return None

    @staticmethod
    def compare_models(results: Dict[str, Dict]) -> Dict:
        """Compare metrics across multiple models.

        Args:
            results: Dictionary with model results

        Returns:
            Dictionary with comparison summary
        """
        comparison = {}

        for model_name, result in results.items():
            if result and "metrics" in result:
                comparison[model_name] = result["metrics"]

        # Find best model by RMSE
        best_model = min(comparison.items(), key=lambda x: x[1].get("rmse", float("inf")))[0]

        return {
            "comparison": comparison,
            "best_model": best_model,
            "best_metrics": comparison[best_model],
        }
