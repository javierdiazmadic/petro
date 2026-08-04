"""End-to-end inference pipeline."""

from typing import Any, Dict, Optional

import numpy as np
from datetime import datetime

from petro.core import get_logger
from .loader import ModelLoader
from .predictor import PricePredictor
from .classifier import DirectionClassifier, PriceDirection

logger = get_logger(__name__)


class InferencePipeline:
    """Complete inference pipeline: load → predict → classify."""

    def __init__(self):
        """Initialize pipeline."""
        self.loader = ModelLoader()
        self.predictor = None
        self.classifier = None
        self.last_price = None

    def initialize(
        self,
        experiment_name: str = "petro-fuel-prediction",
        current_price: Optional[float] = None,
    ) -> bool:
        """Initialize pipeline with model and current price.

        Args:
            experiment_name: MLflow experiment name
            current_price: Current reference price for classification

        Returns:
            True if initialized successfully
        """
        try:
            # Load model
            model, metadata = self.loader.load_production_model(experiment_name)
            if model is None:
                logger.error("Failed to load model")
                return False

            # Initialize predictor
            self.predictor = PricePredictor(model, scaler=None)

            # Initialize classifier
            if current_price is None:
                logger.warning("Current price not provided, using 1.5 as default")
                current_price = 1.5

            self.last_price = current_price
            self.classifier = DirectionClassifier(current_price, threshold_pct=0.5)

            logger.info(
                f"Pipeline initialized. Current price: {current_price}, "
                f"Model RMSE: {metadata['rmse']:.6f}"
            )
            return True

        except Exception as e:
            logger.error(f"Error initializing pipeline: {e}", exc_info=True)
            return False

    def predict_price(
        self, features: np.ndarray, include_bounds: bool = True
    ) -> Optional[Dict]:
        """Predict price and classify direction.

        Args:
            features: Feature vector
            include_bounds: Include confidence bounds

        Returns:
            Dictionary with prediction, direction, confidence
        """
        try:
            if self.predictor is None or self.classifier is None:
                logger.error("Pipeline not initialized")
                return None

            # Predict price
            if include_bounds:
                prediction_dict = self.predictor.predict_with_bounds(features)
                if prediction_dict is None:
                    return None
                predicted_price = prediction_dict["prediction"]
            else:
                predicted_price = self.predictor.predict(features)
                if predicted_price is None:
                    return None
                prediction_dict = {"prediction": predicted_price}

            # Classify direction
            direction = self.classifier.classify_single(predicted_price)
            confidence = self.classifier.classify_with_confidence(predicted_price)

            # Calculate change
            change = predicted_price - self.last_price
            change_pct = (change / self.last_price) * 100 if self.last_price else 0

            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "prediction": predicted_price,
                "current_price": self.last_price,
                "change": round(change, 4),
                "change_pct": round(change_pct, 2),
                "direction": direction.value,
                "direction_label": self.classifier.get_direction_string(direction),
                "confidence": confidence,
            }

            # Add bounds if included
            if include_bounds:
                result["bounds"] = {
                    "lower": prediction_dict.get("lower_bound"),
                    "upper": prediction_dict.get("upper_bound"),
                }

            logger.debug(f"Prediction: {predicted_price:.4f}, Direction: {direction.value}")
            return result

        except Exception as e:
            logger.error(f"Error in predict_price: {e}", exc_info=True)
            return None

    def predict_multiple(
        self, features_list: list, horizons: list = None
    ) -> Optional[Dict]:
        """Predict prices for multiple horizons.

        Args:
            features_list: List of feature vectors (one per horizon)
            horizons: List of horizon labels (e.g., ["1d", "3d", "7d"])

        Returns:
            Dictionary with predictions for each horizon
        """
        try:
            if len(features_list) == 0:
                return None

            if horizons is None:
                horizons = [f"h{i+1}" for i in range(len(features_list))]

            results = {}

            for horizon, features in zip(horizons, features_list):
                result = self.predict_price(features, include_bounds=True)
                if result:
                    results[horizon] = result

            logger.info(f"Predicted {len(results)} horizons")
            return results if results else None

        except Exception as e:
            logger.error(f"Error predicting multiple: {e}", exc_info=True)
            return None

    def update_reference_price(self, new_price: float):
        """Update reference price for direction classification.

        Args:
            new_price: New reference price
        """
        self.last_price = new_price
        if self.classifier:
            self.classifier.current_price = new_price
        logger.info(f"Reference price updated to {new_price}")

    def is_ready(self) -> bool:
        """Check if pipeline is ready for inference.

        Returns:
            True if pipeline is initialized
        """
        return self.predictor is not None and self.classifier is not None

    def get_model_info(self) -> Optional[Dict]:
        """Get information about loaded model.

        Returns:
            Dictionary with model metadata or None
        """
        return self.loader.get_model_info()
