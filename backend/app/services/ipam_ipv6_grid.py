"""IPv6-rutenett for prefiks (adresser + inventory + siste skann)."""

from __future__ import annotations

import ipaddress

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ipam import IpamIpv6Address, IpamIpv6Prefix, IpamScanHost, IpamSubnetScan
from app.schemas.ipam import Ipv6PrefixAddressGridRead, Ipv6PrefixAddressGridRow
from app.services import ipam_ipv6 as ipv6_svc
from app.services import ipam_subnet_scan as scan_svc
from app.services.ipam_errors import ipam_error

# Samme tak som IPv4 /22: 1024 adresser. /64 skal bruke available-ranges.
MAX_GRID_ADDRESSES = 1024
MIN_GRID_PREFIXLEN = 118


def _address_role_for(cidr: str, addr_s: str) -> str | None:
    try:
        net = ipaddress.ip_network(cidr.strip(), strict=False)
        ip = ipaddress.ip_address(addr_s.strip())
    except ValueError:
        return None
    if net.version != 6 or not isinstance(ip, ipaddress.IPv6Address) or ip not in net:
        return None
    if net.prefixlen <= 126 and ip == net.network_address:
        return "network"
    return "host"


def build_ipv6_address_grid(db: Session, prefix_id: int) -> Ipv6PrefixAddressGridRead:
    pfx = db.get(IpamIpv6Prefix, prefix_id)
    if pfx is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")

    try:
        net = ipaddress.ip_network(pfx.cidr, strict=False)
    except ValueError as e:
        raise ipam_error(400, "invalid_cidr", str(e)) from e
    if net.version != 6:
        raise ipam_error(400, "ipv6_only", "kun IPv6")
    if net.prefixlen < MIN_GRID_PREFIXLEN or net.num_addresses > MAX_GRID_ADDRESSES:
        raise ipam_error(
            400,
            "prefix_too_large_for_grid",
            f"address-grid støtter høyst /{MIN_GRID_PREFIXLEN} ({MAX_GRID_ADDRESSES} adresser) — bruk available-ranges",
            max_prefixlen=MIN_GRID_PREFIXLEN,
            max_addresses=MAX_GRID_ADDRESSES,
        )

    candidates = [str(ip) for ip in net]
    inv_rows = list(
        db.execute(
            select(IpamIpv6Address).where(
                IpamIpv6Address.site_id == pfx.site_id,
                IpamIpv6Address.address.in_(candidates),
            ),
        )
        .scalars()
        .all(),
    )
    inv_by_addr = {r.address: r for r in inv_rows}

    scan_row = db.execute(
        select(IpamSubnetScan)
        .where(IpamSubnetScan.ipv6_prefix_id == prefix_id)
        .order_by(IpamSubnetScan.started_at.desc())
        .limit(1),
    ).scalar_one_or_none()
    active_scan = scan_svc.scan_to_read(scan_row) if scan_row is not None else None

    host_by_addr: dict[str, IpamScanHost] = {}
    if scan_row is not None:
        hosts = db.execute(select(IpamScanHost).where(IpamScanHost.scan_id == scan_row.id)).scalars().all()
        host_by_addr = {h.address: h for h in hosts}

    all_addrs = sorted(
        set(candidates) | set(inv_by_addr.keys()),
        key=lambda s: ipaddress.ip_address(s),
    )
    rows_out: list[Ipv6PrefixAddressGridRow] = []
    for addr in all_addrs:
        inv = inv_by_addr.get(addr)
        sh = host_by_addr.get(addr)
        rows_out.append(
            Ipv6PrefixAddressGridRow(
                address=addr,
                address_role=_address_role_for(pfx.cidr, addr),
                inventory=ipv6_svc._addr_read(inv) if inv is not None else None,
                scan_ping_responded=sh.ping_responded if sh is not None else None,
                scan_mac=sh.mac_address if sh is not None else None,
            ),
        )

    return Ipv6PrefixAddressGridRead(
        prefix_id=prefix_id,
        cidr=pfx.cidr,
        active_scan=active_scan,
        rows=rows_out,
    )
