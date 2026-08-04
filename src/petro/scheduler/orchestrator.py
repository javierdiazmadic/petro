"""PHASE 8 Pipeline Orchestrator - Orchestrates complete 15-minute cycle."""

from typing import Dict, Any, Optional
from datetime import datetime

from petro.core import get_logger

logger = get_logger(__name__)


class PipelineOrchestrator:
    """Orchestrates the complete 15-minute data pipeline cycle.

    Coordinates:
    1. Data Ingestion (PHASE 3) — fetch_all_data
    2. NLP Processing (PHASE 4) — process_news
    3. Feature Engineering (PHASE 5) — calculate_features
    4. Inference (PHASE 7) — run_inference
    5. Forecast Saving — save_forecast
    6. Logging — log_cycle_completion

    Also handles periodic retraining (daily):
    - Model Training (PHASE 6) — train_models
    """

    def __init__(self):
        """Initialize orchestrator."""
        self.cycle_start = None
        self.cycle_results = {}
        self.phase_durations = {}

    def orchestrate_full_cycle(self) -> Dict[str, Any]:
        """Execute the complete pipeline cycle.

        Returns:
            Dictionary with cycle results and timing
        """
        self.cycle_start = datetime.utcnow()
        logger.info("=" * 70)
        logger.info("PETRO PIPELINE CYCLE STARTED")
        logger.info(f"Start time: {self.cycle_start.isoformat()}")
        logger.info("=" * 70)

        try:
            # Phase 1: Data Ingestion
            result_ingestion = self._execute_phase(
                "Ingestion",
                self._phase_ingestion,
            )
            self.cycle_results["ingestion"] = result_ingestion

            # Phase 2: News Processing
            result_nlp = self._execute_phase(
                "NLP",
                self._phase_nlp,
            )
            self.cycle_results["nlp"] = result_nlp

            # Phase 3: Feature Engineering
            result_features = self._execute_phase(
                "Features",
                self._phase_features,
            )
            self.cycle_results["features"] = result_features

            # Phase 4: Inference
            result_inference = self._execute_phase(
                "Inference",
                self._phase_inference,
            )
            self.cycle_results["inference"] = result_inference

            # Phase 5: Save Forecast
            result_save = self._execute_phase(
                "SaveForecast",
                self._phase_save,
            )
            self.cycle_results["save"] = result_save

            # Summary
            cycle_end = datetime.utcnow()
            cycle_duration = (cycle_end - self.cycle_start).total_seconds()

            summary = {
                "status": "success",
                "start_time": self.cycle_start.isoformat(),
                "end_time": cycle_end.isoformat(),
                "duration_seconds": cycle_duration,
                "phases": self.cycle_results,
                "phase_durations": self.phase_durations,
            }

            self._log_cycle_summary(summary)
            return summary

        except Exception as e:
            logger.error(f"Pipeline cycle failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "phases": self.cycle_results,
            }

    def _execute_phase(self, phase_name: str, phase_func) -> Dict[str, Any]:
        """Execute a pipeline phase with timing.

        Args:
            phase_name: Name of phase
            phase_func: Callable that executes phase

        Returns:
            Phase result dictionary
        """
        phase_start = datetime.utcnow()
        logger.info(f"\n▶ PHASE: {phase_name}")

        try:
            result = phase_func()

            phase_end = datetime.utcnow()
            duration = (phase_end - phase_start).total_seconds()
            self.phase_durations[phase_name] = duration

            status = result.get("status", "unknown")
            logger.info(f"✓ {phase_name} completed ({duration:.2f}s) — {status}")

            return result

        except Exception as e:
            logger.error(f"✗ {phase_name} failed: {e}")
            return {"status": "error", "error": str(e)}

    def _phase_ingestion(self) -> Dict[str, Any]:
        """Execute PHASE 3: Data Ingestion."""
        from petro.scheduler.tasks import _fetch_data_async
        import asyncio

        result = asyncio.run(_fetch_data_async())
        return result

    def _phase_nlp(self) -> Dict[str, Any]:
        """Execute PHASE 4: NLP Processing."""
        from petro.scheduler.tasks import _process_news_async
        import asyncio

        result = asyncio.run(_process_news_async())
        return result

    def _phase_features(self) -> Dict[str, Any]:
        """Execute PHASE 5: Feature Engineering."""
        from petro.scheduler.tasks import _calculate_features_async
        import asyncio

        result = asyncio.run(_calculate_features_async())
        return result

    def _phase_inference(self) -> Dict[str, Any]:
        """Execute PHASE 7: Inference."""
        from petro.scheduler.tasks import _run_inference_async
        import asyncio

        result = asyncio.run(_run_inference_async())
        return result

    def _phase_save(self) -> Dict[str, Any]:
        """Execute Save Forecast."""
        from petro.scheduler.tasks import _save_forecast_async
        import asyncio

        result = asyncio.run(_save_forecast_async())
        return result

    def _log_cycle_summary(self, summary: Dict[str, Any]):
        """Log cycle summary with timing details.

        Args:
            summary: Cycle summary dictionary
        """
        logger.info("\n" + "=" * 70)
        logger.info("PETRO PIPELINE CYCLE COMPLETED")
        logger.info(f"Total duration: {summary['duration_seconds']:.2f} seconds")
        logger.info("\nPhase timings:")

        for phase_name, duration in self.phase_durations.items():
            logger.info(f"  {phase_name:15} {duration:6.2f}s")

        logger.info("=" * 70)


class PeriodicTrainingOrchestrator:
    """Handles periodic model retraining (daily/weekly)."""

    @staticmethod
    def should_retrain(last_training_date: Optional[datetime], frequency: str = "daily") -> bool:
        """Check if retraining should occur.

        Args:
            last_training_date: Date of last training
            frequency: "daily" or "weekly"

        Returns:
            True if retraining should occur
        """
        if last_training_date is None:
            return True

        now = datetime.utcnow()
        diff = (now - last_training_date).days

        if frequency == "daily":
            return diff >= 1
        elif frequency == "weekly":
            return diff >= 7
        else:
            return False

    @staticmethod
    def execute_retraining() -> Dict[str, Any]:
        """Execute model retraining.

        Returns:
            Training results
        """
        from petro.scheduler.tasks import _train_models_async
        import asyncio

        logger.info("\n" + "=" * 70)
        logger.info("MODEL RETRAINING STARTED")
        logger.info(f"Start time: {datetime.utcnow().isoformat()}")
        logger.info("=" * 70)

        start_time = datetime.utcnow()

        try:
            result = asyncio.run(_train_models_async())

            duration = (datetime.utcnow() - start_time).total_seconds()

            logger.info("\n" + "=" * 70)
            logger.info("MODEL RETRAINING COMPLETED")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Status: {result.get('status')}")
            logger.info("=" * 70)

            return result

        except Exception as e:
            logger.error(f"Model retraining failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
