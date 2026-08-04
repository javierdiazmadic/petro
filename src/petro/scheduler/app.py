"""Celery application configuration."""

from celery import Celery

from petro.core import get_logger
from petro.core.config import settings

logger = get_logger(__name__)

# Create Celery instance
app = Celery("petro")

# Configure Celery
app.conf.update(
    broker_url=settings.celery.broker_url,
    result_backend=settings.celery.result_backend,
    timezone=settings.celery.timezone,
    enable_utc=settings.celery.enable_utc,
    task_serializer=settings.celery.task_serializer,
    result_serializer=settings.celery.result_serializer,
    accept_content=settings.celery.accept_content,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
)

# Auto-discover tasks
app.autodiscover_tasks(["petro.scheduler"])

logger.info("Celery app configured")
