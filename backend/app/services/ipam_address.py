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
    Ipv4AddressEnsure,
    Ipv4AddressPatch,
    Ipv4AddressRead,
    Ipv4AddressRequest,
    UserCreate,
    UserRead,
)
from app.services import dcim as dcim_svc
from app.services import ipam as ipam_svc
from app.services.ipam_errors import ipam_error

_IN_USE_STATUSES = frozenset({"planned", "reserved", "assigned", "dhcp"})
_MODE_TO_STATUS = {"reserve": "reserved", "assign": "assigned"}


def _ipv4_address_read(
    db: Session,
    row: IpamIpv4Address,
    *,
    interface_names: dict[int, str] | None = None,
    created: bool | None = None,
) -> Ipv4AddressRead:
    base = Ipv4AddressRead.model_validate(row)
    extra = {"created": created}
    if row.interface_id is None:
        return base.model_copy(update={**extra, "interface_name": None})
    if interface_names is not None:
        iname = interface_names.get(row.interface_id)
    else:
        iface = db.get(DeviceInterface, row.interface_id)
        iname = iface.name if iface is not None else None
    return base.model_copy(update={**extra, "interface_name": iname})


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
    offset: int = 0,
    address: str | None = None,
    q: str | None = None,
    device_id: int | None = None,
    role: str | None = None,
) -> list[Ipv4AddressRead]:
    stmt: Select = select(IpamIpv4Address).order_by(IpamIpv4Address.address)
    if site_id is not None:
        stmt = stmt.where(IpamIpv4Address.site_id == site_id)
    if ipv4_prefix_id is not None:
        stmt = stmt.where(IpamIpv4Address.ipv4_prefix_id == ipv4_prefix_id)
    if status is not None:
        stmt = stmt.where(IpamIpv4Address.status == status)
    if role is not None:
        stmt = stmt.where(IpamIpv4Address.role == role)
    if device_id is not None:
        stmt = stmt.where(IpamIpv4Address.device_id == device_id)
    if address is not None:
        try:
            ip = ipaddress.ip_address(address.strip())
        except ValueError as e:
            raise ipam_error(400, "invalid_address", f"ugyldig adresse: {e}") from e
        stmt = stmt.where(IpamIpv4Address.address == str(ip))
    rows = list(db.execute(stmt).scalars().all())
    if q is not None:
        needle = q.strip().lower()
        if needle:
            rows = [
                r
                for r in rows
                if needle in (r.address or "").lower()
                or needle in (r.note or "").lower()
                or needle in (getattr(r, "hostname", None) or "").lower()
                or needle in (getattr(r, "fqdn", None) or "").lower()
                or needle in (getattr(r, "dns_name", None) or "").lower()
            ]
    if offset:
        rows = rows[offset:]
    rows = rows[:limit]
    if_ids = {r.interface_id for r in rows if r.interface_id is not None}
    names: dict[int, str] = {}
    if if_ids:
        qi = select(DeviceInterface.id, DeviceInterface.name).where(DeviceInterface.id.in_(if_ids))
        names = dict(db.execute(qi).all())
    return [_ipv4_address_read(db, r, interface_names=names) for r in rows]


def get_ipv4_address(db: Session, addr_id: int) -> IpamIpv4Address | None:
    return db.get(IpamIpv4Address, addr_id)


def get_ipv4_address_read(db: Session, addr_id: int) -> Ipv4AddressRead:
    row = get_ipv4_address(db, addr_id)
    if row is None:
        raise ipam_error(404, "address_not_found", "IP-adresse ikke funnet")
    return _ipv4_address_read(db, row)


def delete_ipv4_address(db: Session, row: IpamIpv4Address) -> None:
    if row.interface_ip_assignment_id is not None:
        assign = db.get(InterfaceIpAssignment, row.interface_ip_assignment_id)
        if assign is not None:
            db.delete(assign)
    db.delete(row)
    db.commit()


