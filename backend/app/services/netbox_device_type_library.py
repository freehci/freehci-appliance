"""Import NetBox Device Type Library into FreeHCI DCIM."""

from __future__ import annotations

import hashlib
import io
import math
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import httpx
import yaml
from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.dcim import (
    DeviceModel,
    DeviceModelIdentity,
    DeviceModelTemplate,
    Manufacturer,
    NetBoxDeviceTypeLibraryImport,
    NetBoxDeviceTypeLibraryItem,
)
from app.schemas.dcim import (
    DeviceModelCreate,
    NetBoxDtlApplyItemRead,
    NetBoxDtlApplyRead,
    NetBoxDtlApplyRequest,
    NetBoxDtlItemPreviewRead,
    NetBoxDtlPreviewRead,
)
from app.services import dcim as dcim_svc

NETBOX_DTL_GITHUB_ZIP = "https://github.com/netbox-community/devicetype-library/archive/refs/heads/{branch}.zip"
COMPONENT_KEYS = (
    "console-ports",
    "console-server-ports",
    "power-ports",
    "power-outlets",
    "interfaces",
    "front-ports",
    "rear-ports",
    "module-bays",
    "device-bays",
    "inventory-items",
)
IMAGE_MIME_BY_EXT = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def list_imports(db: Session) -> list[NetBoxDeviceTypeLibraryImport]:
    stmt = select(NetBoxDeviceTypeLibraryImport).order_by(
        NetBoxDeviceTypeLibraryImport.created_at.desc(),
        NetBoxDeviceTypeLibraryImport.id.desc(),
    )
    return list(db.scalars(stmt))


def list_items(
    db: Session,
    import_id: int | None = None,
    q: str | None = None,
    manufacturer: str | None = None,
    limit: int = 200,
) -> list[NetBoxDeviceTypeLibraryItem]:
    stmt = select(NetBoxDeviceTypeLibraryItem)
    if import_id is not None:
        stmt = stmt.where(NetBoxDeviceTypeLibraryItem.import_id == import_id)
    if manufacturer:
        stmt = stmt.where(func.lower(NetBoxDeviceTypeLibraryItem.manufacturer) == manufacturer.strip().lower())
    if q:
        needle = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            func.lower(NetBoxDeviceTypeLibraryItem.manufacturer + " " + NetBoxDeviceTypeLibraryItem.model + " " + NetBoxDeviceTypeLibraryItem.slug).like(needle)
        )
    stmt = stmt.order_by(NetBoxDeviceTypeLibraryItem.manufacturer, NetBoxDeviceTypeLibraryItem.model).limit(limit)
    return list(db.scalars(stmt))


def list_device_model_templates(db: Session, device_model_id: int) -> list[DeviceModelTemplate]:
    stmt = (
        select(DeviceModelTemplate)
        .where(DeviceModelTemplate.device_model_id == device_model_id)
        .order_by(DeviceModelTemplate.component_type, DeviceModelTemplate.sort_order, DeviceModelTemplate.name)
    )
    return list(db.scalars(stmt))


async def import_github(db: Session, settings: Settings, branch: str = "master") -> NetBoxDeviceTypeLibraryImport:
    branch = branch.strip() or "master"
    return await import_download(
        db,
        settings,
        NETBOX_DTL_GITHUB_ZIP.format(branch=branch),
        name=f"netbox-device-type-library-{branch}.zip",
        source="github",
        branch=branch,
    )


async def import_upload(
    db: Session,
    settings: Settings,
    upload: UploadFile,
) -> NetBoxDeviceTypeLibraryImport:
    filename = Path(upload.filename or "netbox-device-type-library.zip").name
    data = await upload.read(settings.netbox_dtl_max_zip_bytes + 1)
    if len(data) > settings.netbox_dtl_max_zip_bytes:
        raise HTTPException(status_code=413, detail="NetBox Device Type Library ZIP er for stor")
    return import_bytes(db, settings, data, filename=filename, source="upload")


