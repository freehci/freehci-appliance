"""Manglende vendor-MIB i IMPORTS (sammenlign med filer i MIB_ROOT og kjente IETF-moduler)."""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.snmp_catalog import SnmpMibFileMeta
from app.services import snmp_mibs as mib_disk
from app.services.snmp_mib_compile import _PYSMI_INFRA_MODULES
from app.services.snmp_mib_index import mib_module_names_in_root
from app.services.snmp_mib_parse import _STD_IMPORT_MIBS, guess_module_name, imported_mib_modules

# Moduler som PySNMP/pysmi vanligvis løser uten fil i MIB_ROOT (HTTP / innebygd).
_RESOLVED_WITHOUT_LOCAL_FILE: frozenset[str] = frozenset(_STD_IMPORT_MIBS) | frozenset(_PYSMI_INFRA_MODULES)


def missing_vendor_import_modules(
    mib_text: str,
    own_module_name: str | None,
    local_module_names: set[str],
) -> list[str]:
    """Returner modulnavn fra IMPORTS som verken er standard eller finnes som lokal kilde."""
    own = (own_module_name or "").strip()
    own_u = own.upper()
    out: list[str] = []
    seen: set[str] = set()
    for mod in imported_mib_modules(mib_text):
        if mod.upper() == own_u:
            continue
        if mod in _RESOLVED_WITHOUT_LOCAL_FILE:
            continue
        if mod.upper() in {m.upper() for m in local_module_names}:
            continue
        if mod not in seen:
            seen.add(mod)
            out.append(mod)
    return out


def _read_mib_text(settings: Settings, filename: str) -> str:
    root = settings.mib_root_path.resolve()
    path = (root / filename).resolve()
    if not str(path).startswith(str(root)) or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def refresh_missing_imports_all(db: Session, settings: Settings) -> None:
    """Oppdater missing_import_modules_json for alle kjente MIB-filer (etter opplasting/sletting)."""
    root = settings.mib_root_path.resolve()
    local_mods = mib_module_names_in_root(root)
    for row in mib_disk.list_mib_files(settings):
        name = row["name"]
        meta = db.get(SnmpMibFileMeta, name)
        if meta is None:
            continue
        text = _read_mib_text(settings, name)
        if not text:
            meta.missing_import_modules_json = "[]"
            continue
        mod = (meta.module_name or "").strip() or guess_module_name(name, text)
        missing = missing_vendor_import_modules(text, mod, local_mods)
        meta.missing_import_modules_json = json.dumps(missing)
    db.commit()


def parse_missing_imports_json(raw: str | None) -> list[str]:
    if not raw or not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [str(x) for x in data if isinstance(x, str) and x.strip()]