def _parse_ipv4_in_prefix(pfx: IpamIpv4Prefix, address: str) -> ipaddress.IPv4Address:
    try:
        ip = ipaddress.ip_address(address.strip())
    except ValueError as e:
        raise ipam_error(400, "invalid_address", f"ugyldig adresse: {e}") from e
    if not isinstance(ip, ipaddress.IPv4Address):
        raise ipam_error(400, "ipv4_only", "kun IPv4")
    net = ipaddress.ip_network(pfx.cidr, strict=False)
    if ip not in net:
        raise ipam_error(400, "address_outside_prefix", "adressen ligger ikke i prefiksnettet")
    return ip


def ensure_ipv4_address(db: Session, data: Ipv4AddressEnsure, *, update: bool = False) -> Ipv4AddressRead:
    pfx = db.get(IpamIpv4Prefix, data.ipv4_prefix_id)
    if pfx is None:
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    ip = _parse_ipv4_in_prefix(pfx, data.address)
    ip_s = str(ip)

    status = data.status
    if data.mode is not None:
        status = _MODE_TO_STATUS[data.mode]
    addr_role = data.role
    static_alloc = status in ("reserved", "assigned") or data.mode in ("reserve", "assign")
    if static_alloc:
        ipam_svc.require_host_allocation(pfx)
        if ip_s in _network_broadcast_ips(pfx):
            raise ipam_error(
                400,
                "network_broadcast_forbidden",
                "kan ikke reservere eller tildele nettverks- eller broadcast-adresse",
            )
        if ip_s in _gateway_ips(pfx) and addr_role != "gateway":
            raise ipam_error(
                409,
                "gateway_protected",
                "gateway er urørlig med mindre role=gateway settes bevisst",
            )
        if ip_s in _dhcp_range_ips(pfx) and addr_role != "dhcp":
            raise ipam_error(
                409,
                "dhcp_range_protected",
                "adressen ligger i dhcp_range og kan ikke tildeles statisk uten role=dhcp",
            )

    iface = _resolve_assign_interface(db, pfx, data)

    row = _inventory_row_for_site_address(db, site_id=pfx.site_id, address=ip_s)
    if row is not None and not update:
        return _ipv4_address_read(db, row, created=False)

    assign: InterfaceIpAssignment | None = None
    if status == "assigned" and iface is not None and (row is None or row.interface_ip_assignment_id is None):
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
            raise ipam_error(409, "address_already_assigned", "adressen er allerede tildelt i DCIM") from None

    created = row is None
    if row is None:
        row = IpamIpv4Address(
            site_id=pfx.site_id,
            ipv4_prefix_id=pfx.id,
            address=ip_s,
            status=status or "discovered",
            role=addr_role or ("gateway" if ip_s in _gateway_ips(pfx) else "host"),
            hostname=data.hostname,
            fqdn=data.fqdn,
            dns_name=data.dns_name,
            owner_user_id=data.owner_user_id,
            note=data.note,
            mac_address=None,
            last_seen_at=None,
            device_type_id=data.device_type_id,
            device_model_id=data.device_model_id,
            device_id=data.device_id or (iface.device_id if iface is not None else None),
            interface_id=iface.id if iface is not None else None,
            interface_ip_assignment_id=assign.id if assign is not None else None,
        )
        db.add(row)
    else:
        if row.ipv4_prefix_id is None:
            row.ipv4_prefix_id = pfx.id
        if status is not None:
            row.status = status
        if addr_role is not None:
            row.role = addr_role
        if data.hostname is not None:
            row.hostname = data.hostname
        if data.fqdn is not None:
            row.fqdn = data.fqdn
        if data.dns_name is not None:
            row.dns_name = data.dns_name
        if data.note is not None:
            row.note = data.note
        if data.owner_user_id is not None:
            row.owner_user_id = data.owner_user_id
        if data.device_type_id is not None:
            row.device_type_id = data.device_type_id
        if data.device_model_id is not None:
            row.device_model_id = data.device_model_id
        if data.device_id is not None:
            row.device_id = data.device_id
        elif iface is not None:
            row.device_id = iface.device_id
        if iface is not None:
            row.interface_id = iface.id
        if assign is not None:
            row.interface_ip_assignment_id = assign.id

    db.commit()
    db.refresh(row)
    return _ipv4_address_read(db, row, created=created)


