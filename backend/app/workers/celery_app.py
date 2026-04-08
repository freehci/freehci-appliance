"""Celery-app – brukes av worker-container."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "freehci",
    broker=settings.effective_celery_broker,
    backend=settings.effective_celery_backend,
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["app.workers"])
