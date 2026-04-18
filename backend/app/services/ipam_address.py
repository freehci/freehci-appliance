"""IPAM: varig inventory av IPv4-adresser + request/reservering/tildeling."""

from __future__ import annotations

import ipaddress

from fastapi import HTTPException
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInterface, InterfaceIpAssignment
from app.models.iam import User
from app.models.ipam import IpamIpv4Address, IpamIpv4Prefix
from app.schemas.ipam import (
    Ipv4AddressBatchRead,
    Ipv4AddressBatchRequest,
    Ipv4AddressPatch,
    Ipv4AddressRead,
    Ipv4AddressRequest,
    UserCreate,
    UserRead,
)
from app.services import dcim as dcim_svc


def _ipv4_address_read(
    db: Session,
    row: IpamIpv4Address,
    *,
    interface_names: dict[int, str] | None = None,
) -> Ipv4AddressRead:
    base = Ipv4AddressRead.model_validate(row)
    if row.interface_id is None:
        return base.model_copy(update={"interface_name": None})
    if interface_names is not None:
        iname = interface_names.get(row.interface_id)
    else:
        iface = db.get(DeviceInterface, row.interface_id)
        iname = iface.name if iface is not None else None
    return base.model_copy(update={"interface_name": iname})


def list_users(db: Session, *, limit: int = 200, kind: str | None = None) -> list[UserRead]:
    q = select(User).order_by(User.username).limit(limit)
    if kind is not None:
        q = q.where(User.kind == kind)
    return [UserRead.model_validate(x) for x in db.execute(q).scalars().all()]


def create_user(db: Session, data: UserCreate) -> UserRead:
    row = User(
        username=data.username,
        display_name=data.display_name,
        email=data.email,
        phone=data.phone,
        kind=data.kind,
        notes=data.notes,
        external_subject_id=data.external_subject_id,
        identity_provider=data.identity_provider,
    )
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
    rows = list(db.execute(q).scalars().all())
    if_ids = {r.interface_id for r in rows if r.interface_id is not None}
    names: dict[int, str] = {}
    if if_ids:
        qi = select(DeviceInterface.id, DeviceInterface.name).where(DeviceInterface.id.in_(if_ids))
        names = dict(db.execute(qi).all())
    return [_ipv4_address_read(db, r, interface_names=names) for r in rows]


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
    return _ipv4_address_read(db, row)


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


