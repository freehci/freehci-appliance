"""Subnett-skann med ping; MAC fra lokal ARP/neighbor (SNMP/port kan utvides senere)."""

from __future__ import annotations

import ipaddress
import logging
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from collections.abc import Callable

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.db import SessionLocal
from app.models.ipam import (
    IpamIpv4Address,
    IpamIpv4Prefix,
    IpamIpv6Address,
    IpamIpv6Prefix,
    IpamScanHost,
    IpamSubnetScan,
)
from app.schemas.ipam import SubnetScanDetailRead, SubnetScanHostRead, SubnetScanRead
from app.services.ipam_errors import ipam_error

logger = logging.getLogger(__name__)

# Begrensning for å unngå utilsiktede enorme skann (juster senere via config).
MAX_SCAN_HOSTS = 2048

# Maks samtidige ping (sett lavt for å være snill mot nettverk/OS).
PING_WORKERS = 32


def _normalize_mac(raw: str) -> str:
    s = raw.strip().lower().replace("-", ":").replace(".", ":")
    if re.fullmatch(r"([0-9a-f]{2}:){5}[0-9a-f]{2}", s):
        return s
    hx = re.sub(r"[^0-9a-f]", "", s)
    if len(hx) == 12:
        return ":".join(hx[i : i + 2] for i in range(0, 12, 2))
    return s


def _is_all_zero_mac(hwaddr: str) -> bool:
    hx = re.sub(r"[^0-9a-fA-F]", "", hwaddr)
    return len(hx) == 12 and int(hx, 16) == 0


def _parse_proc_net_arp(content: str) -> dict[str, str]:
    """Leser innhold fra /proc/net/arp (Linux)."""
    out: dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("IP address"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        ip_s, hwaddr = parts[0], parts[3]
        if not re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", ip_s):
            continue
        if _is_all_zero_mac(hwaddr):
            continue
        if re.fullmatch(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", hwaddr):
            out[ip_s] = _normalize_mac(hwaddr)
    return out


def _parse_ip_neigh_output(content: str) -> dict[str, str]:
    """Parser `ip neigh show` / `ip -4 neigh show` (Linux, iproute2)."""
    out: dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        # IPv4/IPv6 først på linjen: 192.168.1.1 / fd00::1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE
        m = re.match(
            r"^(\d{1,3}(?:\.\d{1,3}){3}|[0-9a-fA-F:]+)\s+.*?\blladdr\s+([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})\b",
            line,
            re.I,
        )
        if m:
            out[m.group(1)] = _normalize_mac(m.group(2))
    return out


def _parse_linux_arp_a(content: str) -> dict[str, str]:
    """Parser Linux/BusyBox `arp -a`: «? (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0»."""
    out: dict[str, str] = {}
    for line in content.splitlines():
        m = re.search(
            r"\((\d{1,3}(?:\.\d{1,3}){3})\)\s+at\s+([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})\b",
            line,
        )
        if m:
            out[m.group(1)] = _normalize_mac(m.group(2))
            continue
        m2 = re.search(
            r"(\d{1,3}(?:\.\d{1,3}){3})\s+ether\s+([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})\b",
            line,
            re.I,
        )
        if m2:
            out[m2.group(1)] = _normalize_mac(m2.group(2))
    return out


def ping_one_ip(ip: str) -> bool:
    """Én ICMP echo mot én vert (avhengig av OS og rettigheter)."""
    v6 = ":" in ip
    if sys.platform == "win32":
        cmd = ["ping", "-n", "1", "-w", "1500", ip]
    elif sys.platform == "darwin":
        # macOS/BSD: -W er millisekunder.
        cmd = ["ping6" if v6 else "ping", "-c", "1", "-W", "2000", ip]
    else:
        # Linux: -W er sekunder. -6 for IPv6 (ping6 finnes ikke alltid).
        cmd = ["ping", "-6" if v6 else "-4", "-c", "1", "-W", "2", ip]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=4)
        return r.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.debug("ping %s: %s", ip, e)
        return False


def load_mac_by_ip() -> dict[str, str]:
    """IP-str -> MAC kanonisk (kun verter OS-et har i ARP/neighbor-tabell).

    På Linux slås sammen /proc/net/arp, 'ip -4 neigh show' og 'arp -a'.
    Standard arp -a-format «(IP) at MAC [ether]» ble tidligere ikke parsert.
    I Docker bak NAT mot et annet L3-nett finnes ofte ingen MAC for eksterne IP-er
    i containern — da må API kjøre med host-nettverk eller SNMP senere.
    """
    mapping: dict[str, str] = {}
    if sys.platform == "win32":
        try:
            r = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=20, encoding="utf-8", errors="replace")
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return mapping
        if r.returncode != 0:
            return mapping
        for line in r.stdout.splitlines():
            m = re.search(
                r"(\d{1,3}(?:\.\d{1,3}){3})\s+([0-9a-f]{2}(?:[-.][0-9a-f]{2}){5})",
                line,
                re.I,
            )
            if m:
                mapping[m.group(1)] = _normalize_mac(m.group(2))
        return mapping

    try:
        with open("/proc/net/arp", encoding="ascii", errors="replace") as f:
            mapping.update(_parse_proc_net_arp(f.read()))
    except OSError:
        pass

    for cmd in (["ip", "-4", "neigh", "show"], ["ip", "-6", "neigh", "show"], ["ip", "neigh", "show"]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=20, errors="replace")
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
        if r.returncode != 0:
            continue
        mapping.update(_parse_ip_neigh_output(r.stdout))

    try:
        r = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=20, errors="replace")
        if r.returncode == 0:
            mapping.update(_parse_linux_arp_a(r.stdout))
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass

    logger.debug("load_mac_by_ip: %d IP->MAC oppføringer", len(mapping))
    return mapping


