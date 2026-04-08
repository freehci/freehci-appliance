"""IPAM REST API (IPv4 prefiks per site)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.ipam import Ipv4PrefixCreate, Ipv4PrefixRead, Ipv4PrefixUpdate
from app.services import ipam as ipam_svc

router = APIRouter(prefix="/ipam", tags=["ipam"])


@router.get("/ipv4-prefixes", response_model=list[Ipv4PrefixRead])
def list_ipv4_prefixes(
    site_id: int | None = Query(None, description="Filtrer på DCIM site-id"),
    db: Session = Depends(get_db),
) -> list[Ipv4PrefixRead]:
    return ipam_svc.list_ipv4_prefixes(db, site_id=site_id)


@router.post("/ipv4-prefixes", response_model=Ipv4PrefixRead)
def create_ipv4_prefix(data: Ipv4PrefixCreate, db: Session = Depends(get_db)) -> Ipv4PrefixRead:
    return ipam_svc.create_ipv4_prefix(db, data)


@router.get("/ipv4-prefixes/{prefix_id}", response_model=Ipv4PrefixRead)
def get_ipv4_prefix(prefix_id: int, db: Session = Depends(get_db)) -> Ipv4PrefixRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    return Ipv4PrefixRead.model_validate(row)


@router.patch("/ipv4-prefixes/{prefix_id}", response_model=Ipv4PrefixRead)
def patch_ipv4_prefix(
    prefix_id: int,
    data: Ipv4PrefixUpdate,
    db: Session = Depends(get_db),
) -> Ipv4PrefixRead:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    return ipam_svc.update_ipv4_prefix(db, row, data)


@router.delete("/ipv4-prefixes/{prefix_id}", status_code=204)
def delete_ipv4_prefix(prefix_id: int, db: Session = Depends(get_db)) -> None:
    row = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if row is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    ipam_svc.delete_ipv4_prefix(db, row)
