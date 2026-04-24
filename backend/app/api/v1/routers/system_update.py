"""System: host-basert oppdatering (Update now).

Dette endepunktet kaller en liten updater-service som kjører på hosten (utenfor Docker).
"""

from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_deps import get_current_admin
from app.api.deps import get_db
from app.models.admin_account import AdminAccount
from app.schemas.system_update import UpdateStartResponse, UpdateStatusResponse

router = APIRouter(prefix="/system", tags=["system"])

UPDATER_URL = os.environ.get("UPDATER_URL", "http://127.0.0.1:8765").rstrip("/")


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

