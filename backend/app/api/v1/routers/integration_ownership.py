"""Ekstern objektmapping og felteierskap. mapping_json er ikke kilde."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.integration import (
    ExternalObjectMappingCreate,
    ExternalObjectMappingRead,
    ExternalObjectMappingUpdate,
    FieldOwnershipCreate,
    FieldOwnershipRead,
)
from app.services import integration_ownership as own_svc

maps_router = APIRouter(prefix="/external-object-maps", tags=["integration-ownership"])
owns_router = APIRouter(prefix="/field-ownerships", tags=["integration-ownership"])


@maps_router.get("", response_model=list[ExternalObjectMappingRead])
def list_maps(
    connection_id: int | None = Query(None, ge=1),
    device_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
) -> list[ExternalObjectMappingRead]:
    return [
        own_svc.mapping_to_read(r)
        for r in own_svc.list_mappings(db, connection_id=connection_id, device_id=device_id)
    ]


@maps_router.post("", response_model=ExternalObjectMappingRead)
def create_map(data: ExternalObjectMappingCreate, db: Session = Depends(get_db)) -> ExternalObjectMappingRead:
    return own_svc.mapping_to_read(own_svc.create_mapping(db, data))


@maps_router.patch("/{mapping_id}", response_model=ExternalObjectMappingRead)
def patch_map(
    mapping_id: int,
    data: ExternalObjectMappingUpdate,
    db: Session = Depends(get_db),
) -> ExternalObjectMappingRead:
    row = own_svc.get_mapping(db, mapping_id)
    if row is None:
        raise HTTPException(status_code=404, detail="objektmapping ikke funnet")
    return own_svc.mapping_to_read(own_svc.update_mapping(db, row, data))


@maps_router.delete("/{mapping_id}", status_code=204)
def delete_map(mapping_id: int, db: Session = Depends(get_db)) -> None:
    row = own_svc.get_mapping(db, mapping_id)
    if row is None:
        raise HTTPException(status_code=404, detail="objektmapping ikke funnet")
    own_svc.delete_mapping(db, row)


@owns_router.get("", response_model=list[FieldOwnershipRead])
def list_owns(
    connection_id: int | None = Query(None, ge=1),
    device_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
) -> list[FieldOwnershipRead]:
    return [
        own_svc.ownership_to_read(r)
        for r in own_svc.list_ownerships(db, connection_id=connection_id, device_id=device_id)
    ]


@owns_router.post("", response_model=FieldOwnershipRead)
def create_own(data: FieldOwnershipCreate, db: Session = Depends(get_db)) -> FieldOwnershipRead:
    return own_svc.ownership_to_read(own_svc.create_ownership(db, data))


@owns_router.delete("/{ownership_id}", status_code=204)
def delete_own(ownership_id: int, db: Session = Depends(get_db)) -> None:
    row = own_svc.get_ownership(db, ownership_id)
    if row is None:
        raise HTTPException(status_code=404, detail="felteierskap ikke funnet")
    own_svc.delete_ownership(db, row)
