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


class SnmpMibManufacturerBrief(BaseModel):
    id: int
    name: str


class SnmpMibDetailRead(BaseModel):
    name: str
    size_bytes: int
    modified_at: dt.datetime
    module_name: str | None = None
    enterprise_number: int | None = None
    iana_organization: str | None = None
    compile_status: str
    compile_message: str | None = None
    compiled_module_name: str | None = None
    compiled_at: dt.datetime | None = None
    linked_manufacturer: SnmpMibManufacturerBrief | None = None
    effective_enterprise_number: int | None = None
    extends_mib_module: str | None = None
    parent_mib_missing: bool = False
    missing_import_modules: list[str] = Field(default_factory=list)


class SnmpMibTreeNodeRead(BaseModel):
    filename: str
    module_name: str | None = None
    compile_status: str | None = None
    extension_parent_module: str | None = None
    parent_mib_missing: bool = False
    children: list["SnmpMibTreeNodeRead"] = Field(default_factory=list)


class SnmpEnterpriseGroupRead(BaseModel):
    enterprise_number: int | None
    iana_organization: str | None = None
    mib_files: list[str] = Field(default_factory=list)
    mib_tree: list[SnmpMibTreeNodeRead] = Field(default_factory=list)
    linked_manufacturer: SnmpMibManufacturerBrief | None = None


class SnmpEnterpriseAutocreateRequest(BaseModel):
    """enterprise_number=None: opprett for alle PEN med MIB og IANA-navn der det mangler DCIM-produsent."""

    enterprise_number: int | None = Field(None, ge=0, le=2147483647)


class SnmpAutocreateItemRead(BaseModel):
    enterprise_number: int
    manufacturer_id: int
    name: str


class SnmpEnterpriseAutocreateResultRead(BaseModel):
    created: list[SnmpAutocreateItemRead] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)


class SnmpIanaSyncRead(BaseModel):
    rows_imported: int


class SnmpMibCompileAllQueuedRead(BaseModel):
    """Kompilering av alle MIB-er kjøres asynkront for å unngå gateway timeout."""

    queued: Literal[True] = True


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


class SnmpSysInfoRead(BaseModel):
    """sysDescr.0 + sysName.0 for nettverksskann / DCIM-kandidater."""

    ok: bool
    sys_name: str | None = None
    sys_descr: str | None = None
    error: str | None = None


class SnmpInventoryRequest(BaseModel):
    """SNMPv2c-poll av IF-MIB / ifXTable (ingen MIB-kompilering nødvendig)."""

    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(161, ge=1, le=65535)
    community: str = Field("public", min_length=1, max_length=256)
    # Større L2/L3-switcher (f.eks. Juniper EX) har mange ifEntry/ifXEntry-rader — 4k var for lavt.
    max_varbinds: int = Field(20_000, ge=200, le=50_000)
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


class SnmpScanRequest(SnmpInventoryRequest):
    """Samme parametere som inventar; svar utvider med IPv4 og VLAN."""


class SnmpIpAddressRow(BaseModel):
    address: str = Field(..., max_length=45)
    if_index: int
    netmask: str | None = Field(None, max_length=64)
    interface_name: str | None = Field(None, max_length=128)


class SnmpVlanRow(BaseModel):
    vlan_id: int = Field(..., ge=1, le=4094)
    name: str | None = Field(None, max_length=256)


class SnmpInterfaceVlanRow(BaseModel):
    if_index: int
    native_vlan_id: int = Field(..., ge=1, le=4094)
    bridge_port: int | None = Field(None, ge=1)
    interface_name: str | None = Field(None, max_length=128)


class SnmpScanRead(BaseModel):
    ok: bool
    error: str | None = None
    host: str
    sys_name: str | None = None
    sys_descr: str | None = None
    interfaces: list[SnmpInterfaceRow] = Field(default_factory=list)
    ip_addresses: list[SnmpIpAddressRow] = Field(default_factory=list)
    vlans: list[SnmpVlanRow] = Field(default_factory=list)
    interface_vlans: list[SnmpInterfaceVlanRow] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
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


SnmpMibTreeNodeRead.model_rebuild()
