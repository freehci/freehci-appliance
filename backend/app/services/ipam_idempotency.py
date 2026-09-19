"""Idempotency-Key for IPAM request/allocate."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamIdempotencyKey
from app.services.ipam_errors import ipam_error

T = TypeVar("T")


def _canonical_hash(scope: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(f"{scope}\n{raw}".encode()).hexdigest()


def _get(db: Session, key: str) -> IpamIdempotencyKey | None:
    return db.execute(select(IpamIdempotencyKey).where(IpamIdempotencyKey.key == key)).scalar_one_or_none()


def _dump(result: Any) -> dict[str, Any]:
    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")
    if isinstance(result, dict):
        return result
    raise TypeError("idempotent resultat må være pydantic eller dict")


def run_idempotent(
    db: Session,
    key: str | None,
    *,
    scope: str,
    payload: dict[str, Any],
    fn: Callable[[], T],
) -> T | dict[str, Any]:
    """Kjør `fn` én gang per nøkkel. Tom nøkkel = vanlig kall.

    Reserverer nøkkelen først slik at to parallelle bootstrap-jobber ikke
    får to VIP-er. Feil sletter reservasjonen så retry virker.
    """
    if key is None:
        return fn()
    token = key.strip()[:255]
    if not token:
        return fn()

    digest = _canonical_hash(scope, payload)
    existing = _get(db, token)
    if existing is not None:
        if existing.request_hash != digest:
            raise ipam_error(
                409,
                "idempotency_key_reuse",
                "Idempotency-Key er allerede brukt med en annen forespørsel",
            )
        if existing.response_json is not None:
            return existing.response_json
        raise ipam_error(409, "idempotency_in_progress", "samme Idempotency-Key kjøres allerede")

    row = IpamIdempotencyKey(
        key=token,
        scope=scope,
        request_hash=digest,
        status_code=0,
        response_json=None,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raced = _get(db, token)
        if raced is None:
            raise ipam_error(409, "idempotency_conflict", "kunne ikke reservere Idempotency-Key") from None
        if raced.request_hash != digest:
            raise ipam_error(
                409,
                "idempotency_key_reuse",
                "Idempotency-Key er allerede brukt med en annen forespørsel",
            ) from None
        if raced.response_json is not None:
            return raced.response_json
        raise ipam_error(409, "idempotency_in_progress", "samme Idempotency-Key kjøres allerede") from None

    try:
        result = fn()
    except Exception:
        stuck = _get(db, token)
        if stuck is not None and stuck.response_json is None:
            db.delete(stuck)
            db.commit()
        raise

    stored = _get(db, token)
    if stored is not None:
        stored.status_code = 200
        stored.response_json = _dump(result)
        db.commit()
    return result