async def import_download(
    db: Session,
    settings: Settings,
    url: str,
    *,
    name: str | None = None,
    source: str = "download",
    branch: str | None = None,
) -> NetBoxDeviceTypeLibraryImport:
    async with httpx.AsyncClient(follow_redirects=True, timeout=120) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=400, detail=f"Kunne ikke laste ned NetBox DTL ZIP: {exc}") from exc
    data = response.content
    if len(data) > settings.netbox_dtl_max_zip_bytes:
        raise HTTPException(status_code=413, detail="NetBox Device Type Library ZIP er for stor")
    filename = Path(name or url.rstrip("/").rsplit("/", 1)[-1] or "netbox-device-type-library.zip").name
    return import_bytes(db, settings, data, filename=filename, source=source, source_url=url, branch=branch)


def import_bytes(
    db: Session,
    settings: Settings,
    data: bytes,
    *,
    filename: str,
    source: str,
    source_url: str | None = None,
    branch: str | None = None,
) -> NetBoxDeviceTypeLibraryImport:
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise HTTPException(status_code=400, detail="Filen er ikke en gyldig ZIP")
    sha256 = hashlib.sha256(data).hexdigest()
    existing = db.scalar(select(NetBoxDeviceTypeLibraryImport).where(NetBoxDeviceTypeLibraryImport.sha256 == sha256))
    if existing is not None:
        return existing
    archive_path, extract_path = _store_and_extract_zip(settings, data, filename, sha256)
    import_run = NetBoxDeviceTypeLibraryImport(
        name=Path(filename).stem[:255] or f"NetBox DTL {sha256[:12]}",
        source=source,
        source_url=source_url,
        branch=branch,
        file_relpath=_rel(settings.netbox_dtl_root_path, archive_path),
        extract_relpath=_rel(settings.netbox_dtl_root_path, extract_path),
        sha256=sha256,
        status="ready",
        metadata_json={"filename": filename},
    )
    db.add(import_run)
    db.flush()
    items = _index_items(settings, import_run, extract_path)
    import_run.item_count = len(items)
    import_run.manufacturer_count = len({i.manufacturer.strip().lower() for i in items})
    import_run.image_count = sum(1 for i in items if i.front_image_relpath) + sum(1 for i in items if i.rear_image_relpath)
    import_run.component_template_count = sum(sum((i.component_counts_json or {}).values()) for i in items)
    db.add_all(items)
    db.commit()
    db.refresh(import_run)
    return import_run


def preview_apply(db: Session, data: NetBoxDtlApplyRequest) -> NetBoxDtlPreviewRead:
    items = _candidate_items(db, data)
    previews = [_preview_item(db, item) for item in items]
    return NetBoxDtlPreviewRead(import_id=data.import_id, items=previews, total_candidates=len(previews))


def apply_import(db: Session, settings: Settings, data: NetBoxDtlApplyRequest) -> NetBoxDtlApplyRead:
    items = _candidate_items(db, data)
    out: list[NetBoxDtlApplyItemRead] = []
    created = 0
    updated = 0
    for item in items:
        preview = _preview_item(db, item)
        manufacturer = _ensure_manufacturer(db, item.manufacturer)
        model = _find_existing_model(db, item, manufacturer.id)
        if model is None:
            created += 1
            model_read = dcim_svc.create_device_model(
                db,
                DeviceModelCreate(
                    manufacturer_id=manufacturer.id,
                    name=item.model,
                    u_height=_freehci_u_height(item.u_height),
                    form_factor=_form_factor(item),
                    image_front_url=None,
                    image_back_url=None,
                    image_product_url=None,
                ),
            )
            model = db.get(DeviceModel, model_read.id)
            if model is None:
                raise HTTPException(status_code=500, detail="opprettet device model kunne ikke leses")
        else:
            updated += 1
            model.manufacturer_id = manufacturer.id
            model.name = item.model
            model.u_height = _freehci_u_height(item.u_height)
            model.form_factor = _form_factor(item)
            db.add(model)
            db.commit()
            db.refresh(model)
        identities_created = _ensure_device_model_identity(db, model.id, item)
        images_imported = _import_images(db, settings, model, item) if data.include_images else 0
        templates_imported = _sync_templates(db, model.id, item) if data.include_templates else 0
        out.append(
            NetBoxDtlApplyItemRead(
                **preview.model_dump(),
                device_model_id=model.id,
                identities_created=identities_created,
                templates_imported=templates_imported,
                images_imported=images_imported,
            )
        )
    return NetBoxDtlApplyRead(
        import_id=data.import_id,
        applied_count=len(out),
        created_count=created,
        updated_count=updated,
        items=out,
    )


