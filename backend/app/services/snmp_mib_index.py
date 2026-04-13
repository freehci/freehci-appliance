"""PySMI FileReader .index: kartlegg ASN.1-modulnavn → lokal fil (Juniper mib-jnx-*.txt m.m.)."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

# Tillat innrykk før modulnavn, linjeskift før DEFINITIONS, og én eller flere
# ASN.1-linjekommentarer (-- …) mellom navn og DEFINITIONS (vanlig i eldre vendor-MIB).
_MODULE_DEF_RE = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9-]*)(?:\s+|--[^\r\n]*\r?\n)+DEFINITIONS\s*::=",
    re.MULTILINE,
)

_INDEX_NAME = ".index"


def mib_module_names_in_root(mib_root: Path) -> set[str]:
    """Alle MODULE DEFINITIONS-navn funnet som .mib/.my/.txt i katalogen."""
    root = mib_root.resolve()
    names: set[str] = set()
    if not root.is_dir():
        return names
    for p in root.iterdir():
        if not p.is_file():
            continue
        if p.name == _INDEX_NAME or p.name.startswith("."):
            continue
        if p.suffix.lower() not in {".mib", ".my", ".txt"}:
            continue
        try:
            raw = p.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                raw = raw[3:]
            text = raw.decode("utf-8", errors="replace")
        except OSError:
            continue
        mod = extract_module_name_from_mib_text(text)
        if mod:
            names.add(mod)
    return names


def mib_module_to_files_map(mib_root: Path) -> dict[str, list[str]]:
    """Uppercase MODULE DEFINITIONS-navn → MIB-filnavn (alle treff, sortert).

    Brukes av SNMP-tre-topologi slik at foreldermatch følger faktisk kilde, ikke
    kun cachet module_name i DB (som kan være utdatert når fil er byttet på disk).
    """
    root = mib_root.resolve()
    raw_map: dict[str, list[str]] = defaultdict(list)
    if not root.is_dir():
        return {}
    for p in root.iterdir():
        if not p.is_file():
            continue
        if p.name == _INDEX_NAME or p.name.startswith("."):
            continue
        if p.suffix.lower() not in {".mib", ".my", ".txt"}:
            continue
        try:
            b = p.read_bytes()
            if b.startswith(b"\xef\xbb\xbf"):
                b = b[3:]
            text = b.decode("utf-8", errors="replace")
        except OSError:
            continue
        mod = extract_module_name_from_mib_text(text)
        if mod:
            raw_map[mod.upper()].append(p.name)
    return {k: sorted(v) for k, v in raw_map.items()}


def extract_module_name_from_mib_text(text: str) -> str | None:
    text = text.lstrip("\ufeff")
    m = _MODULE_DEF_RE.search(text)
    return m.group(1) if m else None


def rebuild_pysmi_mib_index(mib_root: Path) -> None:
    """Skriv mib_root/.index slik at PySMI finner filer der filnavn ikke matcher modulnavn."""
    root = mib_root.resolve()
    if not root.is_dir():
        return

    candidates: dict[str, list[tuple[str, float]]] = {}
    for p in root.iterdir():
        if not p.is_file():
            continue
        if p.name == _INDEX_NAME or p.name.startswith("."):
            continue
        suf = p.suffix.lower()
        if suf not in {".mib", ".my", ".txt"}:
            continue
        try:
            raw = p.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                raw = raw[3:]
            text = raw.decode("utf-8", errors="replace")
        except OSError:
            continue
        mod = extract_module_name_from_mib_text(text)
        if not mod:
            continue
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        candidates.setdefault(mod, []).append((p.name, mtime))

    lines: list[str] = []
    for mod in sorted(candidates):
        rows = candidates[mod]
        best_name, _best_mtime = max(rows, key=lambda x: (x[1], x[0]))
        lines.append(f"{mod}\t{best_name}")

    index_path = root / _INDEX_NAME
    try:
        index_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    except OSError:
        pass
