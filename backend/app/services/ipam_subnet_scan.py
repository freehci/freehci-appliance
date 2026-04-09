"""Subnett-skann med ping; MAC fra lokal ARP/neighbor (SNMP/port kan utvides senere)."""

from __future__ import annotations

import ipaddress
import logging
import re
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
from app.models.ipam import IpamIpv4Prefix, IpamScanHost, IpamSubnetScan
from app.schemas.ipam import SubnetScanDetailRead, SubnetScanHostRead, SubnetScanRead

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


def ping_one_ip(ip: str) -> bool:
    """Én ICMP echo mot én vert (avhengig av OS og rettigheter)."""
    if sys.platform == "win32":
        cmd = ["ping", "-n", "1", "-w", "1500", ip]
    elif sys.platform == "darwin":
        # macOS/BSD: -W er millisekunder.
        cmd = ["ping", "-c", "1", "-W", "2000", ip]
    else:
        # Linux: -W er sekunder.
        cmd = ["ping", "-c", "1", "-W", "2", ip]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=4)
        return r.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.debug("ping %s: %s", ip, e)
        return False


def load_mac_by_ip() -> dict[str, str]:
    """IP-str -> MAC kanonisk (kun verter OS-et har i ARP/neighbor-tabell)."""
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

    for cmd in (["ip", "neigh", "show"], ["arp", "-a"]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=20, errors="replace")
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
        if r.returncode != 0:
            continue
        for line in r.stdout.splitlines():
            m = re.match(
                r"^(\d{1,3}(?:\.\d{1,3}){3})\s+.*\blladdr\s+([0-9a-f:]{17})\b",
                line.strip(),
                re.I,
            )
            if m:
                mapping[m.group(1)] = _normalize_mac(m.group(2))
                continue
            m2 = re.search(
                r"(\d{1,3}(?:\.\d{1,3}){3})\s+ether\s+([0-9a-f:]{17})",
                line,
                re.I,
            )
            if m2:
                mapping[m2.group(1)] = _normalize_mac(m2.group(2))
        if mapping:
            break
    return mapping


def iter_target_ipv4_addresses(cidr: str) -> list[ipaddress.IPv4Address]:
    """Alle IPv4-adresser i CIDR-et (inkl. nettverks- og broadcast-adresse der de finnes)."""
    net = ipaddress.ip_network(cidr.strip(), strict=False)
    if net.version != 4:
        raise ValueError("kun IPv4")
    return list(net)


def create_pending_scan(db: Session, *, ipv4_prefix_id: int) -> IpamSubnetScan:
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
    limit: int,
) -> list[IpamSubnetScan]:
    q = select(IpamSubnetScan).order_by(IpamSubnetScan.started_at.desc()).limit(limit)
    if site_id is not None:
        q = q.where(IpamSubnetScan.site_id == site_id)
    if ipv4_prefix_id is not None:
        q = q.where(IpamSubnetScan.ipv4_prefix_id == ipv4_prefix_id)
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
        row.status = "running"
        db.commit()

        try:
            targets = iter_target_ipv4_addresses(row.cidr)
        except ValueError as e:
            row.status = "failed"
            row.error_message = str(e)
            row.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        if len(targets) > MAX_SCAN_HOSTS:
            row.status = "failed"
            row.error_message = f"for mange adresser (>{MAX_SCAN_HOSTS}), del opp prefikset"
            row.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        row.hosts_scanned = len(targets)
        db.commit()

        responded: list[str] = []
        with ThreadPoolExecutor(max_workers=PING_WORKERS) as ex:
            futures = {ex.submit(ping, str(ip)): str(ip) for ip in targets}
            for fut in as_completed(futures):
                ip_s = futures[fut]
                try:
                    if fut.result():
                        responded.append(ip_s)
                except Exception as e:  # noqa: BLE001
                    logger.debug("ping future %s: %s", ip_s, e)

        time.sleep(0.3)
        arp = load_macs()

        for ip_s in sorted(responded, key=ipaddress.ip_address):
            mac = arp.get(ip_s)
            db.add(
                IpamScanHost(
                    scan_id=row.id,
                    address=ip_s,
                    mac_address=mac,
                    ping_responded=True,
                ),
            )
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
