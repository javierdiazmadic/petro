"""Price prediction from trained models."""

from typing import Any, Dict, Optional, List

import numpy as np
from sklearn.preprocessing import StandardScaler

from petro.core import get_logger

logger = get_logger(__name__)


class PricePredictor:
    """Predicts fuel prices using trained models."""

    def __init__(self, model: Any, scaler: Optional[StandardScaler] = None):
        """Initialize predictor.

        Args:
            model: Trained ML model
            scaler: StandardScaler for feature normalization
        """
        self.model = model
        self.scaler = scaler

    def predict(
        self, features: np.ndarray, return_raw: bool = False
    ) -> Optional[float]:
        """Predict price for given features.

        Args:
            features: Feature vector or matrix (2D)
            return_raw: If True, return raw model output

        Returns:
            Predicted price or None on failure
        """
        try:
            # Ensure 2D
            if len(features.shape) == 1:
                features = features.reshape(1, -1)

            # Normalize if scaler provided
            if self.scaler:
                features = self.scaler.transform(features)

            # Predict
            prediction = self.model.predict(features)

            # Return scalar if single prediction
            if len(prediction) == 1:
                return float(prediction[0])

            return prediction if return_raw else float(prediction[0])

        except Exception as e:
            logger.error(f"Error predicting price: {e}")
            return None

    def predict_batch(
        self, features_list: List[np.ndarray]
    ) -> Optional[List[float]]:
        """Predict prices for multiple feature vectors.

        Args:
            features_list: List of feature vectors

        Returns:
            List of predictions or None on failure
        """
        try:
            # Stack into matrix
            features = np.vstack(features_list)

            # Normalize if scaler provided
            if self.scaler:
                features = self.scaler.transform(features)

            # Predict
            predictions = self.model.predict(features)

            return [float(p) for p in predictions]

        except Exception as e:
            logger.error(f"Error batch predicting: {e}")
            return None

    def predict_with_bounds(
        self, features: np.ndarray, uncertainty: float = 0.05
    ) -> Optional[Dict[str, float]]:
        """Predict price with confidence bounds.

        Args:
            features: Feature vector
            uncertainty: Uncertainty margin (default 5%)

        Returns:
            Dictionary with prediction, lower, upper bounds
        """
        try:
            prediction = self.predict(features)
            if prediction is None:
                return None

            lower_bound = prediction * (1 - uncertainty)
            upper_bound = prediction * (1 + uncertainty)

            return {
                "prediction": prediction,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "uncertainty": uncertainty,
            }

        except Exception as e:
            logger.error(f"Error computing bounds: {e}")
            return None
