"""GitOps-sync: drift mot siste skann, bulk-ensure og YAML-eksport."""

from __future__ import annotations

from typing import Any

import yaml
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dcim import Cable, DeviceInstance, FiberStrand, Site
from app.models.ipam import (
    IpamAutonomousSystem,
    IpamIpv4Address,
    IpamIpv4Prefix,
    IpamIpv4Range,
    IpamRouteTarget,
    IpamVrfInstance,
    IpamVrfRouteTarget,
    IpamCircuitGroup,
    IpamCircuitStrand,
    IpamContract,
    IpamProvider,
    IpamTunnel,
    IpamTunnelTransport,
    IpamScanHost,
    IpamSubnetScan,
    IpamVpnService,
)
from app.services import ipam_bgp as bgp_svc
from app.schemas.ipam import (
    IpamBulkEnsure,
    IpamBulkEnsureRead,
    IpamBulkItemResult,
    IpamDriftAddress,
    PrefixDriftRead,
    SiteDriftRead,
)
from app.services import ipam as ipam_svc
from app.services import ipam_address as addr_svc
from app.services import ipam_facilities as fac_svc
from app.services import ipam_ipv6 as ipv6_svc
from app.services.ipam_errors import ipam_error

_HELD = frozenset({"reserved", "assigned"})


def _latest_completed_scan(db: Session, prefix_id: int) -> IpamSubnetScan | None:
    return db.execute(
        select(IpamSubnetScan)
        .where(IpamSubnetScan.ipv4_prefix_id == prefix_id, IpamSubnetScan.status == "completed")
        .order_by(IpamSubnetScan.started_at.desc())
        .limit(1),
    ).scalar_one_or_none()


def prefix_drift(db: Session, prefix_id: int) -> PrefixDriftRead:
    pfx = ipam_svc.get_ipv4_prefix(db, prefix_id)
    if pfx is None:
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    scan = _latest_completed_scan(db, prefix_id)
    held = {
        r.address: r
        for r in db.execute(
            select(IpamIpv4Address).where(
                IpamIpv4Address.ipv4_prefix_id == prefix_id,
                IpamIpv4Address.status.in_(tuple(_HELD)),
            ),
        ).scalars().all()
    }
    if scan is None:
        return PrefixDriftRead(
            prefix_id=pfx.id,
            cidr=pfx.cidr,
            reserved_missing=[
                IpamDriftAddress(address=a, status=r.status, role=getattr(r, "role", None))
                for a, r in sorted(held.items())
            ],
        )
    hosts = list(db.execute(select(IpamScanHost).where(IpamScanHost.scan_id == scan.id)).scalars().all())
    seen = {h.address: h for h in hosts if h.ping_responded}
    aligned = sorted(set(held) & set(seen))
    unmanaged = [
        IpamDriftAddress(address=addr, mac_address=h.mac_address)
        for addr, h in sorted(seen.items())
        if addr not in held
    ]
    missing = [
        IpamDriftAddress(address=addr, status=r.status, role=getattr(r, "role", None))
        for addr, r in sorted(held.items())
        if addr not in seen
    ]
    return PrefixDriftRead(
        prefix_id=pfx.id,
        cidr=pfx.cidr,
        scan_id=scan.id,
        scanned_at=scan.completed_at or scan.started_at,
        aligned=aligned,
        seen_unmanaged=unmanaged,
        reserved_missing=missing,
    )


def site_drift(db: Session, site_id: int) -> SiteDriftRead:
    if db.get(Site, site_id) is None:
        raise ipam_error(404, "site_not_found", "site ikke funnet")
    ids = db.execute(select(IpamIpv4Prefix.id).where(IpamIpv4Prefix.site_id == site_id)).scalars().all()
    return SiteDriftRead(site_id=site_id, prefixes=[prefix_drift(db, int(i)) for i in ids])


