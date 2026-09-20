"""Ærlig cluster-inventar — uten observert helsestatus eller VM-liste."""

from __future__ import annotations

import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.platform import PlatformCluster, PlatformClusterMember
from app.schemas.platform import (
    PlatformClusterCreate,
    PlatformClusterMemberCreate,
    PlatformClusterMemberRead,
    PlatformClusterRead,
)
from app.services import dcim as dcim_svc


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "cluster")[:128]


def cluster_to_read(row: PlatformCluster) -> PlatformClusterRead:
    return PlatformClusterRead(
        id=row.id,
        name=row.name,
        slug=row.slug,
        kind=row.kind,
        site_id=row.site_id,
        description=row.description,
        created_at=row.created_at,
        members=[PlatformClusterMemberRead.model_validate(m) for m in row.members],
    )


def _load(db: Session, cluster_id: int) -> PlatformCluster | None:
    return db.execute(
        select(PlatformCluster)
        .options(selectinload(PlatformCluster.members))
        .where(PlatformCluster.id == cluster_id)
    ).scalar_one_or_none()


def list_clusters(db: Session) -> list[PlatformCluster]:
    return list(
        db.execute(
            select(PlatformCluster)
            .options(selectinload(PlatformCluster.members))
            .order_by(PlatformCluster.name)
        ).scalars().all()
    )


def get_cluster(db: Session, cluster_id: int) -> PlatformCluster | None:
    return _load(db, cluster_id)


def get_cluster_by_slug(db: Session, slug: str) -> PlatformCluster | None:
    return db.execute(select(PlatformCluster).where(PlatformCluster.slug == slug)).scalar_one_or_none()


def create_cluster(db: Session, data: PlatformClusterCreate) -> PlatformCluster:
    slug = _slugify(data.slug or data.name)
    if db.execute(select(PlatformCluster.id).where(PlatformCluster.slug == slug)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="cluster-slug finnes allerede")
    if data.site_id is not None and dcim_svc.get_site(db, data.site_id) is None:
        raise HTTPException(status_code=404, detail="site ikke funnet")
    row = PlatformCluster(
        name=data.name.strip(),
        slug=slug,
        kind=data.kind,
        site_id=data.site_id,
        description=(data.description or "").strip() or None,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="cluster-slug finnes allerede")
    loaded = _load(db, row.id)
    assert loaded is not None
    return loaded


def delete_cluster(db: Session, row: PlatformCluster) -> None:
    db.delete(row)
    db.commit()


def add_member(db: Session, cluster: PlatformCluster, data: PlatformClusterMemberCreate) -> PlatformClusterMember:
    device = dcim_svc.get_device(db, data.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="enhet ikke funnet")
    exists = db.execute(
        select(PlatformClusterMember.id).where(
            PlatformClusterMember.cluster_id == cluster.id,
            PlatformClusterMember.device_id == device.id,
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="enheten er allerede medlem")
    row = PlatformClusterMember(cluster_id=cluster.id, device_id=device.id, role=data.role)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="enheten er allerede medlem")
    db.refresh(row)
    return row


def remove_member(db: Session, cluster: PlatformCluster, member_id: int) -> None:
    row = db.get(PlatformClusterMember, member_id)
    if row is None or row.cluster_id != cluster.id:
        raise HTTPException(status_code=404, detail="medlem ikke funnet")
    db.delete(row)
    db.commit()


def shared_site_id(db: Session, device_ids: list[int]) -> int | None:
    sites: set[int] = set()
    for did in device_ids:
        sid = dcim_svc.device_effective_site_id(db, did)
        if sid is not None:
            sites.add(int(sid))
    if len(sites) == 1:
        return next(iter(sites))
    return None