def iter_target_ipv4_addresses(cidr: str) -> list[ipaddress.IPv4Address]:
    """Alle IPv4-adresser i CIDR-et (inkl. nettverks- og broadcast-adresse der de finnes)."""
    net = ipaddress.ip_network(cidr.strip(), strict=False)
    if net.version != 4:
        raise ValueError("kun IPv4")
    return list(net)


def iter_target_addresses(cidr: str) -> list[ipaddress.IPv4Address] | list[ipaddress.IPv6Address]:
    net = ipaddress.ip_network(cidr.strip(), strict=False)
    if net.num_addresses > MAX_SCAN_HOSTS:
        raise ValueError(f"for mange adresser (>{MAX_SCAN_HOSTS}), del opp prefikset")
    return list(net)


def create_pending_scan(
    db: Session,
    *,
    ipv4_prefix_id: int | None = None,
    ipv6_prefix_id: int | None = None,
) -> IpamSubnetScan:
    if (ipv4_prefix_id is None) == (ipv6_prefix_id is None):
        raise ipam_error(400, "invalid_scan_target", "oppgi nøyaktig én av ipv4_prefix_id eller ipv6_prefix_id")
    if ipv6_prefix_id is not None:
        pfx = db.get(IpamIpv6Prefix, ipv6_prefix_id)
        if pfx is None:
            raise HTTPException(status_code=404, detail="prefiks ikke funnet")
        try:
            net = ipaddress.ip_network(pfx.cidr, strict=False)
        except ValueError as e:
            raise ipam_error(400, "invalid_cidr", str(e)) from e
        if net.version != 6 or net.num_addresses > MAX_SCAN_HOSTS:
            raise ipam_error(
                400,
                "prefix_too_large_for_scan",
                f"subnet-scan støtter høyst {MAX_SCAN_HOSTS} adresser — del opp prefikset",
                max_addresses=MAX_SCAN_HOSTS,
            )
        row = IpamSubnetScan(
            site_id=pfx.site_id,
            ipv6_prefix_id=pfx.id,
            cidr=pfx.cidr,
            method="ping",
            status="pending",
            hosts_scanned=0,
            hosts_responding=0,
        )
    else:
        pfx = db.get(IpamIpv4Prefix, ipv4_prefix_id)
        if pfx is None:
            raise HTTPException(status_code=404, detail="prefiks ikke funnet")
        row = IpamSubnetScan(
            site_id=pfx.site_id,
            ipv4_prefix_id=pfx.id,
            cidr=pfx.cidr,
            method="ping",
            status="pending",
            hosts_scanned=0,
            hosts_responding=0,
        )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_scan(db: Session, scan_id: int) -> IpamSubnetScan | None:
    return db.get(IpamSubnetScan, scan_id)


