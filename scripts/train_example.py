#!/usr/bin/env python3
"""Example script showing complete PHASE 6 training pipeline."""

import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from petro.ml.training import (
    ModelTrainer,
    ModelEvaluator,
    HyperparameterTuner,
    ExperimentTracker,
)
from petro.core import get_logger

logger = get_logger(__name__)


def generate_sample_data(n_samples: int = 200, n_features: int = 15):
    """Generate synthetic training data."""
    np.random.seed(42)

    X = np.random.randn(n_samples, n_features)
    # Create target with some correlation to features
    y = 2.0 * X[:, 0] - 1.5 * X[:, 1] + 0.5 * X[:, 2] + np.random.randn(n_samples) * 0.5

    # Split
    split_idx = int(0.8 * n_samples)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    return X_train, X_test, y_train, y_test


def main():
    """Run complete training pipeline."""
    logger.info("Starting PHASE 6 training pipeline example")

    # 1. Generate sample data
    logger.info("Generating sample data...")
    X_train, X_test, y_train, y_test = generate_sample_data()
    logger.info(f"Training set: {X_train.shape}, Test set: {X_test.shape}")

    # 2. Initialize experiment tracking
    logger.info("Initializing MLflow experiment...")
    tracker = ExperimentTracker(experiment_name="petro-fuel-prediction-demo")

    feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]

    # 3. Train each model type
    model_configs = ["xgboost", "lightgbm", "random_forest"]

    results = {}

    for model_type in model_configs:
        logger.info(f"\n{'='*60}")
        logger.info(f"Training {model_type.upper()}")
        logger.info(f"{'='*60}")

        # Start tracking
        run_name = f"{model_type}-optimized-demo"
        tracker.start_run(run_name, tags={"type": model_type, "phase": "phase6"})

        try:
            # Step 1: Optimize hyperparameters
            logger.info(f"Optimizing hyperparameters (3 trials for demo)...")
            tuner = HyperparameterTuner(n_trials=3, n_jobs=-1)

            if model_type == "xgboost":
                tuner_result = tuner.optimize_xgboost(X_train, y_train, cv=3)
            elif model_type == "lightgbm":
                tuner_result = tuner.optimize_lightgbm(X_train, y_train, cv=3)
            else:
                tuner_result = tuner.optimize_random_forest(X_train, y_train, cv=3)

            best_params = tuner_result["best_params"]
            best_cv_score = tuner_result["best_score"]

            logger.info(f"Best CV R²: {best_cv_score:.4f}")
            logger.info(f"Best params: {best_params}")

            tracker.log_params(best_params)
            tracker.log_metrics({"cv_r2": best_cv_score})

            # Step 2: Train with best params
            logger.info("Training model with best hyperparameters...")
            trainer = ModelTrainer()

            if model_type == "xgboost":
                train_result = trainer.train_xgboost(
                    X_train, y_train, X_test, y_test, best_params
                )
            elif model_type == "lightgbm":
                train_result = trainer.train_lightgbm(
                    X_train, y_train, X_test, y_test, best_params
                )
            else:
                train_result = trainer.train_random_forest(X_train, y_train, best_params)

            model = train_result["model"]
            logger.info(f"Model trained successfully")

            # Step 3: Evaluate
            logger.info("Evaluating model...")
            evaluator = ModelEvaluator()
            eval_result = evaluator.evaluate_model(model, X_test, y_test)

            metrics = eval_result["metrics"]
            logger.info(f"Evaluation metrics:")
            logger.info(f"  RMSE: {metrics['rmse']:.6f}")
            logger.info(f"  MAE:  {metrics['mae']:.6f}")
            logger.info(f"  R²:   {metrics['r2']:.6f}")
            logger.info(f"  MAPE: {metrics['mape']:.3f}%")

            tracker.log_metrics(metrics)

            # Step 4: Feature importance
            logger.info("Extracting feature importance...")
            importance = evaluator.get_feature_importance(model, feature_names, top_n=5)

            if importance:
                logger.info("Top 5 features:")
                for fname, imp in zip(importance["features"], importance["importances"]):
                    logger.info(f"  {fname}: {imp:.4f}")

                tracker.log_feature_importance(
                    importance["features"],
                    importance["importances"],
                    model_name=model_type,
                )

            # Step 5: Log model
            logger.info("Logging model to MLflow...")
            tracker.log_model(model, f"{model_type}-v1", model_type, metrics=metrics)

            # Store result
            results[model_type] = {
                "model": model,
                "metrics": metrics,
                "importance": importance,
            }

            tracker.end_run(status="FINISHED")
            logger.info(f"✓ {model_type} completed")

        except Exception as e:
            logger.error(f"Error training {model_type}: {e}", exc_info=True)
            tracker.end_run(status="FAILED")

    # 4. Compare all models
    logger.info(f"\n{'='*60}")
    logger.info("MODEL COMPARISON")
    logger.info(f"{'='*60}")

    eval_results = {}
    for model_type, result in results.items():
        eval_results[model_type] = {"metrics": result["metrics"]}

    comparison = ModelEvaluator.compare_models(eval_results)

    logger.info("All models RMSE comparison:")
    for model_type, metrics in comparison["comparison"].items():
        logger.info(f"  {model_type}: RMSE={metrics['rmse']:.6f}, R²={metrics['r2']:.4f}")

    logger.info(f"\nBest model: {comparison['best_model']}")
    logger.info(f"Best RMSE: {comparison['best_metrics']['rmse']:.6f}")

    # 5. Show MLflow tracking
    logger.info(f"\n{'='*60}")
    logger.info("MLFLOW TRACKING")
    logger.info(f"{'='*60}")

    best_run = ExperimentTracker.get_best_run(
        "petro-fuel-prediction-demo", metric="rmse", mode="min"
    )
    if best_run:
        logger.info(f"Best run ID: {best_run['run_id']}")
        logger.info(f"Best metrics: {best_run['metrics']}")

    all_runs = ExperimentTracker.compare_models("petro-fuel-prediction-demo")
    logger.info(f"\nTotal runs tracked: {len(all_runs['runs'])}")

    logger.info("\n✓ PHASE 6 training pipeline completed successfully!")
    logger.info("View MLflow UI with: mlflow ui")


if __name__ == "__main__":
    main()
