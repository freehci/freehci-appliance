"""MIB-metadata i database, IANA-synk, gruppering og kompilering."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.dcim import Manufacturer
from app.models.snmp_catalog import SnmpIanaEnterprise, SnmpMibFileMeta
from app.services import snmp_mibs as mib_disk
from app.services.snmp_iana import fetch_iana_enterprise_rows
from app.services.snmp_mib_compile import compile_mib_modules, compiled_py_path
from app.services.snmp_mib_parse import guess_module_name, primary_enterprise_number


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def upsert_mib_meta(db: Session, filename: str, content: bytes) -> SnmpMibFileMeta:
    text = content.decode("utf-8", errors="replace")
    mod = guess_module_name(filename, text)
    pen = primary_enterprise_number(text)
    now = _utcnow()
    row = db.get(SnmpMibFileMeta, filename)
    if row is None:
        row = SnmpMibFileMeta(
            filename=filename,
            module_name=mod,
            enterprise_number=pen,
            compile_status="pending",
            compile_message=None,
            compiled_module_name=None,
            compiled_at=None,
            updated_at=now,
        )
        db.add(row)
    else:
        row.module_name = mod
        row.enterprise_number = pen
        row.compile_status = "pending"
        row.compile_message = None
        row.compiled_module_name = None
        row.compiled_at = None
        row.updated_at = now
    db.commit()
    db.refresh(row)
    return row


def refresh_mib_meta_from_disk(db: Session, settings: Settings, filename: str) -> SnmpMibFileMeta | None:
    root = settings.mib_root_path.resolve()
    path = (root / filename).resolve()
    if not str(path).startswith(str(root.resolve())) or not path.is_file():
        return None
    return upsert_mib_meta(db, filename, path.read_bytes())


def _iana_org(db: Session, pen: int | None) -> str | None:
    if pen is None:
        return None
    row = db.get(SnmpIanaEnterprise, pen)
    return row.organization if row else None


def _linked_mfr(db: Session, pen: int | None) -> Manufacturer | None:
    if pen is None:
        return None
    return db.execute(
        select(Manufacturer).where(Manufacturer.iana_enterprise_number == pen).limit(1),
    ).scalar_one_or_none()


def mib_detail_dict(db: Session, settings: Settings, disk_row: dict) -> dict:
    name = disk_row["name"]
    meta = db.get(SnmpMibFileMeta, name)
    if meta is None:
        meta = refresh_mib_meta_from_disk(db, settings, name)
    pen = meta.enterprise_number if meta else None
    mod = meta.module_name if meta else Path(name).stem
    iana_org = _iana_org(db, pen)
    mfr = _linked_mfr(db, pen)
    return {
        "name": name,
        "size_bytes": disk_row["size_bytes"],
        "modified_at": disk_row["modified_at"],
        "module_name": mod,
        "enterprise_number": pen,
        "iana_organization": iana_org,
        "compile_status": meta.compile_status if meta else "pending",
        "compile_message": meta.compile_message if meta else None,
        "compiled_module_name": meta.compiled_module_name if meta else None,
        "compiled_at": meta.compiled_at if meta else None,
        "linked_manufacturer": (
            {"id": mfr.id, "name": mfr.name} if mfr else None
        ),
    }


def list_mibs_detailed(db: Session, settings: Settings) -> list[dict]:
    disk = mib_disk.list_mib_files(settings)
    return [mib_detail_dict(db, settings, r) for r in disk]


def list_enterprise_groups(db: Session, settings: Settings) -> list[dict]:
    detailed = list_mibs_detailed(db, settings)
    by_pen: dict[int | None, list[str]] = defaultdict(list)
    for d in detailed:
        by_pen[d["enterprise_number"]].append(d["name"])
    groups: list[dict] = []
    for pen in sorted(by_pen.keys(), key=lambda x: (x is None, x or 0)):
        names = sorted(by_pen[pen])
        iana_org = _iana_org(db, pen)
        mfr = _linked_mfr(db, pen)
        groups.append(
            {
                "enterprise_number": pen,
                "iana_organization": iana_org,
                "mib_files": names,
                "linked_manufacturer": (
                    {"id": mfr.id, "name": mfr.name} if mfr else None
                ),
            },
        )
    return groups


def sync_iana_enterprises(db: Session) -> int:
    rows = fetch_iana_enterprise_rows()
    db.execute(delete(SnmpIanaEnterprise))
    db.commit()
    batch = 2000
    total = 0
    for i in range(0, len(rows), batch):
        chunk = rows[i : i + batch]
        for pen, org in chunk:
            db.add(SnmpIanaEnterprise(pen=pen, organization=org))
        db.commit()
        total += len(chunk)
    return total


def compile_mib_file(db: Session, settings: Settings, filename: str) -> dict:
    meta = db.get(SnmpMibFileMeta, filename)
    if meta is None:
        meta = refresh_mib_meta_from_disk(db, settings, filename)
    if meta is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="MIB-fil ikke funnet")
    module = meta.module_name or Path(filename).stem
    results = compile_mib_modules(settings, [module], ignore_errors=False, rebuild=True)
    st, err = results.get(module, ("missing", "ukjent feil"))
    now = _utcnow()
    ok = st == "compiled"
    meta.compile_status = "ok" if ok else "error"
    meta.compile_message = None if ok else (err or st)
    meta.compiled_at = now if ok else None
    meta.compiled_module_name = module if ok else None
    meta.updated_at = now
    db.commit()
    db.refresh(meta)
    dr: dict | None = None
    for r in mib_disk.list_mib_files(settings):
        if r["name"] == filename:
            dr = r
            break
    if dr is None:
        dr = {"name": filename, "size_bytes": 0, "modified_at": now}
    return mib_detail_dict(db, settings, dr)


def compile_all_mibs(db: Session, settings: Settings) -> list[dict]:
    out: list[dict] = []
    for row in mib_disk.list_mib_files(settings):
        name = row["name"]
        try:
            out.append(compile_mib_file(db, settings, name))
        except Exception as e:  # noqa: BLE001 — samle feil per fil (nettverk/pysmi)
            meta = db.get(SnmpMibFileMeta, name)
            if meta:
                meta.compile_status = "error"
                meta.compile_message = str(e)[:4000]
                meta.updated_at = _utcnow()
                db.commit()
            out.append(mib_detail_dict(db, settings, row))
    return out


def delete_mib_complete(db: Session, settings: Settings, filename: str) -> None:
    meta = db.get(SnmpMibFileMeta, filename)
    mod = meta.compiled_module_name if meta else None
    mib_disk.delete_mib_file(settings, filename)
    if meta:
        db.delete(meta)
    db.commit()
    if mod:
        p = compiled_py_path(settings, mod)
        if p and p.is_file():
            p.unlink(missing_ok=True)
        if p:
            pyc = p.with_suffix(".pyc")
            if pyc.is_file():
                pyc.unlink(missing_ok=True)
