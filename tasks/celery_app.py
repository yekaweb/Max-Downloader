import os
from celery import Celery
from config import settings

# Initialize Celery app
celery_app = Celery(
    "dlbot_tasks",
    broker=settings.redis_url if settings.REDIS_ENABLED else "redis://localhost:6379/0",
    backend=settings.redis_url if settings.REDIS_ENABLED else "redis://localhost:6379/1",
    include=["tasks.download_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)

__all__ = ["celery_app"]
