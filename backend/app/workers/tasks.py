"""Background tasks."""

from app.services import network_scan as netscan_svc
from app.workers.celery_app import celery_app


@celery_app.task(name="freehci.health_ping")
def health_ping() -> str:
    return "pong"


@celery_app.task(name="freehci.run_network_scan_job")
def run_network_scan_job_task(job_id: int) -> None:
    """Lang kjøring av nettverksskann (kan trigges fra Celery Beat senere)."""
    netscan_svc.execute_network_scan_job(job_id)