def patch_ipv4_address(db: Session, row: IpamIpv4Address, data: Ipv4AddressPatch) -> Ipv4AddressRead:
    patch = data.model_dump(exclude_unset=True)
    if not patch:
        raise ipam_error(400, "empty_patch", "ingen felter å oppdatere")

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


def _existing_ipam_in_use(db: Session, *, site_id: int) -> set[str]:
    rows = db.execute(
        select(IpamIpv4Address.address).where(
            IpamIpv4Address.site_id == site_id,
            IpamIpv4Address.status.in_(tuple(_IN_USE_STATUSES)),
        ),
    ).scalars().all()
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


def _gateway_ips(pfx: IpamIpv4Prefix) -> set[str]:
    services = getattr(pfx, "subnet_services", None) or {}
    if not isinstance(services, dict):
        return set()
    raw = services.get("gateway")
    values: list[str] = []
    if isinstance(raw, str):
        values.append(raw)
    elif isinstance(raw, list):
        values.extend(str(x) for x in raw if x is not None)
    out: set[str] = set()
    try:
        net = ipaddress.ip_network(pfx.cidr, strict=False)
    except ValueError:
        return out
    for v in values:
        try:
            ip = ipaddress.ip_address(str(v).strip())
        except ValueError:
            continue
        if isinstance(ip, ipaddress.IPv4Address) and ip in net:
            out.add(str(ip))
    return out


def _network_broadcast_ips(pfx: IpamIpv4Prefix) -> set[str]:
    try:
        net = ipaddress.ip_network(pfx.cidr, strict=False)
    except ValueError:
        return set()
    if net.version != 4 or net.prefixlen > 30:
        return set()
    return {str(net.network_address), str(net.broadcast_address)}


def _dhcp_range_ips(pfx: IpamIpv4Prefix) -> set[str]:
    services = getattr(pfx, "subnet_services", None) or {}
    if not isinstance(services, dict):
        return set()
    rng = services.get("dhcp_range")
    if not isinstance(rng, dict):
        return set()
    try:
        start = ipaddress.ip_address(str(rng.get("start", "")).strip())
        end = ipaddress.ip_address(str(rng.get("end", "")).strip())
        net = ipaddress.ip_network(pfx.cidr, strict=False)
    except ValueError:
        return set()
    if not isinstance(start, ipaddress.IPv4Address) or not isinstance(end, ipaddress.IPv4Address):
        return set()
    if int(start) > int(end):
        start, end = end, start
    last = min(int(end), int(start) + 65536)
    out: set[str] = set()
    for n in range(int(start), last + 1):
        ip = ipaddress.IPv4Address(n)
        if ip in net:
            out.add(str(ip))
    return out


def infra_reserved_ips(pfx: IpamIpv4Prefix) -> set[str]:
    """Nettverk, broadcast, gateway og DHCP-intervall — hoppes over ved statisk host-alloc."""
    return _network_broadcast_ips(pfx) | _gateway_ips(pfx) | _dhcp_range_ips(pfx)


