"""MIB/SNMP browser: OID-tre + resolv av OID til (modul, symbol) + def-snutter.

Dette er en lettvektsindeks bygget fra kompilerte PySNMP-moduler (pysmi → *.py).
Den er ment for GUI-browsing (lazy tree loading), ikke som en full MIB-analysator.
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import Settings
from app.services import snmp_mibs as mib_disk
from app.services.snmp_mib_index import extract_module_name_from_mib_text, mib_module_to_files_map


_OID_RE = re.compile(r"^\s*(?:\d+\.)*\d+\s*$")


def _parse_oid_dotted(s: str) -> tuple[int, ...]:
    raw = s.strip().strip(".")
    if not raw or not _OID_RE.fullmatch(raw):
        raise ValueError("invalid oid")
    parts = tuple(int(x) for x in raw.split(".") if x != "")
    if not parts:
        raise ValueError("invalid oid")
    return parts


def _oid_to_dotted(oid: tuple[int, ...]) -> str:
    return ".".join(str(int(x)) for x in oid)


@dataclass(frozen=True)
class BrowserSymbol:
    oid: tuple[int, ...]
    label: str
    module: str | None
    symbol: str | None


class _BrowserIndex:
    def __init__(self) -> None:
        self.built_from_compiled_mtime: float | None = None
        self.children: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
        self.best_symbol_for_oid: dict[tuple[int, ...], BrowserSymbol] = {}


_idx = _BrowserIndex()
_idx_lock = threading.Lock()


def _compiled_dir_mtime(settings: Settings) -> float:
    root = settings.mib_compiled_path.resolve()
    if not root.is_dir():
        return 0.0
    try:
        return max((p.stat().st_mtime for p in root.glob("*.py")), default=0.0)
    except OSError:
        return 0.0


def _pick_better_symbol(a: BrowserSymbol, b: BrowserSymbol) -> BrowserSymbol:
    """Velg en stabil 'beste' label når flere symboler deler samme OID."""
    # Foretrekk eksplisitt modul/symbol framfor bare numerisk.
    a_has = int(bool(a.module and a.symbol))
    b_has = int(bool(b.module and b.symbol))
    if a_has != b_has:
        return a if a_has > b_has else b
    # Foretrekk kortere label (iso > iso(1) osv).
    if len(a.label) != len(b.label):
        return a if len(a.label) < len(b.label) else b
    # Stabilt: alfabetisk.
    return a if a.label.casefold() <= b.label.casefold() else b


def _build_index(settings: Settings) -> _BrowserIndex:
    compiled_root = settings.mib_compiled_path.resolve()
    idx = _BrowserIndex()

    # Importer pysnmp kun når vi faktisk bygger indeks (raskere import for resten av appen).
    from pysnmp.smi import builder as pysnmp_builder
    from pysnmp.smi import view as pysnmp_view
    from pysnmp.smi.compiler import addMibCompiler  # type: ignore
    mib_builder = pysnmp_builder.MibBuilder()
    if compiled_root.is_dir():
        mib_builder.addMibSources(pysnmp_builder.DirMibSource(str(compiled_root)))

    # Sørg for at standard MIB-pakker (pysnmp) er tilgjengelig.
    # addMibCompiler gir også mulighet til å hente ASN.1, men vi bruker primært kompilerte *.py her.
    try:
        addMibCompiler(mib_builder)
    except Exception:
        # Ikke fatal; browsing av lokale kompilerte moduler fungerer ofte uansett.
        pass

    module_names: list[str] = []
    if compiled_root.is_dir():
        for p in compiled_root.glob("*.py"):
            if p.name.startswith("_") or p.stem in {"__init__"}:
                continue
            module_names.append(p.stem)

    # Last alltid noen basis-MIB-er slik at iso/org/dod/... navnesettes.
    base_modules = ["SNMPv2-SMI", "SNMPv2-MIB", "SNMPv2-TC"]
    try:
        mib_builder.loadModules(*base_modules)
    except Exception:
        pass

    # Last lokale kompilerte moduler én og én — én ødelagt .py stopper ikke resten.
    if module_names:
        for mod_name in sorted(set(module_names)):
            try:
                mib_builder.loadModules(mod_name)
            except Exception:
                continue

    # Iterer over eksporterte symboler og samle OID-er.
    children: dict[tuple[int, ...], set[tuple[int, ...]]] = {}
    best: dict[tuple[int, ...], BrowserSymbol] = {}

    for mod, syms in (mib_builder.mibSymbols or {}).items():
        for sym_name, obj in (syms or {}).items():
            get_name = getattr(obj, "getName", None)
            if not callable(get_name):
                continue
            try:
                n, oid = get_name()
            except Exception:
                continue
            if not isinstance(oid, tuple) or not oid:
                continue
            # OID er tuple[int,...] i praksis; normaliser defensivt.
            try:
                oid_t = tuple(int(x) for x in oid)
            except Exception:
                continue
            label = str(n) if isinstance(n, str) else str(sym_name)
            bs = BrowserSymbol(oid=oid_t, label=label, module=str(mod), symbol=str(sym_name))
            prev = best.get(oid_t)
            best[oid_t] = bs if prev is None else _pick_better_symbol(prev, bs)
            parent = oid_t[:-1]
            children.setdefault(parent, set()).add(oid_t)

    # Bootstrap OID-sti slik at treet ikke blir tomt i GUI.
    bootstrap: list[tuple[str, str]] = [
        ("1", "iso"),
        ("1.3", "org"),
        ("1.3.6", "dod"),
        ("1.3.6.1", "internet"),
        ("1.3.6.1.2", "mgmt"),
        ("1.3.6.1.2.1", "mib-2"),
        ("1.3.6.1.4", "private"),
        ("1.3.6.1.4.1", "enterprises"),
    ]
    for dotted, label in bootstrap:
        try:
            oid = _parse_oid_dotted(dotted)
        except ValueError:
            continue
        if oid not in best:
            best[oid] = BrowserSymbol(oid=oid, label=label, module="SNMPv2-SMI", symbol=label)
        if len(oid) > 1:
            children.setdefault(oid[:-1], set()).add(oid)
        else:
            children.setdefault(tuple(), set()).add(oid)

    # Legg inn "mellomnoder" slik at treet blir komplett opp til iso.
    for oid_t in list(best.keys()):
        p = oid_t[:-1]
        while p:
            children.setdefault(p[:-1], set()).add(p)
            p = p[:-1]

    # Base OID-er vi vil ha navn på i treet (iso/org/dod/…).
    # Når de ikke finnes i kompilerte moduler, får vi i det minste numerisk tre.
    try:
        mvc = pysnmp_view.MibViewController(mib_builder)
        for dotted in ("1", "1.3", "1.3.6", "1.3.6.1", "1.3.6.1.4", "1.3.6.1.4.1"):
            oid = _parse_oid_dotted(dotted)
            try:
                modn, symn, _suf = mvc.getNodeLocation(oid)  # type: ignore[attr-defined]
                name = mvc.getNodeName(oid)[0]  # type: ignore[attr-defined]
                bs = BrowserSymbol(oid=oid, label=str(name), module=str(modn), symbol=str(symn))
                prev = best.get(oid)
                best[oid] = bs if prev is None else _pick_better_symbol(prev, bs)
            except Exception:
                # fallback label
                if oid not in best:
                    best[oid] = BrowserSymbol(oid=oid, label=_oid_to_dotted(oid), module=None, symbol=None)
    except Exception:
        pass

    idx.children = {k: sorted(v, key=lambda x: (len(x), x)) for k, v in children.items()}
    idx.best_symbol_for_oid = best
    idx.built_from_compiled_mtime = _compiled_dir_mtime(settings)
    return idx


def ensure_index(settings: Settings) -> None:
    """Bygg/rebygg indeksen hvis kompilerte MIB-er endrer seg."""
    with _idx_lock:
        mtime = _compiled_dir_mtime(settings)
        if _idx.built_from_compiled_mtime is not None and mtime <= _idx.built_from_compiled_mtime:
            return
        new_idx = _build_index(settings)
        _idx.children = new_idx.children
        _idx.best_symbol_for_oid = new_idx.best_symbol_for_oid
        _idx.built_from_compiled_mtime = new_idx.built_from_compiled_mtime


def list_children(settings: Settings, parent_oid_dotted: str) -> list[dict[str, Any]]:
    ensure_index(settings)
    parent = _parse_oid_dotted(parent_oid_dotted)
    rows: list[dict[str, Any]] = []
    for child in _idx.children.get(parent, []):
        sym = _idx.best_symbol_for_oid.get(child)
        label = sym.label if sym else str(child[-1])
        rows.append(
            {
                "oid": _oid_to_dotted(child),
                "label": label,
                "has_children": child in _idx.children,
                "module": sym.module if sym else None,
                "symbol": sym.symbol if sym else None,
            }
        )
    return rows


def resolve_oid(settings: Settings, oid_dotted: str) -> dict[str, Any]:
    ensure_index(settings)
    oid = _parse_oid_dotted(oid_dotted)
    sym = _idx.best_symbol_for_oid.get(oid)
    return {
        "oid": _oid_to_dotted(oid),
        "label": sym.label if sym else _oid_to_dotted(oid),
        "module": sym.module if sym else None,
        "symbol": sym.symbol if sym else None,
        "has_children": oid in _idx.children,
    }


def definition_snippet(settings: Settings, *, module_name: str | None, symbol: str | None) -> str:
    """Returner en best-effort definisjons-snutt fra MIB-kilden.

    Hvis vi ikke klarer å finne definisjonen, returneres hele filen (begrenset av frontend).
    """
    if not module_name:
        return ""
    module_to_files = mib_module_to_files_map(settings.mib_root_path.resolve())
    files = module_to_files.get(module_name.upper(), [])
    if not files:
        return ""
    path = (settings.mib_root_path.resolve() / files[0]).resolve()
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not symbol:
        return text
    sym = re.escape(symbol)
    # Start på linje som begynner med symbolet.
    start = re.search(rf"(?m)^\s*{sym}\b", text)
    if not start:
        return text
    # Slutt ved neste definisjon-start (heuristikk), men kun på linjer *etter* første linje
    # i utdraget — ellers treffer mønsteret på «ib-2 …» når vi søker i after[1:] og vi ender
    # opp med å slice til ett tegn («m»).
    after = text[start.start() :]
    first_nl = after.find("\n")
    tail = after[first_nl + 1 :] if first_nl != -1 else ""
    stop = re.search(
        r"(?m)^\s*[A-Za-z][A-Za-z0-9-]*\s+(?:OBJECT-TYPE|OBJECT IDENTIFIER|NOTIFICATION-TYPE|TEXTUAL-CONVENTION|MODULE-IDENTITY)\b",
        tail,
    )
    if stop:
        return (after[: first_nl + 1 + stop.start()] if first_nl != -1 else after[: stop.start()]).rstrip() + "\n"
    return after.rstrip() + "\n"


def _ancestor_prefixes(oid: tuple[int, ...]) -> list[str]:
    out: list[str] = []
    for i in range(1, len(oid)):
        out.append(_oid_to_dotted(oid[:i]))
    return out


def _module_name_variants(name: str) -> list[str]:
    """PySNMP/pysmi bruker ofte «FOO-MIB» som modulnavn; noen kilder bruker «FOO_MIB»."""
    s = name.strip()
    if not s:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for v in (s, s.replace("-", "_"), s.replace("_", "-")):
        k = v.upper()
        if k not in seen:
            seen.add(k)
            out.append(v)
    return out


def locate_module_oid(settings: Settings, module_name: str) -> dict[str, Any]:
    """Returner grunnleggende OID for en ASN.1-modul (pysmi-modulnavn), for GUI-fokus i treet."""
    ensure_index(settings)
    raw = module_name.strip()
    if not raw:
        return {"found": False, "error": "empty module", "module": None, "ancestor_oids": []}
    mu_set = {v.upper() for v in _module_name_variants(raw)}
    candidates: list[tuple[tuple[int, ...], BrowserSymbol]] = []
    for oid_t, sym in _idx.best_symbol_for_oid.items():
        if sym.module and sym.module.upper() in mu_set:
            candidates.append((oid_t, sym))

    if not candidates:
        return {
            "found": False,
            "error": f"ingen OID funnet for modul «{raw}» (kompiler MIB og prøv igjen)",
            "module": raw,
            "ancestor_oids": [],
        }

    # Grunnleggende valg: grunneste OID i modulen (ofte nær modul-roten i treet).
    oid_t, sym = min(candidates, key=lambda x: (len(x[0]), x[0]))
    return {
        "found": True,
        "error": None,
        "module": sym.module,
        "oid": _oid_to_dotted(oid_t),
        "label": sym.label,
        "symbol": sym.symbol,
        "ancestor_oids": _ancestor_prefixes(oid_t),
    }


def locate_from_mib_filename(settings: Settings, filename: str) -> dict[str, Any]:
    """Utled modulnavn fra MIB-fil og lokalisér i indeksen."""
    path = mib_disk.try_resolve_mib_disk_path(settings, filename)
    if path is None or not path.is_file():
        return {
            "found": False,
            "error": f"fant ikke MIB-fil «{filename}»",
            "module": None,
            "ancestor_oids": [],
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    mod = extract_module_name_from_mib_text(text) or Path(filename).stem
    r = locate_module_oid(settings, mod)
    if r.get("found"):
        return r
    return {
        **r,
        "error": r.get("error") or f"fant ikke OID for modul «{mod}» fra «{filename}»",
    }
