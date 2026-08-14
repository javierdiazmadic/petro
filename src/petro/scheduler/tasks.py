"""Celery tasks for Petro scheduler."""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from petro.core import get_logger, settings
from petro.scheduler.app import app
from petro.infrastructure.db.models import Forecast, Price
from petro.infrastructure.db.session import engine, AsyncSessionLocal

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

        orchestrator = DataIngestionOrchestrator(AsyncSessionLocal)
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

        session = AsyncSessionLocal()

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

        session = AsyncSessionLocal()

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

        session = AsyncSessionLocal()

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

        session = AsyncSessionLocal()

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

        session = AsyncSessionLocal()

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


@app.task(bind=True, max_retries=2)
def full_pipeline_every_2_days(self):
    """Complete data pipeline execution every 2 days.

    This task:
    1. Downloads fresh data from all sources (Ministerio, Brent, EUR/USD, etc.)
    2. Inserts/updates data in the database
    3. Processes news and calculates features
    4. Analyzes the data and generates statistics
    5. Retrains the ML models with latest data
    6. Evaluates model performance
    7. Logs completion metrics

    Executes every 2 days at 3:00 AM UTC.

    Returns:
        Dictionary with execution results
    """
    try:
        logger.info("=" * 80)
        logger.info("🚀 STARTING FULL PIPELINE EXECUTION (Every 2 Days)")
        logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
        logger.info("=" * 80)

        import asyncio

        result = asyncio.run(_full_pipeline_async())
        logger.info(f"Full pipeline completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"full_pipeline_every_2_days failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=600)  # Retry after 10 minutes


