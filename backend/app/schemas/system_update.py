"""Systemoppgaver: oppdatering av installasjon (host-service)."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, Field


class UpdateStartResponse(BaseModel):
    job_id: str = Field(..., description="Unik id for oppgraderingsjobb")


class UpdateStatusResponse(BaseModel):
    running: bool
    job_id: str | None = None
    started_at: dt.datetime | None = None
    finished_at: dt.datetime | None = None
    exit_code: int | None = None
    detail: str | None = None
    log_tail: list[str] = Field(default_factory=list)


class UpdateCheckResponse(BaseModel):
    local_version: str
    remote_version: str | None = None
    update_available: bool = False
    remote_error: str | None = None


class SystemStatusResponse(BaseModel):
    update_check: UpdateCheckResponse
    updater_available: bool = False
    updater_error: str | None = None
    updater_status: UpdateStatusResponse | None = None