def get_scan_with_hosts(db: Session, scan_id: int) -> IpamSubnetScan | None:
    return db.execute(
        select(IpamSubnetScan)
        .where(IpamSubnetScan.id == scan_id)
        .options(selectinload(IpamSubnetScan.hosts)),
    ).scalar_one_or_none()


def scan_to_read(row: IpamSubnetScan) -> SubnetScanRead:
    return SubnetScanRead.model_validate(row)


def scan_to_detail_read(row: IpamSubnetScan) -> SubnetScanDetailRead:
    hosts_sorted = sorted(row.hosts, key=lambda h: ipaddress.ip_address(h.address))
    base = SubnetScanRead.model_validate(row)
    return SubnetScanDetailRead(
        **base.model_dump(),
        hosts=[SubnetScanHostRead.model_validate(h) for h in hosts_sorted],
    )


def list_scans(
    db: Session,
    *,
    site_id: int | None,
    ipv4_prefix_id: int | None,
    ipv6_prefix_id: int | None = None,
    limit: int,
) -> list[IpamSubnetScan]:
    q = select(IpamSubnetScan).order_by(IpamSubnetScan.started_at.desc()).limit(limit)
    if site_id is not None:
        q = q.where(IpamSubnetScan.site_id == site_id)
    if ipv4_prefix_id is not None:
        q = q.where(IpamSubnetScan.ipv4_prefix_id == ipv4_prefix_id)
    if ipv6_prefix_id is not None:
        q = q.where(IpamSubnetScan.ipv6_prefix_id == ipv6_prefix_id)
    return list(db.execute(q).scalars().all())


