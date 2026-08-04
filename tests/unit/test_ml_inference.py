"""Unit tests for ML inference pipeline."""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestRegressor

from petro.ml.inference import (
    ModelLoader,
    PricePredictor,
    DirectionClassifier,
    PriceDirection,
    InferencePipeline,
)


@pytest.fixture
def trained_model():
    """Create a simple trained model for testing."""
    X = np.random.randn(100, 10)
    y = 2.0 * X[:, 0] - 1.5 * X[:, 1] + np.random.randn(100) * 0.1
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model


@pytest.fixture
def sample_features():
    """Create sample features."""
    return np.random.randn(10)


@pytest.fixture
def sample_features_batch():
    """Create batch of sample features."""
    return [np.random.randn(10) for _ in range(3)]


class TestPricePredictor:
    """Tests for PricePredictor."""

    def test_predictor_init(self, trained_model):
        """Test predictor initialization."""
        predictor = PricePredictor(trained_model)
        assert predictor.model is not None
        assert predictor.scaler is None

    def test_predict_single(self, trained_model, sample_features):
        """Test single prediction."""
        predictor = PricePredictor(trained_model)
        prediction = predictor.predict(sample_features)

        assert prediction is not None
        assert isinstance(prediction, float)
        assert not np.isnan(prediction)

    def test_predict_batch(self, trained_model, sample_features_batch):
        """Test batch prediction."""
        predictor = PricePredictor(trained_model)
        predictions = predictor.predict_batch(sample_features_batch)

        assert predictions is not None
        assert len(predictions) == 3
        assert all(isinstance(p, float) for p in predictions)

    def test_predict_with_bounds(self, trained_model, sample_features):
        """Test prediction with bounds."""
        predictor = PricePredictor(trained_model)
        result = predictor.predict_with_bounds(sample_features, uncertainty=0.1)

        assert result is not None
        assert "prediction" in result
        assert "lower_bound" in result
        assert "upper_bound" in result

        # Check bounds are correct
        pred = result["prediction"]
        lower = result["lower_bound"]
        upper = result["upper_bound"]

        assert lower < pred < upper
        assert abs(lower / pred - 0.9) < 0.01
        assert abs(upper / pred - 1.1) < 0.01


class TestDirectionClassifier:
    """Tests for DirectionClassifier."""

    def test_classifier_init(self):
        """Test classifier initialization."""
        classifier = DirectionClassifier(current_price=1.5)
        assert classifier.current_price == 1.5
        assert classifier.threshold_pct == 0.5

    def test_classify_up(self):
        """Test UP classification."""
        classifier = DirectionClassifier(current_price=1.5, threshold_pct=0.5)

        # 1% increase should be UP
        direction = classifier.classify_single(1.515)
        assert direction == PriceDirection.UP

    def test_classify_down(self):
        """Test DOWN classification."""
        classifier = DirectionClassifier(current_price=1.5, threshold_pct=0.5)

        # 1% decrease should be DOWN
        direction = classifier.classify_single(1.485)
        assert direction == PriceDirection.DOWN

    def test_classify_stable(self):
        """Test STABLE classification."""
        classifier = DirectionClassifier(current_price=1.5, threshold_pct=0.5)

        # 0.1% change should be STABLE
        direction = classifier.classify_single(1.5015)
        assert direction == PriceDirection.STABLE

    def test_confidence_scores(self):
        """Test confidence score calculation."""
        classifier = DirectionClassifier(current_price=1.5)
        confidence = classifier.classify_with_confidence(1.515)

        assert "up" in confidence
        assert "down" in confidence
        assert "stable" in confidence

        # Scores should sum to 1.0
        total = confidence["up"] + confidence["down"] + confidence["stable"]
        assert abs(total - 1.0) < 0.01

        # UP should be highest for higher price
        assert confidence["up"] > confidence["down"]
        assert confidence["up"] > confidence["stable"]

    def test_batch_classification(self):
        """Test batch classification."""
        classifier = DirectionClassifier(current_price=1.5)
        prices = np.array([1.515, 1.485, 1.5015])

        result = classifier.classify_batch(prices)

        assert "directions" in result
        assert "confidences" in result
        assert len(result["directions"]) == 3
        assert len(result["confidences"]) == 3

        # First should be UP, second DOWN, third STABLE
        assert result["directions"][0] == "up"
        assert result["directions"][1] == "down"
        assert result["directions"][2] == "stable"


class TestInferencePipeline:
    """Tests for InferencePipeline."""

    def test_pipeline_init(self):
        """Test pipeline initialization."""
        pipeline = InferencePipeline()
        assert pipeline.predictor is None
        assert pipeline.classifier is None
        assert not pipeline.is_ready()

    def test_pipeline_manual_setup(self, trained_model):
        """Test manual pipeline setup without MLflow."""
        pipeline = InferencePipeline()

        # Manually set components
        pipeline.predictor = PricePredictor(trained_model)
        pipeline.classifier = DirectionClassifier(current_price=1.5)
        pipeline.last_price = 1.5

        assert pipeline.is_ready()

    def test_pipeline_predict(self, trained_model):
        """Test pipeline prediction."""
        pipeline = InferencePipeline()
        pipeline.predictor = PricePredictor(trained_model)
        pipeline.classifier = DirectionClassifier(current_price=1.5)
        pipeline.last_price = 1.5

        features = np.random.randn(10)
        result = pipeline.predict_price(features, include_bounds=True)

        assert result is not None
        assert "prediction" in result
        assert "direction" in result
        assert "confidence" in result
        assert "bounds" in result

    def test_pipeline_predict_multiple(self, trained_model):
        """Test pipeline multi-horizon prediction."""
        pipeline = InferencePipeline()
        pipeline.predictor = PricePredictor(trained_model)
        pipeline.classifier = DirectionClassifier(current_price=1.5)
        pipeline.last_price = 1.5

        features_list = [np.random.randn(10) for _ in range(3)]
        results = pipeline.predict_multiple(features_list, horizons=["1d", "3d", "7d"])

        assert results is not None
        assert "1d" in results
        assert "3d" in results
        assert "7d" in results

        for horizon_result in results.values():
            assert "prediction" in horizon_result
            assert "direction" in horizon_result

    def test_pipeline_update_reference_price(self, trained_model):
        """Test updating reference price."""
        pipeline = InferencePipeline()
        pipeline.predictor = PricePredictor(trained_model)
        pipeline.classifier = DirectionClassifier(current_price=1.5)
        pipeline.last_price = 1.5

        pipeline.update_reference_price(1.6)

        assert pipeline.last_price == 1.6
        assert pipeline.classifier.current_price == 1.6


class TestModelLoader:
    """Tests for ModelLoader."""

    def test_loader_init(self):
        """Test loader initialization."""
        loader = ModelLoader()
        assert loader.model is None
        assert loader.scaler is None
        assert not loader.is_loaded()

    def test_loader_is_loaded(self, trained_model):
        """Test is_loaded check."""
        loader = ModelLoader()
        assert not loader.is_loaded()

        loader.model = trained_model
        assert loader.is_loaded()

    def test_loader_get_model_info(self):
        """Test getting model info."""
        loader = ModelLoader()
        loader.model_metadata = {"rmse": 0.123, "r2": 0.456}

        info = loader.get_model_info()
        assert info is not None
        assert info["rmse"] == 0.123
        assert info["r2"] == 0.456