def _candidate_items(db: Session, data: NetBoxDtlApplyRequest) -> list[NetBoxDeviceTypeLibraryItem]:
    import_run = db.get(NetBoxDeviceTypeLibraryImport, data.import_id)
    if import_run is None:
        raise HTTPException(status_code=404, detail="NetBox DTL-import ikke funnet")
    stmt = select(NetBoxDeviceTypeLibraryItem).where(NetBoxDeviceTypeLibraryItem.import_id == data.import_id)
    if data.item_ids:
        stmt = stmt.where(NetBoxDeviceTypeLibraryItem.id.in_(data.item_ids))
    if data.manufacturer:
        stmt = stmt.where(func.lower(NetBoxDeviceTypeLibraryItem.manufacturer) == data.manufacturer.strip().lower())
    if data.q:
        needle = f"%{data.q.strip().lower()}%"
        stmt = stmt.where(
            func.lower(NetBoxDeviceTypeLibraryItem.manufacturer + " " + NetBoxDeviceTypeLibraryItem.model + " " + NetBoxDeviceTypeLibraryItem.slug).like(needle)
        )
    stmt = stmt.order_by(NetBoxDeviceTypeLibraryItem.manufacturer, NetBoxDeviceTypeLibraryItem.model).limit(data.limit)
    return list(db.scalars(stmt))


def _preview_item(db: Session, item: NetBoxDeviceTypeLibraryItem) -> NetBoxDtlItemPreviewRead:
    manufacturer = _find_manufacturer(db, item.manufacturer)
    model = _find_existing_model(db, item, manufacturer.id if manufacturer else None)
    return NetBoxDtlItemPreviewRead(
        item_id=item.id,
        manufacturer=item.manufacturer,
        model=item.model,
        slug=item.slug,
        action="update_device_model" if model is not None else "create_device_model",
        manufacturer_action="reuse_manufacturer" if manufacturer is not None else "create_manufacturer",
        existing_device_model_id=model.id if model else None,
        front_image=item.front_image_relpath is not None,
        rear_image=item.rear_image_relpath is not None,
        component_counts={k: int(v) for k, v in (item.component_counts_json or {}).items()},
    )


def _store_and_extract_zip(settings: Settings, data: bytes, filename: str, sha256: str) -> tuple[Path, Path]:
    root = settings.netbox_dtl_root_path
    archive_root = root / "archives"
    extract_root = root / "extracted"
    archive_root.mkdir(parents=True, exist_ok=True)
    extract_root.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", Path(filename).name)[:180] or "netbox-dtl.zip"
    archive_path = archive_root / f"{sha256}-{safe_name}"
    archive_path.write_bytes(data)
    extract_path = extract_root / sha256
    if extract_path.exists():
        shutil.rmtree(extract_path)
    extract_path.mkdir(parents=True)
    try:
        _extract_zip_safely(data, extract_path, settings)
    except Exception:
        shutil.rmtree(extract_path, ignore_errors=True)
        raise
    return archive_path, extract_path


