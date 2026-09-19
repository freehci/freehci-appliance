"""Del IPv6-prefiks i to eller flere barn og flytt inventory."""

from __future__ import annotations

import ipaddress

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.ipam import IpamIpv6Address, IpamIpv6Prefix
from app.schemas.ipam import (
    Ipv4PrefixSplitEqualPlannedRead,
    Ipv6PrefixSplitEqualRequest,
    Ipv6PrefixSplitEqualResponse,
    Ipv6PrefixSplitRequest,
    Ipv6PrefixSplitResponse,
)
from app.services import ipam_ipv6 as ipv6_svc
from app.services.ipam_errors import ipam_error

MAX_EQUAL_SPLIT_SUBNETS = 256


def _same_site(db: Session, site_id: int) -> list[IpamIpv6Prefix]:
    return list(db.execute(select(IpamIpv6Prefix).where(IpamIpv6Prefix.site_id == site_id)).scalars().all())


def _two_nets_partition_parent(
    parent: ipaddress.IPv6Network,
    a: ipaddress.IPv6Network,
    b: ipaddress.IPv6Network,
) -> bool:
    if a.version != 6 or b.version != 6 or parent.version != 6:
        return False
    if not a.subnet_of(parent) or not b.subnet_of(parent):
        return False
    if a == b or a.overlaps(b):
        return False
    rem = list(parent.address_exclude(a))
    if rem == [b]:
        return True
    rem2 = list(parent.address_exclude(b))
    return rem2 == [a]


def _ip_in_net(addr: str, net: ipaddress.IPv6Network) -> bool:
    try:
        ip = ipaddress.ip_address(addr.strip())
    except ValueError:
        return False
    return isinstance(ip, ipaddress.IPv6Address) and ip in net


def _containing_subnet(
    ip: ipaddress.IPv6Address,
    subnets: list[ipaddress.IPv6Network],
) -> ipaddress.IPv6Network | None:
    for n in subnets:
        if ip in n:
            return n
    return None


def ipv6_prefix_split(db: Session, parent_id: int, data: Ipv6PrefixSplitRequest) -> Ipv6PrefixSplitResponse:
    parent = ipv6_svc.get_ipv6_prefix(db, parent_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")

    same_site = _same_site(db, parent.site_id)
    has_children = len(ipv6_svc.child_prefix_orms(parent, same_site)) > 0
    out = Ipv6PrefixSplitResponse(
        dry_run=data.dry_run,
        has_child_prefixes=has_children,
        partition_ok=False,
        detail=None,
    )
    if has_children:
        out.detail = "kan ikke dele prefiks som allerede har registrerte underprefiks — slett eller flytt barn først"
        return out

    try:
        pnet = ipaddress.ip_network(parent.cidr, strict=False)
        a_net = ipaddress.ip_network(ipv6_svc._normalize_cidr(data.first.cidr), strict=False)
        b_net = ipaddress.ip_network(ipv6_svc._normalize_cidr(data.second.cidr), strict=False)
    except Exception as e:  # noqa: BLE001
        out.detail = str(getattr(e, "detail", e))
        return out
    if pnet.version != 6:
        out.detail = "kun IPv6"
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
        db.execute(select(IpamIpv6Address).where(IpamIpv6Address.ipv6_prefix_id == parent_id)).scalars().all(),
    )
    out.ipam_inventory_on_parent = len(inv_rows)
    out.ipam_migrate_left = sum(1 for r in inv_rows if _ip_in_net(r.address, a_net))
    out.ipam_migrate_right = sum(1 for r in inv_rows if _ip_in_net(r.address, b_net))

    if data.dry_run:
        out.detail = "dry_run: ingen endringer lagret"
        return out

    if not data.migrate_inventory and inv_rows:
        raise ipam_error(
            400,
            "must_migrate_inventory",
            "det finnes IPAM-rader på prefikset — slå på migrate_inventory eller rydd først",
        )

    for row in same_site:
        if row.id == parent_id:
            continue
        if str(row.cidr) in (out.first_cidr, out.second_cidr):
            raise ipam_error(409, "prefix_conflict", f"CIDR finnes allerede: {row.cidr}")

    reserved_slugs: set[str] = set()
    left = ipv6_svc.new_ipv6_prefix_orm(
        db,
        site_id=parent.site_id,
        name=data.first.name.strip(),
        cidr=out.first_cidr,
        tenant_id=parent.tenant_id,
        vlan_id=parent.vlan_id,
        vrf_id=parent.vrf_id,
        role=parent.role,
        status=parent.status,
        overlap_policy=parent.overlap_policy,
        dual_stack_group_id=parent.dual_stack_group_id,
        reserved_slugs=reserved_slugs,
    )
    right = ipv6_svc.new_ipv6_prefix_orm(
        db,
        site_id=parent.site_id,
        name=data.second.name.strip(),
        cidr=out.second_cidr,
        tenant_id=parent.tenant_id,
        vlan_id=parent.vlan_id,
        vrf_id=parent.vrf_id,
        role=parent.role,
        status=parent.status,
        overlap_policy=parent.overlap_policy,
        dual_stack_group_id=parent.dual_stack_group_id,
        reserved_slugs=reserved_slugs,
    )
    db.add(left)
    db.add(right)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "prefix_conflict", "kunne ikke opprette barn-prefiks (duplikat?)") from None

    if data.migrate_inventory:
        for r in inv_rows:
            if _ip_in_net(r.address, a_net):
                r.ipv6_prefix_id = left.id
            elif _ip_in_net(r.address, b_net):
                r.ipv6_prefix_id = right.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "prefix_conflict", "migrering feilet (integritet)") from None

    db.refresh(left)
    db.refresh(right)
    out.first_prefix = ipv6_svc.ipv6_prefix_read(db, left, created=True)
    out.second_prefix = ipv6_svc.ipv6_prefix_read(db, right, created=True)
    out.detail = "prefiks delt og migrering fullført"
    return out


