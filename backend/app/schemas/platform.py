"""Skjemaer for cluster-inventar."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator

CLUSTER_KINDS = frozenset({"proxmox", "talos", "other"})
MEMBER_ROLES = frozenset({"node", "control", "worker", "other"})
VM_STATUSES = frozenset({"planned", "active", "retired"})
STORAGE_KINDS = frozenset({"datastore", "pool", "other"})
STORAGE_STATUSES = frozenset({"planned", "active", "retired"})
VIF_STATUSES = frozenset({"planned", "active", "retired"})
DISK_KINDS = frozenset({"disk", "volume", "other"})
DISK_STATUSES = frozenset({"planned", "active", "retired"})
CLOUD_KINDS = frozenset({"aws", "azure", "gcp", "other"})
CLOUD_STATUSES = frozenset({"planned", "active", "retired"})


class PlatformClusterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    kind: str = "other"
    site_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "other"
        if s not in CLUSTER_KINDS:
            raise ValueError(f"kind må være en av: {', '.join(sorted(CLUSTER_KINDS))}")
        return s


class PlatformClusterMemberCreate(BaseModel):
    device_id: int = Field(..., ge=1)
    role: str = "node"

    @field_validator("role")
    @classmethod
    def role_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "node"
        if s not in MEMBER_ROLES:
            raise ValueError(f"role må være en av: {', '.join(sorted(MEMBER_ROLES))}")
        return s


class PlatformClusterMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cluster_id: int
    device_id: int
    role: str
    created_at: dt.datetime


class PlatformVirtualMachineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    device_id: int | None = Field(None, ge=1)
    status: str = "planned"

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "planned"
        if s not in VM_STATUSES:
            raise ValueError(f"status må være en av: {', '.join(sorted(VM_STATUSES))}")
        return s


class PlatformVifIpv4Read(BaseModel):
    id: int
    address: str


class PlatformVifIpv4Assign(BaseModel):
    ipv4_prefix_id: int = Field(..., ge=1)


class PlatformVirtualInterfaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    vm_id: int
    status: str
    created_at: dt.datetime
    ipv4_addresses: list[PlatformVifIpv4Read] = Field(default_factory=list)


class PlatformVirtualInterfaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    status: str = "planned"

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "planned"
        if s not in VIF_STATUSES:
            raise ValueError(f"status må være en av: {', '.join(sorted(VIF_STATUSES))}")
        return s


class PlatformVirtualDiskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    vm_id: int
    storage_pool_id: int | None
    kind: str
    status: str
    created_at: dt.datetime


class PlatformVirtualDiskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    storage_pool_id: int | None = Field(None, ge=1)
    kind: str = "other"
    status: str = "planned"

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "other"
        if s not in DISK_KINDS:
            raise ValueError(f"kind må være en av: {', '.join(sorted(DISK_KINDS))}")
        return s

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "planned"
        if s not in DISK_STATUSES:
            raise ValueError(f"status må være en av: {', '.join(sorted(DISK_STATUSES))}")
        return s


class PlatformVirtualMachineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    cluster_id: int
    device_id: int | None
    status: str
    created_at: dt.datetime
    interfaces: list[PlatformVirtualInterfaceRead] = Field(default_factory=list)
    disks: list[PlatformVirtualDiskRead] = Field(default_factory=list)


class PlatformStoragePoolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    kind: str = "other"
    status: str = "planned"

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "other"
        if s not in STORAGE_KINDS:
            raise ValueError(f"kind må være en av: {', '.join(sorted(STORAGE_KINDS))}")
        return s

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "planned"
        if s not in STORAGE_STATUSES:
            raise ValueError(f"status må være en av: {', '.join(sorted(STORAGE_STATUSES))}")
        return s


class PlatformStoragePoolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    cluster_id: int
    kind: str
    status: str
    created_at: dt.datetime


class PlatformClusterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    kind: str
    site_id: int | None
    description: str | None
    created_at: dt.datetime
    members: list[PlatformClusterMemberRead] = Field(default_factory=list)
    vms: list[PlatformVirtualMachineRead] = Field(default_factory=list)
    storage_pools: list[PlatformStoragePoolRead] = Field(default_factory=list)


class PlatformCloudSubscriptionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    kind: str = "other"
    status: str = "planned"
    description: str | None = None

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "other"
        if s not in CLOUD_KINDS:
            raise ValueError(f"kind må være en av: {', '.join(sorted(CLOUD_KINDS))}")
        return s

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "planned"
        if s not in CLOUD_STATUSES:
            raise ValueError(f"status må være en av: {', '.join(sorted(CLOUD_STATUSES))}")
        return s


class PlatformCloudSubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    kind: str
    status: str
    description: str | None
    created_at: dt.datetime