def _extract_zip_safely(data: bytes, target: Path, settings: Settings) -> None:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if len(infos) > settings.netbox_dtl_max_files:
            raise HTTPException(status_code=400, detail="ZIP inneholder for mange filer")
        total = sum(max(i.file_size, 0) for i in infos)
        if total > settings.netbox_dtl_max_extracted_bytes:
            raise HTTPException(status_code=413, detail="ZIP blir for stor utpakket")
        for info in infos:
            rel = _safe_zip_member(info.filename)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, dest.open("wb") as out:
                shutil.copyfileobj(src, out)


def _safe_zip_member(filename: str) -> Path:
    pure = PurePosixPath(filename.replace("\\", "/"))
    if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise HTTPException(status_code=400, detail="ZIP inneholder ugyldig filsti")
    return Path(*pure.parts)


def _index_items(settings: Settings, import_run: NetBoxDeviceTypeLibraryImport, extract_path: Path) -> list[NetBoxDeviceTypeLibraryItem]:
    items: list[NetBoxDeviceTypeLibraryItem] = []
    image_index = _image_index(extract_path)
    for yaml_path in sorted(extract_path.rglob("*.yaml")):
        parts = yaml_path.relative_to(extract_path).parts
        if "device-types" not in parts:
            continue
        try:
            raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise HTTPException(status_code=400, detail=f"Kunne ikke lese YAML {yaml_path.name}: {exc}") from exc
        if not isinstance(raw, dict):
            continue
        manufacturer = str(raw.get("manufacturer") or _manufacturer_from_path(parts)).strip()
        model = str(raw.get("model") or yaml_path.stem).strip()
        slug = str(raw.get("slug") or _slugify(model)).strip()
        if not manufacturer or not model or not slug:
            continue
        counts = {key: len(raw.get(key) or []) for key in COMPONENT_KEYS if isinstance(raw.get(key), list)}
        front = _find_image(image_index, manufacturer, slug, "front")
        rear = _find_image(image_index, manufacturer, slug, "rear")
        items.append(
            NetBoxDeviceTypeLibraryItem(
                import_id=import_run.id,
                manufacturer=manufacturer,
                model=model,
                slug=slug,
                part_number=str(raw["part_number"]).strip() if raw.get("part_number") else None,
                u_height=float(raw["u_height"]) if raw.get("u_height") is not None else None,
                is_full_depth=bool(raw["is_full_depth"]) if raw.get("is_full_depth") is not None else None,
                airflow=str(raw["airflow"]).strip() if raw.get("airflow") else None,
                front_image_relpath=_rel(settings.netbox_dtl_root_path, front) if front else None,
                rear_image_relpath=_rel(settings.netbox_dtl_root_path, rear) if rear else None,
                yaml_relpath=_rel(settings.netbox_dtl_root_path, yaml_path),
                component_counts_json=counts,
                raw_json=raw,
            )
        )
    return items


def _image_index(extract_path: Path) -> list[Path]:
    images: list[Path] = []
    for path in extract_path.rglob("*"):
        if path.is_file() and "elevation-images" in path.relative_to(extract_path).parts and path.suffix.lower() in IMAGE_MIME_BY_EXT:
            images.append(path)
    return images


def _find_image(images: list[Path], manufacturer: str, slug: str, side: str) -> Path | None:
    mfr = _norm(manufacturer)
    sl = _norm(slug)
    side = side.lower()
    for path in images:
        rel = _norm("/".join(path.parts))
        stem = _norm(path.stem)
        if mfr in rel and sl in stem and side in stem:
            return path
    return None


def _manufacturer_from_path(parts: tuple[str, ...]) -> str:
    idx = parts.index("device-types")
    return parts[idx + 1] if idx + 1 < len(parts) else ""


def _find_manufacturer(db: Session, name: str) -> Manufacturer | None:
    return db.scalar(select(Manufacturer).where(func.lower(Manufacturer.name) == name.strip().lower()))


