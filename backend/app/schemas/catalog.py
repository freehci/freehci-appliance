"""Skjemaer for servicekatalog og én vertikal deploymentflyt."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator

TEMPLATE_KINDS = frozenset(
    {
        "device_instance",
        "cluster",
        "virtual_machine",
        "storage_pool",
        "virtual_interface",
        "virtual_disk",
        "cloud_subscription",
    }
)


class ServiceTemplateSpec(BaseModel):
    kind: str = "device_instance"
    reserve_ipv4: bool = False

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        s = (v or "").strip()
        if s not in TEMPLATE_KINDS:
            raise ValueError(
                "kind må være device_instance, cluster, virtual_machine, storage_pool, virtual_interface, virtual_disk eller cloud_subscription"
            )
        return s


class ServiceTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    description: str | None = None
    spec: ServiceTemplateSpec


class ServiceTemplateVersionCreate(BaseModel):
    version: str = Field(..., min_length=1, max_length=64)
    spec: ServiceTemplateSpec


class ServiceTemplateVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int
    version: str
    spec: dict
    created_at: dt.datetime


class ServiceTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    created_at: dt.datetime
    versions: list[ServiceTemplateVersionRead] = Field(default_factory=list)


class ServiceDeploymentCreate(BaseModel):
    template_version_id: int = Field(..., ge=1)
    device_id: int | None = Field(None, ge=1)
    device_ids: list[int] = Field(default_factory=list)
    ipv4_prefix_id: int | None = Field(None, ge=1)
    name: str | None = Field(None, max_length=255)
    cluster_kind: str | None = Field(None, max_length=32)
    cluster_id: int | None = Field(None, ge=1)
    storage_kind: str | None = Field(None, max_length=32)
    vm_id: int | None = Field(None, ge=1)
    disk_kind: str | None = Field(None, max_length=32)
    storage_pool_id: int | None = Field(None, ge=1)
    cloud_kind: str | None = Field(None, max_length=32)


class ServiceDeploymentStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: str
    detail: str | None
    created_at: dt.datetime


class ServiceInstanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    template_version_id: int
    deployment_id: int
    device_id: int | None
    cluster_id: int | None = None
    vm_id: int | None = None
    storage_pool_id: int | None = None
    virtual_interface_id: int | None = None
    virtual_disk_id: int | None = None
    cloud_subscription_id: int | None = None
    ipv4_address_id: int | None
    status: str
    created_at: dt.datetime


class ServiceDeploymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_version_id: int
    device_id: int | None
    cluster_id: int | None = None
    vm_id: int | None = None
    storage_pool_id: int | None = None
    virtual_interface_id: int | None = None
    virtual_disk_id: int | None = None
    cloud_subscription_id: int | None = None
    ipv4_prefix_id: int | None
    status: str
    plan_json: dict | None
    created_at: dt.datetime
    started_at: dt.datetime | None
    finished_at: dt.datetime | None
    steps: list[ServiceDeploymentStepRead] = Field(default_factory=list)
    instance: ServiceInstanceRead | None = None
