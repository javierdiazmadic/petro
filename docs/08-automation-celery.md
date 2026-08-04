# FASE 8: Automatización con Celery

## Resumen

Automatización del pipeline completo (PHASES 3-7) con Celery Beat, ejecutándose cada 15 minutos:

1. **fetch_all_data** — Recolección de datos (PHASE 3)
2. **process_news** — Procesamiento de noticias (PHASE 4)
3. **calculate_features** — Ingeniería de variables (PHASE 5)
4. **run_inference** — Predicción (PHASE 7)
5. **save_forecast** — Guardar resultados
6. **train_models** — Reentrenamiento (diario)

## Arquitectura

### 15-Minute Pipeline Cycle

```
Celery Beat (every 15 minutes)
    ↓
fetch_all_data (0s)
    ├── Brent, WTI, EUR/USD
    ├── EIA inventory, OPEC production
    ├── Spanish fuel prices (Geoportal)
    └── RSS news feeds
    ↓
process_news (+30s)
    ├── Clean HTML, normalize
    ├── Deduplicate (Levenshtein)
    ├── Language detection
    ├── NER (spaCy)
    ├── Classification (TF-IDF + LR)
    └── Sentiment analysis
    ↓
calculate_features (+60s)
    ├── Economic: price changes, spreads
    ├── Temporal: day of week, season, etc.
    ├── Statistical: MA, volatility, momentum
    ├── Technical: RSI, MACD, Bollinger Bands
    └── News-derived: sentiment, entities
    ↓
run_inference (+90s)
    ├── Load model from MLflow
    ├── Predict price (< 50ms)
    ├── Classify direction (up/down/stable)
    └── Calculate confidence
    ↓
save_forecast (+120s)
    ├── Save to Forecast table
    ├── Cache in Redis
    └── Alert if significant change
    ↓
log_cycle_completion (+150s)
    └── Log timing, status
```

**Total expected duration: < 3-5 minutes per cycle**

### Daily Retraining

```
Celery Beat (daily at 2:00 AM UTC)
    ↓
train_models
    ├── Fetch 1000+ days historical data
    ├── Optimize hyperparameters (Optuna, 10 trials)
    ├── Train XGBoost, LightGBM, RandomForest
    ├── Evaluate metrics
    ├── Track in MLflow
    └── Update if RMSE improves
```

## Components

### 1. Celery Tasks (`src/petro/scheduler/tasks.py`)

#### `fetch_all_data()`
**Schedule**: Every 15 minutes  
**Retry**: 3 attempts with 60s countdown  
**Queue**: default  
**Priority**: 10  
**Timeout**: 900s (15 min)

Integrates with DataIngestionOrchestrator:
```python
@app.task(bind=True, max_retries=3)
def fetch_all_data(self):
    orchestrator = DataIngestionOrchestrator(session)
    result = await orchestrator.run_all_connectors()
    return result
```

#### `process_news()`
**Schedule**: Every 15 minutes (+30s offset)  
**Retry**: 3 attempts  
**Queue**: default  
**Priority**: 9  

Processes unprocessed news articles:
- Cleaning
- Deduplication (Levenshtein, 0.85 threshold)
- Language detection
- NER (spaCy)
- Classification (6 categories)
- Sentiment analysis

#### `calculate_features()`
**Schedule**: Every 15 minutes (+60s offset)  
**Retry**: 3 attempts  
**Queue**: default  
**Priority**: 8  

Computes all feature categories:
- Economic (8 features)
- Temporal (9 features)
- Statistical (10 features)
- Technical (5 features)
- News-derived (8 features)

**Total**: ~40 features per timestamp

#### `run_inference()`
**Schedule**: Every 15 minutes (+90s offset)  
**Retry**: 3 attempts  
**Queue**: predictions (higher priority)  
**Priority**: 10  
**Timeout**: 100s (must finish < 100ms)

