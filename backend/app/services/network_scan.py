"""Nettverksskann: maler, jobber, JSON per vert, DCIM-oppdagelse med navnevalg."""

from __future__ import annotations

import asyncio
import ipaddress
import logging
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.db import SessionLocal
from app.models.ipam import IpamIpv4Prefix
from app.models.network_scan import (
    NetworkScanDiscovery,
    NetworkScanHostResult,
    NetworkScanJob,
    NetworkScanPrefixBinding,
    NetworkScanTemplate,
)
from app.schemas.dcim import DeviceInstanceCreate
from app.schemas.network_scan import (
    NetworkScanDiscoveryApprove,
    NetworkScanDiscoveryRead,
    NetworkScanHostResultRead,
    NetworkScanJobCreate,
    NetworkScanJobDetailRead,
    NetworkScanJobRead,
    NetworkScanPrefixBindingCreate,
    NetworkScanPrefixBindingRead,
    NetworkScanTemplateCreate,
    NetworkScanTemplateRead,
)
from app.services import dcim as dcim_svc
from app.services.ipam_subnet_scan import PING_WORKERS, ping_one_ip
from app.services.snmp_probe import run_snmp_sys_info

logger = logging.getLogger(__name__)

NET_SCAN_MAX_HOSTS = 2048
TCP_SCAN_WORKERS = 64


def ensure_builtin_templates(db: Session) -> None:
    n = db.scalar(select(func.count()).select_from(NetworkScanTemplate))
    if (n or 0) > 0:
        return
    db.add_all(
        [
            NetworkScanTemplate(
                slug="builtin-ping",
                name="Ping scan",
                kind="ping",
                is_builtin=True,
                default_config={},
            ),
            NetworkScanTemplate(
                slug="builtin-snmp-inventory",
                name="SNMP inventory",
                kind="snmp_quick",
                is_builtin=True,
                default_config={"community": "public", "port": 161, "timeout_sec": 2.0, "retries": 1},
            ),
            NetworkScanTemplate(
                slug="builtin-service-discovery",
                name="Service discovery (TCP)",
                kind="tcp_ports",
                is_builtin=True,
                default_config={"ports": [22, 80, 443], "timeout_sec": 1.0},
            ),
        ],
    )
    db.commit()


def list_templates(db: Session) -> list[NetworkScanTemplateRead]:
    ensure_builtin_templates(db)
    rows = list(db.execute(select(NetworkScanTemplate).order_by(NetworkScanTemplate.slug)).scalars().all())
    return [NetworkScanTemplateRead.model_validate(r) for r in rows]


def get_template(db: Session, tid: int) -> NetworkScanTemplate | None:
    ensure_builtin_templates(db)
    return db.get(NetworkScanTemplate, tid)


def create_custom_template(db: Session, data: NetworkScanTemplateCreate) -> NetworkScanTemplateRead:
    ensure_builtin_templates(db)
    existing = db.execute(select(NetworkScanTemplate).where(NetworkScanTemplate.slug == data.slug)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=400, detail="slug allerede i bruk")
    if data.kind == "tcp_ports":
        ports = (data.default_config or {}).get("ports")
        if not isinstance(ports, list) or not ports:
            raise HTTPException(status_code=400, detail="tcp_ports krever default_config.ports som ikke-tom liste")
    row = NetworkScanTemplate(
        slug=data.slug.strip(),
        name=data.name.strip(),
        kind=data.kind,
        is_builtin=False,
        default_config=data.default_config,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return NetworkScanTemplateRead.model_validate(row)


def _bindings_count_for_prefix(db: Session, prefix_id: int) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(NetworkScanPrefixBinding)
            .where(
                NetworkScanPrefixBinding.ipv4_prefix_id == prefix_id,
                NetworkScanPrefixBinding.enabled.is_(True),
            ),
        )
        or 0,
    )


def template_allowed_for_prefix(db: Session, template_id: int, prefix_id: int) -> bool:
    if _bindings_count_for_prefix(db, prefix_id) == 0:
        return True
    row = db.execute(
        select(NetworkScanPrefixBinding).where(
            NetworkScanPrefixBinding.template_id == template_id,
            NetworkScanPrefixBinding.ipv4_prefix_id == prefix_id,
            NetworkScanPrefixBinding.enabled.is_(True),
        ),
    ).scalar_one_or_none()
    return row is not None


def list_prefix_bindings(db: Session, *, ipv4_prefix_id: int | None) -> list[NetworkScanPrefixBindingRead]:
    q = select(NetworkScanPrefixBinding)
    if ipv4_prefix_id is not None:
        q = q.where(NetworkScanPrefixBinding.ipv4_prefix_id == ipv4_prefix_id)
    rows = list(db.execute(q).scalars().all())
    return [NetworkScanPrefixBindingRead.model_validate(r) for r in rows]


