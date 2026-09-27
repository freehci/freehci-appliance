"""Ekstern objektmapping og felteierskap. Navn og mapping_json lager aldri rader."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInstance
from app.models.integration import ExternalObjectMapping, FieldOwnership, IntegrationConnection
from app.schemas.integration import (
    ExternalObjectMappingCreate,
    ExternalObjectMappingRead,
    ExternalObjectMappingUpdate,
    FieldOwnershipCreate,
    FieldOwnershipRead,
)


def mapping_to_read(row: ExternalObjectMapping) -> ExternalObjectMappingRead:
    return ExternalObjectMappingRead.model_validate(row)


def ownership_to_read(row: FieldOwnership) -> FieldOwnershipRead:
    return FieldOwnershipRead.model_validate(row)


def _require_connection(db: Session, connection_id: int) -> IntegrationConnection:
    row = db.get(IntegrationConnection, connection_id)
    if row is None:
        raise HTTPException(status_code=400, detail="tilkobling ikke funnet")
    return row


def _require_device(db: Session, device_id: int) -> DeviceInstance:
    row = db.get(DeviceInstance, device_id)
    if row is None:
        raise HTTPException(status_code=400, detail="enhet ikke funnet")
    return row


def list_mappings(
    db: Session,
    *,
    connection_id: int | None = None,
    device_id: int | None = None,
) -> list[ExternalObjectMapping]:
    q = select(ExternalObjectMapping).order_by(ExternalObjectMapping.id)
    if connection_id is not None:
        q = q.where(ExternalObjectMapping.connection_id == connection_id)
    if device_id is not None:
        q = q.where(ExternalObjectMapping.device_id == device_id)
    return list(db.execute(q).scalars().all())


def get_mapping(db: Session, mapping_id: int) -> ExternalObjectMapping | None:
    return db.get(ExternalObjectMapping, mapping_id)


def create_mapping(db: Session, data: ExternalObjectMappingCreate) -> ExternalObjectMapping:
    _require_connection(db, data.connection_id)
    if data.device_id is not None:
        _require_device(db, data.device_id)
    row = ExternalObjectMapping(
        connection_id=data.connection_id,
        object_type=data.object_type,
        external_id=data.external_id,
        device_id=data.device_id,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="ekstern objektmapping finnes allerede")
    db.refresh(row)
    return row


def update_mapping(db: Session, row: ExternalObjectMapping, data: ExternalObjectMappingUpdate) -> ExternalObjectMapping:
    if "device_id" in data.model_fields_set:
        if data.device_id is not None:
            _require_device(db, data.device_id)
        row.device_id = data.device_id
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete_mapping(db: Session, row: ExternalObjectMapping) -> None:
    db.delete(row)
    db.commit()


def list_ownerships(
    db: Session,
    *,
    connection_id: int | None = None,
    device_id: int | None = None,
) -> list[FieldOwnership]:
    q = select(FieldOwnership).order_by(FieldOwnership.device_id, FieldOwnership.field_name)
    if connection_id is not None:
        q = q.where(FieldOwnership.connection_id == connection_id)
    if device_id is not None:
        q = q.where(FieldOwnership.device_id == device_id)
    return list(db.execute(q).scalars().all())


def get_ownership(db: Session, ownership_id: int) -> FieldOwnership | None:
    return db.get(FieldOwnership, ownership_id)


def create_ownership(db: Session, data: FieldOwnershipCreate) -> FieldOwnership:
    _require_connection(db, data.connection_id)
    _require_device(db, data.device_id)
    existing = db.execute(
        select(FieldOwnership).where(
            FieldOwnership.device_id == data.device_id,
            FieldOwnership.field_name == data.field_name,
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="feltet har allerede en eier")
    row = FieldOwnership(
        connection_id=data.connection_id,
        device_id=data.device_id,
        field_name=data.field_name,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="feltet har allerede en eier")
    db.refresh(row)
    return row


def delete_ownership(db: Session, row: FieldOwnership) -> None:
    db.delete(row)
    db.commit()