def _item_error(exc: HTTPException) -> dict[str, Any]:
    d = exc.detail
    if isinstance(d, dict):
        return d
    return {"code": "error", "detail": str(d)}


def bulk_ensure(db: Session, data: IpamBulkEnsure) -> IpamBulkEnsureRead:
    results: list[IpamBulkItemResult] = []
    created = unchanged = failed = 0
    for p in data.prefixes:
        key = f"{p.site_slug or p.site_id}:{p.cidr}"
        try:
            row = ipam_svc.ensure_ipv4_prefix(db, p, update=data.update)
            was = bool(row.created)
            created += int(was)
            unchanged += int(not was)
            results.append(IpamBulkItemResult(kind="prefix", key=key, ok=True, created=was, id=row.id))
        except HTTPException as e:
            failed += 1
            results.append(IpamBulkItemResult(kind="prefix", key=key, ok=False, error=_item_error(e)))
    for a in data.addresses:
        key = f"{a.prefix_cidr or a.ipv4_prefix_id}:{a.address}"
        try:
            row = addr_svc.ensure_ipv4_address(db, a, update=data.update)
            was = bool(row.created)
            created += int(was)
            unchanged += int(not was)
            results.append(IpamBulkItemResult(kind="address", key=key, ok=True, created=was, id=row.id))
        except HTTPException as e:
            failed += 1
            results.append(IpamBulkItemResult(kind="address", key=key, ok=False, error=_item_error(e)))
    for p in data.ipv6_prefixes:
        key = f"{p.site_slug or p.site_id}:{p.cidr}"
        try:
            row = ipv6_svc.ensure_ipv6_prefix(db, p, update=data.update)
            was = bool(row.created)
            created += int(was)
            unchanged += int(not was)
            results.append(IpamBulkItemResult(kind="ipv6_prefix", key=key, ok=True, created=was, id=row.id))
        except HTTPException as e:
            failed += 1
            results.append(IpamBulkItemResult(kind="ipv6_prefix", key=key, ok=False, error=_item_error(e)))
    for a in data.ipv6_addresses:
        key = f"{a.prefix_cidr or a.ipv6_prefix_id}:{a.address}"
        try:
            row = ipv6_svc.ensure_ipv6_address(db, a, update=data.update)
            was = bool(row.created)
            created += int(was)
            unchanged += int(not was)
            results.append(IpamBulkItemResult(kind="ipv6_address", key=key, ok=True, created=was, id=row.id))
        except HTTPException as e:
            failed += 1
            results.append(IpamBulkItemResult(kind="ipv6_address", key=key, ok=False, error=_item_error(e)))
    return IpamBulkEnsureRead(results=results, created=created, unchanged=unchanged, failed=failed)


