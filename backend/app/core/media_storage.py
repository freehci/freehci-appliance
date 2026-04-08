"""Filsystem-lagring for DCIM-media (logoer m.m.). Ikke lagre binærdato i database."""

from __future__ import annotations

from pathlib import Path

MFR_LOGO_SUBDIR = "dcim/manufacturer_logos"
DM_IMAGE_SUBDIR = "dcim/device_model_images"

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


def device_model_image_relpath(model_id: int, slot: str, mime: str) -> str:
    if slot not in ("front", "back"):
        raise ValueError("slot må være front eller back")
    ext = MIME_TO_EXT[mime]
    return f"{DM_IMAGE_SUBDIR}/{model_id}_{slot}.{ext}"


def write_device_model_image_file(
    upload_root: Path,
    model_id: int,
    slot: str,
    content: bytes,
    mime: str,
) -> str:
    relpath = device_model_image_relpath(model_id, slot, mime)
    dest = safe_join_under_upload_root(upload_root, relpath)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img_dir = safe_join_under_upload_root(upload_root, DM_IMAGE_SUBDIR)
    if img_dir.is_dir():
        for f in img_dir.glob(f"{model_id}_{slot}.*"):
            try:
                f.unlink()
            except OSError:
                pass
    dest.write_bytes(content)
    return relpath


def delete_device_model_image_slot(upload_root: Path, model_id: int, slot: str) -> None:
    img_dir = safe_join_under_upload_root(upload_root, DM_IMAGE_SUBDIR)
    if not img_dir.is_dir():
        return
    for f in img_dir.glob(f"{model_id}_{slot}.*"):
        try:
            f.unlink()
        except OSError:
            pass


def delete_device_model_all_images(upload_root: Path, model_id: int) -> None:
    delete_device_model_image_slot(upload_root, model_id, "front")
    delete_device_model_image_slot(upload_root, model_id, "back")


def resolve_device_model_image_path(upload_root: Path, relpath: str) -> Path | None:
    p = safe_join_under_upload_root(upload_root, relpath)
    return p if p.is_file() else None
