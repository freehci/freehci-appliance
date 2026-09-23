"""IPAM-leverandører, kundekontoer og kontrakter. Aldri gjettet fra fritekst."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamCircuit, IpamContract, IpamProvider, IpamProviderAccount
from app.models.tenant import Tenant
from app.schemas.ipam import (
    IpamContractCreate,
    IpamContractRead,
    IpamContractUpdate,
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
    contracts = list(db.execute(select(IpamContract).where(IpamContract.provider_id == row.id)).scalars().all())
    contract_ids = [c.id for c in contracts]
    if contract_ids:
        for circ in db.execute(select(IpamCircuit).where(IpamCircuit.contract_id.in_(contract_ids))).scalars().all():
            circ.contract_id = None
        for c in contracts:
            db.delete(c)
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


def _unique_contract_slug(db: Session, provider_id: int, desired: str, *, exclude_id: int | None = None) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while True:
        q = select(IpamContract.id).where(IpamContract.provider_id == provider_id, IpamContract.slug == candidate)
        if exclude_id is not None:
            q = q.where(IpamContract.id != exclude_id)
        if db.execute(q).scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"[:128]
        n += 1


def list_contracts(
    db: Session,
    *,
    provider_id: int | None = None,
    tenant_id: int | None = None,
) -> list[IpamContract]:
    q = select(IpamContract)
    if provider_id is not None:
        q = q.where(IpamContract.provider_id == provider_id)
    if tenant_id is not None:
        q = q.where(IpamContract.tenant_id == tenant_id)
    return list(db.execute(q.order_by(IpamContract.name)).scalars().all())


def get_contract(db: Session, contract_id: int) -> IpamContract | None:
    return db.get(IpamContract, contract_id)


def get_contract_by_slug(db: Session, provider_id: int, slug: str) -> IpamContract | None:
    return db.execute(
        select(IpamContract).where(IpamContract.provider_id == provider_id, IpamContract.slug == slug),
    ).scalar_one_or_none()


def _require_contract_account(db: Session, *, provider_id: int, provider_account_id: int | None) -> None:
    if provider_account_id is None:
        return
    acc = db.get(IpamProviderAccount, provider_account_id)
    if acc is None:
        raise ipam_error(404, "provider_account_not_found", "leverandørkonto ikke funnet")
    if acc.provider_id != provider_id:
        raise ipam_error(400, "provider_account_mismatch", "kontoen tilhører en annen leverandør")


def create_contract(db: Session, data: IpamContractCreate) -> IpamContract:
    provider = get_provider(db, data.provider_id)
    if provider is None:
        raise ipam_error(404, "provider_not_found", "leverandør ikke funnet")
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
    _require_contract_account(db, provider_id=provider.id, provider_account_id=data.provider_account_id)
    slug = _slugify(data.slug) if data.slug else _unique_contract_slug(db, provider.id, data.name)
    row = IpamContract(
        provider_id=provider.id,
        provider_account_id=data.provider_account_id,
        tenant_id=data.tenant_id,
        name=data.name.strip(),
        slug=slug,
        reference=data.reference.strip() if data.reference else None,
        starts_on=data.starts_on,
        ends_on=data.ends_on,
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


def update_contract(db: Session, row: IpamContract, data: IpamContractUpdate) -> IpamContract:
    if data.tenant_id is not None:
        _require_tenant(db, data.tenant_id)
        row.tenant_id = data.tenant_id
    if data.provider_account_id is not None:
        _require_contract_account(db, provider_id=row.provider_id, provider_account_id=data.provider_account_id)
        row.provider_account_id = data.provider_account_id
    if data.name is not None:
        row.name = data.name.strip()
    if data.slug is not None:
        row.slug = _unique_contract_slug(db, row.provider_id, data.slug, exclude_id=row.id)
    if data.reference is not None:
        row.reference = data.reference.strip() if data.reference else None
    if data.starts_on is not None:
        row.starts_on = data.starts_on
    if data.ends_on is not None:
        row.ends_on = data.ends_on
    if data.description is not None:
        row.description = data.description
    db.commit()
    db.refresh(row)
    return row


def delete_contract(db: Session, row: IpamContract) -> None:
    for circ in db.execute(select(IpamCircuit).where(IpamCircuit.contract_id == row.id)).scalars().all():
        circ.contract_id = None
    db.delete(row)
    db.commit()


def require_contract_ref(
    db: Session,
    *,
    contract_id: int | None,
    provider_id: int | None,
) -> IpamContract | None:
    if contract_id is None:
        return None
    row = db.get(IpamContract, contract_id)
    if row is None:
        raise ipam_error(404, "contract_not_found", "kontrakt ikke funnet")
    if provider_id is not None and row.provider_id != provider_id:
        raise ipam_error(400, "contract_provider_mismatch", "kontrakten tilhører en annen leverandør")
    return row


def provider_to_read(row: IpamProvider) -> IpamProviderRead:
    return IpamProviderRead.model_validate(row)


def account_to_read(row: IpamProviderAccount) -> IpamProviderAccountRead:
    return IpamProviderAccountRead.model_validate(row)


def contract_to_read(row: IpamContract) -> IpamContractRead:
    return IpamContractRead.model_validate(row)
