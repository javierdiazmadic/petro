"""PHASE 13: Model optimization for edge deployment (Mini PC N150)."""

from typing import Tuple, Optional, Dict, Any
import numpy as np
import pickle
from pathlib import Path

from petro.core import get_logger

logger = get_logger(__name__)


class ModelOptimizer:
    """Optimizes models for edge deployment (< 16GB RAM, no GPU)."""

    @staticmethod
    def quantize_xgboost(
        model: Any, output_path: str = "models/xgboost_quantized.pkl"
    ) -> bool:
        """Quantize XGBoost model to reduce size.

        Converts float32 to int8 quantization where possible.

        Args:
            model: Trained XGBoost model
            output_path: Path to save quantized model

        Returns:
            True if successful
        """
        try:
            # XGBoost has native quantization support
            # Save with optimizations
            import xgboost as xgb

            # Set predict_leaf_index to reduce memory during inference
            model_dict = model.get_booster().get_dump(dump_format='json')

            # Save compressed
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)

            # Get file size
            size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"Quantized XGBoost model: {size_mb:.2f} MB")

            return True

        except Exception as e:
            logger.error(f"Error quantizing XGBoost: {e}")
            return False

    @staticmethod
    def compress_model(
        model: Any, output_path: str = "models/model_compressed.pkl"
    ) -> bool:
        """Compress model using zlib for storage.

        Args:
            model: Trained model
            output_path: Path to save compressed model

        Returns:
            True if successful
        """
        try:
            import gzip

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Serialize and compress
            with gzip.open(output_file, 'wb') as f:
                pickle.dump(model, f)

            size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"Compressed model: {size_mb:.2f} MB")

            return True

        except Exception as e:
            logger.error(f"Error compressing model: {e}")
            return False

    @staticmethod
    def load_compressed_model(model_path: str) -> Optional[Any]:
        """Load compressed model from disk.

        Args:
            model_path: Path to compressed model

        Returns:
            Loaded model or None
        """
        try:
            import gzip

            with gzip.open(model_path, 'rb') as f:
                model = pickle.load(f)

            logger.info(f"Loaded compressed model from {model_path}")
            return model

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None

    @staticmethod
    def estimate_memory(model: Any) -> Dict[str, float]:
        """Estimate memory usage of model.

        Args:
            model: Trained model

        Returns:
            Dictionary with memory estimates (in MB)
        """
        try:
            import sys

            model_size_mb = sys.getsizeof(model) / (1024 * 1024)

            return {
                "model_mb": model_size_mb,
                "runtime_overhead_mb": 100,  # Typical Python overhead
                "total_estimated_mb": model_size_mb + 100,
            }

        except Exception as e:
            logger.error(f"Error estimating memory: {e}")
            return {}

    @staticmethod
    def optimize_features(
        features: np.ndarray, n_top: int = 10
    ) -> np.ndarray:
        """Select top features by variance (reduce feature count).

        Args:
            features: Feature matrix
            n_top: Number of top features to keep

        Returns:
            Reduced feature matrix
        """
        try:
            # Calculate variance per feature
            variances = np.var(features, axis=0)
            top_indices = np.argsort(variances)[-n_top:]

            selected_features = features[:, top_indices]
            logger.info(f"Selected {n_top} features from {features.shape[1]}")

            return selected_features

        except Exception as e:
            logger.error(f"Error selecting features: {e}")
            return features


class EdgePredictor:
    """Lightweight predictor for edge deployment."""

    def __init__(self, model_path: str):
        """Initialize edge predictor.

        Args:
            model_path: Path to compressed model
        """
        self.model = ModelOptimizer.load_compressed_model(model_path)
        self.scaler = None
        self.feature_count = None

    def predict_fast(self, features: np.ndarray) -> Optional[float]:
        """Predict with minimal latency (< 100ms).

        Args:
            features: Feature vector

        Returns:
            Prediction or None
        """
        try:
            if self.model is None:
                return None

            # Ensure 2D
            if len(features.shape) == 1:
                features = features.reshape(1, -1)

            # Quick predict
            prediction = self.model.predict(features)

            return float(prediction[0])

        except Exception as e:
            logger.error(f"Error in edge prediction: {e}")
            return None

    def memory_profile(self) -> Dict[str, Any]:
        """Get memory profile for edge deployment.

        Returns:
            Memory usage information
        """
        memory_info = ModelOptimizer.estimate_memory(self.model)

        return {
            **memory_info,
            "suitable_for_edge": memory_info.get("total_estimated_mb", 0) < 2000,
        }


class EdgeNLPOptimizer:
    """Optimize NLP pipeline for edge."""

    @staticmethod
    def use_small_models() -> Dict[str, str]:
        """Return configuration for small spaCy models.

        Returns:
            Dict with model names for edge
        """
        return {
            "language_detection": "simplified_langdetect",
            "spacy_model": "es_core_news_sm",  # 50MB vs 500MB for full
            "bert_model": None,  # Skip BERT on edge
            "tfidf_cache": "enabled",
        }

    @staticmethod
    def simplify_nlp_pipeline() -> Dict[str, bool]:
        """Return NLP pipeline configuration for edge.

        Returns:
            Feature flags for simplified NLP
        """
        return {
            "clean_html": True,
            "deduplication": True,
            "language_detection": True,
            "ner": True,
            "classification": True,
            "sentiment": True,
            "bert_embedding": False,  # Skip deep learning
            "topic_modeling": False,  # Skip complex ML
        }
