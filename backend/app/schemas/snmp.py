"""Skjemaer for SNMP (MIB-lager og enkel probe)."""

from __future__ import annotations

import datetime as dt

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SnmpMibFileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    size_bytes: int
    modified_at: dt.datetime


class SnmpProbeRequest(BaseModel):
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(161, ge=1, le=65535)
    community: str = Field("public", min_length=1, max_length=256)
    oid: str = Field(..., min_length=1, max_length=512, description="Numerisk OID anbefales, f.eks. 1.3.6.1.2.1.1.1.0")
    operation: Literal["get", "walk"] = "get"
    max_oids: int = Field(200, ge=1, le=2000)
    timeout_sec: float = Field(3.0, ge=0.5, le=30.0)
    retries: int = Field(1, ge=0, le=5)


class SnmpVarBindRead(BaseModel):
    oid: str
    value: str


class SnmpProbeRead(BaseModel):
    ok: bool
    error: str | None = None
    varbinds: list[SnmpVarBindRead] = Field(default_factory=list)
