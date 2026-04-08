"""Background tasks."""

from app.workers.celery_app import celery_app


@celery_app.task(name="freehci.health_ping")
def health_ping() -> str:
    return "pong"
