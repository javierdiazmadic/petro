"""Unit tests for Celery scheduler tasks."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from petro.scheduler.orchestrator import PipelineOrchestrator, PeriodicTrainingOrchestrator
from datetime import datetime, timedelta


class TestPipelineOrchestrator:
    """Tests for PipelineOrchestrator."""

    def test_orchestrator_init(self):
        """Test orchestrator initialization."""
        orchestrator = PipelineOrchestrator()
        assert orchestrator.cycle_start is None
        assert orchestrator.cycle_results == {}
        assert orchestrator.phase_durations == {}

    def test_execute_phase_success(self):
        """Test successful phase execution."""
        orchestrator = PipelineOrchestrator()

        def mock_phase():
            return {"status": "success", "message": "Phase completed"}

        result = orchestrator._execute_phase("TestPhase", mock_phase)

        assert result["status"] == "success"
        assert "TestPhase" in orchestrator.phase_durations
        assert orchestrator.phase_durations["TestPhase"] >= 0

    def test_execute_phase_error(self):
        """Test phase execution with error."""
        orchestrator = PipelineOrchestrator()

        def mock_phase():
            raise ValueError("Phase failed")

        result = orchestrator._execute_phase("FailedPhase", mock_phase)

        assert result["status"] == "error"
        assert "error" in result

    def test_orchestrator_cycle_structure(self):
        """Test cycle results structure."""
        orchestrator = PipelineOrchestrator()

        # Mock all phase functions
        with patch.object(orchestrator, "_phase_ingestion") as mock_ing, \
             patch.object(orchestrator, "_phase_nlp") as mock_nlp, \
             patch.object(orchestrator, "_phase_features") as mock_feat, \
             patch.object(orchestrator, "_phase_inference") as mock_inf, \
             patch.object(orchestrator, "_phase_save") as mock_save:

            mock_ing.return_value = {"status": "success"}
            mock_nlp.return_value = {"status": "success"}
            mock_feat.return_value = {"status": "success"}
            mock_inf.return_value = {"status": "success"}
            mock_save.return_value = {"status": "success"}

            result = orchestrator.orchestrate_full_cycle()

            assert result["status"] == "success"
            assert "ingestion" in result["phases"]
            assert "nlp" in result["phases"]
            assert "features" in result["phases"]
            assert "inference" in result["phases"]
            assert "save" in result["phases"]

    def test_cycle_timing(self):
        """Test cycle timing calculation."""
        orchestrator = PipelineOrchestrator()

        # Mock phase that takes some time
        def mock_phase():
            import time
            time.sleep(0.01)  # 10ms
            return {"status": "success"}

        orchestrator._execute_phase("TimedPhase", mock_phase)

        assert "TimedPhase" in orchestrator.phase_durations
        assert orchestrator.phase_durations["TimedPhase"] >= 0.01

    def test_orchestrator_error_handling(self):
        """Test error handling in orchestrator."""
        orchestrator = PipelineOrchestrator()

        def mock_failing_phase():
            raise RuntimeError("Critical error")

        with patch.object(orchestrator, "_phase_ingestion", side_effect=RuntimeError("Critical error")):
            result = orchestrator.orchestrate_full_cycle()

            assert result["status"] == "error"
            assert "error" in result


class TestPeriodicTrainingOrchestrator:
    """Tests for PeriodicTrainingOrchestrator."""

    def test_should_retrain_first_time(self):
        """Test retraining decision when never trained."""
        should_train = PeriodicTrainingOrchestrator.should_retrain(None, "daily")
        assert should_train is True

    def test_should_retrain_daily_not_yet(self):
        """Test daily retraining not yet due."""
        last_training = datetime.utcnow() - timedelta(hours=12)
        should_train = PeriodicTrainingOrchestrator.should_retrain(last_training, "daily")
        assert should_train is False

    def test_should_retrain_daily_due(self):
        """Test daily retraining due."""
        last_training = datetime.utcnow() - timedelta(days=1, hours=1)
        should_train = PeriodicTrainingOrchestrator.should_retrain(last_training, "daily")
        assert should_train is True

    def test_should_retrain_weekly_not_yet(self):
        """Test weekly retraining not yet due."""
        last_training = datetime.utcnow() - timedelta(days=3)
        should_train = PeriodicTrainingOrchestrator.should_retrain(last_training, "weekly")
        assert should_train is False

    def test_should_retrain_weekly_due(self):
        """Test weekly retraining due."""
        last_training = datetime.utcnow() - timedelta(days=8)
        should_train = PeriodicTrainingOrchestrator.should_retrain(last_training, "weekly")
        assert should_train is True

    def test_should_retrain_invalid_frequency(self):
        """Test with invalid frequency."""
        last_training = datetime.utcnow() - timedelta(days=1)
        should_train = PeriodicTrainingOrchestrator.should_retrain(last_training, "invalid")
        assert should_train is False


class TestCeleryTaskStructure:
    """Tests for Celery task structure and configuration."""

    def test_task_retry_configuration(self):
        """Test that tasks have proper retry configuration."""
        from petro.scheduler.tasks import fetch_all_data, process_news

        assert fetch_all_data.max_retries == 3
        assert process_news.max_retries == 3

    def test_task_bind_configuration(self):
        """Test that tasks are properly bound."""
        from petro.scheduler.tasks import fetch_all_data

        # Bound tasks can access 'self' for retry logic
        assert fetch_all_data.bind is True

    def test_beat_schedule_exists(self):
        """Test that beat schedule is configured."""
        from petro.scheduler.app import app

        assert hasattr(app.conf, "beat_schedule")
        beat_schedule = app.conf.beat_schedule

        # Check main pipeline tasks
        assert "full-pipeline-15min" in beat_schedule
        assert "process-news-15min" in beat_schedule
        assert "calculate-features-15min" in beat_schedule
        assert "run-inference-15min" in beat_schedule
        assert "save-forecast-15min" in beat_schedule
        assert "log-completion-15min" in beat_schedule

        # Check training task
        assert "train-models-daily" in beat_schedule

    def test_beat_schedule_timing(self):
        """Test beat schedule timing configuration."""
        from petro.scheduler.app import app

        beat_schedule = app.conf.beat_schedule

        # 15-min tasks should execute every 15 minutes
        pipeline_task = beat_schedule["full-pipeline-15min"]
        assert pipeline_task["options"]["expires"] == 900  # 15 minutes

        # Daily task should have longer expiry
        daily_task = beat_schedule["train-models-daily"]
        assert daily_task["options"]["expires"] == 3600  # 1 hour

    def test_task_queue_assignment(self):
        """Test that tasks are assigned to proper queues."""
        from petro.scheduler.app import app

        beat_schedule = app.conf.beat_schedule

        # Inference should use predictions queue
        inference_task = beat_schedule["run-inference-15min"]
        assert inference_task["options"]["queue"] == "predictions"

        # Training should use training queue
        training_task = beat_schedule["train-models-daily"]
        assert training_task["options"]["queue"] == "training"

        # Others use default queue
        default_task = beat_schedule["full-pipeline-15min"]
        assert default_task["options"]["queue"] == "default"


class TestPipelineIntegration:
    """Integration tests for pipeline stages."""

    def test_phase_ingestion_returns_dict(self):
        """Test that ingestion phase returns proper structure."""
        orchestrator = PipelineOrchestrator()

        with patch("petro.scheduler.tasks._fetch_data_async") as mock_fetch:
            mock_fetch.return_value = {
                "status": "success",
                "connectors": {},
            }

            result = orchestrator._phase_ingestion()

            assert "status" in result
            assert isinstance(result, dict)

    def test_orchestrator_phase_ordering(self):
        """Test that phases are called in correct order."""
        orchestrator = PipelineOrchestrator()
        call_order = []

        def make_phase_func(name):
            def phase_func():
                call_order.append(name)
                return {"status": "success"}
            return phase_func

        with patch.object(orchestrator, "_phase_ingestion", side_effect=make_phase_func("ingestion")), \
             patch.object(orchestrator, "_phase_nlp", side_effect=make_phase_func("nlp")), \
             patch.object(orchestrator, "_phase_features", side_effect=make_phase_func("features")), \
             patch.object(orchestrator, "_phase_inference", side_effect=make_phase_func("inference")), \
             patch.object(orchestrator, "_phase_save", side_effect=make_phase_func("save")):

            orchestrator.orchestrate_full_cycle()

            expected_order = ["ingestion", "nlp", "features", "inference", "save"]
            assert call_order == expected_order