def create_prefix_binding(db: Session, data: NetworkScanPrefixBindingCreate) -> NetworkScanPrefixBindingRead:
    if get_template(db, data.template_id) is None:
        raise HTTPException(status_code=404, detail="mal ikke funnet")
    pfx = db.get(IpamIpv4Prefix, data.ipv4_prefix_id)
    if pfx is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    row = NetworkScanPrefixBinding(
        template_id=data.template_id,
        ipv4_prefix_id=data.ipv4_prefix_id,
        enabled=data.enabled,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="binding finnes allerede") from e
    db.refresh(row)
    return NetworkScanPrefixBindingRead.model_validate(row)


def delete_prefix_binding(db: Session, binding_id: int) -> None:
    row = db.get(NetworkScanPrefixBinding, binding_id)
    if row is None:
        raise HTTPException(status_code=404, detail="binding ikke funnet")
    db.delete(row)
    db.commit()


def _validate_job_create(db: Session, data: NetworkScanJobCreate) -> tuple[NetworkScanTemplate, IpamIpv4Prefix, dict]:
    tpl = get_template(db, data.template_id)
    if tpl is None:
        raise HTTPException(status_code=404, detail="mal ikke funnet")
    pfx = db.get(IpamIpv4Prefix, data.ipv4_prefix_id)
    if pfx is None:
        raise HTTPException(status_code=404, detail="prefiks ikke funnet")
    if not template_allowed_for_prefix(db, tpl.id, pfx.id):
        raise HTTPException(
            status_code=400,
            detail="mal er ikke knyttet til dette prefikset (legg til binding eller fjern andre bindinger)",
        )
    opts = data.options.model_dump()
    if opts.get("inventory_mode") == "auto" and opts.get("default_device_model_id") is None:
        raise HTTPException(status_code=400, detail="auto inventory krever default_device_model_id")
    pid = opts.get("parent_job_id")
    if pid is not None:
        if opts.get("parent_filter") is None:
            raise HTTPException(status_code=400, detail="parent_filter er påkrevd når parent_job_id er satt")
        parent = db.get(NetworkScanJob, int(pid))
        if parent is None:
            raise HTTPException(status_code=404, detail="foreldre-jobb ikke funnet")
        if parent.status != "completed":
            raise HTTPException(status_code=400, detail="foreldre-jobb må være fullført")
        if parent.ipv4_prefix_id != pfx.id:
            raise HTTPException(status_code=400, detail="foreldre-jobb må gjelde samme prefiks")
    return tpl, pfx, opts


