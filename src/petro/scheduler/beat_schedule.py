"""Celery Beat schedule configuration."""

from celery.schedules import crontab

from petro.scheduler.app import app

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    "full-pipeline-15min": {
        "task": "petro.scheduler.tasks.fetch_all_data",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
        "options": {
            "queue": "default",
            "priority": 10,
            "expires": 900,  # 15 minutes
        },
    },
    "process-news-15min": {
        "task": "petro.scheduler.tasks.process_news",
        "schedule": crontab(minute="*/15", second=30),  # Every 15 minutes, offset by 30s
        "options": {
            "queue": "default",
            "priority": 9,
            "expires": 900,
        },
    },
    "calculate-features-15min": {
        "task": "petro.scheduler.tasks.calculate_features",
        "schedule": crontab(minute="*/15", second=60),  # Every 15 minutes, offset by 60s
        "options": {
            "queue": "default",
            "priority": 8,
            "expires": 900,
        },
    },
    "run-inference-15min": {
        "task": "petro.scheduler.tasks.run_inference",
        "schedule": crontab(minute="*/15", second=90),  # Every 15 minutes, offset by 90s
        "options": {
            "queue": "predictions",
            "priority": 10,
            "expires": 900,
        },
    },
    "save-forecast-15min": {
        "task": "petro.scheduler.tasks.save_forecast",
        "schedule": crontab(minute="*/15", second=120),  # Every 15 minutes, offset by 2min
        "options": {
            "queue": "default",
            "priority": 7,
            "expires": 900,
        },
    },
    "log-completion-15min": {
        "task": "petro.scheduler.tasks.log_cycle_completion",
        "schedule": crontab(minute="*/15", second=150),  # Every 15 minutes, offset by 2.5min
        "options": {
            "queue": "default",
            "priority": 5,
            "expires": 900,
        },
    },
    "train-models-daily": {
        "task": "petro.scheduler.tasks.train_models",
        "schedule": crontab(hour=2, minute=0),  # Every day at 2:00 AM UTC
        "options": {
            "queue": "training",
            "priority": 10,
            "expires": 3600,
        },
    },
    "full-pipeline-every-2-days": {
        "task": "petro.scheduler.tasks.full_pipeline_every_2_days",
        "schedule": crontab(hour=3, minute=0, day_of_week="0,2,4"),  # Every 2 days (Mon, Wed, Fri) at 3:00 AM UTC
        "options": {
            "queue": "training",
            "priority": 10,
            "expires": 7200,  # 2 hours
        },
    },
}

# Optional: Celery Beat schedule with timezone awareness
app.conf.timezone = "UTC"
app.conf.enable_utc = True
