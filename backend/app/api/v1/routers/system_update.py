"""System: host-basert oppdatering (Update now).

Dette endepunktet kaller en liten updater-service som kjører på hosten (utenfor Docker).
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_deps import get_current_admin
from app.api.deps import get_db
from app.models.admin_account import AdminAccount
from app.schemas.system_update import UpdateCheckResponse, UpdateStartResponse, UpdateStatusResponse
from app.services.appliance_version import (
    DEFAULT_REMOTE_VER_URL,
    fetch_remote_version,
    read_local_appliance_version,
    remote_is_newer,
)

router = APIRouter(prefix="/system", tags=["system"])

UPDATER_URL = os.environ.get("UPDATER_URL", "http://127.0.0.1:8765").rstrip("/")
VER_FILE = Path(os.environ.get("FREEHCI_VER_FILE", "/app/.ver"))
REMOTE_VER_URL = os.environ.get("FREEHCI_REMOTE_VER_URL", DEFAULT_REMOTE_VER_URL).strip()


def _http_client() -> httpx.Client:
    return httpx.Client(timeout=httpx.Timeout(connect=2.0, read=20.0, write=20.0, pool=2.0))


@router.post("/update-now", response_model=UpdateStartResponse)
def update_now(
    _: AdminAccount = Depends(get_current_admin),
    __: Session = Depends(get_db),  # holder mønster med db-dependency for auth middleware
) -> UpdateStartResponse:
    try:
        with _http_client() as c:
            r = c.post(f"{UPDATER_URL}/update")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="updater-service utilgjengelig") from None
    if r.status_code == 409:
        raise HTTPException(status_code=409, detail="oppdatering kjører allerede") from None
    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"updater-service feilet ({r.status_code})") from None
    try:
        j = r.json()
        job_id = str(j.get("job_id") or "")
    except Exception:
        job_id = ""
    if not job_id:
        raise HTTPException(status_code=502, detail="updater-service ga ugyldig svar") from None
    return UpdateStartResponse(job_id=job_id)


@router.get("/update-status", response_model=UpdateStatusResponse)
def update_status(
    _: AdminAccount = Depends(get_current_admin),
    __: Session = Depends(get_db),
) -> UpdateStatusResponse:
    try:
        with _http_client() as c:
            r = c.get(f"{UPDATER_URL}/status")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="updater-service utilgjengelig") from None
    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"updater-service feilet ({r.status_code})") from None
    try:
        return UpdateStatusResponse.model_validate(r.json())
    except Exception:
        raise HTTPException(status_code=502, detail="updater-service ga ugyldig status") from None


@router.get("/update-check", response_model=UpdateCheckResponse)
def update_check(
    _: AdminAccount = Depends(get_current_admin),
    __: Session = Depends(get_db),
) -> UpdateCheckResponse:
    local_raw = read_local_appliance_version(VER_FILE)
    local = local_raw or "ukjent"
    remote, err = fetch_remote_version(REMOTE_VER_URL)
    if remote is None:
        return UpdateCheckResponse(
            local_version=local,
            remote_version=None,
            update_available=False,
            remote_error=err or "ukjent feil",
        )
    if local_raw is None:
        return UpdateCheckResponse(
            local_version=local,
            remote_version=remote,
            update_available=False,
            remote_error="mangler lokal versjonsfil (/app/.ver)",
        )
    return UpdateCheckResponse(
        local_version=local_raw,
        remote_version=remote,
        update_available=remote_is_newer(remote, local_raw),
        remote_error=None,
    )

