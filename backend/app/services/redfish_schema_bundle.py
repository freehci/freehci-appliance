"""Import and use Redfish DSP8010 schema bundles."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree

import httpx
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.dcim import RedfishSchemaBundle, RedfishSchemaResource
from app.schemas.dcim import (
    ExternalInventoryImportApplyRequest,
    ExternalInventoryImportPreviewRequest,
    RedfishInventoryApplyRead,
    RedfishInventoryImportRequest,
    RedfishInventoryPreviewRead,
    RedfishInventoryResourcePreviewRead,
    RedfishSchemaValidationRead,
)
from app.services import dcim as dcim_svc

_ODATA_TYPE_RE = re.compile(r"#(?P<resource>[A-Za-z][A-Za-z0-9]+)(?:\.v(?P<version>[0-9_]+))?(?:\.(?P<name>[A-Za-z][A-Za-z0-9]+))?")
_SCHEMA_FILE_RE = re.compile(r"(?P<resource>[A-Za-z][A-Za-z0-9]+)(?:[._-]v(?P<version>[0-9_]+))?", re.IGNORECASE)
_COMPONENT_RESOURCE_TYPES = {
    "Drive",
    "Memory",
    "NetworkAdapter",
    "NetworkDeviceFunction",
    "NetworkPort",
    "PowerSupply",
    "Processor",
}
_DEVICE_SCOPE_RESOURCE_TYPES = {"ComputerSystem", "Chassis", "Manager", "EthernetInterface"}


@dataclass(frozen=True)
class _StoredZip:
    sha256: str
    filename: str
    archive_path: Path
    extract_path: Path


def list_schema_bundles(db: Session) -> list[RedfishSchemaBundle]:
    stmt = select(RedfishSchemaBundle).order_by(RedfishSchemaBundle.created_at.desc(), RedfishSchemaBundle.id.desc())
    return list(db.scalars(stmt))


def list_schema_resources(db: Session, bundle_id: int) -> list[RedfishSchemaResource]:
    bundle = db.get(RedfishSchemaBundle, bundle_id)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Redfish schema bundle ikke funnet")
    stmt = (
        select(RedfishSchemaResource)
        .where(RedfishSchemaResource.bundle_id == bundle_id)
        .order_by(RedfishSchemaResource.resource_type, RedfishSchemaResource.schema_version, RedfishSchemaResource.format)
    )
    return list(db.scalars(stmt))


async def import_schema_bundle_upload(
    db: Session,
    settings: Settings,
    upload: UploadFile,
) -> RedfishSchemaBundle:
    filename = Path(upload.filename or "redfish-schema-bundle.zip").name
    data = await upload.read(settings.redfish_schema_max_zip_bytes + 1)
    if len(data) > settings.redfish_schema_max_zip_bytes:
        raise HTTPException(status_code=413, detail="Redfish schema ZIP er for stor")
    return import_schema_bundle_bytes(db, settings, data, filename=filename, source="upload")


async def import_schema_bundle_download(
    db: Session,
    settings: Settings,
    url: str,
    name: str | None = None,
) -> RedfishSchemaBundle:
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=400, detail=f"Kunne ikke laste ned Redfish schema ZIP: {exc}") from exc
    data = response.content
    if len(data) > settings.redfish_schema_max_zip_bytes:
        raise HTTPException(status_code=413, detail="Redfish schema ZIP er for stor")
    filename = Path(name or url.rstrip("/").rsplit("/", 1)[-1] or "redfish-schema-bundle.zip").name
    return import_schema_bundle_bytes(db, settings, data, filename=filename, source="download", source_url=url)


def import_schema_bundle_bytes(
    db: Session,
    settings: Settings,
    data: bytes,
    *,
    filename: str,
    source: str,
    source_url: str | None = None,
) -> RedfishSchemaBundle:
    if not zipfile.is_zipfile(_BytesPath(data)):
        raise HTTPException(status_code=400, detail="Filen er ikke en gyldig ZIP")
    stored = _store_and_extract_zip(settings, data, filename)
    existing = db.scalar(select(RedfishSchemaBundle).where(RedfishSchemaBundle.sha256 == stored.sha256))
    if existing is not None:
        return existing

    bundle = RedfishSchemaBundle(
        name=_bundle_name(filename, stored.sha256),
        version=_version_from_name(filename),
        source=source,
        source_url=source_url,
        file_relpath=_rel_to_root(settings.redfish_schema_root_path, stored.archive_path),
        extract_relpath=_rel_to_root(settings.redfish_schema_root_path, stored.extract_path),
        sha256=stored.sha256,
        status="ready",
        metadata_json={"filename": filename},
    )
    db.add(bundle)
    db.flush()

    resources = _index_extracted_schemas(settings, bundle, stored.extract_path)
    bundle.schema_count = len(resources)
    bundle.json_schema_count = sum(1 for r in resources if r.format == "json_schema")
    bundle.csdl_count = sum(1 for r in resources if r.format == "csdl")
    bundle.openapi_count = sum(1 for r in resources if r.format == "openapi")
    bundle.dictionaries_count = sum(1 for r in resources if r.format == "dictionary")
    db.add_all(resources)
    db.commit()
    db.refresh(bundle)
    return bundle


def preview_redfish_inventory(
    db: Session,
    settings: Settings,
    data: RedfishInventoryImportRequest,
    *,
    apply: bool = False,
) -> RedfishInventoryPreviewRead | RedfishInventoryApplyRead:
    resources = _collect_redfish_resources(data.payload)
    if not resources:
        resources = [("$", data.payload)]
    previews: list[RedfishInventoryResourcePreviewRead] = []
    applied_count = 0
    for path, payload in resources:
        odata_type = str(payload.get("@odata.type") or "") if isinstance(payload, dict) else ""
        resource_type, _version = _resource_type_from_odata(odata_type)
        if not resource_type:
            resource_type = _resource_type_from_payload(payload)
        validation = _validate_resource_against_schema(db, settings, data.bundle_id, resource_type, odata_type, payload)
        notes: list[str] = []
        component_preview = None
        apply_result = None
        supported = False
        proposed_action = "not_supported_yet"
        if resource_type in _COMPONENT_RESOURCE_TYPES:
            supported = True
            try:
                component_preview = dcim_svc.preview_external_inventory_import(
                    db,
                    ExternalInventoryImportPreviewRequest(source="redfish", resource_type=resource_type, payload=payload),
                )
                proposed_action = component_preview.proposed_action
                if apply and data.apply_components:
                    apply_result = dcim_svc.apply_external_inventory_import(
                        db,
                        ExternalInventoryImportApplyRequest(source="redfish", resource_type=resource_type, payload=payload),
                    )
                    applied_count += 1
                    proposed_action = apply_result.action
            except HTTPException as exc:
                supported = False
                notes.append(str(exc.detail))
        elif resource_type in _DEVICE_SCOPE_RESOURCE_TYPES:
            notes.append(f"{resource_type} valideres mot schema, men apply er ikke aktivert for denne DCIM-overflaten ennå.")
        else:
            notes.append("Ingen Redfish-mapping er registrert for denne resource-typen ennå.")
        previews.append(
            RedfishInventoryResourcePreviewRead(
                resource_type=resource_type or "Unknown",
                odata_type=odata_type or None,
                path=path,
                name=_resource_name(payload),
                supported=supported,
                proposed_action=proposed_action,
                validation=validation,
                component_preview=component_preview,
                apply_result=apply_result,
                notes=notes,
            )
        )
    if apply:
        return RedfishInventoryApplyRead(bundle_id=data.bundle_id, resources=previews, applied_count=applied_count)
    return RedfishInventoryPreviewRead(bundle_id=data.bundle_id, resources=previews)


def _store_and_extract_zip(settings: Settings, data: bytes, filename: str) -> _StoredZip:
    root = settings.redfish_schema_root_path
    archive_root = root / "archives"
    extract_root = root / "extracted"
    archive_root.mkdir(parents=True, exist_ok=True)
    extract_root.mkdir(parents=True, exist_ok=True)
    sha256 = hashlib.sha256(data).hexdigest()
    safe_name = _safe_filename(filename)
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
    return _StoredZip(sha256=sha256, filename=safe_name, archive_path=archive_path, extract_path=extract_path)


def _extract_zip_safely(data: bytes, target: Path, settings: Settings) -> None:
    with zipfile.ZipFile(_BytesPath(data)) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if len(infos) > settings.redfish_schema_max_files:
            raise HTTPException(status_code=400, detail="ZIP inneholder for mange filer")
        total = sum(max(i.file_size, 0) for i in infos)
        if total > settings.redfish_schema_max_extracted_bytes:
            raise HTTPException(status_code=413, detail="ZIP blir for stor utpakket")
        for info in infos:
            rel = _safe_zip_member(info.filename)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, dest.open("wb") as out:
                shutil.copyfileobj(src, out)


def _index_extracted_schemas(settings: Settings, bundle: RedfishSchemaBundle, extract_path: Path) -> list[RedfishSchemaResource]:
    resources: list[RedfishSchemaResource] = []
    seen: set[tuple[str, str]] = set()
    for path in extract_path.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(extract_path).as_posix()
        fmt = _schema_format(rel)
        if fmt is None:
            continue
        meta = _schema_metadata(path, fmt)
        resource_type = str(meta.get("resource_type") or _resource_type_from_filename(path.name))
        if not resource_type:
            continue
        schema_uri = str(meta.get("schema_uri") or rel)
        key = (fmt, schema_uri)
        if key in seen:
            continue
        seen.add(key)
        resources.append(
            RedfishSchemaResource(
                bundle_id=bundle.id,
                resource_type=resource_type,
                schema_version=meta.get("schema_version"),
                schema_uri=schema_uri,
                format=fmt,
                file_relpath=_rel_to_root(settings.redfish_schema_root_path, path),
                title=meta.get("title"),
                description=meta.get("description"),
                metadata_json={k: v for k, v in meta.items() if k not in {"schema_uri", "resource_type", "schema_version", "title", "description"}},
            )
        )
    return resources


def _validate_resource_against_schema(
    db: Session,
    settings: Settings,
    bundle_id: int | None,
    resource_type: str,
    odata_type: str,
    payload: dict[str, Any],
) -> RedfishSchemaValidationRead:
    schema = _lookup_schema(db, bundle_id, resource_type)
    warnings: list[str] = []
    errors: list[str] = []
    if schema is None:
        warnings.append("Schema ikke funnet i importert bundle.")
        return RedfishSchemaValidationRead(resource_type=resource_type or "Unknown", odata_type=odata_type or None, schema_known=False, warnings=warnings)
    schema_doc = _load_json_schema(settings, schema)
    required = schema_doc.get("required") if isinstance(schema_doc, dict) else None
    if isinstance(required, list):
        for key in required:
            if isinstance(key, str) and key not in payload:
                errors.append(f"Mangler påkrevd felt: {key}")
    return RedfishSchemaValidationRead(
        resource_type=resource_type or schema.resource_type,
        odata_type=odata_type or None,
        schema_resource_id=schema.id,
        schema_known=True,
        valid=not errors,
        errors=errors,
        warnings=warnings,
    )


def _lookup_schema(db: Session, bundle_id: int | None, resource_type: str) -> RedfishSchemaResource | None:
    if not resource_type:
        return None
    stmt = select(RedfishSchemaResource).where(
        RedfishSchemaResource.resource_type == resource_type,
        RedfishSchemaResource.format == "json_schema",
    )
    if bundle_id is not None:
        stmt = stmt.where(RedfishSchemaResource.bundle_id == bundle_id)
    stmt = stmt.order_by(RedfishSchemaResource.schema_version.desc().nullslast(), RedfishSchemaResource.id.desc())
    return db.scalars(stmt).first()


def _load_json_schema(settings: Settings, resource: RedfishSchemaResource) -> dict[str, Any]:
    path = settings.redfish_schema_root_path / resource.file_relpath
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _collect_redfish_resources(value: Any, path: str = "$") -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, dict):
        if "@odata.type" in value:
            out.append((path, value))
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                out.extend(_collect_redfish_resources(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            out.extend(_collect_redfish_resources(child, f"{path}[{idx}]"))
    return out


def _schema_format(rel: str) -> str | None:
    lower = rel.replace("\\", "/").lower()
    if "/json-schema/" in f"/{lower}" and lower.endswith(".json"):
        return "json_schema"
    if "/csdl/" in f"/{lower}" and lower.endswith((".xml", ".csdl")):
        return "csdl"
    if "/openapi/" in f"/{lower}" and lower.endswith((".json", ".yaml", ".yml")):
        return "openapi"
    if "/dictionaries/" in f"/{lower}" and lower.endswith((".json", ".xml")):
        return "dictionary"
    return None


def _schema_metadata(path: Path, fmt: str) -> dict[str, Any]:
    if fmt == "json_schema":
        return _json_schema_metadata(path)
    if fmt == "csdl":
        return _csdl_metadata(path)
    return {"resource_type": _resource_type_from_filename(path.name), "schema_uri": path.name}


def _json_schema_metadata(path: Path) -> dict[str, Any]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        doc = {}
    if not isinstance(doc, dict):
        doc = {}
    uri = str(doc.get("$id") or doc.get("id") or path.name)
    title = doc.get("title")
    description = doc.get("description")
    resource_type = _resource_type_from_filename(path.name)
    if isinstance(title, str) and "." not in title:
        resource_type = title
    return {
        "schema_uri": uri,
        "resource_type": resource_type,
        "schema_version": _version_from_name(path.name),
        "title": title if isinstance(title, str) else None,
        "description": description if isinstance(description, str) else None,
        "property_count": len(doc.get("properties", {})) if isinstance(doc.get("properties"), dict) else 0,
    }


def _csdl_metadata(path: Path) -> dict[str, Any]:
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError):
        return {"resource_type": _resource_type_from_filename(path.name), "schema_uri": path.name}
    schema = next((el for el in root.iter() if el.tag.endswith("Schema")), None)
    namespace = schema.attrib.get("Namespace") if schema is not None else None
    resource_type = str(namespace).split(".", 1)[0] if namespace else _resource_type_from_filename(path.name)
    return {
        "schema_uri": namespace or path.name,
        "resource_type": resource_type,
        "schema_version": _version_from_name(str(namespace or path.name)),
        "namespace": namespace,
    }


def _resource_type_from_odata(odata_type: str) -> tuple[str, str | None]:
    match = _ODATA_TYPE_RE.search(odata_type or "")
    if not match:
        return "", None
    name = match.group("name") or match.group("resource") or ""
    return name, match.group("version")


def _resource_type_from_payload(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "Unknown"
    type_value = payload.get("ResourceType") or payload.get("resource_type")
    return str(type_value) if type_value else "Unknown"


def _resource_type_from_filename(name: str) -> str:
    stem = Path(name).stem
    match = _SCHEMA_FILE_RE.match(stem)
    if not match:
        return stem
    return match.group("resource")


def _version_from_name(name: str) -> str | None:
    match = re.search(r"v([0-9]+(?:[_\.][0-9]+){1,3})", name, re.IGNORECASE)
    return match.group(1).replace("_", ".") if match else None


def _bundle_name(filename: str, sha256: str) -> str:
    stem = Path(filename).stem.strip()
    return stem[:255] if stem else f"Redfish schema bundle {sha256[:12]}"


def _resource_name(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get("Name") or payload.get("Id") or payload.get("Model")
    return str(value) if value is not None else None


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip() or "redfish-schema-bundle.zip"
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", name)[:180]


def _safe_zip_member(filename: str) -> Path:
    pure = PurePosixPath(filename.replace("\\", "/"))
    if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise HTTPException(status_code=400, detail="ZIP inneholder ugyldig filsti")
    return Path(*pure.parts)


def _rel_to_root(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


class _BytesPath:
    """Tiny file-like wrapper for zipfile/is_zipfile without persisting first."""

    def __init__(self, data: bytes) -> None:
        import io

        self._bio = io.BytesIO(data)

    def read(self, *args: Any) -> bytes:
        return self._bio.read(*args)

    def seek(self, *args: Any) -> int:
        return self._bio.seek(*args)

    def tell(self) -> int:
        return self._bio.tell()

    def seekable(self) -> bool:
        return True
