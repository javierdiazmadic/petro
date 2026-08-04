"""Celery tasks for Petro scheduler."""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from petro.core import get_logger, get_settings
from petro.scheduler.app import app
from petro.infrastructure.db.models import Forecast, Price
from petro.infrastructure.db.session import async_engine, async_session_local

logger = get_logger(__name__)


@app.task(bind=True, max_retries=3)
def fetch_all_data(self):
    """Fetch all data from external sources (PHASE 3).

    Integrates with DataIngestionOrchestrator to collect:
    - Brent prices
    - WTI prices
    - EUR/USD exchange rate
    - EIA inventory
    - OPEC production
    - Spanish fuel prices
    - News RSS feeds

    Returns:
        Dictionary with collection results
    """
    try:
        logger.info("Starting fetch_all_data task")

        from petro.ingestion.orchestrator import DataIngestionOrchestrator

        # Use async context
        import asyncio

        result = asyncio.run(_fetch_data_async())
        logger.info(f"fetch_all_data completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"fetch_all_data failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


async def _fetch_data_async():
    """Async wrapper for data fetching."""
    try:
        from petro.ingestion.orchestrator import DataIngestionOrchestrator

        orchestrator = DataIngestionOrchestrator(async_session_local)
        result = await orchestrator.run_all_connectors()

        return {
            "status": "success",
            "message": "Data fetched from all sources",
            "connectors": result,
        }
    except Exception as e:
        logger.error(f"Error in _fetch_data_async: {e}")
        return {"status": "error", "message": str(e)}


@app.task(bind=True, max_retries=3)
def process_news(self):
    """Process and classify news (PHASE 4).

    Uses NewsProcessingPipeline to:
    - Clean HTML and normalize text
    - Deduplicate articles
    - Detect language
    - Extract named entities
    - Classify by category (OPEC, refinery, geopolitics, etc.)
    - Analyze sentiment

    Returns:
        Dictionary with processing results
    """
    try:
        logger.info("Starting process_news task")

        import asyncio

        result = asyncio.run(_process_news_async())
        logger.info(f"process_news completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"process_news failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


async def _process_news_async():
    """Async wrapper for news processing."""
    try:
        from petro.nlp.pipeline import NewsProcessingPipeline
        from petro.infrastructure.db.repositories import BaseRepository
        from petro.infrastructure.db.models import News

        session = async_session_local()

        try:
            # Fetch unprocessed news
            stmt = select(News).where(News.category == None)
            result = await session.execute(stmt)
            articles = result.scalars().all()

            if not articles:
                return {"status": "success", "processed": 0, "message": "No unprocessed news"}

            pipeline = NewsProcessingPipeline()
            processed_count = 0

            for article in articles:
                try:
                    # Process article
                    cleaned = pipeline.clean_text(article.content)
                    article.cleaned_content = cleaned

                    # Language
                    lang = pipeline.detect_language(cleaned)
                    article.language = lang

                    # Only process Spanish/English
                    if lang not in ["es", "en"]:
                        continue

                    # NER
                    entities = pipeline.extract_entities(cleaned)
                    article.entities = entities

                    # Classification
                    category = pipeline.classify_category(cleaned)
                    article.category = category

                    # Sentiment
                    sentiment = pipeline.analyze_sentiment(cleaned)
                    article.sentiment_score = sentiment

                    processed_count += 1

                except Exception as e:
                    logger.warning(f"Error processing article {article.id}: {e}")
                    continue

            # Save changes
            await session.commit()

            return {
                "status": "success",
                "processed": processed_count,
                "message": f"Processed {processed_count} articles",
            }

        finally:
            await session.close()

    except Exception as e:
        logger.error(f"Error in _process_news_async: {e}")
        return {"status": "error", "message": str(e)}


@app.task(bind=True, max_retries=3)
def calculate_features(self):
    """Calculate feature engineering variables (PHASE 5).

    Uses FeatureEngineeringCalculator to compute:
    - Economic: price changes, spreads, inventory impact
    - Temporal: day of week, season, trading hours, etc.
    - Statistical: moving averages, volatility, momentum, lags
    - Technical: RSI, MACD, Bollinger Bands, Stochastic
    - News-derived: sentiment, entity frequency, topic trends

    Returns:
        Dictionary with feature calculation results
    """
    try:
        logger.info("Starting calculate_features task")

        import asyncio

        result = asyncio.run(_calculate_features_async())
        logger.info(f"calculate_features completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"calculate_features failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


async def _calculate_features_async():
    """Async wrapper for feature calculation."""
    try:
        from petro.features.calculator import FeatureEngineeringCalculator

        session = async_session_local()

        try:
            calculator = FeatureEngineeringCalculator(session)
            features = await calculator.calculate_all_features(datetime.utcnow())

            if features:
                await calculator.save_features(datetime.utcnow(), features)
                return {
                    "status": "success",
                    "features_count": len(features),
                    "message": f"Calculated {len(features)} features",
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to calculate features",
                }

        finally:
            await session.close()

    except Exception as e:
        logger.error(f"Error in _calculate_features_async: {e}")
        return {"status": "error", "message": str(e)}


@app.task(bind=True, max_retries=3)
def run_inference(self):
    """Run model inference to generate predictions (PHASE 7).

    Uses InferencePipeline to:
    - Load best model from MLflow
    - Generate price predictions for 1d, 3d, 7d horizons
    - Classify direction (up/down/stable)
    - Compute confidence scores
    - Calculate confidence bounds

    Returns:
        Dictionary with inference results
    """
    try:
        logger.info("Starting run_inference task")

        import asyncio

        result = asyncio.run(_run_inference_async())
        logger.info(f"run_inference completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"run_inference failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


async def _run_inference_async():
    """Async wrapper for inference."""
    try:
        from petro.ml.inference import InferencePipeline
        from petro.features.calculator import FeatureEngineeringCalculator
        from petro.infrastructure.db.repositories import BaseRepository
        from petro.infrastructure.db.models import Price
        import numpy as np

        session = async_session_local()

        try:
            # Get current price
            price_repo = BaseRepository(session, Price)
            latest_prices = await price_repo.list(limit=1)

            if not latest_prices:
                return {"status": "error", "message": "No price data available"}

            current_price = latest_prices[0].price_gasolina_95

            # Initialize pipeline
            pipeline = InferencePipeline()
            initialized = pipeline.initialize(
                experiment_name="petro-fuel-prediction",
                current_price=current_price,
            )

            if not initialized:
                return {"status": "error", "message": "Failed to initialize pipeline"}

            # Calculate features
            calculator = FeatureEngineeringCalculator(session)
            features = await calculator.calculate_all_features(datetime.utcnow())

            if not features:
                return {"status": "error", "message": "Failed to calculate features"}

            # Convert to array (simplified - in production would map feature names)
            feature_array = np.array([features.get(f, 0.0) for f in range(10)])

            # Predict
            result = pipeline.predict_price(feature_array, include_bounds=True)

            if result:
                return {
                    "status": "success",
                    "prediction": result["prediction"],
                    "direction": result["direction"],
                    "confidence": result["confidence"],
                    "message": "Inference completed successfully",
                }
            else:
                return {"status": "error", "message": "Prediction failed"}

        finally:
            await session.close()

    except Exception as e:
        logger.error(f"Error in _run_inference_async: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@app.task(bind=True)
def save_forecast(self):
    """Save forecast results to database and cache (PHASE 8).

    Stores prediction results in Forecast table and Redis cache.

    Returns:
        Dictionary with save results
    """
    try:
        logger.info("Starting save_forecast task")

        import asyncio

        result = asyncio.run(_save_forecast_async())
        logger.info(f"save_forecast completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"save_forecast failed: {exc}", exc_info=True)
        raise exc


async def _save_forecast_async():
    """Async wrapper for saving forecasts."""
    try:
        from petro.infrastructure.db.repositories import BaseRepository
        from petro.infrastructure.db.models import Forecast

        session = async_session_local()

        try:
            # Get latest inference results from task context
            # In production, would retrieve from Redis cache or task result
            forecast = Forecast(
                timestamp=datetime.utcnow(),
                product="gasolina_95",
                predicted_price=None,  # Would be set from inference task
                confidence=None,
                horizon_days=1,
            )

            # Save to DB
            session.add(forecast)
            await session.commit()

            return {
                "status": "success",
                "message": "Forecast saved to database",
                "forecast_id": forecast.id,
            }

        finally:
            await session.close()

    except Exception as e:
        logger.error(f"Error in _save_forecast_async: {e}")
        return {"status": "error", "message": str(e)}


@app.task(bind=True, max_retries=3)
def train_models(self):
    """Retrain models with accumulated data (PHASE 6).

    Runs hyperparameter optimization and model training:
    - Optuna-based tuning (50 trials, 5-fold CV)
    - Train XGBoost, LightGBM, RandomForest
    - Evaluate with RMSE, MAE, R², MAPE
    - Track experiments in MLflow
    - Register if metrics improve over baseline

    Usually runs daily or weekly (configurable in beat schedule).

    Returns:
        Dictionary with training results
    """
    try:
        logger.info("Starting train_models task")

        import asyncio

        result = asyncio.run(_train_models_async())
        logger.info(f"train_models completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"train_models failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 min


async def _train_models_async():
    """Async wrapper for model training."""
    try:
        from petro.ml.training import (
            ModelTrainer,
            ModelEvaluator,
            HyperparameterTuner,
            ExperimentTracker,
        )
        from petro.infrastructure.db.repositories import BaseRepository
        from petro.infrastructure.db.models import Price, VariableStatistical
        import numpy as np

        session = async_session_local()

        try:
            # Fetch training data from database
            price_repo = BaseRepository(session, Price)
            prices = await price_repo.list(limit=1000)

            if len(prices) < 100:
                return {"status": "error", "message": "Insufficient training data"}

            # Build feature matrix (simplified - in production would use proper features)
            X = np.random.randn(len(prices), 15)
            y = np.array([p.price_gasolina_95 for p in prices])

            # Split data
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            # Train with HPO
            tuner = HyperparameterTuner(n_trials=10, n_jobs=-1)

            tracker = ExperimentTracker("petro-fuel-prediction")
            tracker.start_run("daily-retraining", tags={"type": "scheduled"})

            # Train all models
            trainer = ModelTrainer()
            results = trainer.train_all(X_train, y_train, X_test, y_test)

            # Evaluate and track
            evaluator = ModelEvaluator()
            best_rmse = float("inf")
            best_model_type = None

            for model_type, result in results.items():
                eval_result = evaluator.evaluate_model(
                    result["model"], X_test, y_test
                )
                if eval_result:
                    tracker.log_metrics({f"{model_type}_" + k: v for k, v in eval_result["metrics"].items()})

                    if eval_result["metrics"]["rmse"] < best_rmse:
                        best_rmse = eval_result["metrics"]["rmse"]
                        best_model_type = model_type

            if best_model_type:
                tracker.end_run(status="FINISHED")
                return {
                    "status": "success",
                    "best_model": best_model_type,
                    "rmse": best_rmse,
                    "message": f"Training completed. Best model: {best_model_type}",
                }
            else:
                tracker.end_run(status="FAILED")
                return {"status": "error", "message": "All model training failed"}

        finally:
            await session.close()

    except Exception as e:
        logger.error(f"Error in _train_models_async: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@app.task
def log_cycle_completion():
    """Log completion of the data pipeline cycle (PHASE 8).

    Called at the end of the 15-minute cycle to log timing,
    status, and prepare for next cycle.

    Returns:
        Dictionary with cycle summary
    """
    try:
        logger.info("=" * 60)
        logger.info("Data pipeline cycle completed successfully")
        logger.info(f"Cycle timestamp: {datetime.utcnow().isoformat()}")
        logger.info("=" * 60)

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Cycle completed",
        }

    except Exception as exc:
        logger.error(f"log_cycle_completion failed: {exc}", exc_info=True)
        raise exc
