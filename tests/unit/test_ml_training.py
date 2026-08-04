"""Unit tests for ML training pipeline."""

import numpy as np
import pytest

from petro.ml.training.trainer import ModelTrainer
from petro.ml.training.evaluator import ModelEvaluator
from petro.ml.training.hyperparameter_tuner import HyperparameterTuner
from petro.ml.training.experiment import ExperimentTracker


@pytest.fixture
def sample_data():
    """Create sample training data."""
    np.random.seed(42)
    n_samples = 100
    n_features = 10

    X_train = np.random.randn(n_samples, n_features)
    y_train = np.random.randn(n_samples)

    X_test = np.random.randn(30, n_features)
    y_test = np.random.randn(30)

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
    }


class TestModelTrainer:
    """Tests for ModelTrainer."""

    def test_trainer_init(self):
        """Test trainer initialization."""
        trainer = ModelTrainer()
        assert trainer.models == {}
        assert trainer.scalers == {}

    def test_prepare_data(self, sample_data):
        """Test data preparation."""
        trainer = ModelTrainer()
        X_train, X_test, scaler = trainer.prepare_data(
            sample_data["X_train"], sample_data["X_test"]
        )

        assert X_train.shape == sample_data["X_train"].shape
        assert X_test.shape == sample_data["X_test"].shape
        assert scaler is not None

        # Check normalization (mean ~0, std ~1)
        assert np.abs(X_train.mean()) < 0.1
        assert np.abs(X_train.std() - 1.0) < 0.1

    def test_train_xgboost(self, sample_data):
        """Test XGBoost training."""
        trainer = ModelTrainer()
        X_train, X_test, _ = trainer.prepare_data(
            sample_data["X_train"], sample_data["X_test"]
        )

        result = trainer.train_xgboost(
            X_train, sample_data["y_train"], X_test, sample_data["y_test"]
        )

        assert result is not None
        assert "model" in result
        assert "model_type" in result
        assert result["model_type"] == "xgboost"
        assert trainer.models["xgboost"] is not None

    def test_train_lightgbm(self, sample_data):
        """Test LightGBM training."""
        trainer = ModelTrainer()
        X_train, X_test, _ = trainer.prepare_data(
            sample_data["X_train"], sample_data["X_test"]
        )

        result = trainer.train_lightgbm(
            X_train, sample_data["y_train"], X_test, sample_data["y_test"]
        )

        assert result is not None
        assert "model" in result
        assert result["model_type"] == "lightgbm"
        assert trainer.models["lightgbm"] is not None

    def test_train_random_forest(self, sample_data):
        """Test Random Forest training."""
        trainer = ModelTrainer()
        X_train, X_test, _ = trainer.prepare_data(
            sample_data["X_train"], sample_data["X_test"]
        )

        result = trainer.train_random_forest(
            X_train, sample_data["y_train"],
        )

        assert result is not None
        assert "model" in result
        assert result["model_type"] == "random_forest"
        assert trainer.models["random_forest"] is not None

    def test_train_all(self, sample_data):
        """Test training all models."""
        trainer = ModelTrainer()

        results = trainer.train_all(
            sample_data["X_train"],
            sample_data["y_train"],
            sample_data["X_test"],
            sample_data["y_test"],
        )

        assert len(results) == 3
        assert "xgboost" in results
        assert "lightgbm" in results
        assert "random_forest" in results
        assert len(trainer.scalers) == 1


