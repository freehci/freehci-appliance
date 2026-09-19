"""IPAM-audit: hvem tok hvilken adresse, når og hvorfor."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.request_context import get_actor
from app.models.ipam import IpamAuditEvent


def record(
    db: Session,
    *,
    action: str,
    resource_type: str,
    resource_id: int | None = None,
    site_id: int | None = None,
    **detail: Any,
) -> None:
    actor = get_actor()
    payload = {k: v for k, v in detail.items() if v is not None} or None
    db.add(
        IpamAuditEvent(
            actor_type=actor.actor_type,
            actor_id=actor.actor_id,
            actor_name=actor.actor_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            site_id=site_id,
            detail=payload,
        ),
    )


def list_events(
    db: Session,
    *,
    site_id: int | None = None,
    resource_type: str | None = None,
    action: str | None = None,
    limit: int = 100,
) -> list[IpamAuditEvent]:
    q = select(IpamAuditEvent).order_by(IpamAuditEvent.id.desc()).limit(limit)
    if site_id is not None:
        q = q.where(IpamAuditEvent.site_id == site_id)
    if resource_type is not None:
        q = q.where(IpamAuditEvent.resource_type == resource_type)
    if action is not None:
        q = q.where(IpamAuditEvent.action == action)
    return list(db.execute(q).scalars().all())
