"""Tilkoblinger mot plugin-pakker og identitetskonflikter."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.integration import (
    DeviceIdentityIngest,
    DeviceIdentityIngestRead,
    IdentityConflictRead,
    IntegrationConnectionCreate,
    IntegrationConnectionRead,
)
from app.services import integration_connections as conn_svc

router = APIRouter(prefix="/integration-connections", tags=["integration-connections"])


@router.get("", response_model=list[IntegrationConnectionRead])
def list_connections(
    plugin_id: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[IntegrationConnectionRead]:
    return [conn_svc.connection_to_read(r) for r in conn_svc.list_connections(db, plugin_id=plugin_id)]


@router.post("", response_model=IntegrationConnectionRead)
def create_connection(data: IntegrationConnectionCreate, db: Session = Depends(get_db)) -> IntegrationConnectionRead:
    return conn_svc.connection_to_read(conn_svc.create_connection(db, data))


@router.get("/conflicts", response_model=list[IdentityConflictRead])
def list_conflicts(
    status: str | None = Query("open"),
    db: Session = Depends(get_db),
) -> list[IdentityConflictRead]:
    return [conn_svc.conflict_to_read(r) for r in conn_svc.list_conflicts(db, status=status)]


@router.delete("/{connection_id}", status_code=204)
def delete_connection(connection_id: int, db: Session = Depends(get_db)) -> None:
    row = conn_svc.get_connection(db, connection_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tilkobling ikke funnet")
    conn_svc.delete_connection(db, row)


@router.post("/{connection_id}/ingest", response_model=DeviceIdentityIngestRead)
def ingest_identity(
    connection_id: int,
    data: DeviceIdentityIngest,
    db: Session = Depends(get_db),
) -> DeviceIdentityIngestRead:
    row = conn_svc.get_connection(db, connection_id)
    if row is None:
        raise HTTPException(status_code=404, detail="tilkobling ikke funnet")
    return conn_svc.ingest(db, row, data)
