"""GitOps-sync: drift mot siste skann, bulk-ensure og YAML-eksport."""

from __future__ import annotations

from typing import Any

import yaml
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dcim import Site
from app.models.ipam import IpamIpv4Address, IpamIpv4Prefix, IpamScanHost, IpamSubnetScan
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
    vrfs = fac_svc.list_vrfs(db, site_id=site_id)
    circuits = fac_svc.list_circuits(db, site_id=site_id)
    vlan_by_id = {v.id: v for v in vlans}
    vrf_by_id = {v.id: v for v in vrfs}
    prefix_by_id = {p.id: p for p in prefixes}
    v6_by_id = {p.id: p for p in v6}
    tenant_slug = site.tenant.slug if getattr(site, "tenant", None) is not None else None
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
        "vlans": [{"id": v.id, "vid": v.vid, "name": v.name, "slug": v.slug} for v in vlans],
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
        "circuits": [
            {
                "circuit_number": c.circuit_number,
                "name": c.name,
                "circuit_type": c.circuit_type,
                "tenant_id": c.tenant_id,
                "a_site_id": c.a_site_id,
                "z_site_id": c.z_site_id,
            }
            for c in circuits
        ],
    }


def export_site_yaml(db: Session, site_id: int) -> str:
    return yaml.safe_dump(export_site(db, site_id), sort_keys=False, allow_unicode=True)
