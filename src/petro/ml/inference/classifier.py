"""Classify price direction from predictions."""

from enum import Enum
from typing import Dict, Optional, Tuple

import numpy as np

from petro.core import get_logger

logger = get_logger(__name__)


class PriceDirection(Enum):
    """Price direction classification."""

    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class DirectionClassifier:
    """Classifies price direction (up/down/stable) from regression predictions."""

    def __init__(
        self,
        current_price: float,
        threshold_pct: float = 0.5,
    ):
        """Initialize classifier.

        Args:
            current_price: Current reference price
            threshold_pct: Percentage threshold for classification (default 0.5%)
        """
        self.current_price = current_price
        self.threshold_pct = threshold_pct

    def classify_single(self, predicted_price: float) -> PriceDirection:
        """Classify direction for single prediction.

        Args:
            predicted_price: Predicted price value

        Returns:
            PriceDirection (UP, DOWN, STABLE)
        """
        try:
            change_pct = ((predicted_price - self.current_price) / self.current_price) * 100

            if change_pct > self.threshold_pct:
                return PriceDirection.UP
            elif change_pct < -self.threshold_pct:
                return PriceDirection.DOWN
            else:
                return PriceDirection.STABLE

        except Exception as e:
            logger.error(f"Error classifying direction: {e}")
            return PriceDirection.STABLE

    def classify_with_confidence(
        self, predicted_price: float
    ) -> Dict[str, float]:
        """Classify direction with confidence scores.

        Args:
            predicted_price: Predicted price value

        Returns:
            Dictionary with probabilities for each direction
        """
        try:
            change_pct = ((predicted_price - self.current_price) / self.current_price) * 100

            # Use sigmoid-like function for smooth confidence
            # Center at current price, spread increases with std of change
            std_change = self.threshold_pct

            if change_pct > self.threshold_pct:
                # UP direction
                up_confidence = min(
                    1.0, 0.5 + (change_pct / (2 * std_change))
                )
                down_confidence = max(0.0, 0.25 - (change_pct / (4 * std_change)))
                stable_confidence = 1.0 - up_confidence - down_confidence

            elif change_pct < -self.threshold_pct:
                # DOWN direction
                down_confidence = min(
                    1.0, 0.5 + (-change_pct / (2 * std_change))
                )
                up_confidence = max(0.0, 0.25 + (change_pct / (4 * std_change)))
                stable_confidence = 1.0 - down_confidence - up_confidence

            else:
                # STABLE direction
                stable_confidence = 0.7
                up_confidence = 0.15
                down_confidence = 0.15

            # Normalize to sum to 1.0
            total = up_confidence + down_confidence + stable_confidence
            if total > 0:
                up_confidence /= total
                down_confidence /= total
                stable_confidence /= total

            return {
                "up": round(float(up_confidence), 4),
                "stable": round(float(stable_confidence), 4),
                "down": round(float(down_confidence), 4),
            }

        except Exception as e:
            logger.error(f"Error computing confidence: {e}")
            return {"up": 0.33, "stable": 0.34, "down": 0.33}

    def classify_batch(
        self, predicted_prices: np.ndarray
    ) -> Dict[str, list]:
        """Classify multiple predictions.

        Args:
            predicted_prices: Array of predicted prices

        Returns:
            Dictionary with directions and confidences
        """
        try:
            directions = []
            confidences = []

            for price in predicted_prices:
                direction = self.classify_single(price)
                confidence = self.classify_with_confidence(price)
                directions.append(direction.value)
                confidences.append(confidence)

            return {
                "directions": directions,
                "confidences": confidences,
            }

        except Exception as e:
            logger.error(f"Error batch classifying: {e}")
            return {"directions": [], "confidences": []}

    def get_direction_string(self, direction: PriceDirection) -> str:
        """Get human-readable direction string.

        Args:
            direction: PriceDirection enum

        Returns:
            String representation
        """
        descriptions = {
            PriceDirection.UP: "📈 Subida (esperado aumento de precio)",
            PriceDirection.DOWN: "📉 Bajada (esperado descenso de precio)",
            PriceDirection.STABLE: "➡️ Estable (sin cambios significativos)",
        }
        return descriptions.get(direction, "Desconocido")