def create_job(db: Session, data: NetworkScanJobCreate) -> NetworkScanJobRead:
    tpl, pfx, opts = _validate_job_create(db, data)
    parent_id = opts.get("parent_job_id")
    row = NetworkScanJob(
        template_id=tpl.id,
        ipv4_prefix_id=pfx.id,
        site_id=pfx.site_id,
        cidr=pfx.cidr,
        parent_job_id=int(parent_id) if parent_id is not None else None,
        status="pending",
        options_json=opts,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return NetworkScanJobRead.model_validate(row)


def get_job(db: Session, job_id: int) -> NetworkScanJob | None:
    return db.get(NetworkScanJob, job_id)


def job_to_read(row: NetworkScanJob) -> NetworkScanJobRead:
    return NetworkScanJobRead.model_validate(row)


def get_job_detail(db: Session, job_id: int) -> NetworkScanJobDetailRead | None:
    row = db.execute(
        select(NetworkScanJob)
        .where(NetworkScanJob.id == job_id)
        .options(selectinload(NetworkScanJob.host_results)),
    ).scalar_one_or_none()
    if row is None:
        return None
    hosts = sorted(row.host_results, key=lambda h: ipaddress.ip_address(h.address))
    base = NetworkScanJobRead.model_validate(row)
    return NetworkScanJobDetailRead(
        **base.model_dump(),
        host_results=[NetworkScanHostResultRead.model_validate(h) for h in hosts],
    )


def list_jobs(db: Session, *, ipv4_prefix_id: int | None, limit: int) -> list[NetworkScanJobRead]:
    q = select(NetworkScanJob).order_by(NetworkScanJob.started_at.desc()).limit(limit)
    if ipv4_prefix_id is not None:
        q = q.where(NetworkScanJob.ipv4_prefix_id == ipv4_prefix_id)
    rows = list(db.execute(q).scalars().all())
    return [NetworkScanJobRead.model_validate(r) for r in rows]


def delete_job(db: Session, job_id: int) -> None:
    row = db.get(NetworkScanJob, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="jobb ikke funnet")
    db.delete(row)
    db.commit()


def reverse_dns_ptr(ip: str) -> str | None:
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        return name.strip() if name else None
    except OSError:
        return None


def _merge_tcp_config(tpl: NetworkScanTemplate, opts: dict) -> dict[str, Any]:
    cfg = dict(tpl.default_config or {})
    cfg.setdefault("ports", [])
    cfg.setdefault("timeout_sec", 1.0)
    return cfg


def _merge_snmp_config(tpl: NetworkScanTemplate, opts: dict) -> dict[str, Any]:
    cfg = dict(tpl.default_config or {})
    cfg.setdefault("community", "public")
    cfg.setdefault("port", 161)
    cfg.setdefault("timeout_sec", 2.0)
    cfg.setdefault("retries", 1)
    if opts.get("snmp_community"):
        cfg["community"] = str(opts["snmp_community"])
    if opts.get("snmp_port"):
        cfg["port"] = int(opts["snmp_port"])
    return cfg


def _pick_name(candidates: dict[str, str], priority: list[str]) -> tuple[str, str]:
    """Returner (kilde, navn)."""
    for src in priority:
        if src == "custom":
            continue
        raw = (candidates.get(src) or "").strip()
        if raw:
            return src, raw
    return "ip", candidates.get("ip", "")


def _resolve_targets_from_parent(
    db: Session,
    *,
    parent_job_id: int,
    parent_filter: str,
) -> list[str]:
    parent = db.get(NetworkScanJob, parent_job_id)
    if parent is None:
        return []
    rows = list(
        db.execute(select(NetworkScanHostResult).where(NetworkScanHostResult.job_id == parent_job_id)).scalars().all(),
    )
    out: list[str] = []
    for h in rows:
        j = h.result_json or {}
        if parent_filter == "alive" and j.get("alive") is True:
            out.append(h.address)
        elif parent_filter == "snmp_ok" and j.get("ok") is True:
            out.append(h.address)
    return out


def _iter_prefix_targets(cidr: str) -> list[str]:
    net = ipaddress.ip_network(cidr.strip(), strict=False)
    if net.version != 4:
        raise ValueError("kun IPv4")
    return [str(ip) for ip in net]


def tcp_probe_ports(host: str, ports: list[int], timeout_sec: float) -> list[int]:
    open_ports: list[int] = []
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_sec)
        try:
            s.connect((host, p))
            open_ports.append(p)
        except OSError:
            pass
        finally:
            s.close()
    return open_ports


def _inventory_candidate(tpl_kind: str, result_json: dict) -> bool:
    if tpl_kind == "ping":
        return result_json.get("alive") is True
    if tpl_kind == "snmp_quick":
        return result_json.get("ok") is True
    if tpl_kind == "tcp_ports":
        return bool(result_json.get("open_ports"))
    return False


def _build_candidates_for_row(
    *,
    address: str,
    tpl_kind: str,
    result_json: dict,
    ptr: str | None,
) -> dict[str, str]:
    snmp_name = (result_json.get("sys_name") or "").strip() if tpl_kind == "snmp_quick" else ""
    return {
        "ip": address,
        "ptr": (ptr or "").strip(),
        "snmp_sysname": snmp_name,
    }


def _finalize_inventory_for_job(db: Session, job: NetworkScanJob, tpl: NetworkScanTemplate) -> None:
    opts = job.options_json or {}
    mode = opts.get("inventory_mode") or "none"
    if mode == "none":
        return
    priority = opts.get("name_priority") or ["snmp_sysname", "ptr", "ip"]
    model_id = opts.get("default_device_model_id")
    results = list(
        db.execute(select(NetworkScanHostResult).where(NetworkScanHostResult.job_id == job.id)).scalars().all(),
    )

    for h in results:
        if not _inventory_candidate(tpl.kind, h.result_json or {}):
            continue
        ptr: str | None = None
        if mode in ("discovered_queue", "auto"):
            ptr = reverse_dns_ptr(h.address)
        cands = _build_candidates_for_row(
            address=h.address,
            tpl_kind=tpl.kind,
            result_json=h.result_json or {},
            ptr=ptr,
        )
        if mode == "discovered_queue":
            db.add(
                NetworkScanDiscovery(
                    job_id=job.id,
                    site_id=job.site_id,
                    address=h.address,
                    name_candidates_json=cands,
                    status="pending",
                ),
            )
        elif mode == "auto":
            src, name = _pick_name(cands, priority)
            if not name:
                name = h.address
                src = "ip"
            if model_id is None:
                continue
            dev = dcim_svc.create_device(
                db,
                DeviceInstanceCreate(
                    device_model_id=int(model_id),
                    device_type_id=None,
                    name=name[:255],
                    serial_number=None,
                    asset_tag=None,
                    attributes={"snmp_host": h.address},
                ),
            )
            db.add(
                NetworkScanDiscovery(
                    job_id=job.id,
                    site_id=job.site_id,
                    address=h.address,
                    name_candidates_json=cands,
                    chosen_name_source=src,
                    chosen_name=name[:255],
                    status="auto_promoted",
                    dcim_device_id=dev.id,
                ),
            )
    db.commit()