def _ensure_manufacturer(db: Session, name: str) -> Manufacturer:
    row = _find_manufacturer(db, name)
    if row is not None:
        return row
    row = Manufacturer(name=name.strip())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _find_existing_model(db: Session, item: NetBoxDeviceTypeLibraryItem, manufacturer_id: int | None) -> DeviceModel | None:
    identity_value = _identity_value(item)
    identity = db.scalar(
        select(DeviceModelIdentity).where(
            DeviceModelIdentity.identity_type == "vendor_api",
            DeviceModelIdentity.namespace == "netbox_dtl",
            DeviceModelIdentity.normalized_value == identity_value.lower(),
        )
    )
    if identity is not None:
        return db.get(DeviceModel, identity.device_model_id)
    if manufacturer_id is None:
        return None
    return db.scalar(
        select(DeviceModel).where(
            DeviceModel.manufacturer_id == manufacturer_id,
            func.lower(DeviceModel.name) == item.model.strip().lower(),
        )
    )


def _ensure_device_model_identity(db: Session, device_model_id: int, item: NetBoxDeviceTypeLibraryItem) -> int:
    value = _identity_value(item)
    existing = db.scalar(
        select(DeviceModelIdentity).where(
            DeviceModelIdentity.identity_type == "vendor_api",
            DeviceModelIdentity.namespace == "netbox_dtl",
            DeviceModelIdentity.normalized_value == value.lower(),
        )
    )
    if existing is not None:
        return 0
    row = DeviceModelIdentity(
        device_model_id=device_model_id,
        identity_type="vendor_api",
        namespace="netbox_dtl",
        value=value,
        normalized_value=value.lower(),
        source="netbox_dtl",
        confidence=95,
        raw_json={"import_id": item.import_id, "item_id": item.id},
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return 0
    return 1


def _import_images(db: Session, settings: Settings, model: DeviceModel, item: NetBoxDeviceTypeLibraryItem) -> int:
    imported = 0
    for slot, relpath in (("front", item.front_image_relpath), ("back", item.rear_image_relpath)):
        if not relpath:
            continue
        path = settings.netbox_dtl_root_path / relpath
        mime = IMAGE_MIME_BY_EXT.get(path.suffix.lower())
        if mime is None or not path.is_file():
            continue
        dcim_svc.set_device_model_image(db, model, slot, path.read_bytes(), mime)
        imported += 1
    return imported


def _sync_templates(db: Session, device_model_id: int, item: NetBoxDeviceTypeLibraryItem) -> int:
    db.query(DeviceModelTemplate).filter(
        DeviceModelTemplate.device_model_id == device_model_id,
        DeviceModelTemplate.source == "netbox_dtl",
    ).delete(synchronize_session=False)
    raw = item.raw_json or {}
    created = 0
    for component_type in COMPONENT_KEYS:
        rows = raw.get(component_type) or []
        if not isinstance(rows, list):
            continue
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or row.get("label") or f"{component_type}-{idx + 1}").strip()
            db.add(
                DeviceModelTemplate(
                    device_model_id=device_model_id,
                    source="netbox_dtl",
                    component_type=component_type,
                    name=name,
                    label=str(row["label"]).strip() if row.get("label") else None,
                    sort_order=idx,
                    raw_json=row,
                )
            )
            created += 1
    db.commit()
    return created


def _freehci_u_height(value: float | None) -> int:
    if value is None:
        return 1
    return max(0, int(math.ceil(float(value))))


def _form_factor(item: NetBoxDeviceTypeLibraryItem) -> str | None:
    if item.u_height == 0:
        return "child"
    if item.is_full_depth is False:
        return "half-depth"
    return "rackmount"


def _identity_value(item: NetBoxDeviceTypeLibraryItem) -> str:
    return f"{item.manufacturer.strip()}/{item.slug.strip()}"


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "-", value.strip().lower()).strip("-")


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()
