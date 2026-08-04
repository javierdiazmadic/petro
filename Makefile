.PHONY: help install install-dev docker-build docker-up docker-down docker-logs test lint format clean

help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make install-dev      - Install dev dependencies"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-ml          - Run ML training tests"
	@echo "  make test-inference   - Run ML inference tests"
	@echo "  make lint             - Run linters"
	@echo "  make format           - Format code"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make train-example    - Run training pipeline example"
	@echo "  make inference-example - Run inference pipeline example"
	@echo "  make mlflow-ui        - Launch MLflow UI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-logs-all:
	docker-compose logs -f

test:
	pytest tests/ -v --cov=src/petro

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

test-ml:
	pytest tests/unit/test_ml_training.py -v

test-inference:
	pytest tests/unit/test_ml_inference.py -v

test-scheduler:
	pytest tests/unit/test_scheduler_tasks.py -v

test-api:
	pytest tests/integration/test_api_endpoints.py -v

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.coverage' -delete
	rm -rf build/ dist/ *.egg-info/

db-migrate:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

celery-worker:
	celery -A petro.scheduler.app worker --loglevel=info --concurrency=2

celery-beat:
	celery -A petro.scheduler.app beat --loglevel=info

celery-flower:
	celery -A petro.scheduler.app flower --port=5555

orchestrate-test:
	python3 -c "from petro.scheduler.orchestrator import PipelineOrchestrator; import json; result = PipelineOrchestrator().orchestrate_full_cycle(); print(json.dumps(result, indent=2, default=str))"

api-dev:
	uvicorn petro.api.main:app --reload --host 0.0.0.0 --port 8000

train-example:
	python scripts/train_example.py

inference-example:
	python3 scripts/inference_example.py

mlflow-ui:
	mlflow ui --host 0.0.0.0 --port 5000