def execute_network_scan_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        row = db.get(NetworkScanJob, job_id)
        if row is None or row.status != "pending":
            return
        tpl = get_template(db, row.template_id)
        if tpl is None:
            return
        opts = row.options_json or {}
        row.status = "running"
        db.commit()

        try:
            if tpl.kind == "ping":
                _run_ping_job(db, row, tpl, opts)
            elif tpl.kind == "snmp_quick":
                _run_snmp_job(db, row, tpl, opts)
            elif tpl.kind == "tcp_ports":
                _run_tcp_job(db, row, tpl, opts)
            else:
                raise RuntimeError(f"ukjent kind {tpl.kind}")
        except Exception as e:  # noqa: BLE001
            logger.exception("network scan job %s failed", job_id)
            row = db.get(NetworkScanJob, job_id)
            if row is not None:
                row.status = "failed"
                row.error_message = str(e)[:2000]
                row.completed_at = datetime.now(timezone.utc)
                db.commit()
            return

        row = db.get(NetworkScanJob, job_id)
        if row is not None and row.status == "running":
            row.status = "completed"
            row.completed_at = datetime.now(timezone.utc)
            row.error_message = None
            db.commit()
            tpl = get_template(db, row.template_id)
            if tpl is not None:
                _finalize_inventory_for_job(db, row, tpl)
    finally:
        db.close()


def _targets_for_job(db: Session, row: NetworkScanJob, opts: dict) -> list[str]:
    pid = opts.get("parent_job_id")
    if pid is not None:
        pf = opts.get("parent_filter")
        if not pf:
            return []
        addrs = _resolve_targets_from_parent(db, parent_job_id=int(pid), parent_filter=str(pf))
        return sorted(addrs, key=lambda a: ipaddress.ip_address(a))
    return _iter_prefix_targets(row.cidr)


def _run_ping_job(db: Session, row: NetworkScanJob, _tpl: NetworkScanTemplate, opts: dict) -> None:
    targets = _targets_for_job(db, row, opts)
    if len(targets) > NET_SCAN_MAX_HOSTS:
        raise ValueError(f"for mange adresser (>{NET_SCAN_MAX_HOSTS})")
    row.hosts_scanned = len(targets)
    db.commit()
    matched = 0
    chunk: list[tuple[str, dict]] = []

    def flush() -> None:
        for addr, rj in chunk:
            db.add(NetworkScanHostResult(job_id=row.id, address=addr, result_json=rj))
        chunk.clear()
        db.commit()

    with ThreadPoolExecutor(max_workers=PING_WORKERS) as ex:
        futures = {ex.submit(ping_one_ip, a): a for a in targets}
        for fut in as_completed(futures):
            addr = futures[fut]
            try:
                ok = bool(fut.result())
            except Exception:  # noqa: BLE001
                ok = False
            if ok:
                matched += 1
            chunk.append((addr, {"alive": ok}))
            if len(chunk) >= 48:
                flush()
    flush()
    row.hosts_matched = matched
    db.commit()


async def _snmp_one(ip: str, cfg: dict) -> tuple[str, dict]:
    port = int(cfg.get("port") or 161)
    community = str(cfg.get("community") or "public")
    timeout = float(cfg.get("timeout_sec") or 2.0)
    retries = int(cfg.get("retries") or 1)
    info = await run_snmp_sys_info(
        host=ip,
        port=port,
        community=community,
        timeout_sec=timeout,
        retries=retries,
    )
    if info.ok:
        return ip, {
            "ok": True,
            "sys_name": info.sys_name,
            "sys_descr": info.sys_descr,
        }
    return ip, {"ok": False, "error": info.error or "SNMP feilet"}


async def _run_snmp_gather(ips: list[str], cfg: dict) -> list[tuple[str, dict]]:
    sem = asyncio.Semaphore(32)

    async def wrapped(i: str) -> tuple[str, dict]:
        async with sem:
            return await _snmp_one(i, cfg)

    return list(await asyncio.gather(*(wrapped(i) for i in ips)))


