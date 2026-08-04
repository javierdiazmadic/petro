"""Hyperparameter optimization using Optuna."""

from typing import Callable, Dict, Optional

import optuna
from optuna.samplers import TPESampler
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

from petro.core import get_logger

logger = get_logger(__name__)


class HyperparameterTuner:
    """Optimizes hyperparameters using Optuna."""

    def __init__(self, n_trials: int = 50, n_jobs: int = -1):
        """Initialize tuner.

        Args:
            n_trials: Number of optimization trials
            n_jobs: Number of parallel jobs
        """
        self.n_trials = n_trials
        self.n_jobs = n_jobs

    def optimize_xgboost(
        self, X_train, y_train, cv: int = 5
    ) -> Dict:
        """Optimize XGBoost hyperparameters.

        Args:
            X_train: Training features
            y_train: Training target
            cv: Cross-validation folds

        Returns:
            Dictionary with best params and best score
        """

        def objective(trial):
            params = {
                "objective": "reg:squarederror",
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "learning_rate": trial.suggest_float("learning_rate", 0.001, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
            }

            model = xgb.XGBRegressor(**params, random_state=42, n_jobs=self.n_jobs)
            score = cross_val_score(model, X_train, y_train, cv=cv, scoring="r2").mean()
            return score

        try:
            sampler = TPESampler(seed=42)
            study = optuna.create_study(sampler=sampler, direction="maximize")
            study.optimize(objective, n_trials=self.n_trials, show_progress_bar=False)

            best_trial = study.best_trial

            logger.info(
                f"XGBoost optimization completed. Best R2: {best_trial.value:.4f}"
            )

            return {
                "best_params": best_trial.params,
                "best_score": best_trial.value,
                "n_trials": len(study.trials),
            }

        except Exception as e:
            logger.error(f"Error optimizing XGBoost: {e}")
            return None

    def optimize_lightgbm(
        self, X_train, y_train, cv: int = 5
    ) -> Dict:
        """Optimize LightGBM hyperparameters.

        Args:
            X_train: Training features
            y_train: Training target
            cv: Cross-validation folds

        Returns:
            Dictionary with best params and best score
        """

        def objective(trial):
            params = {
                "objective": "regression",
                "metric": "mse",
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "num_leaves": trial.suggest_int("num_leaves", 20, 100),
                "learning_rate": trial.suggest_float("learning_rate", 0.001, 0.3, log=True),
                "feature_fraction": trial.suggest_float("feature_fraction", 0.5, 1.0),
                "bagging_fraction": trial.suggest_float("bagging_fraction", 0.5, 1.0),
                "num_threads": self.n_jobs,
            }

            model = lgb.LGBMRegressor(**params, random_state=42)
            score = cross_val_score(model, X_train, y_train, cv=cv, scoring="r2").mean()
            return score

        try:
            sampler = TPESampler(seed=42)
            study = optuna.create_study(sampler=sampler, direction="maximize")
            study.optimize(objective, n_trials=self.n_trials, show_progress_bar=False)

            best_trial = study.best_trial

            logger.info(
                f"LightGBM optimization completed. Best R2: {best_trial.value:.4f}"
            )

            return {
                "best_params": best_trial.params,
                "best_score": best_trial.value,
                "n_trials": len(study.trials),
            }

        except Exception as e:
            logger.error(f"Error optimizing LightGBM: {e}")
            return None

    def optimize_random_forest(
        self, X_train, y_train, cv: int = 5
    ) -> Dict:
        """Optimize Random Forest hyperparameters.

        Args:
            X_train: Training features
            y_train: Training target
            cv: Cross-validation folds

        Returns:
            Dictionary with best params and best score
        """

        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 500),
                "max_depth": trial.suggest_int("max_depth", 5, 30),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
                "random_state": 42,
                "n_jobs": self.n_jobs,
            }

            model = RandomForestRegressor(**params)
            score = cross_val_score(model, X_train, y_train, cv=cv, scoring="r2").mean()
            return score

        try:
            sampler = TPESampler(seed=42)
            study = optuna.create_study(sampler=sampler, direction="maximize")
            study.optimize(objective, n_trials=self.n_trials, show_progress_bar=False)

            best_trial = study.best_trial

            logger.info(
                f"Random Forest optimization completed. Best R2: {best_trial.value:.4f}"
            )

            return {
                "best_params": best_trial.params,
                "best_score": best_trial.value,
                "n_trials": len(study.trials),
            }

        except Exception as e:
            logger.error(f"Error optimizing Random Forest: {e}")
            return None