def _ordered_ip_candidates_for_batch(pfx: IpamIpv4Prefix, preferred_raw: list[str]) -> list[str]:
    """Foretrukne (gyldige i nettet, unike) først; deretter øvrige vertsadresser (hosts)."""
    try:
        net = ipaddress.ip_network(pfx.cidr, strict=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ugyldig prefiks CIDR: {e}") from e
    if net.version != 4:
        raise HTTPException(status_code=400, detail="kun IPv4 støttes")
    host_ips = list(net.hosts()) if net.prefixlen <= 30 else list(net)
    pref_order: list[str] = []
    seen: set[str] = set()
    for raw in preferred_raw:
        s = raw.strip()
        if not s:
            continue
        try:
            ip = ipaddress.ip_address(s)
        except ValueError:
            continue
        if not isinstance(ip, ipaddress.IPv4Address) or ip not in net:
            continue
        t = str(ip)
        if t in seen:
            continue
        pref_order.append(t)
        seen.add(t)
    rest = [str(ip) for ip in host_ips if str(ip) not in seen]
    return pref_order + rest


def _resolve_assign_interface(db: Session, pfx: IpamIpv4Prefix, data: Ipv4AddressRequest | Ipv4AddressBatchRequest) -> DeviceInterface:
    if data.interface_id is None:
        raise HTTPException(status_code=400, detail="interface_id er påkrevd når mode=assign")
    iface = db.get(DeviceInterface, data.interface_id)
    if iface is None:
        raise HTTPException(status_code=404, detail="interface ikke funnet")
    if data.device_id is not None and data.device_id != iface.device_id:
        raise HTTPException(
            status_code=400,
            detail="device_id stemmer ikke med grensesnittets enhet",
        )
    dev_site = dcim_svc.device_effective_site_id(db, iface.device_id)
    if dev_site is None:
        raise HTTPException(status_code=400, detail="enhet uten rack-plassering kan ikke allokeres IP på site-prefiks")
    if dev_site != pfx.site_id:
        raise HTTPException(status_code=400, detail="interface tilhører en annen site enn prefikset")
    return iface


def _try_allocate_one_ip(
    db: Session,
    pfx: IpamIpv4Prefix,
    ip_s: str,
    *,
    mode: str,
    iface: DeviceInterface | None,
    owner_user_id: int | None,
    note: str | None,
    device_type_id: int | None,
    device_model_id: int | None,
    device_id: int | None,
    used_dcim: set[str],
    used_ipam: set[str],
) -> IpamIpv4Address | None:
    if ip_s in used_dcim or ip_s in used_ipam:
        return None

    if mode == "reserve":
        row = IpamIpv4Address(
            site_id=pfx.site_id,
            ipv4_prefix_id=pfx.id,
            address=ip_s,
            status="reserved",
            owner_user_id=owner_user_id,
            note=note,
            mac_address=None,
            last_seen_at=None,
            device_type_id=device_type_id,
            device_model_id=device_model_id,
            device_id=device_id,
            interface_id=None,
            interface_ip_assignment_id=None,
        )
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            used_ipam.add(ip_s)
            return None
        db.refresh(row)
        return row

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
        return None

    row = IpamIpv4Address(
        site_id=pfx.site_id,
        ipv4_prefix_id=pfx.id,
        address=ip_s,
        status="assigned",
        owner_user_id=owner_user_id,
        note=note,
        mac_address=None,
        last_seen_at=None,
        device_type_id=device_type_id,
        device_model_id=device_model_id,
        device_id=device_id or iface.device_id,
        interface_id=iface.id,
        interface_ip_assignment_id=assign.id,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        try:
            db.delete(assign)
            db.commit()
        except Exception:  # noqa: BLE001
            db.rollback()
        used_ipam.add(ip_s)
        return None

    db.refresh(row)
    return row


def request_ipv4_addresses_batch(db: Session, data: Ipv4AddressBatchRequest) -> Ipv4AddressBatchRead:
    pfx = db.get(IpamIpv4Prefix, data.ipv4_prefix_id)
    if pfx is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")

    iface: DeviceInterface | None = None
    if data.mode == "assign":
        iface = _resolve_assign_interface(db, pfx, data)

    order = _ordered_ip_candidates_for_batch(pfx, data.preferred_addresses)
    used_dcim = _existing_ipv4_addresses_in_use(db)
    used_ipam = _existing_ipam_inventory_site(db, site_id=pfx.site_id)
    reads: list[Ipv4AddressRead] = []

    for _ in range(data.count):
        got_row: IpamIpv4Address | None = None
        for ip_s in order:
            row = _try_allocate_one_ip(
                db,
                pfx,
                ip_s,
                mode=data.mode,
                iface=iface,
                owner_user_id=data.owner_user_id,
                note=data.note,
                device_type_id=data.device_type_id,
                device_model_id=data.device_model_id,
                device_id=data.device_id,
                used_dcim=used_dcim,
                used_ipam=used_ipam,
            )
            if row is not None:
                got_row = row
                used_ipam.add(ip_s)
                break
        if got_row is None:
            break
        reads.append(_ipv4_address_read(db, got_row))

    if not reads:
        raise HTTPException(status_code=409, detail="ingen ledig adresse i prefikset")
    return Ipv4AddressBatchRead(
        addresses=reads,
        requested_count=data.count,
        allocated_count=len(reads),
    )


def request_ipv4_address(db: Session, data: Ipv4AddressRequest) -> Ipv4AddressRead:
    batch = Ipv4AddressBatchRequest(
        ipv4_prefix_id=data.ipv4_prefix_id,
        mode=data.mode,
        count=1,
        preferred_addresses=[],
        interface_id=data.interface_id,
        owner_user_id=data.owner_user_id,
        note=data.note,
        device_type_id=data.device_type_id,
        device_model_id=data.device_model_id,
        device_id=data.device_id,
    )
    out = request_ipv4_addresses_batch(db, batch)
    return out.addresses[0]


def release_ipv4_address(db: Session, row: IpamIpv4Address) -> Ipv4AddressRead:
    """Frigi reservasjon/tildeling.

    - Hvis raden peker på `dcim_interface_ip_assignments`, slettes den tildelingen.
    - Inventory-raden beholdes, men settes til status=discovered og koblinger nulles.
    """
    if row.interface_ip_assignment_id is not None:
        assign = db.get(InterfaceIpAssignment, row.interface_ip_assignment_id)
        if assign is not None:
            db.delete(assign)

    row.status = "discovered"
    row.interface_ip_assignment_id = None
    row.interface_id = None
    row.device_id = None
    row.device_model_id = None
    row.device_type_id = None
    db.commit()
    db.refresh(row)
    return _ipv4_address_read(db, row)