def _run_snmp_job(db: Session, row: NetworkScanJob, tpl: NetworkScanTemplate, opts: dict) -> None:
    cfg = _merge_snmp_config(tpl, opts)
    targets = _targets_for_job(db, row, opts)
    if len(targets) > NET_SCAN_MAX_HOSTS:
        raise ValueError(f"for mange adresser (>{NET_SCAN_MAX_HOSTS})")
    row.hosts_scanned = len(targets)
    db.commit()
    pairs = asyncio.run(_run_snmp_gather(targets, cfg))
    matched = 0
    for addr, rj in pairs:
        if rj.get("ok"):
            matched += 1
        db.add(NetworkScanHostResult(job_id=row.id, address=addr, result_json=rj))
    row.hosts_matched = matched
    db.commit()


def _run_tcp_job(db: Session, row: NetworkScanJob, tpl: NetworkScanTemplate, opts: dict) -> None:
    cfg = _merge_tcp_config(tpl, opts)
    ports = cfg.get("ports")
    if not isinstance(ports, list) or not ports:
        raise ValueError("ingen porter i mal-konfigurasjon")
    ports_i = [int(p) for p in ports]
    timeout_sec = float(cfg.get("timeout_sec") or 1.0)
    targets = _targets_for_job(db, row, opts)
    if len(targets) > NET_SCAN_MAX_HOSTS:
        raise ValueError(f"for mange adresser (>{NET_SCAN_MAX_HOSTS})")
    row.hosts_scanned = len(targets)
    db.commit()
    matched = 0

    def probe(addr: str) -> tuple[str, dict]:
        open_p = tcp_probe_ports(addr, ports_i, timeout_sec)
        return addr, {"open_ports": open_p, "ports_checked": ports_i}

    with ThreadPoolExecutor(max_workers=TCP_SCAN_WORKERS) as ex:
        futures = {ex.submit(probe, a): a for a in targets}
        for fut in as_completed(futures):
            addr, rj = fut.result()
            if rj.get("open_ports"):
                matched += 1
            db.add(NetworkScanHostResult(job_id=row.id, address=addr, result_json=rj))
    row.hosts_matched = matched
    db.commit()


def list_discoveries(
    db: Session,
    *,
    status: str | None,
    site_id: int | None,
    limit: int,
) -> list[NetworkScanDiscoveryRead]:
    q = select(NetworkScanDiscovery).order_by(NetworkScanDiscovery.created_at.desc()).limit(limit)
    if status:
        q = q.where(NetworkScanDiscovery.status == status)
    if site_id is not None:
        q = q.where(NetworkScanDiscovery.site_id == site_id)
    rows = list(db.execute(q).scalars().all())
    return [NetworkScanDiscoveryRead.model_validate(r) for r in rows]


def approve_discovery(db: Session, discovery_id: int, data: NetworkScanDiscoveryApprove) -> NetworkScanDiscoveryRead:
    row = db.get(NetworkScanDiscovery, discovery_id)
    if row is None:
        raise HTTPException(status_code=404, detail="oppdagelse ikke funnet")
    if row.status != "pending":
        raise HTTPException(status_code=400, detail="kun ventende rader kan godkjennes")
    cands = row.name_candidates_json or {}
    src = data.chosen_name_source
    if src == "custom":
        name = (data.chosen_name or "").strip()
    elif src == "ip":
        name = (cands.get("ip") or row.address).strip()
    elif src == "ptr":
        name = (cands.get("ptr") or "").strip() or row.address
    elif src == "snmp_sysname":
        name = (cands.get("snmp_sysname") or "").strip() or row.address
    else:
        name = row.address
    if not name:
        name = row.address
    dev = dcim_svc.create_device(
        db,
        DeviceInstanceCreate(
            device_model_id=data.device_model_id,
            device_type_id=None,
            name=name[:255],
            serial_number=None,
            asset_tag=None,
            attributes={"snmp_host": row.address},
        ),
    )
    row.chosen_name_source = src
    row.chosen_name = name[:255]
    row.status = "promoted"
    row.dcim_device_id = dev.id
    db.commit()
    db.refresh(row)
    return NetworkScanDiscoveryRead.model_validate(row)


def reject_discovery(db: Session, discovery_id: int) -> None:
    row = db.get(NetworkScanDiscovery, discovery_id)
    if row is None:
        raise HTTPException(status_code=404, detail="oppdagelse ikke funnet")
    if row.status != "pending":
        raise HTTPException(status_code=400, detail="kun ventende rader kan avvises")
    row.status = "rejected"
    db.commit()
