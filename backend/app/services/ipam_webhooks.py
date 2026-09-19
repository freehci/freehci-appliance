"""IPAM-webhooks: abonnement + levering etter commit."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any
from urllib.parse import urlparse

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models.ipam import IpamWebhook, IpamWebhookDelivery
from app.schemas.ipam import IpamWebhookCreate, IpamWebhookDeliveryRead, IpamWebhookRead
from app.services.ipam_errors import ipam_error

KNOWN_EVENTS = frozenset(
    {
        "prefix.created",
        "prefix.updated",
        "address.ensured",
        "address.released",
    },
)


def _validate_url(url: str) -> str:
    raw = url.strip()
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ipam_error(400, "invalid_webhook_url", "url må være http eller https")
    return raw


def create_webhook(db: Session, data: IpamWebhookCreate) -> IpamWebhook:
    events = data.events
    if events:
        unknown = [e for e in events if e not in KNOWN_EVENTS]
        if unknown:
            raise ipam_error(400, "invalid_webhook_event", f"ukjent event: {', '.join(unknown)}")
    row = IpamWebhook(
        url=_validate_url(data.url),
        secret=data.secret.strip() if data.secret else None,
        events=events,
        enabled=data.enabled,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_webhooks(db: Session) -> list[IpamWebhook]:
    return list(db.execute(select(IpamWebhook).order_by(IpamWebhook.id)).scalars().all())


def get_webhook(db: Session, webhook_id: int) -> IpamWebhook | None:
    return db.get(IpamWebhook, webhook_id)


def delete_webhook(db: Session, row: IpamWebhook) -> None:
    db.delete(row)
    db.commit()


def list_deliveries(db: Session, webhook_id: int, *, limit: int = 50) -> list[IpamWebhookDelivery]:
    return list(
        db.execute(
            select(IpamWebhookDelivery)
            .where(IpamWebhookDelivery.webhook_id == webhook_id)
            .order_by(IpamWebhookDelivery.id.desc())
            .limit(limit),
        ).scalars().all(),
    )


def webhook_to_read(row: IpamWebhook) -> IpamWebhookRead:
    return IpamWebhookRead.model_validate(row)


def delivery_to_read(row: IpamWebhookDelivery) -> IpamWebhookDeliveryRead:
    return IpamWebhookDeliveryRead.model_validate(row)


def _sign(secret: str | None, body: bytes) -> str | None:
    if not secret:
        return None
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _matches(hook: IpamWebhook, event: str) -> bool:
    if not hook.enabled:
        return False
    ev = hook.events
    return not ev or event in ev


def fire(event: str, payload: dict[str, Any]) -> None:
    """Kalles etter commit. Egen sesjon så kallerens transaksjon ikke påvirkes."""
    envelope = {"event": event, "payload": payload}
    body = json.dumps(envelope, default=str).encode("utf-8")
    db = SessionLocal()
    try:
        hooks = [h for h in db.execute(select(IpamWebhook)).scalars().all() if _matches(h, event)]
        for hook in hooks:
            status = "failed"
            code = None
            err = None
            try:
                if get_settings().freehci_skip_auth:
                    status = "skipped"
                    err = "http skipped in test/skip-auth"
                else:
                    headers = {"Content-Type": "application/json", "X-FreeHCI-Event": event}
                    sig = _sign(hook.secret, body)
                    if sig:
                        headers["X-FreeHCI-Signature"] = sig
                    resp = httpx.post(hook.url, content=body, headers=headers, timeout=1.5)
                    code = resp.status_code
                    if 200 <= resp.status_code < 300:
                        status = "ok"
                    else:
                        err = f"http {resp.status_code}"
            except Exception as exc:  # noqa: BLE001 — levering skal ikke knekke API-et
                err = str(exc)[:500]
            db.add(
                IpamWebhookDelivery(
                    webhook_id=hook.id,
                    event=event,
                    status=status,
                    status_code=code,
                    error=err,
                    payload=envelope,
                ),
            )
        if hooks:
            db.commit()
    finally:
        db.close()
