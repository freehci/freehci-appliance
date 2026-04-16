"""Administrer dynamiske backend-plugins (opplasting / git)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.config import Settings, get_settings
from app.schemas.plugin_install import (
    GitInstallRequest,
    GitRefsResponse,
    GitScanRequest,
    GitScanResponse,
    InstalledPluginListResponse,
    InstalledPluginRow,
    PluginInstallResult,
)
from app.services import plugin_install_service as pis

router = APIRouter(prefix="/plugin-install", tags=["plugin-install"])


@router.get("/installed", response_model=InstalledPluginListResponse)
def list_installed(settings: Settings = Depends(get_settings)) -> InstalledPluginListResponse:
    rows = [
        InstalledPluginRow(
            slug=str(r["slug"]),
            path=str(r["path"]),
            has_plugin_py=bool(r["has_plugin_py"]),
        )
        for r in pis.list_installed(settings)
    ]
    return InstalledPluginListResponse(items=rows)


@router.post("/upload", response_model=PluginInstallResult)
async def upload_plugin(
    slug: str = Form(...),
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> PluginInstallResult:
    if not file.filename or not str(file.filename).lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Kun .zip-filer støttes")
    raw = await file.read()
    r = pis.install_from_zip_bytes(settings, slug=slug, zip_bytes=raw)
    return PluginInstallResult(**r)


@router.post("/git/refs", response_model=GitRefsResponse)
def git_refs(body: GitScanRequest, settings: Settings = Depends(get_settings)) -> GitRefsResponse:
    _ = settings
    refs = pis.git_ls_remote_refs(body.git_url.strip())
    return GitRefsResponse(refs=refs)


@router.post("/git/scan", response_model=GitScanResponse)
def git_scan(body: GitScanRequest, settings: Settings = Depends(get_settings)) -> GitScanResponse:
    _ = settings
    data = pis.scan_git_for_plugins(body.git_url.strip(), body.ref.strip() or "main")
    return GitScanResponse(
        ref_used=str(data["ref_used"]),
        plugin_py_relative_paths=list(data["plugin_py_relative_paths"]),
    )


@router.post("/git/install", response_model=PluginInstallResult)
def git_install(body: GitInstallRequest, settings: Settings = Depends(get_settings)) -> PluginInstallResult:
    r = pis.install_from_git(
        settings,
        git_url=body.git_url.strip(),
        ref=body.ref.strip() or "main",
        slug=body.slug.strip(),
        plugin_subpath=body.plugin_subpath,
    )
    return PluginInstallResult(**r)