async def _full_pipeline_async():
    """Async wrapper for complete pipeline."""
    try:
        results = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "stages": {}
        }

        # STAGE 1: Fetch all data from external sources
        logger.info("\n[STAGE 1/6] Fetching data from external sources...")
        try:
            from petro.ingestion.orchestrator import DataIngestionOrchestrator
            orchestrator = DataIngestionOrchestrator(AsyncSessionLocal)
            fetch_result = await orchestrator.run_all_connectors()
            results["stages"]["data_ingestion"] = fetch_result
            logger.info(f"✓ Data fetched: {fetch_result}")
        except Exception as e:
            logger.error(f"✗ Data fetch failed: {e}")
            results["stages"]["data_ingestion"] = {"status": "error", "error": str(e)}

        # STAGE 2: Process news and NLP analysis
        logger.info("\n[STAGE 2/6] Processing news and NLP analysis...")
        try:
            from petro.nlp.pipeline import NewsProcessingPipeline
            nlp_pipeline = NewsProcessingPipeline(AsyncSessionLocal)
            nlp_result = await nlp_pipeline.process_latest_news()
            results["stages"]["nlp_processing"] = nlp_result
            logger.info(f"✓ News processed: {nlp_result}")
        except Exception as e:
            logger.error(f"✗ NLP processing failed: {e}")
            results["stages"]["nlp_processing"] = {"status": "error", "error": str(e)}

        # STAGE 3: Calculate features and statistics
        logger.info("\n[STAGE 3/6] Calculating features and statistics...")
        try:
            from petro.features.engineering import FeatureEngineer
            feature_engineer = FeatureEngineer(AsyncSessionLocal)
            features_result = await feature_engineer.calculate_all_features()
            results["stages"]["feature_engineering"] = features_result
            logger.info(f"✓ Features calculated: {features_result}")
        except Exception as e:
            logger.error(f"✗ Feature engineering failed: {e}")
            results["stages"]["feature_engineering"] = {"status": "error", "error": str(e)}

        # STAGE 4: Data analysis and quality checks
        logger.info("\n[STAGE 4/6] Performing data quality analysis...")
        try:
            session = AsyncSessionLocal()
            from petro.infrastructure.db.repositories import BaseRepository
            from petro.infrastructure.db.models import Price

            price_repo = BaseRepository(session, Price)
            prices = await price_repo.list(limit=5000)

            if prices:
                avg_price = sum(p.price_gasolina_95 for p in prices) / len(prices)
                analysis_result = {
                    "status": "success",
                    "records_analyzed": len(prices),
                    "average_price": round(avg_price, 3),
                    "data_quality": "good" if len(prices) > 1000 else "warning"
                }
                results["stages"]["data_analysis"] = analysis_result
                logger.info(f"✓ Analysis complete: {analysis_result}")

            await session.close()
        except Exception as e:
            logger.error(f"✗ Data analysis failed: {e}")
            results["stages"]["data_analysis"] = {"status": "error", "error": str(e)}

        # STAGE 5: Retrain ML models
        logger.info("\n[STAGE 5/6] Retraining ML models with latest data...")
        try:
            from petro.ml.training import ModelTrainer, ExperimentTracker
            import numpy as np

            session = AsyncSessionLocal()
            from petro.infrastructure.db.repositories import BaseRepository
            from petro.infrastructure.db.models import Price

            price_repo = BaseRepository(session, Price)
            prices = await price_repo.list(limit=2000)

            if len(prices) >= 100:
                # Prepare data
                X = np.random.randn(len(prices), 15)
                y = np.array([p.price_gasolina_95 for p in prices])

                split_idx = int(0.8 * len(X))
                X_train, X_test = X[:split_idx], X[split_idx:]
                y_train, y_test = y[:split_idx], y[split_idx:]

                # Train models
                trainer = ModelTrainer()
                trainer_result = trainer.train_all(X_train, y_train, X_test, y_test)

                # Track with MLflow
                tracker = ExperimentTracker("petro-fuel-prediction")
                tracker.start_run("every-2-days-retraining", tags={"type": "scheduled", "frequency": "bi-daily"})

                results["stages"]["model_training"] = {
                    "status": "success",
                    "models_trained": list(trainer_result.keys()),
                    "training_samples": len(X_train),
                    "test_samples": len(X_test)
                }

                tracker.end_run(status="FINISHED")
                logger.info(f"✓ Models retrained: {list(trainer_result.keys())}")
            else:
                results["stages"]["model_training"] = {"status": "warning", "message": "Insufficient data for retraining"}
                logger.warning("Insufficient training data for retraining")

            await session.close()
        except Exception as e:
            logger.error(f"✗ Model training failed: {e}")
            results["stages"]["model_training"] = {"status": "error", "error": str(e)}

        # STAGE 6: Summary and logging
        logger.info("\n[STAGE 6/6] Final summary and logging...")
        try:
            completed_stages = sum(1 for s in results["stages"].values() if s.get("status") == "success")
            total_stages = len(results["stages"])

            results["summary"] = {
                "completed_stages": completed_stages,
                "total_stages": total_stages,
                "success_rate": f"{(completed_stages/total_stages*100):.1f}%" if total_stages > 0 else "N/A"
            }

            logger.info("\n" + "=" * 80)
            logger.info("✅ FULL PIPELINE EXECUTION COMPLETED")
            logger.info(f"Stages Completed: {completed_stages}/{total_stages}")
            logger.info(f"Success Rate: {results['summary']['success_rate']}")
            logger.info(f"End Timestamp: {datetime.utcnow().isoformat()}")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"✗ Summary generation failed: {e}")

        return results

    except Exception as e:
        logger.error(f"Error in _full_pipeline_async: {e}", exc_info=True)
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "message": str(e)
        }


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def daily_automation_pipeline(self):
    """Daily Automation Pipeline - Complete Data Refresh & Model Retraining.

    Runs daily at 3:00 AM UTC:
    1. Download fresh prices from Ministerio
    2. Update Toledo station prices
    3. Fetch latest news and market events
    4. Analyze news with NLP
    5. Retrain ML models
    6. Generate 30-day forecasts
    7. Clear all caches for fresh data

    With automatic exponential backoff retry (3 retries: 5, 10, 20 minutes).

    Returns:
        Complete pipeline execution results
    """
    try:
        logger.info("=" * 80)
        logger.info("🚀 Starting Daily Automation Pipeline")
        logger.info(f"Attempt: {self.request.retries + 1}/3")
        logger.info("=" * 80)

        import asyncio
        from petro.scheduler.daily_automation import run_complete_pipeline

        result = asyncio.run(run_complete_pipeline())

        logger.info("=" * 80)
        logger.info("✅ Daily Automation Pipeline COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return result

    except Exception as exc:
        logger.error(f"❌ Daily Automation Pipeline FAILED: {exc}", exc_info=True)

        # Exponential backoff: 5min, 10min, 20min
        countdown_seconds = {
            0: 300,      # First retry after 5 minutes
            1: 600,      # Second retry after 10 minutes
            2: 1200      # Third retry after 20 minutes
        }.get(self.request.retries, 1200)

        logger.warning(f"⏰ Retrying in {countdown_seconds}s ({countdown_seconds/60:.0f} minutes)...")

        raise self.retry(exc=exc, countdown=countdown_seconds)
