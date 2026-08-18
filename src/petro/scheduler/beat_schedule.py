"""Celery Beat schedule configuration."""

from celery.schedules import crontab

from petro.scheduler.app import app

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    "daily-automation-pipeline": {
        "task": "petro.scheduler.tasks.daily_automation_pipeline",
        "schedule": crontab(hour=3, minute=0),  # Every day at 3:00 AM UTC (4:00 AM Spain time)
        "options": {
            "queue": "training",
            "priority": 10,
            "expires": 7200,  # 2 hours
            "time_limit": 1800,  # 30 minutes hard limit
        },
    },
}

# Optional: Celery Beat schedule with timezone awareness
app.conf.timezone = "UTC"
app.conf.enable_utc = True