def export_site(db: Session, site_id: int) -> dict[str, Any]:
    site = db.get(Site, site_id)
    if site is None:
        raise ipam_error(404, "site_not_found", "site ikke funnet")
    prefixes, _ = ipam_svc.list_ipv4_prefixes(db, site_id=site_id)
    addrs, _ = addr_svc.list_ipv4_addresses(db, site_id=site_id, ipv4_prefix_id=None, status=None, limit=5000)
    v6, _ = ipv6_svc.list_ipv6_prefixes(db, site_id=site_id)
    v6a, _ = ipv6_svc.list_ipv6_addresses(db, site_id=site_id, limit=5000)
    vlans = fac_svc.list_vlans(db, site_id=site_id)
    vlan_groups = fac_svc.list_vlan_groups(db, site_id=site_id)
    vrfs = fac_svc.list_vrfs(db, site_id=site_id)
    circuits = fac_svc.list_circuits(db, site_id=site_id)
    vlan_by_id = {v.id: v for v in vlans}
    group_by_id = {g.id: g for g in vlan_groups}
    vrf_by_id = {v.id: v for v in vrfs}
    prefix_by_id = {p.id: p for p in prefixes}
    v6_by_id = {p.id: p for p in v6}
    site_ids = {c.a_site_id for c in circuits if c.a_site_id} | {c.z_site_id for c in circuits if c.z_site_id}
    site_by_id = {s.id: s for s in db.execute(select(Site).where(Site.id.in_(site_ids))).scalars().all()} if site_ids else {}
    group_ids = {c.group_id for c in circuits if getattr(c, "group_id", None)}
    group_by_id = (
        {g.id: g for g in db.execute(select(IpamCircuitGroup).where(IpamCircuitGroup.id.in_(group_ids))).scalars().all()}
        if group_ids
        else {}
    )
    contract_ids = {c.contract_id for c in circuits if getattr(c, "contract_id", None)}
    contract_by_id = (
        {x.id: x for x in db.execute(select(IpamContract).where(IpamContract.id.in_(contract_ids))).scalars().all()}
        if contract_ids
        else {}
    )
    provider_ids = {c.provider_id for c in circuits if c.provider_id} | {
        x.provider_id for x in contract_by_id.values()
    }
    provider_by_id = (
        {p.id: p for p in db.execute(select(IpamProvider).where(IpamProvider.id.in_(provider_ids))).scalars().all()}
        if provider_ids
        else {}
    )
    contracts = (
        list(db.execute(select(IpamContract).where(IpamContract.provider_id.in_(list(provider_by_id)))).scalars().all())
        if provider_by_id
        else []
    )
    account_ids = {x.provider_account_id for x in contracts if x.provider_account_id}
    account_by_id: dict[int, Any] = {}
    if account_ids:
        from app.models.ipam import IpamProviderAccount

        account_by_id = {
            a.id: a
            for a in db.execute(select(IpamProviderAccount).where(IpamProviderAccount.id.in_(account_ids))).scalars().all()
        }
    circuit_ids = {c.id for c in circuits}
    binds = (
        list(db.execute(select(IpamCircuitStrand).where(IpamCircuitStrand.circuit_id.in_(circuit_ids))).scalars().all())
        if circuit_ids
        else []
    )
    strand_ids = {b.strand_id for b in binds}
    strands = (
        {s.id: s for s in db.execute(select(FiberStrand).where(FiberStrand.id.in_(strand_ids))).scalars().all()}
        if strand_ids
        else {}
    )
    cable_ids = {s.cable_id for s in strands.values()}
    cables = (
        {c.id: c for c in db.execute(select(Cable).where(Cable.id.in_(cable_ids))).scalars().all()}
        if cable_ids
        else {}
    )
    extra_site_ids = {c.site_id for c in cables.values() if c.site_id not in site_by_id}
    if extra_site_ids:
        site_by_id.update(
            {s.id: s for s in db.execute(select(Site).where(Site.id.in_(extra_site_ids))).scalars().all()}
        )
    vpn_rows = (
        list(db.execute(select(IpamVpnService).where(IpamVpnService.source_circuit_id.in_(circuit_ids))).scalars().all())
        if circuit_ids
        else []
    )
    vpn_ids = {v.id for v in vpn_rows}
    vpn_by_id = {v.id: v for v in vpn_rows}
    tunnels = (
        list(db.execute(select(IpamTunnel).where(IpamTunnel.vpn_service_id.in_(vpn_ids))).scalars().all())
        if vpn_ids
        else []
    )
    tunnel_ids = {t.id for t in tunnels}
    tunnel_by_id = {t.id: t for t in tunnels}
    transports = (
        list(db.execute(select(IpamTunnelTransport).where(IpamTunnelTransport.tunnel_id.in_(tunnel_ids))).scalars().all())
        if tunnel_ids
        else []
    )
    as_assignments = bgp_svc.list_as_assignments(db, site_id=site_id)
    bgp_sessions = bgp_svc.list_bgp_sessions(db, site_id=site_id)
    as_ids = {x.autonomous_system_id for x in as_assignments} | {s.local_as_id for s in bgp_sessions} | {
        s.remote_as_id for s in bgp_sessions if s.remote_as_id
    }
    as_by_id = (
        {a.id: a for a in db.execute(select(IpamAutonomousSystem).where(IpamAutonomousSystem.id.in_(as_ids))).scalars().all()}
        if as_ids
        else {}
    )
    vrf_rt_binds = (
        list(db.execute(select(IpamVrfRouteTarget).where(IpamVrfRouteTarget.vrf_id.in_(list(vrf_by_id)))).scalars().all())
        if vrf_by_id
        else []
    )
    rt_ids = {x.route_target_id for x in vrf_rt_binds}
    rt_by_id = (
        {r.id: r for r in db.execute(select(IpamRouteTarget).where(IpamRouteTarget.id.in_(rt_ids))).scalars().all()}
        if rt_ids
        else {}
    )
    vrf_instances = (
        list(db.execute(select(IpamVrfInstance).where(IpamVrfInstance.vrf_id.in_(list(vrf_by_id)))).scalars().all())
        if vrf_by_id
        else []
    )
    inst_device_ids = {x.device_id for x in vrf_instances}
    inst_device_by_id = (
        {d.id: d for d in db.execute(select(DeviceInstance).where(DeviceInstance.id.in_(inst_device_ids))).scalars().all()}
        if inst_device_ids
        else {}
    )
    range_rows = (
        list(
            db.execute(select(IpamIpv4Range).where(IpamIpv4Range.ipv4_prefix_id.in_(list(prefix_by_id)))).scalars().all()
        )
        if prefix_by_id
        else []
    )
    tenant_slug = site.tenant.slug if getattr(site, "tenant", None) is not None else None
    vif_ids = {a.virtual_interface_id for a in addrs if getattr(a, "virtual_interface_id", None)}
    vif_by_id: dict[int, Any] = {}
    if vif_ids:
        from app.models.platform import PlatformVirtualInterface

        vif_by_id = {
            v.id: v
            for v in db.execute(
                select(PlatformVirtualInterface).where(PlatformVirtualInterface.id.in_(vif_ids))
            ).scalars().all()
        }
    return {
        "apiVersion": "freehci.ipam/v1",
        "kind": "SiteIpam",
        "site": {
            "id": site.id,
            "name": site.name,
            "slug": site.slug,
            "tenant_slug": tenant_slug,
        },
        "vrfs": [{"id": v.id, "name": v.name, "slug": v.slug} for v in vrfs],
        "vlan_groups": [{"id": g.id, "name": g.name, "slug": g.slug} for g in vlan_groups],
        "vlans": [
            {
                "id": v.id,
                "vid": v.vid,
                "name": v.name,
                "slug": v.slug,
                "vlan_group_id": v.vlan_group_id,
                "vlan_group_slug": group_by_id[v.vlan_group_id].slug if v.vlan_group_id in group_by_id else None,
            }
            for v in vlans
        ],
        "prefixes": [
            {
                "cidr": p.cidr,
                "slug": p.slug,
                "name": p.name,
                "role": p.role,
                "status": p.status,
                "site_slug": site.slug,
                "vlan_id": p.vlan_id,
                "vlan_slug": vlan_by_id[p.vlan_id].slug if p.vlan_id and p.vlan_id in vlan_by_id else None,
                "vrf_id": p.vrf_id,
                "vrf_slug": vrf_by_id[p.vrf_id].slug if p.vrf_id and p.vrf_id in vrf_by_id else None,
                "overlap_policy": p.overlap_policy,
                "dual_stack_group_id": p.dual_stack_group_id,
                "subnet_services": p.subnet_services,
            }
            for p in prefixes
        ],
        "addresses": [
            {
                "address": a.address,
                "status": a.status,
                "role": a.role,
                "note": a.note,
                "ipv4_prefix_id": a.ipv4_prefix_id,
                "prefix_cidr": prefix_by_id[a.ipv4_prefix_id].cidr if a.ipv4_prefix_id in prefix_by_id else None,
                "site_slug": site.slug,
                "virtual_interface_slug": (
                    vif_by_id[a.virtual_interface_id].slug
                    if getattr(a, "virtual_interface_id", None) and a.virtual_interface_id in vif_by_id
                    else None
                ),
            }
            for a in addrs
            if a.status in _HELD
        ],
        "ipv6_prefixes": [
            {"cidr": p.cidr, "slug": p.slug, "role": p.role, "status": p.status, "site_slug": site.slug} for p in v6
        ],
        "ipv6_addresses": [
            {
                "address": a.address,
                "status": a.status,
                "role": a.role,
                "site_slug": site.slug,
                "prefix_cidr": v6_by_id[a.ipv6_prefix_id].cidr if a.ipv6_prefix_id and a.ipv6_prefix_id in v6_by_id else None,
            }
            for a in v6a
            if a.status in _HELD
        ],
        "providers": [{"name": p.name, "slug": p.slug} for p in provider_by_id.values()],
        "circuit_groups": [
            {
                "name": g.name,
                "slug": g.slug,
                "shared_risk": g.shared_risk,
                "description": g.description,
            }
            for g in group_by_id.values()
        ],
        "contracts": [
            {
                "name": c.name,
                "slug": c.slug,
                "provider_slug": provider_by_id[c.provider_id].slug if c.provider_id in provider_by_id else None,
                "account_slug": (
                    account_by_id[c.provider_account_id].slug
                    if c.provider_account_id and c.provider_account_id in account_by_id
                    else None
                ),
                "reference": c.reference,
                "starts_on": c.starts_on.isoformat() if c.starts_on else None,
                "ends_on": c.ends_on.isoformat() if c.ends_on else None,
                "description": c.description,
            }
            for c in contracts
        ],
        "circuits": [
            {
                "circuit_number": c.circuit_number,
                "name": c.name,
                "circuit_type": c.circuit_type,
                "layer": c.layer,
                "tenant_id": c.tenant_id,
                "a_site_id": c.a_site_id,
                "z_site_id": c.z_site_id,
                "a_site_slug": site_by_id[c.a_site_id].slug if c.a_site_id in site_by_id else None,
                "z_site_slug": site_by_id[c.z_site_id].slug if c.z_site_id in site_by_id else None,
                "provider_id": c.provider_id,
                "provider_slug": provider_by_id[c.provider_id].slug if c.provider_id in provider_by_id else None,
                "provider_name": c.provider_name,
                "contract_slug": (
                    contract_by_id[c.contract_id].slug
                    if getattr(c, "contract_id", None) and c.contract_id in contract_by_id
                    else None
                ),
                "group_slug": (
                    group_by_id[c.group_id].slug
                    if getattr(c, "group_id", None) and c.group_id in group_by_id
                    else None
                ),
                "provider_circuit_id": getattr(c, "provider_circuit_id", None),
                "capacity_mbps": getattr(c, "capacity_mbps", None),
                "cir_mbps": getattr(c, "cir_mbps", None),
            }
            for c in circuits
        ],
        "circuit_strands": [
            {
                "circuit_number": next((c.circuit_number for c in circuits if c.id == b.circuit_id), None),
                "site_slug": (
                    site_by_id[cables[strands[b.strand_id].cable_id].site_id].slug
                    if b.strand_id in strands
                    and strands[b.strand_id].cable_id in cables
                    and cables[strands[b.strand_id].cable_id].site_id in site_by_id
                    else site.slug
                ),
                "cable_slug": cables[strands[b.strand_id].cable_id].slug
                if b.strand_id in strands and strands[b.strand_id].cable_id in cables
                else None,
                "position": strands[b.strand_id].position if b.strand_id in strands else None,
            }
            for b in binds
            if b.strand_id in strands
        ],
        "vpn_services": [
            {
                "name": v.name,
                "slug": v.slug,
                "vpn_type": v.vpn_type,
                "source_circuit_number": next(
                    (c.circuit_number for c in circuits if c.id == v.source_circuit_id),
                    None,
                ),
            }
            for v in vpn_rows
        ],
        "tunnels": [
            {
                "vpn_slug": vpn_by_id[t.vpn_service_id].slug if t.vpn_service_id in vpn_by_id else None,
                "name": t.name,
                "slug": t.slug,
                "status": t.status,
            }
            for t in tunnels
        ],
        "tunnel_transports": [
            {
                "vpn_slug": (
                    vpn_by_id[tunnel_by_id[b.tunnel_id].vpn_service_id].slug
                    if b.tunnel_id in tunnel_by_id and tunnel_by_id[b.tunnel_id].vpn_service_id in vpn_by_id
                    else None
                ),
                "tunnel_slug": tunnel_by_id[b.tunnel_id].slug if b.tunnel_id in tunnel_by_id else None,
                "circuit_number": next((c.circuit_number for c in circuits if c.id == b.circuit_id), None),
            }
            for b in transports
        ],
        "autonomous_systems": [
            {"asn": a.asn, "name": a.name, "slug": a.slug, "is_private": a.is_private} for a in as_by_id.values()
        ],
        "as_assignments": [
            {
                "asn": as_by_id[x.autonomous_system_id].asn if x.autonomous_system_id in as_by_id else None,
                "site_slug": site.slug,
                "vrf_slug": vrf_by_id[x.vrf_id].slug if x.vrf_id and x.vrf_id in vrf_by_id else None,
            }
            for x in as_assignments
        ],
        "bgp_sessions": [
            {
                "name": s.name,
                "slug": s.slug,
                "local_asn": as_by_id[s.local_as_id].asn if s.local_as_id in as_by_id else None,
                "remote_asn": s.remote_asn,
                "peer_ip": s.peer_ip,
                "site_slug": site.slug,
                "vrf_slug": vrf_by_id[s.vrf_id].slug if s.vrf_id and s.vrf_id in vrf_by_id else None,
                "address_families": s.address_families,
                "desired_status": s.desired_status,
            }
            for s in bgp_sessions
        ],
        "route_targets": [
            {"name": r.name, "slug": r.slug, "value": r.value, "description": r.description} for r in rt_by_id.values()
        ],
        "vrf_route_targets": [
            {
                "vrf_slug": vrf_by_id[x.vrf_id].slug if x.vrf_id in vrf_by_id else None,
                "route_target_slug": rt_by_id[x.route_target_id].slug if x.route_target_id in rt_by_id else None,
                "direction": x.direction,
            }
            for x in vrf_rt_binds
        ],
        "vrf_instances": [
            {
                "vrf_slug": vrf_by_id[x.vrf_id].slug if x.vrf_id in vrf_by_id else None,
                "site_slug": site.slug,
                "device_name": inst_device_by_id[x.device_id].name if x.device_id in inst_device_by_id else None,
                "slug": x.slug,
                "intent": x.intent,
                "route_distinguisher": x.route_distinguisher,
                "description": x.description,
            }
            for x in vrf_instances
        ],
        "ipv4_ranges": [
            {
                "prefix_cidr": prefix_by_id[r.ipv4_prefix_id].cidr if r.ipv4_prefix_id in prefix_by_id else None,
                "site_slug": site.slug,
                "slug": r.slug,
                "name": r.name,
                "kind": r.kind,
                "start_address": r.start_address,
                "end_address": r.end_address,
                "description": r.description,
            }
            for r in range_rows
        ],
    }


def export_site_yaml(db: Session, site_id: int) -> str:
    return yaml.safe_dump(export_site(db, site_id), sort_keys=False, allow_unicode=True)