Loads model from MLflow and predicts:
- Handles multi-model ensemble fallback
- Returns prediction + direction + confidence
- Sets alarm if price change > 2%

#### `save_forecast()`
**Schedule**: Every 15 minutes (+120s offset)  
**Retry**: None (non-critical)  
**Queue**: default  
**Priority**: 7  
**Timeout**: 30s

Saves results to database and cache:
- Forecast table (predictions)
- Redis cache (latest price)
- System logs (events)

#### `train_models()`
**Schedule**: Daily at 2:00 AM UTC  
**Retry**: 3 attempts with 300s countdown  
**Queue**: training (dedicated)  
**Priority**: 10  
**Timeout**: 3600s (1 hour max)

Retrains models with accumulated data:
- Fetches 1000+ days historical
- Optuna HPO (10 trials for speed)
- Trains all 3 algorithms
- Tracks in MLflow
- Registers if RMSE improves

#### `log_cycle_completion()`
**Schedule**: Every 15 minutes (+150s offset)  
**Queue**: default  
**Priority**: 5  

Logs cycle summary with timings.

### 2. Beat Schedule (`src/petro/scheduler/beat_schedule.py`)

Cron-based scheduling with staggered offsets:

```python
app.conf.beat_schedule = {
    "full-pipeline-15min": {
        "task": "petro.scheduler.tasks.fetch_all_data",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "default", "priority": 10, "expires": 900},
    },
    "process-news-15min": {
        "task": "petro.scheduler.tasks.process_news",
        "schedule": crontab(minute="*/15", second=30),
        "options": {"queue": "default", "priority": 9, "expires": 900},
    },
    # ... more tasks with staggered timing
    "train-models-daily": {
        "task": "petro.scheduler.tasks.train_models",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "training", "priority": 10, "expires": 3600},
    },
}
```

**Staggering** prevents thundering herd:
- 0s: fetch_all_data
- 30s: process_news
- 60s: calculate_features
- 90s: run_inference
- 120s: save_forecast
- 150s: log_cycle_completion

### 3. Pipeline Orchestrator (`src/petro/scheduler/orchestrator.py`)

Coordinates the complete cycle:

```python
class PipelineOrchestrator:
    def orchestrate_full_cycle(self) -> Dict:
        # Execute phases in order
        # Track timing for each
        # Log summary
        # Return results
        
    def _execute_phase(self, name, func) -> Dict:
        # Run phase
        # Measure duration
        # Handle errors
```

Can be invoked directly for testing:
```bash
python -c "from petro.scheduler.orchestrator import PipelineOrchestrator; \
    PipelineOrchestrator().orchestrate_full_cycle()"
```

## Deployment

### Docker Compose

Three services (from PHASE 1):

1. **API Worker** — Handles HTTP requests
2. **Celery Worker** — Executes tasks
3. **Celery Beat** — Schedules tasks

```bash
docker-compose up celery-worker celery-beat -d
```

### Local Development

Terminal 1 - Worker:
```bash
make celery-worker
```

Terminal 2 - Beat:
```bash
make celery-beat
```

Terminal 3 - Monitor (Flower):
```bash
celery -A petro.scheduler.app flower --port=5555
```

Browse: http://localhost:5555

### Configuration

`.env` variables:
```env
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_TIMEZONE=UTC
```

## Monitoring

### Flower UI
Dashboard at http://localhost:5555:
- Task execution history
- Worker status
- Queue monitoring
- Real-time task stats

### Logs

All tasks log to:
- **stdout** (JSON format, collected by Docker)
- **system_logs table** (key events)

Example log entry:
```json
{
  "timestamp": "2026-08-04T15:30:00.123456Z",
  "level": "INFO",
  "message": "fetch_all_data task started",
  "task_id": "abc-123-def-456",
  "worker": "celery@worker-1"
}
```

### Metrics

