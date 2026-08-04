"""Model training for comparing multiple algorithms."""

from typing import Dict, Optional, Tuple

import lightgbm as lgb
import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from petro.core import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """Trains and compares multiple regression models."""

    def __init__(self):
        """Initialize trainer."""
        self.models = {}
        self.scalers = {}

    def prepare_data(
        self, X_train: np.ndarray, X_test: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, StandardScaler]:
        """Normalize features using StandardScaler.

        Args:
            X_train: Training features
            X_test: Test features

        Returns:
            Tuple of (normalized X_train, normalized X_test, scaler)
        """
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, scaler

    def train_xgboost(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        params: Optional[Dict] = None,
    ) -> Dict:
        """Train XGBoost model.

        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            params: Hyperparameters

        Returns:
            Dictionary with model and metrics
        """
        if params is None:
            params = {
                "objective": "reg:squarederror",
                "max_depth": 7,
                "learning_rate": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "random_state": 42,
                "n_jobs": -1,
            }

        try:
            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

            self.models["xgboost"] = model
            logger.info("XGBoost model trained")

            return {
                "model": model,
                "model_type": "xgboost",
                "params": params,
            }

        except Exception as e:
            logger.error(f"Error training XGBoost: {e}")
            return None

    def train_lightgbm(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        params: Optional[Dict] = None,
    ) -> Dict:
        """Train LightGBM model.

        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            params: Hyperparameters

        Returns:
            Dictionary with model and metrics
        """
        if params is None:
            params = {
                "objective": "regression",
                "metric": "mse",
                "max_depth": 7,
                "num_leaves": 31,
                "learning_rate": 0.1,
                "feature_fraction": 0.8,
                "bagging_fraction": 0.8,
                "num_threads": -1,
            }

        try:
            train_data = lgb.Dataset(X_train, label=y_train)
            test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

            model = lgb.train(
                params,
                train_data,
                num_boost_round=100,
                valid_sets=[test_data],
                verbose_eval=False,
            )

            self.models["lightgbm"] = model
            logger.info("LightGBM model trained")

            return {
                "model": model,
                "model_type": "lightgbm",
                "params": params,
            }

        except Exception as e:
            logger.error(f"Error training LightGBM: {e}")
            return None

    def train_random_forest(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        params: Optional[Dict] = None,
    ) -> Dict:
        """Train Random Forest model.

        Args:
            X_train: Training features
            y_train: Training target
            params: Hyperparameters

        Returns:
            Dictionary with model and metrics
        """
        if params is None:
            params = {
                "n_estimators": 100,
                "max_depth": 15,
                "min_samples_split": 5,
                "min_samples_leaf": 2,
                "random_state": 42,
                "n_jobs": -1,
            }

        try:
            model = RandomForestRegressor(**params)
            model.fit(X_train, y_train)

            self.models["random_forest"] = model
            logger.info("Random Forest model trained")

            return {
                "model": model,
                "model_type": "random_forest",
                "params": params,
            }

        except Exception as e:
            logger.error(f"Error training Random Forest: {e}")
            return None

    def train_all(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> Dict[str, Dict]:
        """Train all models.

        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target

        Returns:
            Dictionary with results for all models
        """
        # Normalize data
        X_train_scaled, X_test_scaled, scaler = self.prepare_data(X_train, X_test)
        self.scalers["default"] = scaler

        results = {}

        # Train XGBoost
        xgb_result = self.train_xgboost(X_train_scaled, y_train, X_test_scaled, y_test)
        if xgb_result:
            results["xgboost"] = xgb_result

        # Train LightGBM
        lgb_result = self.train_lightgbm(X_train_scaled, y_train, X_test_scaled, y_test)
        if lgb_result:
            results["lightgbm"] = lgb_result

        # Train Random Forest
        rf_result = self.train_random_forest(X_train_scaled, y_train)
        if rf_result:
            results["random_forest"] = rf_result

        logger.info(f"Training completed for {len(results)} models")
        return results
