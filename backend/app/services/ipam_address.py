"""IPAM: varig inventory av IPv4-adresser + request/reservering/tildeling."""

from __future__ import annotations

import ipaddress
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInterface, InterfaceIpAssignment
from app.models.iam import User
from app.models.ipam import IpamIpv4Address, IpamIpv4Prefix
from app.schemas.ipam import Ipv4AddressPatch, Ipv4AddressRead, Ipv4AddressRequest, UserCreate, UserRead
from app.services import dcim as dcim_svc


def list_users(db: Session, *, limit: int = 200) -> list[UserRead]:
    q = select(User).order_by(User.username).limit(limit)
    return [UserRead.model_validate(x) for x in db.execute(q).scalars().all()]


def create_user(db: Session, data: UserCreate) -> UserRead:
    row = User(username=data.username, display_name=data.display_name)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="username finnes allerede") from None
    db.refresh(row)
    return UserRead.model_validate(row)


def list_ipv4_addresses(
    db: Session,
    *,
    site_id: int | None,
    ipv4_prefix_id: int | None,
    status: str | None,
    limit: int,
) -> list[Ipv4AddressRead]:
    q: Select = select(IpamIpv4Address).order_by(IpamIpv4Address.address).limit(limit)
    if site_id is not None:
        q = q.where(IpamIpv4Address.site_id == site_id)
    if ipv4_prefix_id is not None:
        q = q.where(IpamIpv4Address.ipv4_prefix_id == ipv4_prefix_id)
    if status is not None:
        q = q.where(IpamIpv4Address.status == status)
    return [Ipv4AddressRead.model_validate(x) for x in db.execute(q).scalars().all()]


def get_ipv4_address(db: Session, addr_id: int) -> IpamIpv4Address | None:
    return db.get(IpamIpv4Address, addr_id)


def patch_ipv4_address(db: Session, row: IpamIpv4Address, data: Ipv4AddressPatch) -> Ipv4AddressRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(status_code=400, detail="ingen felter å oppdatere")

    for k, v in patch.items():
        setattr(row, k, v)

    db.commit()
    db.refresh(row)
    return Ipv4AddressRead.model_validate(row)


def _iter_candidate_ipv4_addresses(prefix: IpamIpv4Prefix) -> list[ipaddress.IPv4Address]:
    try:
        net = ipaddress.ip_network(prefix.cidr, strict=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ugyldig prefiks CIDR: {e}") from e
    if net.version != 4:
        raise HTTPException(status_code=400, detail="kun IPv4 støttes")

    # Default: ikke del ut nettverks-/broadcast-adresse for normale subnett.
    if net.prefixlen <= 30:
        return [ipaddress.ip_address(ip) for ip in net.hosts()]  # type: ignore[arg-type]
    return [ipaddress.ip_address(ip) for ip in net]  # /31-/32: alle er brukbare


def _existing_ipv4_addresses_in_use(db: Session) -> set[str]:
    rows = db.execute(select(InterfaceIpAssignment.address).where(InterfaceIpAssignment.family == "ipv4")).scalars().all()
    out: set[str] = set()
    for a in rows:
        s = str(a).strip()
        try:
            ip = ipaddress.ip_address(s)
            if isinstance(ip, ipaddress.IPv4Address):
                out.add(str(ip))
        except ValueError:
            continue
    return out


def _existing_ipam_inventory_site(db: Session, *, site_id: int) -> set[str]:
    rows = db.execute(select(IpamIpv4Address.address).where(IpamIpv4Address.site_id == site_id)).scalars().all()
    out: set[str] = set()
    for a in rows:
        s = str(a).strip()
        try:
            ip = ipaddress.ip_address(s)
            if isinstance(ip, ipaddress.IPv4Address):
                out.add(str(ip))
        except ValueError:
            continue
    return out


def request_ipv4_address(db: Session, data: Ipv4AddressRequest) -> Ipv4AddressRead:
    pfx = db.get(IpamIpv4Prefix, data.ipv4_prefix_id)
    if pfx is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")

    candidates = _iter_candidate_ipv4_addresses(pfx)
    used_dcim = _existing_ipv4_addresses_in_use(db)
    used_ipam = _existing_ipam_inventory_site(db, site_id=pfx.site_id)

    iface: DeviceInterface | None = None
    if data.mode == "assign":
        if data.interface_id is None:
            raise HTTPException(status_code=400, detail="interface_id er påkrevd når mode=assign")
        iface = db.get(DeviceInterface, data.interface_id)
        if iface is None:
            raise HTTPException(status_code=404, detail="interface ikke funnet")
        dev_site = dcim_svc.device_effective_site_id(db, iface.device_id)
        if dev_site is None:
            raise HTTPException(status_code=400, detail="enhet uten rack-plassering kan ikke allokeres IP på site-prefiks")
        if dev_site != pfx.site_id:
            raise HTTPException(status_code=400, detail="interface tilhører en annen site enn prefikset")

    for ip in candidates:
        ip_s = str(ip)
        if ip_s in used_dcim or ip_s in used_ipam:
            continue

        if data.mode == "reserve":
            row = IpamIpv4Address(
                site_id=pfx.site_id,
                ipv4_prefix_id=pfx.id,
                address=ip_s,
                status="reserved",
                owner_user_id=data.owner_user_id,
                note=data.note,
                mac_address=None,
                last_seen_at=None,
                device_type_id=data.device_type_id,
                device_model_id=data.device_model_id,
                device_id=data.device_id,
                interface_id=None,
                interface_ip_assignment_id=None,
            )
            db.add(row)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                # race: prøv neste IP
                used_ipam.add(ip_s)
                continue
            db.refresh(row)
            return Ipv4AddressRead.model_validate(row)

        # mode == assign
        assert iface is not None
        assign = InterfaceIpAssignment(
            interface_id=iface.id,
            ipv4_prefix_id=pfx.id,
            family="ipv4",
            address=ip_s,
            is_primary=False,
        )
        db.add(assign)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            used_dcim.add(ip_s)
            continue

        # Opprett inventory-raden etter at assignment finnes, slik at vi kan linke stabilt.
        row = IpamIpv4Address(
            site_id=pfx.site_id,
            ipv4_prefix_id=pfx.id,
            address=ip_s,
            status="assigned",
            owner_user_id=data.owner_user_id,
            note=data.note,
            mac_address=None,
            last_seen_at=None,
            device_type_id=data.device_type_id,
            device_model_id=data.device_model_id,
            device_id=data.device_id or iface.device_id,
            interface_id=iface.id,
            interface_ip_assignment_id=assign.id,
        )
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # rydde i tildeling hvis inventory-unikhet stopper oss
            try:
                db.delete(assign)
                db.commit()
            except Exception:  # noqa: BLE001
                db.rollback()
            used_ipam.add(ip_s)
            continue

        db.refresh(row)
        return Ipv4AddressRead.model_validate(row)

    raise HTTPException(status_code=409, detail="ingen ledig adresse i prefikset")