Prometheus metrics available at `/metrics`:
- `celery_task_executed_total` — Task count
- `celery_task_duration_seconds` — Task latency
- `celery_worker_pool_size` — Worker concurrency
- `celery_worker_online` — Worker availability

## Fault Tolerance

### Retry Policy

**Transient errors** (network, timeouts):
- Automatic retry (3 attempts max)
- Exponential backoff: 60s → 120s → 240s
- Task expires after 15 minutes

**Permanent errors** (data validation, model failure):
- Task fails after 3 retries
- Logged to system_logs
- Alert sent to monitoring

### Idempotency

All tasks designed to be idempotent:
- Duplicate news processed → no-op (Levenshtein dedup)
- Duplicate predictions → overwrite latest
- Duplicate features → recalculate

### Dead Letter Queue

Failed tasks after 3 retries:
- Move to DLQ
- Logged with full context
- Manual review required

## Performance Targets

### 15-Minute Cycle
- fetch_all_data: < 30s
- process_news: < 60s
- calculate_features: < 30s
- run_inference: < 10s
- save_forecast: < 10s
- **Total**: < 3-5 minutes

### Daily Training
- HPO (10 trials): ~15 minutes
- Training (3 models): ~5 minutes
- Evaluation + tracking: ~2 minutes
- **Total**: ~20-30 minutes (at 2 AM, low traffic)

## Testing

### Unit Tests
```bash
make test-scheduler
pytest tests/unit/test_scheduler_tasks.py -v
```

Tests cover:
- Task retry configuration
- Beat schedule setup
- Orchestrator logic
- Phase ordering
- Error handling

### Integration Tests
```bash
pytest tests/integration/test_scheduler_integration.py -v
```

(Will be added in PHASE 9)

### Manual Testing

Test full cycle locally:
```python
from petro.scheduler.orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()
result = orchestrator.orchestrate_full_cycle()
print(result)
```

Test specific task:
```bash
celery -A petro.scheduler.app call petro.scheduler.tasks.fetch_all_data
```

## Scaling

### Horizontal Scaling

Add more workers for higher throughput:
```bash
# Start 4 workers (one per CPU core)
for i in {1..4}; do
  celery -A petro.scheduler.app worker -n worker$i &
done
```

Beat remains single instance (leader election handled by Redis).

### Queue Prioritization

Different task types use different queues:
- **default**: ingestion, nlp, features, save (9 tasks/hour)
- **predictions**: inference only (4 tasks/hour, high priority)
- **training**: daily retraining (1 task/day, can be slow)

### Concurrency

Worker concurrency (default 4):
```bash
celery -A petro.scheduler.app worker --concurrency=8 --pool=prefork
```

Avoid over-provisioning:
- Feature calc is CPU-heavy (NLP models)
- Keep concurrency ≤ CPU cores
- Use prefork pool for CPU-bound work

## Next Phase: PHASE 9

PHASE 9 (REST API) will expose:
- `/api/v1/predict` — Latest prediction
- `/api/v1/forecast?days=7` — Multi-day forecast
- `/api/v1/metrics` — Model performance
- `/api/v1/explanations` — SHAP + feature importance

Predictions cached in Redis, updated every 15 min by Celery.

## Troubleshooting

### Task Not Running
```bash
# Check Beat schedule
celery -A petro.scheduler.app inspect scheduled

# Check worker
celery -A petro.scheduler.app inspect active

# Restart Beat with debug
celery -A petro.scheduler.app beat -l debug
```

### High Latency
```bash
# Check worker queue
celery -A petro.scheduler.app inspect active

# Monitor Redis
redis-cli info stats

# Reduce other workload
docker-compose down # other services
```

### Memory Leak
```bash
# Monitor worker
celery -A petro.scheduler.app inspect stats

# Restart worker weekly
systemctl restart celery-worker
```

---

**Completado**: 2026-08-04  
**Status**: PHASE 8 READY FOR APPROVAL
