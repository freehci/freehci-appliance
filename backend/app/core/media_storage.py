"""Filsystem-lagring for DCIM-media (logoer m.m.). Ikke lagre binærdato i database."""

from __future__ import annotations

from pathlib import Path

MFR_LOGO_SUBDIR = "dcim/manufacturer_logos"

MIME_TO_EXT: dict[str, str] = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
    "image/svg+xml": "svg",
}


def safe_join_under_upload_root(upload_root: Path, *parts: str) -> Path:
    """Sikrer at resultatet ligger under upload_root (ingen path traversal)."""
    root = upload_root.resolve()
    target = (root.joinpath(*parts)).resolve()
    target.relative_to(root)
    return target


def manufacturer_logo_relpath(manufacturer_id: int, mime: str) -> str:
    ext = MIME_TO_EXT[mime]
    return f"{MFR_LOGO_SUBDIR}/{manufacturer_id}.{ext}"


def write_manufacturer_logo_file(upload_root: Path, manufacturer_id: int, content: bytes, mime: str) -> str:
    """Skriver logo til disk; sletter eventuelle andre filendelser for samme produsent-ID."""
    relpath = manufacturer_logo_relpath(manufacturer_id, mime)
    dest = safe_join_under_upload_root(upload_root, relpath)
    dest.parent.mkdir(parents=True, exist_ok=True)
    logo_dir = safe_join_under_upload_root(upload_root, MFR_LOGO_SUBDIR)
    if logo_dir.is_dir():
        for f in logo_dir.glob(f"{manufacturer_id}.*"):
            try:
                f.unlink()
            except OSError:
                pass
    dest.write_bytes(content)
    return relpath


def delete_manufacturer_logo_files(upload_root: Path, manufacturer_id: int) -> None:
    logo_dir = safe_join_under_upload_root(upload_root, MFR_LOGO_SUBDIR)
    if not logo_dir.is_dir():
        return
    for f in logo_dir.glob(f"{manufacturer_id}.*"):
        try:
            f.unlink()
        except OSError:
            pass


def resolve_manufacturer_logo_path(upload_root: Path, relpath: str) -> Path | None:
    p = safe_join_under_upload_root(upload_root, relpath)
    return p if p.is_file() else None
