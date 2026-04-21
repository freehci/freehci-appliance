"""Del IPv4-prefiks i to barn med validering og valgfri migrering av IPAM/DCIM."""

from __future__ import annotations

import ipaddress

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dcim import DeviceIpAssignment, DeviceInterface, InterfaceIpAssignment
from app.models.ipam import IpamIpv4Address, IpamIpv4Prefix
from app.schemas.ipam import (
    Ipv4PrefixRead,
    Ipv4PrefixSplitConflictRead,
    Ipv4PrefixSplitRequest,
    Ipv4PrefixSplitResponse,
)
from app.services import dcim as dcim_svc
from app.services import ipam as ipam_svc


def _same_site_prefix_rows(db: Session, site_id: int) -> list[IpamIpv4Prefix]:
    return list(db.execute(select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == site_id)).scalars().all())


def _two_nets_partition_parent(
    parent: ipaddress.IPv4Network,
    a: ipaddress.IPv4Network,
    b: ipaddress.IPv4Network,
) -> bool:
    if a.version != 4 or b.version != 4 or parent.version != 4:
        return False
    if not a.subnet_of(parent) or not b.subnet_of(parent):
        return False
    if a == b:
        return False
    if a.overlaps(b):
        return False
    rem = list(parent.address_exclude(a))
    if rem == [b]:
        return True
    rem2 = list(parent.address_exclude(b))
    return rem2 == [a]


def _ip_net_role(ip: ipaddress.IPv4Address, net: ipaddress.IPv4Network) -> str | None:
    if ip == net.network_address:
        return "network"
    if ip == net.broadcast_address:
        return "broadcast"
    return None


def _child_label_for_ip(
    ip: ipaddress.IPv4Address,
    first: ipaddress.IPv4Network,
    second: ipaddress.IPv4Network,
) -> str:
    if ip in first:
        return "first"
    if ip in second:
        return "second"
    raise ValueError("adresse utenfor begge barn")


