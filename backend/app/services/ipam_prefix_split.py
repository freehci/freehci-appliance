"""Del IPv4-prefiks i to eller flere barn med validering og valgfri migrering av IPAM/DCIM."""

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
    Ipv4PrefixSplitEqualPlannedRead,
    Ipv4PrefixSplitEqualRequest,
    Ipv4PrefixSplitEqualResponse,
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


def _ip_net_role_for_split_conflict(ip: ipaddress.IPv4Address, net: ipaddress.IPv4Network) -> str | None:
    """RFC 3021 /31: ingen nett/broadcast-rolle for konfliktdeteksjon."""
    if net.prefixlen == 31:
        return None
    return _ip_net_role(ip, net)


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

    def note_conflict(ip_s: str, net: ipaddress.IPv4Network) -> None:
        try:
            ip = ipaddress.ip_address(ip_s.strip())
        except ValueError:
            return
        if not isinstance(ip, ipaddress.IPv4Address):
            return
        role = _ip_net_role_for_split_conflict(ip, net)
        if role is None:
            return
        key = (str(ip), str(net), role)
        if key in conflict_keys:
            return
        conflict_keys.add(key)
        msg = f"adressen er {role} i {net}"
        conflicts.append(
            Ipv4PrefixSplitConflictRead(
                address=str(ip),
                role=role,  # type: ignore[arg-type]
                message=msg,
                subnet_cidr=str(net),
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
        note_conflict(r.address, net)

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
        note_conflict(r.address, net)

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
        note_conflict(r.address, net)

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
        parts = [f"{c.address} ({c.role} i {c.subnet_cidr})" for c in conflicts]
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


MAX_EQUAL_SPLIT_SUBNETS = 256


def _containing_subnet(
    ip: ipaddress.IPv4Address,
    subnets: list[ipaddress.IPv4Network],
) -> ipaddress.IPv4Network | None:
    for n in subnets:
        if ip in n:
            return n
    return None


def ipv4_prefix_split_equal(db: Session, parent_id: int, data: Ipv4PrefixSplitEqualRequest) -> Ipv4PrefixSplitEqualResponse:
    parent = ipam_svc.get_ipv4_prefix(db, parent_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")

    same_site = _same_site_prefix_rows(db, parent.site_id)
    children = ipam_svc._child_prefix_orms(parent, same_site)  # type: ignore[attr-defined]
    has_children = len(children) > 0

    try:
        pnet = ipaddress.ip_network(parent.cidr, strict=False)
    except ValueError:
        return Ipv4PrefixSplitEqualResponse(
            dry_run=data.dry_run,
            has_child_prefixes=has_children,
            parent_cidr=str(parent.cidr),
            new_prefix_len=int(data.new_prefix_len),
            subnet_count=0,
            partition_ok=False,
            detail="ugyldig forelder-CIDR",
            planned=[],
            conflicts=[],
        )

    if pnet.version != 4:
        return Ipv4PrefixSplitEqualResponse(
            dry_run=data.dry_run,
            has_child_prefixes=has_children,
            parent_cidr=str(pnet),
            new_prefix_len=int(data.new_prefix_len),
            subnet_count=0,
            partition_ok=False,
            detail="kun IPv4",
            planned=[],
            conflicts=[],
        )

    p = pnet.prefixlen
    new_pl = int(data.new_prefix_len)
    if new_pl <= p or new_pl > 32:
        return Ipv4PrefixSplitEqualResponse(
            dry_run=data.dry_run,
            has_child_prefixes=has_children,
            parent_cidr=str(pnet),
            new_prefix_len=new_pl,
            subnet_count=0,
            partition_ok=False,
            detail=f"ny prefikslengde må være strengere enn forelder (/{p} < /{new_pl} ≤ /32)",
            planned=[],
            conflicts=[],
        )

    subnets = list(pnet.subnets(new_prefix=new_pl))
    n_sub = len(subnets)
    if n_sub > MAX_EQUAL_SPLIT_SUBNETS:
        raise HTTPException(
            status_code=400,
            detail=f"for mange delnett ({n_sub}), maks {MAX_EQUAL_SPLIT_SUBNETS} — velg grovere maske",
        )

    names_map: dict[str, str] = {}
    if data.names_by_cidr:
        for k, v in data.names_by_cidr.items():
            ks = k.strip()
            if not ks:
                continue
            try:
                nk_net = ipaddress.ip_network(ks, strict=False)
            except ValueError:
                nk = ks
            else:
                nk = str(nk_net) if nk_net.version == 4 else ks
            names_map[nk] = (v or "").strip()

    planned_list = [
        Ipv4PrefixSplitEqualPlannedRead(
            cidr=str(s),
            suggested_name=(names_map.get(str(s)) or str(s))[:255],
        )
        for s in subnets
    ]

    inv_rows = list(
        db.execute(select(IpamIpv4Address).where(IpamIpv4Address.ipv4_prefix_id == parent_id)).scalars().all(),
    )
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

    conflict_keys: set[tuple[str, str, str]] = set()
    conflicts: list[Ipv4PrefixSplitConflictRead] = []

    def note_conflict(ip_s: str, net: ipaddress.IPv4Network) -> None:
        try:
            ip = ipaddress.ip_address(ip_s.strip())
        except ValueError:
            return
        if not isinstance(ip, ipaddress.IPv4Address):
            return
        role = _ip_net_role_for_split_conflict(ip, net)
        if role is None:
            return
        key = (str(ip), str(net), role)
        if key in conflict_keys:
            return
        conflict_keys.add(key)
        msg = f"adressen er {role} i {net}"
        conflicts.append(
            Ipv4PrefixSplitConflictRead(
                address=str(ip),
                role=role,  # type: ignore[arg-type]
                message=msg,
                subnet_cidr=str(net),
            ),
        )

    for r in inv_rows:
        try:
            ip = ipaddress.ip_address(r.address.strip())
        except ValueError:
            continue
        if not isinstance(ip, ipaddress.IPv4Address):
            continue
        sn = _containing_subnet(ip, subnets)
        if sn is not None:
            note_conflict(r.address, sn)

    for r in iface_rows + dev_rows:
        try:
            ip = ipaddress.ip_address(r.address.strip())
        except ValueError:
            continue
        if not isinstance(ip, ipaddress.IPv4Address):
            continue
        sn = _containing_subnet(ip, subnets)
        if sn is not None:
            note_conflict(r.address, sn)

    planned_cidr_set = {str(s) for s in subnets}
    dup_detail: str | None = None
    for row in same_site:
        if row.id == parent_id:
            continue
        try:
            oc_net = ipaddress.ip_network(str(row.cidr).strip(), strict=False)
            oc = str(oc_net) if oc_net.version == 4 else str(row.cidr)
        except ValueError:
            oc = str(row.cidr)
        if oc in planned_cidr_set:
            dup_detail = f"CIDR finnes allerede og kolliderer med plan: {row.cidr}"
            break

    partition_ok = not has_children and dup_detail is None

    out = Ipv4PrefixSplitEqualResponse(
        dry_run=data.dry_run,
        has_child_prefixes=has_children,
        parent_cidr=str(pnet),
        new_prefix_len=new_pl,
        subnet_count=n_sub,
        partition_ok=partition_ok,
        detail=None,
        planned=planned_list,
        ipam_inventory_on_parent=len(inv_rows),
        dcim_iface_on_parent=len(iface_rows),
        dcim_device_on_parent=len(dev_rows),
        conflicts=conflicts,
        created_prefixes=[],
    )

    if has_children:
        out.detail = "kan ikke dele prefiks som allerede har registrerte underprefiks — slett eller flytt barn først"
        return out

    if dup_detail is not None:
        out.detail = dup_detail
        out.partition_ok = False
        return out

    if data.dry_run:
        out.detail = "dry_run: ingen endringer lagret"
        return out

    if not data.migrate_inventory and (len(inv_rows) > 0 or len(iface_rows) > 0 or len(dev_rows) > 0):
        raise HTTPException(
            status_code=400,
            detail="det finnes IPAM-rader eller DCIM-tildelinger på prefikset — slå på migrate_inventory eller rydd først",
        )

    if conflicts and not data.acknowledge_network_broadcast:
        parts = [f"{c.address} ({c.role} i {c.subnet_cidr})" for c in conflicts]
        raise HTTPException(
            status_code=409,
            detail="nettverks-/broadcast-konflikter: "
            + "; ".join(parts)
            + " — bekreft med acknowledge_network_broadcast=true",
        )

    for s in subnets:
        ipam_svc._require_no_partial_overlap(db, site_id=parent.site_id, cidr=str(s))  # type: ignore[attr-defined]

    created_orms: list[IpamIpv4Prefix] = []
    for s in subnets:
        cidr_s = str(s)
        name = (names_map.get(cidr_s) or cidr_s).strip()
        if not name:
            name = cidr_s
        if len(name) > 255:
            name = name[:255]
        pr = IpamIpv4Prefix(
            site_id=parent.site_id,
            tenant_id=parent.tenant_id,
            vlan_id=parent.vlan_id,
            vrf_id=parent.vrf_id,
            name=name,
            cidr=cidr_s,
            description=None,
            subnet_services=None,
        )
        db.add(pr)
        created_orms.append(pr)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="kunne ikke opprette barn-prefiks (duplikat?)") from None

    net_to_row = {str(s): row for s, row in zip(subnets, created_orms, strict=True)}

    if data.migrate_inventory:
        for r in inv_rows:
            try:
                ip = ipaddress.ip_address(r.address.strip())
            except ValueError:
                continue
            if not isinstance(ip, ipaddress.IPv4Address):
                continue
            sn = _containing_subnet(ip, subnets)
            if sn is None:
                continue
            tgt = net_to_row[str(sn)]
            r.ipv4_prefix_id = tgt.id

        for r in iface_rows:
            try:
                ip = ipaddress.ip_address(r.address.strip())
            except ValueError:
                continue
            if not isinstance(ip, ipaddress.IPv4Address):
                continue
            sn = _containing_subnet(ip, subnets)
            if sn is None:
                continue
            iface = db.get(DeviceInterface, r.interface_id)
            if iface is None:
                continue
            tgt = net_to_row[str(sn)]
            r.ipv4_prefix_id = dcim_svc._validate_ipv4_prefix_for_assignment(  # type: ignore[attr-defined]
                db,
                device_id=iface.device_id,
                prefix_id=tgt.id,
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
            sn = _containing_subnet(ip, subnets)
            if sn is None:
                continue
            tgt = net_to_row[str(sn)]
            r.ipv4_prefix_id = dcim_svc._validate_ipv4_prefix_for_assignment(  # type: ignore[attr-defined]
                db,
                device_id=r.device_id,
                prefix_id=tgt.id,
                family="ipv4",
                address=r.address,
            )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="migrering feilet (integritet)") from None

    reads = [ipam_svc.ipv4_prefix_read(db, row) for row in created_orms]
    out.created_prefixes = reads
    out.partition_ok = True
    out.detail = f"opprettet {len(reads)} prefiks og migrert tilknytninger"
    return out
