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


class SnmpInventoryRequest(BaseModel):
    """SNMPv2c-poll av IF-MIB / ifXTable (ingen MIB-kompilering nødvendig)."""

    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(161, ge=1, le=65535)
    community: str = Field("public", min_length=1, max_length=256)
    max_varbinds: int = Field(4000, ge=200, le=50_000)
    timeout_sec: float = Field(3.0, ge=0.5, le=30.0)
    retries: int = Field(1, ge=0, le=5)


class SnmpInterfaceRow(BaseModel):
    if_index: int
    name: str = Field(..., max_length=128)
    description: str | None = None
    if_descr: str | None = None
    if_alias: str | None = None
    if_type: int | None = None
    if_type_label: str | None = None
    mtu: int | None = None
    speed_mbps: int | None = None
    mac_address: str | None = None
    admin_status: str
    oper_status: str
    enabled: bool


class SnmpInventoryRead(BaseModel):
    ok: bool
    error: str | None = None
    host: str
    sys_name: str | None = None
    sys_descr: str | None = None
    interfaces: list[SnmpInterfaceRow] = Field(default_factory=list)
    truncated: bool = False
    varbinds_collected: int | None = None


class SnmpInventoryApplyRequest(SnmpInventoryRequest):
    device_id: int = Field(..., ge=1)


class SnmpInventoryApplyRead(BaseModel):
    ok: bool
    error: str | None = None
    device_id: int
    host: str | None = None
    created: int = 0
    updated: int = 0
    skipped: int = 0
    poll: SnmpInventoryRead | None = None
