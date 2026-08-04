"""SHAP explainability for model predictions."""

from typing import Any, Dict, List, Optional

import numpy as np
import shap

from petro.core import get_logger

logger = get_logger(__name__)


class SHAPExplainer:
    """Generates SHAP explanations for model predictions."""

    def __init__(self, model: Any, model_type: str = "xgboost"):
        """Initialize SHAP explainer.

        Args:
            model: Trained model (XGBoost, LightGBM, or RandomForest)
            model_type: Type of model
        """
        self.model = model
        self.model_type = model_type
        self.explainer = None
        self._initialize_explainer()

    def _initialize_explainer(self):
        """Initialize appropriate SHAP explainer."""
        try:
            if self.model_type == "xgboost":
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("XGBoost TreeExplainer initialized")
            elif self.model_type == "lightgbm":
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("LightGBM TreeExplainer initialized")
            elif self.model_type == "random_forest":
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("RandomForest TreeExplainer initialized")
            else:
                logger.warning(f"Unknown model type: {self.model_type}, using TreeExplainer")
                self.explainer = shap.TreeExplainer(self.model)

        except Exception as e:
            logger.error(f"Error initializing SHAP explainer: {e}")
            self.explainer = None

    def explain_single(
        self, features: np.ndarray, feature_names: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Generate SHAP explanation for single prediction.

        Args:
            features: Feature vector (1D or reshaped to 2D)
            feature_names: Optional feature names

        Returns:
            Dictionary with SHAP values and explanation
        """
        try:
            if self.explainer is None:
                return None

            # Ensure 2D shape
            if len(features.shape) == 1:
                features = features.reshape(1, -1)

            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features)

            # Handle array of shap values (for multi-class)
            if isinstance(shap_values, list):
                shap_values = shap_values[0] if len(shap_values) > 0 else shap_values

            # Flatten to 1D for single prediction
            if shap_values.ndim > 1:
                shap_values = shap_values[0]

            # Get base value
            base_value = self.explainer.expected_value
            if isinstance(base_value, (list, np.ndarray)):
                base_value = float(base_value[0]) if len(base_value) > 0 else float(base_value)
            base_value = float(base_value)

            # Create feature importance ranking
            feature_importance = []
            for idx, shap_val in enumerate(shap_values):
                feature_importance.append({
                    "index": int(idx),
                    "name": feature_names[idx] if feature_names else f"feature_{idx}",
                    "shap_value": float(shap_val),
                    "feature_value": float(features[0, idx]),
                })

            # Sort by absolute SHAP value
            feature_importance.sort(
                key=lambda x: abs(x["shap_value"]), reverse=True
            )

            return {
                "base_value": base_value,
                "shap_values": [float(v) for v in shap_values],
                "feature_importance": feature_importance,
                "prediction": float(base_value + sum(shap_values)),
            }

        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {e}")
            return None

    def explain_batch(
        self,
        features: np.ndarray,
        feature_names: Optional[List[str]] = None,
    ) -> Optional[List[Dict]]:
        """Generate SHAP explanations for multiple predictions.

        Args:
            features: Feature matrix (N x M)
            feature_names: Optional feature names

        Returns:
            List of explanations
        """
        try:
            if self.explainer is None:
                return None

            explanations = []
            for i in range(features.shape[0]):
                explanation = self.explain_single(
                    features[i:i+1], feature_names
                )
                if explanation:
                    explanations.append(explanation)

            return explanations if explanations else None

        except Exception as e:
            logger.error(f"Error batch explaining: {e}")
            return None

    def get_feature_contribution(
        self, features: np.ndarray, feature_names: Optional[List[str]] = None
    ) -> Optional[Dict[str, float]]:
        """Get feature contribution to prediction (SHAP approach).

        Args:
            features: Feature vector
            feature_names: Feature names

        Returns:
            Dictionary mapping feature name to contribution
        """
        try:
            explanation = self.explain_single(features, feature_names)
            if not explanation:
                return None

            contributions = {}
            for feature in explanation["feature_importance"]:
                name = feature["name"]
                contribution = feature["shap_value"]
                contributions[name] = float(contribution)

            return contributions

        except Exception as e:
            logger.error(f"Error getting feature contribution: {e}")
            return None

    def summary_plot_data(
        self,
        features: np.ndarray,
        feature_names: Optional[List[str]] = None,
    ) -> Optional[Dict]:
        """Prepare data for SHAP summary plot.

        Args:
            features: Training or test features
            feature_names: Feature names

        Returns:
            Dictionary with plot data
        """
        try:
            if self.explainer is None:
                return None

            # Calculate SHAP values for all samples
            shap_values = self.explainer.shap_values(features)

            # Handle array of shap values
            if isinstance(shap_values, list):
                shap_values = np.array(shap_values[0])
            else:
                shap_values = np.array(shap_values)

            # Calculate mean absolute SHAP per feature
            mean_abs_shap = np.abs(shap_values).mean(axis=0)

            feature_importance = []
            for idx, importance in enumerate(mean_abs_shap):
                feature_importance.append({
                    "name": feature_names[idx] if feature_names else f"feature_{idx}",
                    "importance": float(importance),
                    "index": int(idx),
                })

            # Sort
            feature_importance.sort(key=lambda x: x["importance"], reverse=True)

            return {
                "feature_importance": feature_importance,
                "total_samples": features.shape[0],
                "total_features": features.shape[1],
            }

        except Exception as e:
            logger.error(f"Error preparing summary plot: {e}")
            return None
