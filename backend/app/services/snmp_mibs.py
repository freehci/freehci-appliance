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


def _normalize_mib_filename_base(base: str) -> str:
    """Kanonisk lagringsnavn: alltid *.mib (pysmi støtter .mib; ett suffiks unngår rare filnavn)."""
    while True:
        lower = base.lower()
        if lower.endswith(".mib.txt"):
            base = base[: -len(".mib.txt")] + ".mib"
            continue
        if lower.endswith(".my.txt"):
            base = base[: -len(".my.txt")] + ".mib"
            continue
        break
    p = Path(base)
    suf = p.suffix.lower()
    if suf == ".txt":
        return f"{p.stem}.mib"
    if suf == ".my":
        return f"{p.stem}.mib"
    return base


def _ensure_mib_root(settings: Settings) -> Path:
    root = settings.mib_root_path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _mib_path_candidates(settings: Settings, name: str) -> list[Path]:
    """Absolutte stier under MIB-root: kanonisk *.mib først, deretter rå basename og vanlige legacy-varianter."""
    if Path(name).name != name:
        raise HTTPException(status_code=400, detail="ugyldig MIB-filnavn")
    raw = Path(name).name
    root = _ensure_mib_root(settings)
    rr = root.resolve()
    safe = validate_mib_filename(name)
    seq: list[str] = [safe, raw] if raw != safe else [safe]
    stem = Path(safe).stem
    if safe.lower().endswith(".mib"):
        for alt in (f"{stem}.txt", f"{stem}.my", f"{stem}.mib.txt", f"{stem}.my.txt"):
            if alt not in seq:
                seq.append(alt)
    out: list[Path] = []
    seen_resolved: set[str] = set()
    for rel in seq:
        path = (rr / rel).resolve()
        key = str(path)
        if key in seen_resolved:
            continue
        seen_resolved.add(key)
        if not str(path).startswith(str(rr)):
            raise HTTPException(status_code=400, detail="ugyldig sti")
        out.append(path)
    return out


def try_resolve_mib_disk_path(settings: Settings, name: str) -> Path | None:
    """Returner første eksisterende MIB-fil under root, eller None."""
    for path in _mib_path_candidates(settings, name):
        if path.is_file():
            return path
    return None


def resolve_mib_disk_path(settings: Settings, name: str) -> Path:
    """Som try_resolve_mib_disk_path, men 404 hvis ingen fil matcher."""
    p = try_resolve_mib_disk_path(settings, name)
    if p is None:
        raise HTTPException(status_code=404, detail="MIB-fil ikke funnet")
    return p


def validate_mib_filename(name: str) -> str:
    """Valider inndatafilnavn; returner alltid kanonisk *.mib for lagring/oppslag."""
    raw_in = Path(name).name
    if raw_in != name:
        raise HTTPException(status_code=400, detail="ugyldig MIB-filnavn")
    suf_in = Path(raw_in).suffix.lower()
    if suf_in not in {".mib", ".my", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="kun .mib, .my eller .txt er tillatt som opplastet filnavn",
        )
    base = _normalize_mib_filename_base(raw_in)
    if not _MIB_NAME_RE.fullmatch(base):
        raise HTTPException(status_code=400, detail="ugyldig MIB-filnavn")
    suf = Path(base).suffix.lower()
    if suf != ".mib":
        raise HTTPException(status_code=400, detail="ugyldig MIB-filnavn")
    stem_l = Path(base).stem.lower()
    if stem_l.endswith(".my"):
        raise HTTPException(
            status_code=400,
            detail="bruk ett suffiks (.mib, .my eller .txt), ikke .my.mib",
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
    max_b = settings.mib_upload_max_bytes
    if len(data) > max_b:
        mib_mb = max_b // (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"MIB-fil for stor (maks {mib_mb} MiB)",
        )
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
    path = resolve_mib_disk_path(settings, filename)
    return path.read_text(encoding="utf-8", errors="replace")


def delete_mib_file(settings: Settings, filename: str) -> None:
    path = resolve_mib_disk_path(settings, filename)
    path.unlink()
    rebuild_pysmi_mib_index(_ensure_mib_root(settings))
