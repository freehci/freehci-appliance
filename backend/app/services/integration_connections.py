"""Tilkoblinger og enhetsidentitet. Konflikt vises; duplikat opprettes ikke."""

from __future__ import annotations

import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInstance
from app.models.integration import DeviceIdentity, DeviceIdentityClaim, IdentityConflict, IntegrationConnection
from app.schemas.integration import (
    DeviceIdentityIngest,
    DeviceIdentityIngestRead,
    IdentityConflictRead,
    IntegrationConnectionCreate,
    IntegrationConnectionRead,
)


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "item")[:128]


def _normalize_value(value: str) -> str:
    return re.sub(r"\s+", "", (value or "").strip()).lower()


def connection_to_read(row: IntegrationConnection) -> IntegrationConnectionRead:
    return IntegrationConnectionRead.model_validate(row)


def list_connections(db: Session, *, plugin_id: str | None = None) -> list[IntegrationConnection]:
    q = select(IntegrationConnection).order_by(IntegrationConnection.name)
    if plugin_id:
        q = q.where(IntegrationConnection.plugin_id == plugin_id)
    return list(db.execute(q).scalars().all())


def get_connection(db: Session, connection_id: int) -> IntegrationConnection | None:
    return db.get(IntegrationConnection, connection_id)


def create_connection(db: Session, data: IntegrationConnectionCreate) -> IntegrationConnection:
    slug = _slugify(data.slug or data.name)
    if db.execute(select(IntegrationConnection.id).where(IntegrationConnection.slug == slug)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="tilkoblings-slug finnes allerede")
    row = IntegrationConnection(
        name=data.name.strip(),
        slug=slug,
        plugin_id=data.plugin_id.strip(),
        base_url=(data.base_url or "").strip() or None,
        credential_ref=data.credential_ref,
        status=data.status,
        last_sync_at=None,
        mapping_json=data.mapping_json,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="tilkoblings-slug finnes allerede")
    db.refresh(row)
    return row


def delete_connection(db: Session, row: IntegrationConnection) -> None:
    db.delete(row)
    db.commit()


def list_conflicts(db: Session, *, status: str | None = "open") -> list[IdentityConflict]:
    q = select(IdentityConflict).order_by(IdentityConflict.id.desc())
    if status:
        q = q.where(IdentityConflict.status == status)
    return list(db.execute(q).scalars().all())


def conflict_to_read(row: IdentityConflict) -> IdentityConflictRead:
    return IdentityConflictRead.model_validate(row)


def _open_conflict(
    db: Session,
    *,
    identity_type: str,
    namespace: str,
    value: str,
    normalized: str,
    connection_a_id: int | None,
    connection_b_id: int | None,
    device_a_id: int | None,
    device_b_id: int | None,
) -> IdentityConflict:
    ids = sorted(i for i in (device_a_id, device_b_id) if i is not None)
    a_id = ids[0] if ids else None
    b_id = ids[1] if len(ids) > 1 else (ids[0] if ids and device_a_id != device_b_id else None)
    if a_id is not None and b_id is not None and a_id > b_id:
        a_id, b_id = b_id, a_id
    found = db.execute(
        select(IdentityConflict).where(
            IdentityConflict.identity_type == identity_type,
            IdentityConflict.namespace == namespace,
            IdentityConflict.normalized_value == normalized,
            IdentityConflict.device_a_id == a_id,
            IdentityConflict.device_b_id == b_id,
            IdentityConflict.status == "open",
        ),
    ).scalar_one_or_none()
    if found is not None:
        return found
    row = IdentityConflict(
        identity_type=identity_type,
        namespace=namespace,
        value=value,
        normalized_value=normalized,
        connection_a_id=connection_a_id,
        connection_b_id=connection_b_id,
        device_a_id=a_id,
        device_b_id=b_id,
        status="open",
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(IdentityConflict).where(
                IdentityConflict.identity_type == identity_type,
                IdentityConflict.namespace == namespace,
                IdentityConflict.normalized_value == normalized,
                IdentityConflict.device_a_id == a_id,
                IdentityConflict.device_b_id == b_id,
            ),
        ).scalar_one_or_none()
        if existing is None:
            raise
        return existing
    db.refresh(row)
    return row


def _match_devices(db: Session, data: DeviceIdentityIngest, normalized: str) -> list[DeviceInstance]:
    if data.device_id is not None:
        row = db.get(DeviceInstance, data.device_id)
        return [row] if row is not None else []
    q = select(DeviceInstance)
    if data.identity_type == "serial":
        q = q.where(DeviceInstance.serial_number.is_not(None))
        rows = [d for d in db.execute(q).scalars().all() if _normalize_value(d.serial_number or "") == normalized]
        return rows
    if data.identity_type == "asset_tag":
        q = q.where(DeviceInstance.asset_tag.is_not(None))
        return [d for d in db.execute(q).scalars().all() if _normalize_value(d.asset_tag or "") == normalized]
    return []


