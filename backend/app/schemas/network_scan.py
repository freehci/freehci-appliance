"""Skjemaer for nettverksskann (maler, jobber, oppdagelseskø)."""

from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

NameSource = Literal["snmp_sysname", "ptr", "ip", "custom"]
ParentFilter = Literal["alive", "snmp_ok"]
InventoryMode = Literal["none", "discovered_queue", "auto"]
TemplateKind = Literal["ping", "snmp_quick", "tcp_ports"]


class NetworkScanTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    kind: str
    is_builtin: bool
    default_config: dict | None = None


class NetworkScanTemplateCreate(BaseModel):
    """Egendefinert mal (typisk tcp_ports med portliste)."""

    slug: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(..., min_length=1, max_length=255)
    kind: TemplateKind
    default_config: dict | None = None


class NetworkScanPrefixBindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int
    ipv4_prefix_id: int
    enabled: bool


class NetworkScanPrefixBindingCreate(BaseModel):
    template_id: int = Field(..., ge=1)
    ipv4_prefix_id: int = Field(..., ge=1)
    enabled: bool = True


class NetworkScanJobOptions(BaseModel):
    """Valg per jobb (lagres i options_json)."""

    parent_job_id: int | None = None
    parent_filter: ParentFilter | None = None
    inventory_mode: InventoryMode = "none"
    name_priority: list[NameSource] = Field(
        default_factory=lambda: ["snmp_sysname", "ptr", "ip"],
    )
    default_device_model_id: int | None = None
    snmp_community: str | None = Field(None, max_length=256)
    snmp_port: int | None = Field(None, ge=1, le=65535)

    @field_validator("name_priority")
    @classmethod
    def no_custom_in_priority(cls, v: list[NameSource]) -> list[NameSource]:
        if any(x == "custom" for x in v):
            raise ValueError("name_priority kan ikke inneholde custom (brukes kun ved manuell godkjenning)")
        seen: set[str] = set()
        out: list[NameSource] = []
        for x in v:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out


class NetworkScanJobCreate(BaseModel):
    template_id: int = Field(..., ge=1)
    ipv4_prefix_id: int = Field(..., ge=1)
    options: NetworkScanJobOptions = Field(default_factory=NetworkScanJobOptions)


class NetworkScanHostResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    address: str
    result_json: dict


class NetworkScanJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int
    ipv4_prefix_id: int
    site_id: int
    cidr: str
    parent_job_id: int | None
    status: str
    options_json: dict | None
    error_message: str | None
    hosts_scanned: int
    hosts_matched: int
    started_at: dt.datetime
    completed_at: dt.datetime | None


class NetworkScanJobDetailRead(NetworkScanJobRead):
    host_results: list[NetworkScanHostResultRead] = Field(default_factory=list)


class NetworkScanDiscoveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    site_id: int
    address: str
    name_candidates_json: dict
    chosen_name_source: str | None
    chosen_name: str | None
    status: str
    dcim_device_id: int | None
    created_at: dt.datetime


class NetworkScanDiscoveryApprove(BaseModel):
    chosen_name_source: NameSource
    chosen_name: str | None = Field(None, max_length=255)
    device_model_id: int = Field(..., ge=1)

    @model_validator(mode="after")
    def custom_needs_name(self) -> NetworkScanDiscoveryApprove:
        if self.chosen_name_source == "custom":
            if self.chosen_name is None or not self.chosen_name.strip():
                raise ValueError("chosen_name er påkrevd når chosen_name_source er custom")
            self.chosen_name = self.chosen_name.strip()
        return self
