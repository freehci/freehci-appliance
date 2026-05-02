"""Pydantic-skjemaer for DCIM API."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_FA_ICON_NAME_RE = re.compile(r"^[a-z0-9-]{1,50}$")


def normalize_device_type_fa_icon(v: object) -> str | None:
    """Normaliserer FA solid-ikonnavn (lagres uten «fa-»-prefiks). Tom / ugyldig → None."""
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("", "none", "null", "default", "-"):
        return None
    if s.startswith("fa-"):
        s = s[3:]
    if s == "":
        return None
    if not _FA_ICON_NAME_RE.match(s):
        raise ValueError(
            "fa_icon må være 1–50 tegn: små bokstaver, tall og bindestrek (ikonnavn som i Font Awesome, uten fa-)"
        )
    return s


class SiteCreate(BaseModel):
    tenant_id: int | None = Field(None, ge=1, description="Utelates → default-tenant")
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    address_line1: str | None = Field(None, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    postal_code: str | None = Field(None, max_length=32)
    city: str | None = Field(None, max_length=255)
    county: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    address_note: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if not _SLUG_RE.match(s):
            raise ValueError("slug må være lowercase bokstaver, tall og bindestrek")
        return s


class SiteUpdate(BaseModel):
    tenant_id: int | None = Field(None, ge=1)
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    address_line1: str | None = Field(None, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    postal_code: str | None = Field(None, max_length=32)
    city: str | None = Field(None, max_length=255)
    county: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    address_note: str | None = None


class SiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    name: str
    slug: str
    description: str | None
    address_line1: str | None
    address_line2: str | None
    postal_code: str | None
    city: str | None
    county: str | None
    country: str | None
    latitude: float | None
    longitude: float | None
    address_note: str | None
    created_at: dt.datetime


class SiteGeocodeRequest(BaseModel):
    """Geokod adressefeltene for en site.

    Hvis `query` er satt, brukes den direkte; ellers bygges query fra site-feltene.
    """

    query: str | None = Field(None, max_length=512)
    limit: int = Field(default=5, ge=1, le=10)


class SiteGeocodeCandidateRead(BaseModel):
    display_name: str
    latitude: float
    longitude: float


class SiteGeocodeResponse(BaseModel):
    query: str
    candidates: list[SiteGeocodeCandidateRead]


class SiteRoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=64)
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if not _SLUG_RE.match(s):
            raise ValueError("slug må være lowercase bokstaver, tall og bindestrek")
        return s


class SiteRoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class SiteRoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None


class SiteAccessGrantCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    role_id: int = Field(..., ge=1)
    is_contact: bool = False
    valid_from: dt.datetime | None = None
    valid_to: dt.datetime | None = None
    notes: str | None = None


class SiteAccessGrantUpdate(BaseModel):
    role_id: int | None = Field(None, ge=1)
    is_contact: bool | None = None
    valid_from: dt.datetime | None = None
    valid_to: dt.datetime | None = None
    notes: str | None = None


class SiteAccessGrantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    user_id: int
    role_id: int
    is_contact: bool
    valid_from: dt.datetime | None
    valid_to: dt.datetime | None
    notes: str | None


class RoomCreate(BaseModel):
    site_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    floor: str | None = Field(None, max_length=128)


class RoomUpdate(BaseModel):
    site_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    floor: str | None = Field(None, max_length=128)


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    name: str
    description: str | None
    floor: str | None = None
    has_floorplan: bool


class RackCreate(BaseModel):
    room_id: int
    tenant_id: int | None = Field(None, ge=1, description="Valgfritt: colo-/kunde-tenant for rack")
    name: str = Field(..., min_length=1, max_length=255)
    u_height: int = Field(42, ge=1, le=64)
    sort_order: int = 0
    height_mm: int | None = Field(None, ge=1, le=100_000)
    width_mm: int | None = Field(None, ge=1, le=100_000)
    depth_mm: int | None = Field(None, ge=1, le=100_000)
    brand: str | None = Field(None, max_length=255)
    purchase_date: dt.date | None = None
    commissioned_date: dt.date | None = None
    notes: str | None = None
    attributes: dict[str, Any] | None = None


class RackUpdate(BaseModel):
    tenant_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    u_height: int | None = Field(None, ge=1, le=64)
    sort_order: int | None = None
    height_mm: int | None = Field(None, ge=1, le=100_000)
    width_mm: int | None = Field(None, ge=1, le=100_000)
    depth_mm: int | None = Field(None, ge=1, le=100_000)
    brand: str | None = Field(None, max_length=255)
    purchase_date: dt.date | None = None
    commissioned_date: dt.date | None = None
    notes: str | None = None
    attributes: dict[str, Any] | None = None


class RackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    tenant_id: int | None = None
    name: str
    u_height: int
    sort_order: int
    height_mm: int | None
    width_mm: int | None
    depth_mm: int | None
    brand: str | None
    purchase_date: dt.date | None
    commissioned_date: dt.date | None
    notes: str | None
    attributes: dict[str, Any] | None


class ManufacturerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    website_url: str | None = Field(None, max_length=1024)


class ManufacturerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    website_url: str | None = Field(None, max_length=1024)
    iana_enterprise_number: int | None = Field(None, ge=0, le=2147483647)


class ManufacturerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    website_url: str | None
    has_logo: bool
    iana_enterprise_number: int | None = None


class DeviceTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    fa_icon: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if not _SLUG_RE.match(s):
            raise ValueError("slug må være lowercase bokstaver, tall og bindestrek")
        return s

    @field_validator("fa_icon", mode="before")
    @classmethod
    def fa_icon_create(cls, v: object) -> str | None:
        return normalize_device_type_fa_icon(v)


class DeviceTypeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    fa_icon: str | None = None

    @field_validator("fa_icon", mode="before")
    @classmethod
    def fa_icon_update(cls, v: object) -> str | None:
        return normalize_device_type_fa_icon(v)


class DeviceTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    fa_icon: str | None = None


class DeviceModelBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    u_height: int
    device_type_id: int | None
    snmp_sys_object_id_prefix: str | None = None


class ManufacturerDetailRead(BaseModel):
    id: int
    name: str
    description: str | None
    website_url: str | None
    has_logo: bool
    iana_enterprise_number: int | None = None
    device_models: list[DeviceModelBrief]


class DeviceModelCreate(BaseModel):
    manufacturer_id: int | None = None
    device_type_id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    u_height: int = Field(1, ge=0, le=64)
    form_factor: str | None = Field(None, max_length=64)
    image_front_url: str | None = Field(None, max_length=1024)
    image_back_url: str | None = Field(None, max_length=1024)
    image_product_url: str | None = Field(None, max_length=1024)
    snmp_sys_object_id_prefix: str | None = Field(None, max_length=512)


class DeviceModelUpdate(BaseModel):
    manufacturer_id: int | None = None
    device_type_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    u_height: int | None = Field(None, ge=0, le=64)
    form_factor: str | None = Field(None, max_length=64)
    image_front_url: str | None = Field(None, max_length=1024)
    image_back_url: str | None = Field(None, max_length=1024)
    image_product_url: str | None = Field(None, max_length=1024)
    snmp_sys_object_id_prefix: str | None = Field(None, max_length=512)


class DeviceModelRead(BaseModel):
    """Bygges eksplisitt i tjenesten (inkl. has_image_* fra relpath)."""

    id: int
    manufacturer_id: int | None
    device_type_id: int | None
    name: str
    u_height: int
    form_factor: str | None
    image_front_url: str | None
    image_back_url: str | None
    image_product_url: str | None
    has_image_front_file: bool
    has_image_back_file: bool
    has_image_product_file: bool
    snmp_sys_object_id_prefix: str | None = None


class DeviceInstanceCreate(BaseModel):
    device_model_id: int | None = None
    device_type_id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    serial_number: str | None = Field(None, max_length=128)
    asset_tag: str | None = Field(None, max_length=128)
    attributes: dict[str, Any] | None = None


class DeviceInstanceUpdate(BaseModel):
    device_model_id: int | None = None
    device_type_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    serial_number: str | None = Field(None, max_length=128)
    asset_tag: str | None = Field(None, max_length=128)
    attributes: dict[str, Any] | None = None


class DeviceInstanceRead(BaseModel):
    """Bygges i tjenesten (effective_device_type_id fra modell eller override)."""

    id: int
    device_model_id: int | None
    device_type_id: int | None
    effective_device_type_id: int | None
    # Site fra rack → rom når enheten er plassert; brukes bl.a. for IPAM-prefiks i riktig site.
    effective_site_id: int | None
    name: str
    serial_number: str | None
    asset_tag: str | None
    attributes: dict[str, Any] = Field(default_factory=dict)


COMPONENT_FIELD_TYPES = {"text", "number", "integer", "boolean", "choice", "date"}
EXTERNAL_IDENTITY_TYPES = {
    "mac",
    "oui",
    "pci",
    "pci_vendor",
    "usb",
    "usb_vendor",
    "iana_pen",
    "snmp_sysobjectid",
    "redfish",
    "smbios",
    "lldp",
    "vendor_api",
    "other",
}


class ComponentClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    icon: str | None = Field(None, max_length=64)
    active: bool = True

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if not _SLUG_RE.match(s):
            raise ValueError("slug må være lowercase bokstaver, tall og bindestrek")
        return s


class ComponentClassUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    icon: str | None = Field(None, max_length=64)
    active: bool | None = None


class ComponentClassRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    icon: str | None
    active: bool


class ComponentStandardCatalogSeedResponse(BaseModel):
    classes_created: int = 0
    fields_created: int = 0
    parents_created: int = 0
    class_slugs: list[str] = Field(default_factory=list)


class ComponentExternalMappingFieldRead(BaseModel):
    source_path: str
    target_field_key: str
    transform: str | None = None
    notes: str | None = None


class ComponentExternalMappingResourceRead(BaseModel):
    source_type: str
    target_class_slug: str
    relation: str = "component"
    notes: str | None = None
    fields: list[ComponentExternalMappingFieldRead] = Field(default_factory=list)


class ComponentExternalMappingProfileRead(BaseModel):
    source: str
    display_name: str
    description: str
    resources: list[ComponentExternalMappingResourceRead] = Field(default_factory=list)


class ExternalIdentityObservation(BaseModel):
    identity_type: str = Field(..., min_length=1, max_length=32)
    namespace: str = Field(..., min_length=1, max_length=64)
    value: str = Field(..., min_length=1, max_length=255)
    source: str | None = Field(None, max_length=64)
    confidence: int = Field(100, ge=0, le=100)
    raw_json: dict[str, Any] | None = None

    @field_validator("identity_type")
    @classmethod
    def identity_type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in EXTERNAL_IDENTITY_TYPES:
            raise ValueError("identity_type er ikke støttet")
        return s

    @field_validator("namespace")
    @classmethod
    def namespace_ok(cls, v: str) -> str:
        return v.strip().lower()


class ExternalIdentityResolveRequest(BaseModel):
    observations: list[ExternalIdentityObservation] = Field(..., min_length=1)


class ExternalIdentityResolveMatch(BaseModel):
    owner_type: str
    owner_id: int
    owner_name: str
    identity_type: str
    namespace: str
    value: str
    normalized_value: str
    source: str | None = None
    identity_confidence: int
    observation_confidence: int
    score: int
    reason: str


class ComponentExternalMappingPreviewRequest(BaseModel):
    source: str = Field(..., min_length=1, max_length=64)
    resource_type: str = Field(..., min_length=1, max_length=255)
    payload: dict[str, Any]


class ComponentExternalMappingPreviewRead(BaseModel):
    source: str
    source_type: str
    target_class_slug: str
    relation: str
    mapped_values: dict[str, Any] = Field(default_factory=dict)
    specs_json: dict[str, Any] = Field(default_factory=dict)
    component_defaults: dict[str, Any] = Field(default_factory=dict)
    extra_values: dict[str, Any] = Field(default_factory=dict)
    identity_observations: list[ExternalIdentityObservation] = Field(default_factory=list)
    identity_matches: list[ExternalIdentityResolveMatch] = Field(default_factory=list)
    missing_paths: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ExternalInventoryImportPreviewRequest(ComponentExternalMappingPreviewRequest):
    pass


class ExternalInventoryImportPreviewRead(BaseModel):
    source: str
    source_type: str
    target_class_slug: str
    relation: str
    proposed_action: str
    component_defaults: dict[str, Any] = Field(default_factory=dict)
    specs_json: dict[str, Any] = Field(default_factory=dict)
    identity_matches: list[ExternalIdentityResolveMatch] = Field(default_factory=list)
    identity_observations: list[ExternalIdentityObservation] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ComponentClassParentCreate(BaseModel):
    parent_class_id: int = Field(..., ge=1)
    sort_order: int = 0


class ComponentClassParentUpdate(BaseModel):
    sort_order: int | None = None


class ComponentClassParentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    child_class_id: int
    parent_class_id: int
    sort_order: int


class ComponentClassFieldCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=64)
    label: str = Field(..., min_length=1, max_length=255)
    data_type: str = Field(..., max_length=16)
    unit: str | None = Field(None, max_length=32)
    required: bool = False
    sort_order: int = 0
    min_number: float | None = None
    max_number: float | None = None
    choices_json: list[str] | None = None
    default_value: Any | None = None
    description: str | None = None
    active: bool = True

    @field_validator("key")
    @classmethod
    def key_ok(cls, v: str) -> str:
        s = v.strip().lower().replace(" ", "_")
        if not re.match(r"^[a-z][a-z0-9_]{0,63}$", s):
            raise ValueError("key må starte med bokstav og kan inneholde små bokstaver, tall og _")
        return s

    @field_validator("data_type")
    @classmethod
    def data_type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in COMPONENT_FIELD_TYPES:
            raise ValueError("data_type må være text, number, integer, boolean, choice eller date")
        return s


class ComponentClassFieldUpdate(BaseModel):
    label: str | None = Field(None, min_length=1, max_length=255)
    data_type: str | None = Field(None, max_length=16)
    unit: str | None = Field(None, max_length=32)
    required: bool | None = None
    sort_order: int | None = None
    min_number: float | None = None
    max_number: float | None = None
    choices_json: list[str] | None = None
    default_value: Any | None = None
    description: str | None = None
    active: bool | None = None

    @field_validator("data_type")
    @classmethod
    def data_type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in COMPONENT_FIELD_TYPES:
            raise ValueError("data_type må være text, number, integer, boolean, choice eller date")
        return s


class ComponentClassFieldRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    class_id: int
    key: str
    label: str
    data_type: str
    unit: str | None
    required: bool
    sort_order: int
    min_number: float | None
    max_number: float | None
    choices_json: list[str] | None
    default_value: Any | None
    description: str | None
    active: bool


class ComponentClassEffectiveFieldRead(ComponentClassFieldRead):
    inherited_from_class_id: int | None = None
    inherited_from_class_name: str | None = None
    inherited: bool = False


class ComponentFieldImpactRead(BaseModel):
    breaking: bool
    affected_components: int = 0
    affected_model_links: int = 0
    affected_instance_links: int = 0
    messages: list[str] = Field(default_factory=list)


class ComponentCreate(BaseModel):
    class_id: int = Field(..., ge=1)
    manufacturer_id: int | None = Field(None, ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    part_number: str | None = Field(None, max_length=128)
    description: str | None = None
    specs_json: dict[str, Any] | None = None
    active: bool = True


class ComponentUpdate(BaseModel):
    class_id: int | None = Field(None, ge=1)
    manufacturer_id: int | None = Field(None, ge=1)
    name: str | None = Field(None, min_length=1, max_length=255)
    part_number: str | None = Field(None, max_length=128)
    description: str | None = None
    specs_json: dict[str, Any] | None = None
    active: bool | None = None


class ComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    class_id: int
    manufacturer_id: int | None
    name: str
    part_number: str | None
    description: str | None
    specs_json: dict[str, Any] = Field(default_factory=dict)
    active: bool


class ExternalIdentityBaseCreate(BaseModel):
    identity_type: str = Field(..., min_length=1, max_length=32)
    namespace: str = Field(..., min_length=1, max_length=64)
    value: str = Field(..., min_length=1, max_length=255)
    source: str | None = Field(None, max_length=64)
    confidence: int = Field(100, ge=0, le=100)
    raw_json: dict[str, Any] | None = None
    notes: str | None = None

    @field_validator("identity_type")
    @classmethod
    def identity_type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in EXTERNAL_IDENTITY_TYPES:
            raise ValueError("identity_type er ikke støttet")
        return s

    @field_validator("namespace")
    @classmethod
    def namespace_ok(cls, v: str) -> str:
        return v.strip().lower()


class ExternalIdentityBaseUpdate(BaseModel):
    identity_type: str | None = Field(None, min_length=1, max_length=32)
    namespace: str | None = Field(None, min_length=1, max_length=64)
    value: str | None = Field(None, min_length=1, max_length=255)
    source: str | None = Field(None, max_length=64)
    confidence: int | None = Field(None, ge=0, le=100)
    raw_json: dict[str, Any] | None = None
    notes: str | None = None

    @field_validator("identity_type")
    @classmethod
    def identity_type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in EXTERNAL_IDENTITY_TYPES:
            raise ValueError("identity_type er ikke støttet")
        return s

    @field_validator("namespace")
    @classmethod
    def namespace_ok(cls, v: str | None) -> str | None:
        return v.strip().lower() if v is not None else None


class ComponentIdentityCreate(ExternalIdentityBaseCreate):
    pass


class ComponentIdentityUpdate(ExternalIdentityBaseUpdate):
    pass


class ManufacturerIdentityCreate(ExternalIdentityBaseCreate):
    pass


class ManufacturerIdentityUpdate(ExternalIdentityBaseUpdate):
    pass


class DeviceModelIdentityCreate(ExternalIdentityBaseCreate):
    pass


class DeviceModelIdentityUpdate(ExternalIdentityBaseUpdate):
    pass


class ExternalIdentityReadBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identity_type: str
    namespace: str
    value: str
    normalized_value: str
    source: str | None
    confidence: int
    raw_json: dict[str, Any] = Field(default_factory=dict)
    notes: str | None
    created_at: dt.datetime


class ComponentIdentityRead(ExternalIdentityReadBase):
    component_id: int


class ManufacturerIdentityRead(ExternalIdentityReadBase):
    manufacturer_id: int


class DeviceModelIdentityRead(ExternalIdentityReadBase):
    device_model_id: int


class ComponentChildTemplateCreate(BaseModel):
    child_class_id: int = Field(..., ge=1)
    child_component_id: int | None = Field(None, ge=1)
    quantity: int = Field(1, ge=1, le=1_000_000)
    name_pattern: str | None = Field(None, max_length=128)
    slot_label: str | None = Field(None, max_length=128)
    overrides_json: dict[str, Any] | None = None
    materialize_as: str | None = Field(None, max_length=32)
    sort_order: int = 0


class ComponentChildTemplateUpdate(BaseModel):
    child_class_id: int | None = Field(None, ge=1)
    child_component_id: int | None = Field(None, ge=1)
    quantity: int | None = Field(None, ge=1, le=1_000_000)
    name_pattern: str | None = Field(None, max_length=128)
    slot_label: str | None = Field(None, max_length=128)
    overrides_json: dict[str, Any] | None = None
    materialize_as: str | None = Field(None, max_length=32)
    sort_order: int | None = None


class ComponentChildTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_component_id: int
    child_class_id: int
    child_component_id: int | None
    quantity: int
    name_pattern: str | None
    slot_label: str | None
    overrides_json: dict[str, Any] = Field(default_factory=dict)
    materialize_as: str | None
    sort_order: int


class ComponentMaterializeInterfacesRequest(BaseModel):
    component_link_id: int = Field(..., ge=1)
    overwrite_existing: bool = False


class DeviceModelComponentCreate(BaseModel):
    component_id: int = Field(..., ge=1)
    quantity: int = Field(1, ge=1, le=1_000_000)
    slot_label: str | None = Field(None, max_length=128)
    notes: str | None = None
    overrides_json: dict[str, Any] | None = None
    sort_order: int = 0


class DeviceModelComponentUpdate(BaseModel):
    component_id: int | None = Field(None, ge=1)
    quantity: int | None = Field(None, ge=1, le=1_000_000)
    slot_label: str | None = Field(None, max_length=128)
    notes: str | None = None
    overrides_json: dict[str, Any] | None = None
    sort_order: int | None = None


class DeviceModelComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_model_id: int
    component_id: int
    quantity: int
    slot_label: str | None
    notes: str | None
    overrides_json: dict[str, Any] = Field(default_factory=dict)
    sort_order: int


class DeviceInstanceComponentCreate(BaseModel):
    component_id: int = Field(..., ge=1)
    quantity: int = Field(1, ge=1, le=1_000_000)
    slot_label: str | None = Field(None, max_length=128)
    serial_number: str | None = Field(None, max_length=128)
    asset_tag: str | None = Field(None, max_length=128)
    installed_at: dt.datetime | None = None
    notes: str | None = None
    overrides_json: dict[str, Any] | None = None
    sort_order: int = 0


class DeviceInstanceComponentUpdate(BaseModel):
    component_id: int | None = Field(None, ge=1)
    quantity: int | None = Field(None, ge=1, le=1_000_000)
    slot_label: str | None = Field(None, max_length=128)
    serial_number: str | None = Field(None, max_length=128)
    asset_tag: str | None = Field(None, max_length=128)
    installed_at: dt.datetime | None = None
    notes: str | None = None
    overrides_json: dict[str, Any] | None = None
    sort_order: int | None = None


class DeviceInstanceComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    component_id: int
    quantity: int
    slot_label: str | None
    serial_number: str | None
    asset_tag: str | None
    installed_at: dt.datetime | None
    notes: str | None
    overrides_json: dict[str, Any] = Field(default_factory=dict)
    sort_order: int


class DeviceInterfaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    mac_address: str | None = Field(None, max_length=32)
    speed_mbps: int | None = Field(None, ge=0, le=1_000_000_000)
    mtu: int | None = Field(None, ge=68, le=65535)
    vlan_id: int | None = Field(None, ge=1, le=4094)
    enabled: bool = True
    sort_order: int = 0
    parent_interface_id: int | None = Field(None, ge=1)


class DeviceInterfaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    mac_address: str | None = Field(None, max_length=32)
    speed_mbps: int | None = Field(None, ge=0, le=1_000_000_000)
    mtu: int | None = Field(None, ge=68, le=65535)
    vlan_id: int | None = Field(None, ge=1, le=4094)
    enabled: bool | None = None
    sort_order: int | None = None
    parent_interface_id: int | None = Field(None, ge=1)


class IpAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    interface_id: int
    ipv4_prefix_id: int | None = None
    family: str
    address: str
    is_primary: bool


class DeviceInterfaceRead(BaseModel):
    """Bygges i tjenesten (ip_assignments inkludert)."""

    id: int
    device_id: int
    parent_interface_id: int | None
    name: str
    description: str | None
    mac_address: str | None
    speed_mbps: int | None
    mtu: int | None
    vlan_id: int | None
    enabled: bool
    sort_order: int
    ip_assignments: list[IpAssignmentRead] = Field(default_factory=list)


class IpAssignmentCreate(BaseModel):
    address: str = Field(..., min_length=1, max_length=45)
    is_primary: bool = False
    ipv4_prefix_id: int | None = None


class IpAssignmentUpdate(BaseModel):
    is_primary: bool | None = None
    ipv4_prefix_id: int | None = None


class DeviceIpAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    ipv4_prefix_id: int | None = None
    family: str
    address: str
    is_primary: bool


class DeviceIpAssignmentCreate(BaseModel):
    address: str = Field(..., min_length=1, max_length=45)
    is_primary: bool = False
    ipv4_prefix_id: int | None = None


class DeviceIpAssignmentUpdate(BaseModel):
    is_primary: bool | None = None
    ipv4_prefix_id: int | None = None


class RackPlacementCreate(BaseModel):
    rack_id: int
    device_id: int
    u_position: int = Field(..., ge=0)
    mounting: str = Field(default="front", max_length=16)

    @field_validator("mounting")
    @classmethod
    def mounting_ok(cls, v: str) -> str:
        x = v.lower().strip()
        if x not in ("front", "rear"):
            raise ValueError("mounting må være front eller rear")
        return x


class RackPlacementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rack_id: int
    device_id: int
    u_position: int
    mounting: str


class RackPlacementUpdate(BaseModel):
    rack_id: int | None = None
    u_position: int | None = Field(None, ge=0)
    mounting: str | None = Field(None, max_length=16)

    @field_validator("mounting")
    @classmethod
    def mounting_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        x = v.lower().strip()
        if x not in ("front", "rear"):
            raise ValueError("mounting må være front eller rear")
        return x
