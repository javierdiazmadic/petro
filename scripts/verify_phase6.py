#!/usr/bin/env python3
"""Verify PHASE 6 structure and imports."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def verify_files():
    """Verify all PHASE 6 files exist."""
    base_path = Path(__file__).parent.parent

    files_to_check = [
        "src/petro/ml/training/trainer.py",
        "src/petro/ml/training/evaluator.py",
        "src/petro/ml/training/hyperparameter_tuner.py",
        "src/petro/ml/training/experiment.py",
        "src/petro/ml/training/__init__.py",
        "tests/unit/test_ml_training.py",
        "docs/06-model-training.md",
        "scripts/train_example.py",
    ]

    print("Checking PHASE 6 files...")
    all_exist = True

    for filepath in files_to_check:
        full_path = base_path / filepath
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {filepath}")
        if not exists:
            all_exist = False

    return all_exist

def verify_imports():
    """Verify all imports work."""
    print("\nVerifying imports...")

    try:
        from petro.ml.training import (
            ModelTrainer,
            ModelEvaluator,
            HyperparameterTuner,
            ExperimentTracker,
        )
        print("  ✓ All training components importable")
        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_classes():
    """Verify all classes are properly defined."""
    print("\nVerifying classes...")

    try:
        from petro.ml.training import (
            ModelTrainer,
            ModelEvaluator,
            HyperparameterTuner,
            ExperimentTracker,
        )

        # Check ModelTrainer
        trainer = ModelTrainer()
        assert hasattr(trainer, 'prepare_data')
        assert hasattr(trainer, 'train_xgboost')
        assert hasattr(trainer, 'train_lightgbm')
        assert hasattr(trainer, 'train_random_forest')
        assert hasattr(trainer, 'train_all')
        print("  ✓ ModelTrainer: all methods present")

        # Check ModelEvaluator (static methods)
        assert hasattr(ModelEvaluator, 'calculate_metrics')
        assert hasattr(ModelEvaluator, 'evaluate_model')
        assert hasattr(ModelEvaluator, 'get_feature_importance')
        assert hasattr(ModelEvaluator, 'compare_models')
        print("  ✓ ModelEvaluator: all methods present")

        # Check HyperparameterTuner
        tuner = HyperparameterTuner()
        assert hasattr(tuner, 'optimize_xgboost')
        assert hasattr(tuner, 'optimize_lightgbm')
        assert hasattr(tuner, 'optimize_random_forest')
        print("  ✓ HyperparameterTuner: all methods present")

        # Check ExperimentTracker
        tracker = ExperimentTracker()
        assert hasattr(tracker, 'start_run')
        assert hasattr(tracker, 'log_params')
        assert hasattr(tracker, 'log_metrics')
        assert hasattr(tracker, 'log_model')
        assert hasattr(tracker, 'end_run')
        print("  ✓ ExperimentTracker: all methods present")

        return True
    except Exception as e:
        print(f"  ✗ Class verification error: {e}")
        return False

def main():
    """Run all verifications."""
    print("="*60)
    print("PHASE 6 VERIFICATION")
    print("="*60)

    files_ok = verify_files()
    imports_ok = verify_imports()
    classes_ok = verify_classes()

    print("\n" + "="*60)
    if files_ok and imports_ok and classes_ok:
        print("✓ PHASE 6 VERIFICATION PASSED")
        print("="*60)
        return 0
    else:
        print("✗ PHASE 6 VERIFICATION FAILED")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