def ipv4_prefix_split(db: Session, parent_id: int, data: Ipv4PrefixSplitRequest) -> Ipv4PrefixSplitResponse:
    parent = ipam_svc.get_ipv4_prefix(db, parent_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")

    same_site = _same_site_prefix_rows(db, parent.site_id)
    children = ipam_svc._child_prefix_orms(parent, same_site)  # type: ignore[attr-defined]
    has_children = len(children) > 0

    out = Ipv4PrefixSplitResponse(
        dry_run=data.dry_run,
        has_child_prefixes=has_children,
        partition_ok=False,
        detail=None,
        first_cidr=None,
        second_cidr=None,
        ipam_inventory_on_parent=0,
        ipam_migrate_left=0,
        ipam_migrate_right=0,
        dcim_iface_on_parent=0,
        dcim_device_on_parent=0,
        conflicts=[],
        first_prefix=None,
        second_prefix=None,
    )

    if has_children:
        out.detail = "kan ikke dele prefiks som allerede har registrerte underprefiks — slett eller flytt barn først"
        return out

    try:
        pnet = ipaddress.ip_network(parent.cidr, strict=False)
        if pnet.version != 4:
            raise ValueError("kun IPv4")
        a_net = ipaddress.ip_network(ipam_svc._normalize_ipv4_cidr(data.first.cidr), strict=False)  # type: ignore[attr-defined]
        b_net = ipaddress.ip_network(ipam_svc._normalize_ipv4_cidr(data.second.cidr), strict=False)  # type: ignore[attr-defined]
    except ValueError as e:
        out.detail = str(e)
        return out
    except HTTPException as e:
        out.detail = str(e.detail) if isinstance(e.detail, str) else "ugyldig CIDR"
        return out

    if not _two_nets_partition_parent(pnet, a_net, b_net):
        out.detail = (
            "de to CIDR-ene må være disjunkte undernett av forelderen og til sammen dekke hele "
            f"{parent.cidr} uten hull (f.eks. to like halvdeler /{pnet.prefixlen + 1})"
        )
        return out

    out.partition_ok = True
    out.first_cidr = str(a_net)
    out.second_cidr = str(b_net)

    inv_rows = list(
        db.execute(select(IpamIpv4Address).where(IpamIpv4Address.ipv4_prefix_id == parent_id)).scalars().all(),
    )
    out.ipam_inventory_on_parent = len(inv_rows)

    iface_rows = list(
        db.execute(
            select(InterfaceIpAssignment).where(
                InterfaceIpAssignment.ipv4_prefix_id == parent_id,
                InterfaceIpAssignment.family == "ipv4",
            ),
        )
        .scalars()
        .all(),
    )
    out.dcim_iface_on_parent = len(iface_rows)

    dev_rows = list(
        db.execute(
            select(DeviceIpAssignment).where(
                DeviceIpAssignment.ipv4_prefix_id == parent_id,
                DeviceIpAssignment.family == "ipv4",
            ),
        )
        .scalars()
        .all(),
    )
    out.dcim_device_on_parent = len(dev_rows)

    conflict_keys: set[tuple[str, str, str]] = set()
    conflicts: list[Ipv4PrefixSplitConflictRead] = []

    def note_conflict(ip_s: str, net: ipaddress.IPv4Network, ch: str) -> None:
        try:
            ip = ipaddress.ip_address(ip_s.strip())
        except ValueError:
            return
        if not isinstance(ip, ipaddress.IPv4Address):
            return
        role = _ip_net_role(ip, net)
        if role is None:
            return
        key = (str(ip), ch, role)
        if key in conflict_keys:
            return
        conflict_keys.add(key)
        msg = f"adressen er {role} i {net}"
        conflicts.append(
            Ipv4PrefixSplitConflictRead(
                address=str(ip),
                role=role,  # type: ignore[arg-type]
                child=ch,  # type: ignore[arg-type]
                message=msg,
            ),
        )

    for r in inv_rows:
        try:
            ip = ipaddress.ip_address(r.address.strip())
        except ValueError:
            continue
        if not isinstance(ip, ipaddress.IPv4Address):
            continue
        try:
            ch = _child_label_for_ip(ip, a_net, b_net)
        except ValueError:
            continue
        net = a_net if ch == "first" else b_net
        note_conflict(r.address, net, ch)

    for r in iface_rows:
        try:
            ip = ipaddress.ip_address(r.address.strip())
        except ValueError:
            continue
        if not isinstance(ip, ipaddress.IPv4Address):
            continue
        try:
            ch = _child_label_for_ip(ip, a_net, b_net)
        except ValueError:
            continue
        net = a_net if ch == "first" else b_net
        note_conflict(r.address, net, ch)

    for r in dev_rows:
        try:
            ip = ipaddress.ip_address(r.address.strip())
        except ValueError:
            continue
        if not isinstance(ip, ipaddress.IPv4Address):
            continue
        try:
            ch = _child_label_for_ip(ip, a_net, b_net)
        except ValueError:
            continue
        net = a_net if ch == "first" else b_net
        note_conflict(r.address, net, ch)

    out.conflicts = conflicts

    out.ipam_migrate_left = sum(
        1
        for r in inv_rows
        if _ipv4_in_net_safe(r.address, a_net)
    )
    out.ipam_migrate_right = sum(
        1
        for r in inv_rows
        if _ipv4_in_net_safe(r.address, b_net)
    )

    if data.dry_run:
        out.detail = "dry_run: ingen endringer lagret"
        return out

    if not data.migrate_inventory and (
        out.ipam_inventory_on_parent > 0 or out.dcim_iface_on_parent > 0 or out.dcim_device_on_parent > 0
    ):
        raise HTTPException(
            status_code=400,
            detail="det finnes IPAM-rader eller DCIM-tildelinger på prefikset — slå på migrate_inventory eller rydd først",
        )

    if conflicts and not data.acknowledge_network_broadcast:
        parts = [f"{c.address} ({c.role} i {c.child})" for c in conflicts]
        raise HTTPException(
            status_code=409,
            detail="nettverks-/broadcast-konflikter: "
            + "; ".join(parts)
            + " — bekreft med acknowledge_network_broadcast=true",
        )

    for row in same_site:
        if row.id == parent_id:
            continue
        if str(row.cidr) in (out.first_cidr, out.second_cidr):
            raise HTTPException(status_code=409, detail=f"CIDR finnes allerede: {row.cidr}")

    ipam_svc._require_no_partial_overlap(db, site_id=parent.site_id, cidr=out.first_cidr)  # type: ignore[attr-defined]
    ipam_svc._require_no_partial_overlap(db, site_id=parent.site_id, cidr=out.second_cidr)  # type: ignore[attr-defined]

    left = IpamIpv4Prefix(
        site_id=parent.site_id,
        tenant_id=parent.tenant_id,
        vlan_id=parent.vlan_id,
        vrf_id=parent.vrf_id,
        name=data.first.name.strip(),
        cidr=out.first_cidr,
        description=None,
        subnet_services=None,
    )
    right = IpamIpv4Prefix(
        site_id=parent.site_id,
        tenant_id=parent.tenant_id,
        vlan_id=parent.vlan_id,
        vrf_id=parent.vrf_id,
        name=data.second.name.strip(),
        cidr=out.second_cidr,
        description=None,
        subnet_services=None,
    )
    db.add(left)
    db.add(right)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="kunne ikke opprette barn-prefiks (duplikat?)") from None

    if data.migrate_inventory:
        for r in inv_rows:
            try:
                ip = ipaddress.ip_address(r.address.strip())
            except ValueError:
                continue
            if not isinstance(ip, ipaddress.IPv4Address):
                continue
            if ip in a_net:
                r.ipv4_prefix_id = left.id
            elif ip in b_net:
                r.ipv4_prefix_id = right.id

        for r in iface_rows:
            try:
                ip = ipaddress.ip_address(r.address.strip())
            except ValueError:
                continue
            if not isinstance(ip, ipaddress.IPv4Address):
                continue
            iface = db.get(DeviceInterface, r.interface_id)
            if iface is None:
                continue
            new_id = left.id if ip in a_net else right.id
            r.ipv4_prefix_id = dcim_svc._validate_ipv4_prefix_for_assignment(  # type: ignore[attr-defined]
                db,
                device_id=iface.device_id,
                prefix_id=new_id,
                family="ipv4",
                address=r.address,
            )

        for r in dev_rows:
            try:
                ip = ipaddress.ip_address(r.address.strip())
            except ValueError:
                continue
            if not isinstance(ip, ipaddress.IPv4Address):
                continue
            new_id = left.id if ip in a_net else right.id
            r.ipv4_prefix_id = dcim_svc._validate_ipv4_prefix_for_assignment(  # type: ignore[attr-defined]
                db,
                device_id=r.device_id,
                prefix_id=new_id,
                family="ipv4",
                address=r.address,
            )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="migrering feilet (integritet)") from None

    db.refresh(left)
    db.refresh(right)
    out.first_prefix = ipam_svc.ipv4_prefix_read(db, left)
    out.second_prefix = ipam_svc.ipv4_prefix_read(db, right)
    out.detail = "prefiks delt og migrering fullført"
    return out


def _ipv4_in_net_safe(addr: str, net: ipaddress.IPv4Network) -> bool:
    try:
        ip = ipaddress.ip_address(addr.strip())
    except ValueError:
        return False
    return isinstance(ip, ipaddress.IPv4Address) and ip in net