def _ensure_claim(db: Session, connection_id: int, identity_id: int) -> None:
    found = db.execute(
        select(DeviceIdentityClaim.id).where(
            DeviceIdentityClaim.connection_id == connection_id,
            DeviceIdentityClaim.identity_id == identity_id,
        ),
    ).scalar_one_or_none()
    if found is not None:
        return
    db.add(DeviceIdentityClaim(connection_id=connection_id, identity_id=identity_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def _bind_identity(
    db: Session,
    *,
    device_id: int,
    identity_type: str,
    namespace: str,
    value: str,
    normalized: str,
    connection_id: int,
) -> DeviceIdentity:
    row = db.execute(
        select(DeviceIdentity).where(
            DeviceIdentity.identity_type == identity_type,
            DeviceIdentity.namespace == namespace,
            DeviceIdentity.normalized_value == normalized,
        ),
    ).scalar_one_or_none()
    if row is None:
        row = DeviceIdentity(
            device_id=device_id,
            identity_type=identity_type,
            namespace=namespace,
            value=value,
            normalized_value=normalized,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    _ensure_claim(db, connection_id, row.id)
    return row


def ingest(db: Session, connection: IntegrationConnection, data: DeviceIdentityIngest) -> DeviceIdentityIngestRead:
    value = data.value.strip()
    normalized = _normalize_value(value)
    namespace = data.namespace
    identity = db.execute(
        select(DeviceIdentity).where(
            DeviceIdentity.identity_type == data.identity_type,
            DeviceIdentity.namespace == namespace,
            DeviceIdentity.normalized_value == normalized,
        ),
    ).scalar_one_or_none()

    if identity is not None:
        if data.device_id is not None and data.device_id != identity.device_id:
            conflict = _open_conflict(
                db,
                identity_type=data.identity_type,
                namespace=namespace,
                value=value,
                normalized=normalized,
                connection_a_id=connection.id,
                connection_b_id=None,
                device_a_id=identity.device_id,
                device_b_id=data.device_id,
            )
            return DeviceIdentityIngestRead(
                action="conflict",
                device_id=identity.device_id,
                identity_id=identity.id,
                conflict_id=conflict.id,
            )
        other_claim = db.execute(
            select(DeviceIdentityClaim).where(DeviceIdentityClaim.identity_id == identity.id),
        ).scalars().all()
        other_conn = next((c for c in other_claim if c.connection_id != connection.id), None)
        _ensure_claim(db, connection.id, identity.id)
        if other_conn is not None:
            # To kilder, samme enhet: det er ønsket, ikke konflikt.
            pass
        return DeviceIdentityIngestRead(
            action="matched",
            device_id=identity.device_id,
            identity_id=identity.id,
            conflict_id=None,
        )

    matches = _match_devices(db, data, normalized)
    if len(matches) > 1:
        conflict = _open_conflict(
            db,
            identity_type=data.identity_type,
            namespace=namespace,
            value=value,
            normalized=normalized,
            connection_a_id=connection.id,
            connection_b_id=None,
            device_a_id=matches[0].id,
            device_b_id=matches[1].id,
        )
        return DeviceIdentityIngestRead(
            action="conflict",
            device_id=None,
            identity_id=None,
            conflict_id=conflict.id,
        )
    if len(matches) == 1:
        bound = _bind_identity(
            db,
            device_id=matches[0].id,
            identity_type=data.identity_type,
            namespace=namespace,
            value=value,
            normalized=normalized,
            connection_id=connection.id,
        )
        return DeviceIdentityIngestRead(
            action="matched",
            device_id=bound.device_id,
            identity_id=bound.id,
            conflict_id=None,
        )

    if data.create_if_missing:
        name = (data.name or "").strip() or f"{data.identity_type}-{normalized[:24]}"
        device = DeviceInstance(name=name, serial_number=value if data.identity_type == "serial" else None)
        db.add(device)
        db.commit()
        db.refresh(device)
        bound = _bind_identity(
            db,
            device_id=device.id,
            identity_type=data.identity_type,
            namespace=namespace,
            value=value,
            normalized=normalized,
            connection_id=connection.id,
        )
        return DeviceIdentityIngestRead(
            action="created",
            device_id=device.id,
            identity_id=bound.id,
            conflict_id=None,
            created=True,
        )

    return DeviceIdentityIngestRead(action="unmatched", device_id=None, identity_id=None, conflict_id=None)
