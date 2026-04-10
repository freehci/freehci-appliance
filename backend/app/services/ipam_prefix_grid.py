"""Samlet IPv4-rutenett for prefiks (alle adresser + inventory + DCIM + skann)."""

from __future__ import annotations

import ipaddress

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dcim import DeviceInterface
from app.models.ipam import IpamIpv4Address, IpamIpv4Prefix, IpamScanHost, IpamSubnetScan
from app.schemas.ipam import (
    Ipv4AddressRead,
    Ipv4AssignmentInPrefixRead,
    PrefixAddressGridRead,
    PrefixAddressGridRow,
)
from app.services import ipam as ipam_svc
from app.services import ipam_subnet_scan as scan_svc
from app.services.ipam_address import _ipv4_address_read

# Samme øvre grense som subnett-skann.
MAX_GRID_ADDRESSES = scan_svc.MAX_SCAN_HOSTS


def _candidate_strings_in_prefix(cidr: str) -> list[str]:
    try:
        ips = scan_svc.iter_target_ipv4_addresses(cidr)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return [str(x) for x in ips]


def ensure_ipv4_address_row(db: Session, *, ipv4_prefix_id: int, address: str) -> IpamIpv4Address:
    """Opprett inventory-rad for én IP i prefikset hvis den mangler (for manuell enhetskobling)."""
    pfx = db.get(IpamIpv4Prefix, ipv4_prefix_id)
    if pfx is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    ip_s = address.strip()
    try:
        ip = ipaddress.ip_address(ip_s)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ugyldig adresse: {e}") from e
    if not isinstance(ip, ipaddress.IPv4Address):
        raise HTTPException(status_code=400, detail="kun IPv4")
    net = ipaddress.ip_network(pfx.cidr, strict=False)
    if ip not in net:
        raise HTTPException(status_code=400, detail="adressen ligger ikke i prefiksnettet")

    row = db.execute(
        select(IpamIpv4Address).where(
            IpamIpv4Address.site_id == pfx.site_id,
            IpamIpv4Address.address == str(ip),
        ),
    ).scalar_one_or_none()
    if row is not None:
        if row.ipv4_prefix_id is None:
            row.ipv4_prefix_id = pfx.id
            db.commit()
            db.refresh(row)
        return row

    row = IpamIpv4Address(
        site_id=pfx.site_id,
        ipv4_prefix_id=pfx.id,
        address=str(ip),
        status="discovered",
        owner_user_id=None,
        note=None,
        mac_address=None,
        last_seen_at=None,
        device_type_id=None,
        device_model_id=None,
        device_id=None,
        interface_id=None,
        interface_ip_assignment_id=None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def build_prefix_address_grid(db: Session, prefix_id: int) -> PrefixAddressGridRead:
    pfx = db.get(IpamIpv4Prefix, prefix_id)
    if pfx is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")

    candidates = _candidate_strings_in_prefix(pfx.cidr)
    if len(candidates) > MAX_GRID_ADDRESSES:
        raise HTTPException(
            status_code=400,
            detail=f"for mange adresser (>{MAX_GRID_ADDRESSES}) — del opp prefikset",
        )

    assigns = ipam_svc.ipv4_assignments_for_prefix_id(db, prefix_id)
    assign_by_addr: dict[str, Ipv4AssignmentInPrefixRead] = {a.address: a for a in assigns}

    inv_rows = list(
        db.execute(
            select(IpamIpv4Address).where(
                IpamIpv4Address.site_id == pfx.site_id,
                IpamIpv4Address.address.in_(candidates),
            ),
        )
        .scalars()
        .all(),
    )
    inv_by_addr: dict[str, IpamIpv4Address] = {r.address: r for r in inv_rows}
    if_ids = {r.interface_id for r in inv_rows if r.interface_id is not None}
    if_names: dict[int, str] = {}
    if if_ids:
        qi = select(DeviceInterface.id, DeviceInterface.name).where(DeviceInterface.id.in_(if_ids))
        if_names = dict(db.execute(qi).all())

    scan_row = db.execute(
        select(IpamSubnetScan)
        .where(IpamSubnetScan.ipv4_prefix_id == prefix_id)
        .order_by(IpamSubnetScan.started_at.desc())
        .limit(1),
    ).scalar_one_or_none()

    active_scan_read = scan_svc.scan_to_read(scan_row) if scan_row is not None else None

    host_by_addr: dict[str, IpamScanHost] = {}
    if scan_row is not None:
        hosts = db.execute(select(IpamScanHost).where(IpamScanHost.scan_id == scan_row.id)).scalars().all()
        host_by_addr = {h.address: h for h in hosts}

    all_addrs = sorted(
        set(candidates) | set(inv_by_addr.keys()) | set(assign_by_addr.keys()),
        key=lambda s: ipaddress.ip_address(s),
    )

    rows_out: list[PrefixAddressGridRow] = []
    for addr in all_addrs:
        inv_orm = inv_by_addr.get(addr)
        inv_read: Ipv4AddressRead | None = None
        if inv_orm is not None:
            inv_read = _ipv4_address_read(db, inv_orm, interface_names=if_names)
        asn = assign_by_addr.get(addr)
        sh = host_by_addr.get(addr)
        ping = sh.ping_responded if sh is not None else None
        mac = sh.mac_address if sh is not None else None
        rows_out.append(
            PrefixAddressGridRow(
                address=addr,
                inventory=inv_read,
                assignment=asn,
                scan_ping_responded=ping,
                scan_mac=mac,
            ),
        )

    return PrefixAddressGridRead(
        prefix_id=prefix_id,
        cidr=pfx.cidr,
        active_scan=active_scan_read,
        rows=rows_out,
    )