class TestModelEvaluator:
    """Tests for ModelEvaluator."""

    def test_calculate_metrics(self):
        """Test metric calculation."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])

        metrics = ModelEvaluator.calculate_metrics(y_true, y_pred)

        assert "mse" in metrics
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert "mape" in metrics

        assert metrics["mae"] > 0
        assert metrics["rmse"] > 0
        assert -1 <= metrics["r2"] <= 1

    def test_evaluate_model(self, sample_data):
        """Test model evaluation."""
        trainer = ModelTrainer()
        results = trainer.train_all(
            sample_data["X_train"],
            sample_data["y_train"],
            sample_data["X_test"],
            sample_data["y_test"],
        )

        xgb_model = results["xgboost"]["model"]
        eval_result = ModelEvaluator.evaluate_model(
            xgb_model, sample_data["X_test"], sample_data["y_test"]
        )

        assert eval_result is not None
        assert "predictions" in eval_result
        assert "metrics" in eval_result
        assert "y_true" in eval_result
        assert len(eval_result["predictions"]) == len(sample_data["y_test"])

    def test_get_feature_importance(self, sample_data):
        """Test feature importance extraction."""
        trainer = ModelTrainer()
        results = trainer.train_all(
            sample_data["X_train"],
            sample_data["y_train"],
            sample_data["X_test"],
            sample_data["y_test"],
        )

        xgb_model = results["xgboost"]["model"]
        feature_names = [f"feature_{i}" for i in range(10)]

        importance = ModelEvaluator.get_feature_importance(
            xgb_model, feature_names, top_n=5
        )

        assert importance is not None
        assert "features" in importance
        assert "importances" in importance
        assert len(importance["features"]) <= 5
        assert len(importance["importances"]) == len(importance["features"])

    def test_compare_models(self, sample_data):
        """Test model comparison."""
        trainer = ModelTrainer()
        results = trainer.train_all(
            sample_data["X_train"],
            sample_data["y_train"],
            sample_data["X_test"],
            sample_data["y_test"],
        )

        # Evaluate all models
        eval_results = {}
        for name, result in results.items():
            eval_results[name] = ModelEvaluator.evaluate_model(
                result["model"], sample_data["X_test"], sample_data["y_test"]
            )

        comparison = ModelEvaluator.compare_models(eval_results)

        assert "comparison" in comparison
        assert "best_model" in comparison
        assert "best_metrics" in comparison
        assert comparison["best_model"] in ["xgboost", "lightgbm", "random_forest"]


class TestHyperparameterTuner:
    """Tests for HyperparameterTuner."""

    def test_tuner_init(self):
        """Test tuner initialization."""
        tuner = HyperparameterTuner(n_trials=10, n_jobs=1)
        assert tuner.n_trials == 10
        assert tuner.n_jobs == 1

    def test_optimize_xgboost(self, sample_data):
        """Test XGBoost optimization."""
        tuner = HyperparameterTuner(n_trials=3, n_jobs=1)
        result = tuner.optimize_xgboost(
            sample_data["X_train"], sample_data["y_train"], cv=2
        )

        assert result is not None
        assert "best_params" in result
        assert "best_score" in result
        assert "n_trials" in result
        assert result["n_trials"] <= 3

    def test_optimize_lightgbm(self, sample_data):
        """Test LightGBM optimization."""
        tuner = HyperparameterTuner(n_trials=3, n_jobs=1)
        result = tuner.optimize_lightgbm(
            sample_data["X_train"], sample_data["y_train"], cv=2
        )

        assert result is not None
        assert "best_params" in result
        assert "best_score" in result
        assert result["best_score"] is not None

    def test_optimize_random_forest(self, sample_data):
        """Test Random Forest optimization."""
        tuner = HyperparameterTuner(n_trials=3, n_jobs=1)
        result = tuner.optimize_random_forest(
            sample_data["X_train"], sample_data["y_train"], cv=2
        )

        assert result is not None
        assert "best_params" in result
        assert "best_score" in result


class TestExperimentTracker:
    """Tests for ExperimentTracker."""

    def test_tracker_init(self):
        """Test tracker initialization."""
        tracker = ExperimentTracker(experiment_name="test-exp")
        assert tracker.experiment_name == "test-exp"

    def test_log_params(self):
        """Test parameter logging."""
        tracker = ExperimentTracker(experiment_name="test-exp-params")
        tracker.start_run("test-run-params")

        params = {
            "max_depth": 7,
            "learning_rate": 0.1,
            "n_estimators": 100,
        }
        tracker.log_params(params)

        tracker.end_run()

    def test_log_metrics(self):
        """Test metrics logging."""
        tracker = ExperimentTracker(experiment_name="test-exp-metrics")
        tracker.start_run("test-run-metrics")

        metrics = {
            "mse": 0.125,
            "mae": 0.234,
            "rmse": 0.353,
            "r2": 0.89,
        }
        tracker.log_metrics(metrics)

        tracker.end_run()

    def test_run_lifecycle(self):
        """Test full run lifecycle."""
        tracker = ExperimentTracker(experiment_name="test-exp-lifecycle")

        # Start run
        run_id = tracker.start_run("test-lifecycle", tags={"phase": "phase6"})
        assert run_id is not None

        # Log data
        tracker.log_params({"test_param": 42})
        tracker.log_metrics({"test_metric": 0.95})

        # End run
        tracker.end_run(status="FINISHED")
