"""Slå opp site/tenant/VLAN/VRF/prefiks via slug eller lokal id."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dcim import Site
from app.models.ipam import IpamIpv4Prefix, IpamIpv6Prefix, IpamVlan, IpamVrf
from app.models.tenant import Tenant
from app.schemas.ipam import Ipv4AddressEnsure, Ipv4PrefixEnsure, Ipv6AddressEnsure, Ipv6PrefixEnsure
from app.services.ipam_errors import ipam_error


def resolve_site_id(db: Session, *, site_id: int | None, site_slug: str | None) -> int:
    if site_id is not None:
        if db.get(Site, site_id) is None:
            raise ipam_error(404, "site_not_found", "site ikke funnet")
        return site_id
    slug = (site_slug or "").strip().lower()
    if not slug:
        raise ipam_error(400, "site_required", "site_id eller site_slug kreves")
    row = db.execute(select(Site).where(Site.slug == slug)).scalar_one_or_none()
    if row is None:
        raise ipam_error(404, "site_not_found", "site ikke funnet")
    return row.id


def resolve_tenant_id(db: Session, *, tenant_id: int | None, tenant_slug: str | None) -> int | None:
    if tenant_id is not None:
        return tenant_id
    slug = (tenant_slug or "").strip().lower()
    if not slug:
        return None
    row = db.execute(select(Tenant).where(Tenant.slug == slug)).scalar_one_or_none()
    if row is None:
        raise ipam_error(404, "tenant_not_found", "tenant ikke funnet")
    return row.id


def resolve_vlan_id(db: Session, *, site_id: int, vlan_id: int | None, vlan_slug: str | None) -> int | None:
    if vlan_id is not None:
        return vlan_id
    slug = (vlan_slug or "").strip().lower()
    if not slug:
        return None
    row = db.execute(select(IpamVlan).where(IpamVlan.site_id == site_id, IpamVlan.slug == slug)).scalar_one_or_none()
    if row is None:
        raise ipam_error(404, "vlan_not_found", "vlan ikke funnet")
    return row.id


def resolve_vrf_id(db: Session, *, site_id: int, vrf_id: int | None, vrf_slug: str | None) -> int | None:
    if vrf_id is not None:
        return vrf_id
    slug = (vrf_slug or "").strip().lower()
    if not slug:
        return None
    row = db.execute(select(IpamVrf).where(IpamVrf.site_id == site_id, IpamVrf.slug == slug)).scalar_one_or_none()
    if row is None:
        raise ipam_error(404, "vrf_not_found", "vrf ikke funnet")
    return row.id


def resolve_prefix_ensure(db: Session, data: Ipv4PrefixEnsure | Ipv6PrefixEnsure) -> Ipv4PrefixEnsure | Ipv6PrefixEnsure:
    site_id = resolve_site_id(db, site_id=data.site_id, site_slug=data.site_slug)
    tenant_id = resolve_tenant_id(db, tenant_id=data.tenant_id, tenant_slug=data.tenant_slug)
    vlan_id = resolve_vlan_id(db, site_id=site_id, vlan_id=data.vlan_id, vlan_slug=data.vlan_slug)
    vrf_id = resolve_vrf_id(db, site_id=site_id, vrf_id=data.vrf_id, vrf_slug=data.vrf_slug)
    return data.model_copy(update={"site_id": site_id, "tenant_id": tenant_id, "vlan_id": vlan_id, "vrf_id": vrf_id})


def resolve_ipv4_prefix_id(db: Session, data: Ipv4AddressEnsure) -> int:
    if data.ipv4_prefix_id is not None:
        return data.ipv4_prefix_id
    cidr = (data.prefix_cidr or "").strip()
    site_id = resolve_site_id(db, site_id=data.site_id, site_slug=data.site_slug)
    row = db.execute(
        select(IpamIpv4Prefix).where(IpamIpv4Prefix.site_id == site_id, IpamIpv4Prefix.cidr == cidr),
    ).scalar_one_or_none()
    if row is None:
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    return row.id


def resolve_ipv6_prefix_id(db: Session, data: Ipv6AddressEnsure) -> int:
    if data.ipv6_prefix_id is not None:
        return data.ipv6_prefix_id
    cidr = (data.prefix_cidr or "").strip()
    site_id = resolve_site_id(db, site_id=data.site_id, site_slug=data.site_slug)
    row = db.execute(
        select(IpamIpv6Prefix).where(IpamIpv6Prefix.site_id == site_id, IpamIpv6Prefix.cidr == cidr),
    ).scalar_one_or_none()
    if row is None:
        raise ipam_error(404, "prefix_not_found", "prefiks ikke funnet")
    return row.id
