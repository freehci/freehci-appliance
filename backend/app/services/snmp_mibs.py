"""Lagring av opplastede MIB-filer på disk."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException

from app.core.config import Settings
from app.services.snmp_mib_index import rebuild_pysmi_mib_index
from app.services.snmp_mib_normalize import normalize_mib_source_text

_MIB_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,199}$")
_ALLOWED_SUFFIX = frozenset({".mib", ".my", ".txt"})


def _ensure_mib_root(settings: Settings) -> Path:
    root = settings.mib_root_path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def validate_mib_filename(name: str) -> str:
    base = Path(name).name
    if not _MIB_NAME_RE.fullmatch(base):
        raise HTTPException(status_code=400, detail="ugyldig MIB-filnavn")
    suf = Path(base).suffix.lower()
    if suf not in _ALLOWED_SUFFIX:
        raise HTTPException(
            status_code=400,
            detail="kun .mib, .my eller .txt er tillatt",
        )
    stem = Path(base).stem
    stem_l = stem.lower()
    # pysmi prøver f.eks. «BROCADE-REG-MIB» + «.txt» → Brocade-REG-MIB.txt, aldri *.mib.txt.
    if suf == ".txt" and (stem_l.endswith(".mib") or stem_l.endswith(".my")):
        raise HTTPException(
            status_code=400,
            detail="bruk ett suffiks (.mib, .my eller .txt), ikke .mib.txt eller .my.txt",
        )
    if suf == ".mib" and stem_l.endswith(".my"):
        raise HTTPException(
            status_code=400,
            detail="bruk ett suffiks (.mib, .my eller .txt), ikke .my.mib",
        )
    if suf == ".my" and stem_l.endswith(".mib"):
        raise HTTPException(
            status_code=400,
            detail="bruk ett suffiks (.mib, .my eller .txt), ikke .mib.my",
        )
    return base


def list_mib_files(settings: Settings) -> list[dict]:
    root = _ensure_mib_root(settings)
    out: list[dict] = []
    for p in sorted(root.iterdir()):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        st = p.stat()
        out.append(
            {
                "name": p.name,
                "size_bytes": st.st_size,
                "modified_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc),
            },
        )
    return out


def save_mib_file(settings: Settings, filename: str, data: bytes) -> dict:
    safe = validate_mib_filename(filename)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="MIB-fil for stor (maks 5 MiB)")
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    text = data.decode("utf-8", errors="replace")
    text, _normalized = normalize_mib_source_text(text)
    data = text.encode("utf-8")
    root = _ensure_mib_root(settings)
    path = (root / safe).resolve()
    if not str(path).startswith(str(root.resolve())):
        raise HTTPException(status_code=400, detail="ugyldig sti")
    path.write_bytes(data)
    rebuild_pysmi_mib_index(root)
    st = path.stat()
    return {
        "name": path.name,
        "size_bytes": st.st_size,
        "modified_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc),
    }


def read_mib_text(settings: Settings, filename: str) -> str:
    """Les dekodet MIB-kildetekst (UTF-8 med feil-erstatning)."""
    safe = validate_mib_filename(filename)
    root = _ensure_mib_root(settings)
    path = (root / safe).resolve()
    if not str(path).startswith(str(root.resolve())):
        raise HTTPException(status_code=400, detail="ugyldig sti")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="MIB-fil ikke funnet")
    return path.read_text(encoding="utf-8", errors="replace")


def delete_mib_file(settings: Settings, filename: str) -> None:
    safe = validate_mib_filename(filename)
    root = _ensure_mib_root(settings)
    path = (root / safe).resolve()
    if not str(path).startswith(str(root.resolve())):
        raise HTTPException(status_code=400, detail="ugyldig sti")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="MIB-fil ikke funnet")
    path.unlink()
    rebuild_pysmi_mib_index(root)