def run_scan_background(
    scan_id: int,
    *,
    ping_fn: Callable[[str], bool] | None = None,
    load_mac_fn: Callable[[], dict[str, str]] | None = None,
) -> None:
    """Kjør ping-sveip og lagre svar + MAC. Bruk egen DB-sesjon."""
    ping = ping_fn or ping_one_ip
    load_macs = load_mac_fn or load_mac_by_ip
    db = SessionLocal()
    try:
        row = db.get(IpamSubnetScan, scan_id)
        if row is None:
            return
        if row.status not in ("pending",):
            return

        if ping_fn is None and not shutil.which("ping"):
            row.status = "failed"
            row.error_message = (
                "Fant ikke kommandoen «ping». I Docker må API-imaget inneholde iputils-ping "
                "(standard i vårt Dockerfile). Lokalt: installer ping-verktøyet for OS-et ditt."
            )
            row.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.error("subnet scan %s: ping binary missing", scan_id)
            return

        row.status = "running"
        db.commit()

        try:
            targets = iter_target_addresses(row.cidr)
        except ValueError as e:
            row.status = "failed"
            row.error_message = str(e)
            row.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        n_targets = len(targets)
        row.hosts_scanned = n_targets
        db.commit()

        logger.info("subnet scan %s: pinger %s (%d adresser)", scan_id, row.cidr, n_targets)

        responded: list[str] = []
        chunk: list[tuple[str, bool]] = []
        CHUNK = 48

        def flush_scan_hosts() -> None:
            if not chunk:
                return
            for addr, ok in chunk:
                db.add(
                    IpamScanHost(
                        scan_id=row.id,
                        address=addr,
                        mac_address=None,
                        ping_responded=ok,
                    ),
                )
            chunk.clear()
            row.hosts_responding = len(responded)
            db.commit()

        with ThreadPoolExecutor(max_workers=PING_WORKERS) as ex:
            futures = {ex.submit(ping, str(ip)): str(ip) for ip in targets}
            for fut in as_completed(futures):
                ip_s = futures[fut]
                try:
                    ok = bool(fut.result())
                except Exception as e:  # noqa: BLE001
                    logger.debug("ping future %s: %s", ip_s, e)
                    ok = False
                if ok:
                    responded.append(ip_s)
                chunk.append((ip_s, ok))
                if len(chunk) >= CHUNK:
                    flush_scan_hosts()

        flush_scan_hosts()

        time.sleep(0.75)
        arp_raw = load_macs()
        arp: dict[str, str] = {}
        for k, v in arp_raw.items():
            try:
                arp[str(ipaddress.ip_address(k))] = v
            except ValueError:
                arp[k] = v

        # Fyll inn MAC på skannverter som svarte på ping.
        host_rows = list(
            db.execute(select(IpamScanHost).where(IpamScanHost.scan_id == row.id)).scalars().all(),
        )
        for h in host_rows:
            if h.ping_responded:
                h.mac_address = arp.get(h.address) or h.mac_address
        db.commit()

        # Upsert responderende IP-er til varig inventory.
        now = datetime.now(timezone.utc)
        arp_canon = arp
        if row.ipv6_prefix_id is not None:
            for ip_s in responded:
                existing = db.execute(
                    select(IpamIpv6Address).where(
                        IpamIpv6Address.site_id == row.site_id,
                        IpamIpv6Address.address == ip_s,
                    ),
                ).scalar_one_or_none()
                mac = arp_canon.get(ip_s)
                if existing is None:
                    db.add(
                        IpamIpv6Address(
                            site_id=row.site_id,
                            ipv6_prefix_id=row.ipv6_prefix_id,
                            address=ip_s,
                            status="discovered",
                            mac_address=mac,
                            last_seen_at=now,
                        ),
                    )
                else:
                    existing.last_seen_at = now
                    if existing.status not in ("reserved", "assigned"):
                        existing.status = "discovered"
                    if existing.ipv6_prefix_id is None:
                        existing.ipv6_prefix_id = row.ipv6_prefix_id
                    if existing.status == "discovered" and existing.mac_address is None:
                        existing.mac_address = mac or existing.mac_address
        else:
            for ip_s in responded:
                existing = db.execute(
                    select(IpamIpv4Address).where(
                        IpamIpv4Address.site_id == row.site_id,
                        IpamIpv4Address.address == ip_s,
                    ),
                ).scalar_one_or_none()
                if existing is None:
                    db.add(
                        IpamIpv4Address(
                            site_id=row.site_id,
                            ipv4_prefix_id=row.ipv4_prefix_id,
                            address=ip_s,
                            status="discovered",
                            mac_address=arp_canon.get(ip_s),
                            last_seen_at=now,
                        ),
                    )
                else:
                    existing.last_seen_at = now
                    if existing.status not in ("reserved", "assigned"):
                        existing.status = "discovered"
                    if existing.ipv4_prefix_id is None and row.ipv4_prefix_id is not None:
                        existing.ipv4_prefix_id = row.ipv4_prefix_id
                    if existing.status == "discovered" and (existing.mac_address is None):
                        existing.mac_address = arp_canon.get(ip_s) or existing.mac_address
        db.commit()

        row.hosts_responding = len(responded)
        row.status = "completed"
        row.completed_at = datetime.now(timezone.utc)
        row.error_message = None
        db.commit()
    except Exception as e:  # noqa: BLE001
        logger.exception("subnet scan %s failed", scan_id)
        try:
            row = db.get(IpamSubnetScan, scan_id)
            if row is not None:
                row.status = "failed"
                row.error_message = str(e)[:2000]
                row.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:  # noqa: BLE001
            db.rollback()
    finally:
        db.close()