def ipv6_prefix_split_equal(
    db: Session,
    parent_id: int,
    data: Ipv6PrefixSplitEqualRequest,
) -> Ipv6PrefixSplitEqualResponse:
    parent = ipv6_svc.get_ipv6_prefix(db, parent_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")

    same_site = _same_site(db, parent.site_id)
    has_children = len(ipv6_svc.child_prefix_orms(parent, same_site)) > 0
    try:
        pnet = ipaddress.ip_network(parent.cidr, strict=False)
    except ValueError:
        return Ipv6PrefixSplitEqualResponse(
            dry_run=data.dry_run,
            has_child_prefixes=has_children,
            parent_cidr=str(parent.cidr),
            new_prefix_len=int(data.new_prefix_len),
            subnet_count=0,
            partition_ok=False,
            detail="ugyldig forelder-CIDR",
        )
    if pnet.version != 6:
        return Ipv6PrefixSplitEqualResponse(
            dry_run=data.dry_run,
            has_child_prefixes=has_children,
            parent_cidr=str(pnet),
            new_prefix_len=int(data.new_prefix_len),
            subnet_count=0,
            partition_ok=False,
            detail="kun IPv6",
        )

    new_pl = int(data.new_prefix_len)
    if new_pl <= pnet.prefixlen or new_pl > 128:
        return Ipv6PrefixSplitEqualResponse(
            dry_run=data.dry_run,
            has_child_prefixes=has_children,
            parent_cidr=str(pnet),
            new_prefix_len=new_pl,
            subnet_count=0,
            partition_ok=False,
            detail=f"ny prefikslengde må være strengere enn forelder (/{pnet.prefixlen} < /{new_pl} ≤ /128)",
        )

    subnets = list(pnet.subnets(new_prefix=new_pl))
    if len(subnets) > MAX_EQUAL_SPLIT_SUBNETS:
        raise ipam_error(
            400,
            "too_many_subnets",
            f"for mange delnett ({len(subnets)}), maks {MAX_EQUAL_SPLIT_SUBNETS} — velg grovere maske",
        )

    names_map: dict[str, str] = {}
    if data.names_by_cidr:
        for k, v in data.names_by_cidr.items():
            try:
                nk = str(ipaddress.ip_network(k.strip(), strict=False))
            except ValueError:
                nk = k.strip()
            names_map[nk] = (v or "").strip()

    planned = [
        Ipv4PrefixSplitEqualPlannedRead(cidr=str(s), suggested_name=(names_map.get(str(s)) or str(s))[:255])
        for s in subnets
    ]
    inv_rows = list(
        db.execute(select(IpamIpv6Address).where(IpamIpv6Address.ipv6_prefix_id == parent_id)).scalars().all(),
    )
    planned_cidr_set = {str(s) for s in subnets}
    dup_detail: str | None = None
    for row in same_site:
        if row.id == parent_id:
            continue
        if str(row.cidr) in planned_cidr_set:
            dup_detail = f"CIDR finnes allerede og kolliderer med plan: {row.cidr}"
            break

    out = Ipv6PrefixSplitEqualResponse(
        dry_run=data.dry_run,
        has_child_prefixes=has_children,
        parent_cidr=str(pnet),
        new_prefix_len=new_pl,
        subnet_count=len(subnets),
        partition_ok=not has_children and dup_detail is None,
        planned=planned,
        ipam_inventory_on_parent=len(inv_rows),
    )
    if has_children:
        out.detail = "kan ikke dele prefiks som allerede har registrerte underprefiks — slett eller flytt barn først"
        return out
    if dup_detail is not None:
        out.detail = dup_detail
        return out
    if data.dry_run:
        out.detail = "dry_run: ingen endringer lagret"
        return out
    if not data.migrate_inventory and inv_rows:
        raise ipam_error(
            400,
            "must_migrate_inventory",
            "det finnes IPAM-rader på prefikset — slå på migrate_inventory eller rydd først",
        )

    reserved_slugs: set[str] = set()
    created_orms: list[IpamIpv6Prefix] = []
    for s in subnets:
        cidr_s = str(s)
        name = (names_map.get(cidr_s) or cidr_s).strip()[:255] or cidr_s
        pr = ipv6_svc.new_ipv6_prefix_orm(
            db,
            site_id=parent.site_id,
            name=name,
            cidr=cidr_s,
            tenant_id=parent.tenant_id,
            vlan_id=parent.vlan_id,
            vrf_id=parent.vrf_id,
            role=parent.role,
            status=parent.status,
            overlap_policy=parent.overlap_policy,
            dual_stack_group_id=parent.dual_stack_group_id,
            reserved_slugs=reserved_slugs,
        )
        db.add(pr)
        created_orms.append(pr)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "prefix_conflict", "kunne ikke opprette barn-prefiks (duplikat?)") from None

    net_to_row = {str(s): row for s, row in zip(subnets, created_orms, strict=True)}
    if data.migrate_inventory:
        for r in inv_rows:
            try:
                ip = ipaddress.ip_address(r.address.strip())
            except ValueError:
                continue
            if not isinstance(ip, ipaddress.IPv6Address):
                continue
            sn = _containing_subnet(ip, subnets)
            if sn is None:
                continue
            r.ipv6_prefix_id = net_to_row[str(sn)].id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ipam_error(409, "prefix_conflict", "migrering feilet (integritet)") from None

    out.created_prefixes = [ipv6_svc.ipv6_prefix_read(db, row, created=True) for row in created_orms]
    out.detail = f"opprettet {len(out.created_prefixes)} prefiks og migrert tilknytninger"
    return out