def _ordered_ip_candidates_for_batch(pfx: IpamIpv4Prefix, preferred_raw: list[str]) -> list[str]:
    """Foretrukne (gyldige i nettet, unike) først; deretter øvrige vertsadresser (hosts)."""
    try:
        net = ipaddress.ip_network(pfx.cidr, strict=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ugyldig prefiks CIDR: {e}") from e
    if net.version != 4:
        raise HTTPException(status_code=400, detail="kun IPv4 støttes")
    blocked = infra_reserved_ips(pfx)
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
        if t in seen or t in blocked:
            continue
        pref_order.append(t)
        seen.add(t)
    rest = [str(ip) for ip in host_ips if str(ip) not in seen and str(ip) not in blocked]
    return pref_order + rest


def _resolve_assign_interface(
    db: Session,
    pfx: IpamIpv4Prefix,
    data: Ipv4AddressRequest | Ipv4AddressBatchRequest | Ipv4AddressEnsure,
) -> DeviceInterface | None:
    if data.interface_id is None:
        return None
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


def _inventory_row_for_site_address(db: Session, *, site_id: int, address: str) -> IpamIpv4Address | None:
    return db.execute(
        select(IpamIpv4Address).where(
            IpamIpv4Address.site_id == site_id,
            IpamIpv4Address.address == address,
        ),
    ).scalar_one_or_none()


def _fill_inventory_fields(
    row: IpamIpv4Address,
    *,
    status: str,
    owner_user_id: int | None,
    note: str | None,
    device_type_id: int | None,
    device_model_id: int | None,
    device_id: int | None,
    interface_id: int | None,
    interface_ip_assignment_id: int | None,
    ipv4_prefix_id: int,
) -> None:
    row.status = status
    row.ipv4_prefix_id = ipv4_prefix_id
    if owner_user_id is not None:
        row.owner_user_id = owner_user_id
    if note is not None:
        row.note = note
    if device_type_id is not None:
        row.device_type_id = device_type_id
    if device_model_id is not None:
        row.device_model_id = device_model_id
    if device_id is not None:
        row.device_id = device_id
    row.interface_id = interface_id
    row.interface_ip_assignment_id = interface_ip_assignment_id


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

    existing = _inventory_row_for_site_address(db, site_id=pfx.site_id, address=ip_s)
    if existing is not None and existing.status in _IN_USE_STATUSES:
        used_ipam.add(ip_s)
        return None

    status = _MODE_TO_STATUS[mode]
    bind_iface = iface if mode == "assign" else None
    assign: InterfaceIpAssignment | None = None
    if bind_iface is not None:
        assign = InterfaceIpAssignment(
            interface_id=bind_iface.id,
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

    if existing is None:
        row = IpamIpv4Address(
            site_id=pfx.site_id,
            ipv4_prefix_id=pfx.id,
            address=ip_s,
            status=status,
            owner_user_id=owner_user_id,
            note=note,
            mac_address=None,
            last_seen_at=None,
            device_type_id=device_type_id,
            device_model_id=device_model_id,
            device_id=device_id or (bind_iface.device_id if bind_iface is not None else None),
            interface_id=bind_iface.id if bind_iface is not None else None,
            interface_ip_assignment_id=assign.id if assign is not None else None,
        )
        db.add(row)
    else:
        _fill_inventory_fields(
            existing,
            status=status,
            owner_user_id=owner_user_id,
            note=note,
            device_type_id=device_type_id,
            device_model_id=device_model_id,
            device_id=device_id or (bind_iface.device_id if bind_iface is not None else existing.device_id),
            interface_id=bind_iface.id if bind_iface is not None else None,
            interface_ip_assignment_id=assign.id if assign is not None else None,
            ipv4_prefix_id=pfx.id,
        )
        row = existing

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if assign is not None:
            try:
                gone = db.get(InterfaceIpAssignment, assign.id)
                if gone is not None:
                    db.delete(gone)
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
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    ipam_svc.require_host_allocation(pfx)

    iface = _resolve_assign_interface(db, pfx, data)

    order = _ordered_ip_candidates_for_batch(pfx, data.preferred_addresses)
    used_dcim = _existing_ipv4_addresses_in_use(db)
    used_ipam = _existing_ipam_in_use(db, site_id=pfx.site_id)
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
        raise ipam_error(409, "no_free_address", "ingen ledig adresse i prefikset")
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
