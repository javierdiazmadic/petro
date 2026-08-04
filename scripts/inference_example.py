#!/usr/bin/env python3
"""Example script showing inference pipeline usage."""

import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sklearn.ensemble import RandomForestRegressor
from petro.ml.inference import InferencePipeline
from petro.core import get_logger

logger = get_logger(__name__)


def create_dummy_model():
    """Create a dummy trained model for demonstration."""
    logger.info("Creating dummy model for demonstration...")

    np.random.seed(42)
    X = np.random.randn(200, 10)
    y = (
        2.0 * X[:, 0]
        - 1.5 * X[:, 1]
        + 0.5 * X[:, 2]
        + np.random.randn(200) * 0.2
    )

    model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10)
    model.fit(X, y)

    logger.info("Model trained successfully")
    return model


def main():
    """Run inference example."""
    logger.info("Starting PHASE 7 inference pipeline example")

    print("\n" + "=" * 60)
    print("PHASE 7: Inference Pipeline Example")
    print("=" * 60)

    # 1. Create dummy model
    model = create_dummy_model()

    # 2. Initialize pipeline
    logger.info("Initializing inference pipeline...")
    pipeline = InferencePipeline()

    # Manually set components (simulating loading from MLflow)
    from petro.ml.inference import PricePredictor, DirectionClassifier

    pipeline.predictor = PricePredictor(model)
    pipeline.classifier = DirectionClassifier(current_price=1.50)
    pipeline.last_price = 1.50

    if not pipeline.is_ready():
        logger.error("Pipeline not ready")
        return 1

    print("\n✓ Pipeline initialized")
    print(f"  Current price: {pipeline.last_price:.4f}")

    # 3. Single prediction
    print("\n" + "-" * 60)
    print("Single Prediction (1-day horizon)")
    print("-" * 60)

    features_1d = np.random.randn(10)
    result_1d = pipeline.predict_price(features_1d, include_bounds=True)

    if result_1d:
        print(f"Predicted price:     {result_1d['prediction']:.4f}€/L")
        print(f"Current price:       {result_1d['current_price']:.4f}€/L")
        print(f"Change:              {result_1d['change']:+.4f}€/L ({result_1d['change_pct']:+.2f}%)")
        print(f"Direction:           {result_1d['direction_label']}")
        print(f"Confidence scores:")
        print(f"  ↑ UP:              {result_1d['confidence']['up']:.1%}")
        print(f"  → STABLE:          {result_1d['confidence']['stable']:.1%}")
        print(f"  ↓ DOWN:            {result_1d['confidence']['down']:.1%}")
        print(f"Confidence bounds:")
        print(f"  Lower:             {result_1d['bounds']['lower']:.4f}€/L")
        print(f"  Upper:             {result_1d['bounds']['upper']:.4f}€/L")

    # 4. Multi-horizon prediction
    print("\n" + "-" * 60)
    print("Multi-Horizon Prediction (1d, 3d, 7d)")
    print("-" * 60)

    features_3d = np.random.randn(10)
    features_7d = np.random.randn(10)

    results_multi = pipeline.predict_multiple(
        [features_1d, features_3d, features_7d],
        horizons=["1d", "3d", "7d"]
    )

    if results_multi:
        for horizon, result in results_multi.items():
            print(f"\n{horizon.upper()} Horizon:")
            print(f"  Prediction:        {result['prediction']:.4f}€/L")
            print(f"  Direction:         {result['direction'].upper()}")
            print(f"  Confidence:        {max(result['confidence'].values()):.1%}")

    # 5. Update reference price
    print("\n" + "-" * 60)
    print("Update Reference Price & Re-predict")
    print("-" * 60)

    new_price = 1.52
    print(f"\nUpdating reference price from {pipeline.last_price:.4f} to {new_price:.4f}")
    pipeline.update_reference_price(new_price)

    result_updated = pipeline.predict_price(features_1d, include_bounds=True)

    if result_updated:
        print(f"\nRe-prediction with new reference:")
        print(f"Predicted price:     {result_updated['prediction']:.4f}€/L")
        print(f"Current price:       {result_updated['current_price']:.4f}€/L")
        print(f"Change:              {result_updated['change']:+.4f}€/L ({result_updated['change_pct']:+.2f}%)")
        print(f"Direction:           {result_updated['direction_label']}")

    # 6. Model info
    print("\n" + "-" * 60)
    print("Model Information")
    print("-" * 60)

    print(f"\nModel type:          RandomForest")
    print(f"Number of features:  {model.n_features_in_}")
    print(f"Number of trees:     {model.n_estimators}")
    print(f"Max depth:           {model.max_depth}")

    print("\n" + "=" * 60)
    print("✓ PHASE 7 inference example completed successfully!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
