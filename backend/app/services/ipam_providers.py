"""IPAM-leverandører og kundekontoer. Aldri gjettet fra fritekst."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamProvider, IpamProviderAccount
from app.models.tenant import Tenant
from app.schemas.ipam import (
    IpamProviderAccountCreate,
    IpamProviderAccountRead,
    IpamProviderAccountUpdate,
    IpamProviderCreate,
    IpamProviderRead,
    IpamProviderUpdate,
)
from app.services.ipam_errors import ipam_error


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "item")[:128]


def _require_tenant(db: Session, tenant_id: int) -> Tenant:
    row = db.get(Tenant, tenant_id)
    if row is None:
        raise ValueError("tenant ikke funnet")
    return row


def _unique_provider_slug(db: Session, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamProvider.id).where(IpamProvider.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamProvider.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def _unique_account_slug(db: Session, provider_id: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamProviderAccount.id).where(
            IpamProviderAccount.provider_id == provider_id,
            IpamProviderAccount.slug == candidate,
        )
        if exclude_id is not None:
            q = q.where(IpamProviderAccount.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def list_providers(db: Session) -> list[IpamProvider]:
    return list(db.execute(select(IpamProvider).order_by(IpamProvider.name)).scalars().all())


def get_provider(db: Session, provider_id: int) -> IpamProvider | None:
    return db.get(IpamProvider, provider_id)


def get_provider_by_slug(db: Session, slug: str) -> IpamProvider | None:
    return db.execute(select(IpamProvider).where(IpamProvider.slug == slug)).scalar_one_or_none()


def create_provider(db: Session, data: IpamProviderCreate) -> IpamProvider:
    slug = _unique_provider_slug(db, data.slug or data.name)
    row = IpamProvider(
        name=data.name.strip(),
        slug=slug,
        asn=data.asn,
        website=data.website.strip() if data.website else None,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def update_provider(db: Session, row: IpamProvider, data: IpamProviderUpdate) -> IpamProvider:
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_provider_slug(db, data.slug, exclude_id=row.id)
    if data.asn is not None:
        row.asn = data.asn
    if data.website is not None:
        row.website = data.website.strip() if data.website else None
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_provider(db: Session, row: IpamProvider) -> None:
    db.delete(row)
    db.commit()


def list_accounts(db: Session, provider_id: int) -> list[IpamProviderAccount]:
    q = (
        select(IpamProviderAccount)
        .where(IpamProviderAccount.provider_id == provider_id)
        .order_by(IpamProviderAccount.name)
    )
    return list(db.execute(q).scalars().all())


def get_account(db: Session, account_id: int) -> IpamProviderAccount | None:
    return db.get(IpamProviderAccount, account_id)


def create_account(db: Session, provider: IpamProvider, data: IpamProviderAccountCreate) -> IpamProviderAccount:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
    slug = _unique_account_slug(db, provider.id, data.slug or data.name)
    row = IpamProviderAccount(
        provider_id=provider.id,
        tenant_id=data.tenant_id,
        name=data.name.strip(),
        slug=slug,
        account_number=data.account_number.strip() if data.account_number else None,
        description=data.description,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(row)
    return row


def update_account(db: Session, row: IpamProviderAccount, data: IpamProviderAccountUpdate) -> IpamProviderAccount:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
        row.tenant_id = data.tenant_id
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_account_slug(db, row.provider_id, data.slug, exclude_id=row.id)
    if data.account_number is not None:
        row.account_number = data.account_number.strip() if data.account_number else None
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_account(db: Session, row: IpamProviderAccount) -> None:
    db.delete(row)
    db.commit()


def require_provider_refs(
    db: Session,
    *,
    provider_id: int | None,
    provider_account_id: int | None,
) -> None:
    if provider_id is not None and db.get(IpamProvider, provider_id) is None:
        raise ipam_error(404, "provider_not_found", "leverandør ikke funnet")
    if provider_account_id is None:
        return
    acc = db.get(IpamProviderAccount, provider_account_id)
    if acc is None:
        raise ipam_error(404, "provider_account_not_found", "leverandørkonto ikke funnet")
    if provider_id is not None and acc.provider_id != provider_id:
        raise ipam_error(400, "provider_account_mismatch", "kontoen tilhører en annen leverandør")


def provider_to_read(row: IpamProvider) -> IpamProviderRead:
    return IpamProviderRead.model_validate(row)


def account_to_read(row: IpamProviderAccount) -> IpamProviderAccountRead:
    return IpamProviderAccountRead.model_validate(row)
