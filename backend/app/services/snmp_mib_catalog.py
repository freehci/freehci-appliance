"""MIB-metadata i database, IANA-synk, gruppering og kompilering."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from typing import Any

from fastapi import HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.db import SessionLocal
from app.models.dcim import Manufacturer
from app.models.snmp_catalog import SnmpIanaEnterprise, SnmpMibFileMeta
from app.services import snmp_mibs as mib_disk
from app.services.snmp_iana import fetch_iana_enterprise_rows
from app.services.snmp_mib_compile import compile_mib_modules, compile_status_is_success, compiled_py_path
from app.services.snmp_mib_normalize import normalize_mib_source_text
from app.services.snmp_mib_dependencies import parse_missing_imports_json, refresh_missing_imports_all
from app.services.snmp_mib_index import mib_module_to_files_map, rebuild_pysmi_mib_index
from app.services.snmp_mib_parse import guess_module_name, imported_vendor_mib_modules, primary_enterprise_number

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _mib_file_text(settings: Settings, filename: str) -> str:
    path = mib_disk.try_resolve_mib_disk_path(settings, filename)
    if path is None:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def upsert_mib_meta(db: Session, settings: Settings, filename: str, content: bytes) -> SnmpMibFileMeta:
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
            missing_import_modules_json="[]",
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
    path = mib_disk.try_resolve_mib_disk_path(settings, filename)
    if path is None:
        return None
    row = upsert_mib_meta(db, settings, filename, path.read_bytes())
    refresh_missing_imports_all(db, settings)
    db.refresh(row)
    return row


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


def discovery_context_for_pen(db: Session, settings: Settings, pen: int | None) -> dict:
    """IANA-navn, DCIM-produsent og MIB-filer gruppert på PEN (for SNMP host discovery)."""
    if pen is None:
        return {
            "iana_organization": None,
            "linked_manufacturer": None,
            "mib_files_in_library": [],
        }
    iana = _iana_org(db, pen)
    mfr = _linked_mfr(db, pen)
    mib_files: list[str] = []
    for g in list_enterprise_groups(db, settings):
        if g.get("enterprise_number") == pen:
            mib_files = sorted(g.get("mib_files") or [])
            break
    return {
        "iana_organization": iana,
        "linked_manufacturer": (
            {"id": mfr.id, "name": mfr.name} if mfr else None
        ),
        "mib_files_in_library": mib_files,
    }


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
        "effective_enterprise_number": pen,
        "extends_mib_module": None,
        "parent_mib_missing": False,
        "missing_import_modules": parse_missing_imports_json(
            getattr(meta, "missing_import_modules_json", None) if meta else None,
        ),
    }


def _snmp_file_topology(db: Session, settings: Settings, disk_rows: list[dict]) -> dict[str, dict]:
    """Utvid metadata per fil: effective PEN, import-parent, tre-bruk."""
    by_file: dict[str, dict] = {}

    for row in disk_rows:
        fn = row["name"]
        d = mib_detail_dict(db, settings, row)
        by_file[fn] = d

    # Modul → fil: alltid fra DEFINITIONS i filinnhold (samme som .index / manglende IMPORTS),
    # ikke fra DB-felt module_name (kan skille seg fra kilden etter manuell filbytte).
    module_to_files_map = mib_module_to_files_map(settings.mib_root_path.resolve())

    def resolve_parent_file(fn: str) -> str | None:
        text = _mib_file_text(settings, fn)
        if not text:
            return None
        for im in imported_vendor_mib_modules(text):
            for c in module_to_files_map.get(im.upper(), []):
                if c != fn:
                    return c
        return None

    def effective_pen_for(fn: str, visited: frozenset[str]) -> int | None:
        if fn in visited:
            return None
        nvisited = visited | {fn}
        pen = by_file[fn].get("enterprise_number")
        if pen is not None:
            return pen
        p = resolve_parent_file(fn)
        if p:
            return effective_pen_for(p, nvisited)
        return None

    out: dict[str, dict] = {}
    for fn, d in by_file.items():
        text = _mib_file_text(settings, fn)
        vimports = imported_vendor_mib_modules(text) if text else []
        ip = resolve_parent_file(fn)
        pen = d.get("enterprise_number")
        parent_missing = pen is None and len(vimports) > 0 and ip is None
        eff = effective_pen_for(fn, frozenset())
        out[fn] = {
            **d,
            "immediate_parent_file": ip,
            "effective_enterprise_number": eff,
            "vendor_import_modules": vimports,
            "extends_mib_module": vimports[0] if vimports else None,
            "parent_mib_missing": parent_missing,
        }
    return out


def _build_mib_tree_for_group(group_files: list[str], topo: dict[str, dict], group_pen: int | None) -> list[dict]:
    gf = set(group_files)

    def ancestor_in_group(fn: str) -> str | None:
        p = topo[fn].get("immediate_parent_file")
        visited: set[str] = set()
        while p and p not in visited:
            visited.add(p)
            if p in gf:
                return p
            p = topo.get(p, {}).get("immediate_parent_file")
        return None

    children: dict[str, list[str]] = defaultdict(list)
    roots: list[str] = []
    for fn in group_files:
        anc = ancestor_in_group(fn)
        if anc:
            children[anc].append(fn)
        else:
            roots.append(fn)

    def root_key(f: str) -> tuple:
        t = topo[f]
        has_native = t.get("enterprise_number") is not None and t.get("enterprise_number") == group_pen
        return (0 if has_native else 1, f)

    roots.sort(key=root_key)

    def node_dict(fn: str) -> dict:
        t = topo[fn]
        ch = sorted(children.get(fn, []))
        ext_mod = None
        if t.get("enterprise_number") is None:
            ext_mod = t.get("extends_mib_module")
        return {
            "filename": fn,
            "module_name": t.get("module_name"),
            "compile_status": t.get("compile_status"),
            "extension_parent_module": ext_mod,
            "parent_mib_missing": bool(t.get("parent_mib_missing")),
            "children": [node_dict(c) for c in ch],
        }

    return [node_dict(r) for r in roots]


def list_mibs_detailed(db: Session, settings: Settings) -> list[dict]:
    disk = mib_disk.list_mib_files(settings)
    topo = _snmp_file_topology(db, settings, disk)
    out: list[dict] = []
    for row in disk:
        fn = row["name"]
        t = topo[fn]
        d = {
            k: v
            for k, v in t.items()
            if k
            not in (
                "immediate_parent_file",
                "vendor_import_modules",
            )
        }
        if d.get("enterprise_number") is None and d.get("effective_enterprise_number") is not None:
            m = _linked_mfr(db, d["effective_enterprise_number"])
            if m:
                d["linked_manufacturer"] = {"id": m.id, "name": m.name}
        out.append(d)
    return out


def list_enterprise_groups(db: Session, settings: Settings) -> list[dict]:
    disk = mib_disk.list_mib_files(settings)
    topo = _snmp_file_topology(db, settings, disk)
    by_eff: dict[int | None, list[str]] = defaultdict(list)
    for fn, t in topo.items():
        by_eff[t["effective_enterprise_number"]].append(fn)

    groups: list[dict] = []
    for pen in sorted(by_eff.keys(), key=lambda x: (x is None, x or 0)):
        names = sorted(by_eff[pen])
        iana_org = _iana_org(db, pen)
        mfr = _linked_mfr(db, pen)
        tree = _build_mib_tree_for_group(names, topo, pen)
        groups.append(
            {
                "enterprise_number": pen,
                "iana_organization": iana_org,
                "mib_files": names,
                "mib_tree": tree,
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
        for p, org in chunk:
            db.add(SnmpIanaEnterprise(pen=p, organization=org))
        db.commit()
        total += len(chunk)
    return total


def autocreate_dcim_manufacturers(
    db: Session,
    settings: Settings,
    *,
    enterprise_number: int | None = None,
) -> dict:
    """Opprett DCIM-produsent med IANA PEN der det mangler. enterprise_number=None: alle aktuelle PEN."""
    if enterprise_number is not None:
        pens = [enterprise_number]
    else:
        rows = mib_disk.list_mib_files(settings)
        topo = _snmp_file_topology(db, settings, rows)
        pens_set: set[int] = set()
        for t in topo.values():
            p = t.get("effective_enterprise_number")
            if p is not None:
                pens_set.add(p)
        pens = sorted(pens_set)

    created: list[dict] = []
    skipped: list[str] = []

    for pen in pens:
        if pen is None:
            continue
        existing = _linked_mfr(db, pen)
        if existing:
            skipped.append(f"PEN {pen}: produsent finnes allerede ({existing.name})")
            continue
        org = _iana_org(db, pen)
        if not org or not str(org).strip():
            skipped.append(f"PEN {pen}: mangler IANA-navn (kjør IANA-synk)")
            continue
        name = str(org).strip()
        if len(name) > 255:
            name = name[:252] + "…"
        clash = db.execute(select(Manufacturer).where(Manufacturer.name == name)).scalar_one_or_none()
        if clash:
            suffix = f" (IANA PEN {pen})"
            name = (name[: 255 - len(suffix)] + suffix)[:255]

        row = Manufacturer(
            name=name,
            description=None,
            website_url=None,
            iana_enterprise_number=pen,
        )
        db.add(row)
        try:
            db.commit()
            db.refresh(row)
            created.append({"enterprise_number": pen, "manufacturer_id": row.id, "name": row.name})
        except IntegrityError:
            db.rollback()
            skipped.append(f"PEN {pen}: kunne ikke opprette (navn/PEN-konflikt)")
        except Exception as e:  # noqa: BLE001
            db.rollback()
            skipped.append(f"PEN {pen}: {e!s}"[:500])

    return {"created": created, "skipped": skipped}


def compile_mib_file(db: Session, settings: Settings, filename: str) -> dict:
    meta = db.get(SnmpMibFileMeta, filename)
    if meta is None:
        meta = refresh_mib_meta_from_disk(db, settings, filename)
    if meta is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="MIB-fil ikke funnet")

    path = mib_disk.resolve_mib_disk_path(settings, filename)

    text = path.read_text(encoding="utf-8", errors="replace")
    text, mib_normalized = normalize_mib_source_text(text)
    if mib_normalized:
        path.write_text(text, encoding="utf-8", newline="\n")
    module = guess_module_name(filename, text)
    meta.module_name = module
    stem = Path(filename).stem
    hints = list(dict.fromkeys([module, stem]))
    # pysmi leter etter «stem» + .txt/.mib/.my (f.eks. MBG-SNMP-NTP-DISPLAY.mib), ikke nødvendigvis DEFINITIONS-navnet
    # (MBG-SNMP-NTP-DISPLAY-MIB.mib). Ulik stem → kompilér med filnavn som frø.
    compile_seed = stem if stem.casefold() != module.casefold() else module
    results = compile_mib_modules(
        settings,
        [compile_seed],
        ignore_errors=False,
        rebuild=True,
        resolution_hints=hints,
    )
    st, err, resolved = results.get(compile_seed, ("missing", "ukjent feil", None))
    now = _utcnow()
    ok = compile_status_is_success(st)
    meta.compile_status = "ok" if ok else "error"
    meta.compile_message = None if ok else (err or st)
    meta.compiled_at = now if ok else None
    meta.compiled_module_name = (resolved or module) if ok else None
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
    for row in list_mibs_detailed(db, settings):
        if row["name"] == filename:
            return row
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


def compile_pending_mibs(db: Session, settings: Settings) -> list[dict]:
    out: list[dict] = []
    for row in mib_disk.list_mib_files(settings):
        name = row["name"]
        meta = db.get(SnmpMibFileMeta, name)
        if meta is None or meta.compile_status != "pending":
            continue
        try:
            out.append(compile_mib_file(db, settings, name))
        except Exception as e:  # noqa: BLE001
            m = db.get(SnmpMibFileMeta, name)
            if m:
                m.compile_status = "error"
                m.compile_message = str(e)[:4000]
                m.updated_at = _utcnow()
                db.commit()
            out.append(mib_detail_dict(db, settings, row))
    return out


def run_compile_all_mibs_background() -> None:
    """Kall fra FastAPI BackgroundTasks; egen DB-sesjon (request-sesjonen er lukket)."""
    settings = get_settings()
    db = SessionLocal()
    try:
        compile_all_mibs(db, settings)
        logger.info("MIB compile-all (background) fullført")
    except Exception:
        logger.exception("MIB compile-all (background) feilet")
    finally:
        db.close()


def run_compile_pending_mibs_background() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        compile_pending_mibs(db, settings)
        logger.info("MIB compile-pending (background) fullført")
    except Exception:
        logger.exception("MIB compile-pending (background) feilet")
    finally:
        db.close()


def delete_mib_complete(db: Session, settings: Settings, filename: str) -> None:
    meta = db.get(SnmpMibFileMeta, filename)
    mod = meta.compiled_module_name if meta else None
    mib_disk.delete_mib_file(settings, filename)
    if meta:
        db.delete(meta)
    db.commit()
    refresh_missing_imports_all(db, settings)
    if mod:
        p = compiled_py_path(settings, mod)
        if p and p.is_file():
            p.unlink(missing_ok=True)
        if p:
            pyc = p.with_suffix(".pyc")
            if pyc.is_file():
                pyc.unlink(missing_ok=True)


def _rename_mib_file_meta_row(db: Session, old_filename: str, new_filename: str) -> None:
    if old_filename == new_filename:
        return
    row = db.get(SnmpMibFileMeta, old_filename)
    if row is None:
        return
    if db.get(SnmpMibFileMeta, new_filename) is not None:
        db.delete(row)
        return
    db.execute(
        update(SnmpMibFileMeta)
        .where(SnmpMibFileMeta.filename == old_filename)
        .values(filename=new_filename),
    )


def normalize_mib_library_filenames_on_disk(db: Session, settings: Settings) -> dict[str, Any]:
    """Døp om *.txt/*.my/*.mib.txt m.m. til kanonisk *.mib; oppdater snmp_mib_file_meta. Hopper over treff der målfil finnes."""
    root = settings.mib_root_path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    paths = [
        p
        for p in root.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.name != ".index"
    ]
    paths.sort(key=lambda p: (-len(p.name), p.name))
    moved: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for p in paths:
        try:
            target = mib_disk.validate_mib_filename(p.name)
        except HTTPException as e:
            detail = e.detail if isinstance(e.detail, str) else str(e.detail)
            skipped.append({"file": p.name, "reason": detail})
            continue
        if p.name == target:
            continue
        dest = (root / target).resolve()
        src = p.resolve()
        if not str(src).startswith(str(root)) or not str(dest).startswith(str(root)):
            skipped.append({"file": p.name, "reason": "ugyldig sti"})
            continue
        if dest.exists():
            skipped.append({"file": p.name, "to": target, "reason": "målfil finnes allerede"})
            continue
        old_name = p.name
        p.rename(dest)
        moved.append({"from": old_name, "to": target})
        _rename_mib_file_meta_row(db, old_name, target)
    db.commit()
    rebuild_pysmi_mib_index(root)
    refresh_missing_imports_all(db, settings)
    return {"moved": moved, "skipped": skipped, "moved_count": len(moved)}
