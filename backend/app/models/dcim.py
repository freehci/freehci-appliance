"""DCIM: sites, rooms, racks, modeller og plassering."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.iam import User
    from app.models.tenant import Tenant


class Site(Base):
    __tablename__ = "dcim_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    county: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="sites")
    rooms: Mapped[list["Room"]] = relationship(back_populates="site", cascade="all, delete-orphan")
    access_grants: Mapped[list["SiteAccessGrant"]] = relationship(
        back_populates="site",
        cascade="all, delete-orphan",
    )


class SiteRole(Base):
    __tablename__ = "dcim_site_roles"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_dcim_site_role_slug"),
        UniqueConstraint("name", name="uq_dcim_site_role_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    grants: Mapped[list["SiteAccessGrant"]] = relationship(back_populates="role")


class SiteAccessGrant(Base):
    __tablename__ = "dcim_site_access"
    __table_args__ = (
        UniqueConstraint("site_id", "user_id", "role_id", "is_contact", name="uq_dcim_site_access"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("dcim_sites.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("dcim_site_roles.id", ondelete="CASCADE"), nullable=False)
    is_contact: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    valid_from: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    site: Mapped["Site"] = relationship(back_populates="access_grants")
    role: Mapped["SiteRole"] = relationship(back_populates="grants")
    # relationship til IAM User; `User` importeres kun under TYPE_CHECKING (flake8 F821).
    user: Mapped["User"] = relationship("User")


class Room(Base):
    __tablename__ = "dcim_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("dcim_sites.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    floor: Mapped[str | None] = mapped_column(String(128), nullable=True)
    floorplan_relpath: Mapped[str | None] = mapped_column(String(512), nullable=True)
    floorplan_mime_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    @hybrid_property
    def has_floorplan(self) -> bool:
        return self.floorplan_relpath is not None

    site: Mapped["Site"] = relationship(back_populates="rooms")
    racks: Mapped[list["Rack"]] = relationship(back_populates="room", cascade="all, delete-orphan")


class Rack(Base):
    __tablename__ = "dcim_racks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("dcim_rooms.id", ondelete="CASCADE"), nullable=False)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    u_height: Mapped[int] = mapped_column(Integer, nullable=False, default=42)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Fysiske mål i millimeter (H × B × D); valgfritt for planlegging og senere 3D/plugin.
    height_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    depth_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchase_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    commissioned_date: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    room: Mapped["Room"] = relationship(back_populates="racks")
    placements: Mapped[list["RackPlacement"]] = relationship(
        back_populates="rack",
        cascade="all, delete-orphan",
    )


class Manufacturer(Base):
    __tablename__ = "dcim_manufacturers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    logo_mime_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    logo_relpath: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # IANA SMI Network Management Private Enterprise Number (1.3.6.1.4.1.<pen>) — kobler produsent til SNMP enterprise.
    iana_enterprise_number: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True)

    identities: Mapped[list["ManufacturerIdentity"]] = relationship(
        back_populates="manufacturer",
        cascade="all, delete-orphan",
        order_by="ManufacturerIdentity.identity_type, ManufacturerIdentity.namespace, ManufacturerIdentity.normalized_value",
    )


class ManufacturerIdentity(Base):
    """Ekstern identitet som gjenkjenner en canonical produsent/vendor."""

    __tablename__ = "dcim_manufacturer_identities"
    __table_args__ = (
        UniqueConstraint("identity_type", "namespace", "normalized_value", name="uq_dcim_manufacturer_identity_value"),
        Index("ix_dcim_manufacturer_identities_mfr", "manufacturer_id"),
        Index("ix_dcim_manufacturer_identities_lookup", "identity_type", "namespace", "normalized_value"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("dcim_manufacturers.id", ondelete="CASCADE"), nullable=False)
    identity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    namespace: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="identities")


class DeviceType(Base):
    """Logisk klasse utstyr (switch, server, router, …) — grunnlag for attributter og plugin-kobling."""

    __tablename__ = "dcim_device_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Ikonnavn for Font Awesome solid (f.eks. «server» → klasse fa-server); NULL = bruk heuristikk ut fra slug.
    fa_icon: Mapped[str | None] = mapped_column(String(64), nullable=True)


class DeviceModel(Base):
    __tablename__ = "dcim_device_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manufacturer_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_manufacturers.id", ondelete="SET NULL"),
        nullable=True,
    )
    device_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    u_height: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    form_factor: Mapped[str | None] = mapped_column(String(64), nullable=True)
    image_front_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    image_back_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    image_front_relpath: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image_front_mime_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    image_back_relpath: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image_back_mime_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    image_product_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    image_product_relpath: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image_product_mime_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Numerisk sysObjectID (f.eks. 1.3.6.1.4.1.890.1.5.8.40) — matching: agent-OID starter med denne strengen.
    snmp_sys_object_id_prefix: Mapped[str | None] = mapped_column(String(512), nullable=True)

    components: Mapped[list["DeviceModelComponent"]] = relationship(
        back_populates="device_model",
        cascade="all, delete-orphan",
        order_by="DeviceModelComponent.sort_order, DeviceModelComponent.id",
    )
    identities: Mapped[list["DeviceModelIdentity"]] = relationship(
        back_populates="device_model",
        cascade="all, delete-orphan",
        order_by="DeviceModelIdentity.identity_type, DeviceModelIdentity.namespace, DeviceModelIdentity.normalized_value",
    )
    templates: Mapped[list["DeviceModelTemplate"]] = relationship(
        back_populates="device_model",
        cascade="all, delete-orphan",
        order_by="DeviceModelTemplate.component_type, DeviceModelTemplate.sort_order, DeviceModelTemplate.name",
    )


class DeviceModelIdentity(Base):
    """Ekstern identitet som gjenkjenner en canonical enhetsmodell."""

    __tablename__ = "dcim_device_model_identities"
    __table_args__ = (
        UniqueConstraint("identity_type", "namespace", "normalized_value", name="uq_dcim_device_model_identity_value"),
        Index("ix_dcim_device_model_identities_model", "device_model_id"),
        Index("ix_dcim_device_model_identities_lookup", "identity_type", "namespace", "normalized_value"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_model_id: Mapped[int] = mapped_column(ForeignKey("dcim_device_models.id", ondelete="CASCADE"), nullable=False)
    identity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    namespace: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device_model: Mapped["DeviceModel"] = relationship(back_populates="identities")


class DeviceInstance(Base):
    __tablename__ = "dcim_device_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_model_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_models.id", ondelete="SET NULL"),
        nullable=True,
    )
    device_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    asset_tag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Fleksible nøkkel/verdi (f.eks. os, port_count); porter/IPAM kommer som egne tabeller senere.
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    placement: Mapped["RackPlacement | None"] = relationship(
        back_populates="device",
        uselist=False,
        cascade="all, delete-orphan",
    )
    interfaces: Mapped[list["DeviceInterface"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        order_by="DeviceInterface.sort_order, DeviceInterface.name",
    )
    device_ip_assignments: Mapped[list["DeviceIpAssignment"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        order_by="DeviceIpAssignment.family, DeviceIpAssignment.address",
    )
    components: Mapped[list["DeviceInstanceComponent"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        order_by="DeviceInstanceComponent.sort_order, DeviceInstanceComponent.id",
    )


class ComponentClass(Base):
    """Komponentklasse (RAM, CPU, HDD, PSU, ...), med validerte egendefinerte felt."""

    __tablename__ = "dcim_component_classes"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_dcim_component_classes_slug"),
        UniqueConstraint("name", name="uq_dcim_component_classes_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    fields: Mapped[list["ComponentClassField"]] = relationship(
        back_populates="component_class",
        cascade="all, delete-orphan",
        order_by="ComponentClassField.sort_order, ComponentClassField.id",
    )
    components: Mapped[list["Component"]] = relationship(back_populates="component_class")
    parent_links: Mapped[list["ComponentClassParent"]] = relationship(
        back_populates="child_class",
        cascade="all, delete-orphan",
        foreign_keys="ComponentClassParent.child_class_id",
        order_by="ComponentClassParent.sort_order, ComponentClassParent.id",
    )
    child_links: Mapped[list["ComponentClassParent"]] = relationship(
        back_populates="parent_class",
        cascade="all, delete-orphan",
        foreign_keys="ComponentClassParent.parent_class_id",
    )


class ComponentClassParent(Base):
    """Fler-arv/mixins mellom komponentklasser."""

    __tablename__ = "dcim_component_class_parents"
    __table_args__ = (
        UniqueConstraint("child_class_id", "parent_class_id", name="uq_dcim_component_class_parent"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    child_class_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_component_classes.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_class_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_component_classes.id", ondelete="CASCADE"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    child_class: Mapped["ComponentClass"] = relationship(
        "ComponentClass",
        back_populates="parent_links",
        foreign_keys=[child_class_id],
    )
    parent_class: Mapped["ComponentClass"] = relationship(
        "ComponentClass",
        back_populates="child_links",
        foreign_keys=[parent_class_id],
    )


class ComponentClassField(Base):
    __tablename__ = "dcim_component_class_fields"
    __table_args__ = (
        UniqueConstraint("class_id", "key", name="uq_dcim_component_class_fields_class_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("dcim_component_classes.id", ondelete="CASCADE"), nullable=False)
    key: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(16), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    min_number: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_number: Mapped[float | None] = mapped_column(Float, nullable=True)
    choices_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    default_value: Mapped[object | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    component_class: Mapped["ComponentClass"] = relationship(back_populates="fields")


class Component(Base):
    """Gjenbrukbar komponent i biblioteket (f.eks. Samsung 32GB DDR4 DIMM)."""

    __tablename__ = "dcim_components"
    __table_args__ = (
        UniqueConstraint("class_id", "manufacturer_id", "part_number", name="uq_dcim_components_class_mfr_part"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("dcim_component_classes.id", ondelete="RESTRICT"), nullable=False)
    manufacturer_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_manufacturers.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    part_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    specs_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    component_class: Mapped["ComponentClass"] = relationship(back_populates="components")
    manufacturer: Mapped["Manufacturer | None"] = relationship("Manufacturer")
    model_links: Mapped[list["DeviceModelComponent"]] = relationship(back_populates="component")
    instance_links: Mapped[list["DeviceInstanceComponent"]] = relationship(back_populates="component")
    child_templates: Mapped[list["ComponentChildTemplate"]] = relationship(
        back_populates="parent_component",
        cascade="all, delete-orphan",
        foreign_keys="ComponentChildTemplate.parent_component_id",
        order_by="ComponentChildTemplate.sort_order, ComponentChildTemplate.id",
    )
    identities: Mapped[list["ComponentIdentity"]] = relationship(
        back_populates="component",
        cascade="all, delete-orphan",
        order_by="ComponentIdentity.identity_type, ComponentIdentity.namespace, ComponentIdentity.normalized_value",
    )


class ComponentIdentity(Base):
    """Ekstern identitet som gjenkjenner en canonical FreeHCI-komponent."""

    __tablename__ = "dcim_component_identities"
    __table_args__ = (
        UniqueConstraint("identity_type", "namespace", "normalized_value", name="uq_dcim_component_identity_value"),
        Index("ix_dcim_component_identities_component", "component_id"),
        Index("ix_dcim_component_identities_lookup", "identity_type", "namespace", "normalized_value"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("dcim_components.id", ondelete="CASCADE"), nullable=False)
    identity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    namespace: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    component: Mapped["Component"] = relationship(back_populates="identities")


class RedfishSchemaBundle(Base):
    """Importert DMTF Redfish Schema Bundle (DSP8010)."""

    __tablename__ = "dcim_redfish_schema_bundles"
    __table_args__ = (
        UniqueConstraint("sha256", name="uq_dcim_redfish_schema_bundles_sha256"),
        Index("ix_dcim_redfish_schema_bundles_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_relpath: Mapped[str] = mapped_column(String(512), nullable=False)
    extract_relpath: Mapped[str] = mapped_column(String(512), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ready")
    schema_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    json_schema_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    csdl_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    openapi_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dictionaries_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    resources: Mapped[list["RedfishSchemaResource"]] = relationship(
        back_populates="bundle",
        cascade="all, delete-orphan",
        order_by="RedfishSchemaResource.resource_type, RedfishSchemaResource.schema_version",
    )


class RedfishSchemaResource(Base):
    """Indeksert Redfish schema/resource fra en DSP8010-bundle."""

    __tablename__ = "dcim_redfish_schema_resources"
    __table_args__ = (
        UniqueConstraint("bundle_id", "format", "schema_uri", name="uq_dcim_redfish_schema_resource_uri"),
        Index("ix_dcim_redfish_schema_resources_bundle", "bundle_id"),
        Index("ix_dcim_redfish_schema_resources_lookup", "resource_type", "format"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bundle_id: Mapped[int] = mapped_column(ForeignKey("dcim_redfish_schema_bundles.id", ondelete="CASCADE"), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False)
    schema_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    schema_uri: Mapped[str] = mapped_column(String(512), nullable=False)
    format: Mapped[str] = mapped_column(String(32), nullable=False)
    file_relpath: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    bundle: Mapped["RedfishSchemaBundle"] = relationship(back_populates="resources")


class NetBoxDeviceTypeLibraryImport(Base):
    """Importert NetBox Device Type Library-kopi."""

    __tablename__ = "dcim_netbox_dtl_imports"
    __table_args__ = (
        UniqueConstraint("sha256", name="uq_dcim_netbox_dtl_imports_sha256"),
        Index("ix_dcim_netbox_dtl_imports_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_relpath: Mapped[str] = mapped_column(String(512), nullable=False)
    extract_relpath: Mapped[str] = mapped_column(String(512), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ready")
    item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    manufacturer_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    image_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    component_template_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    items: Mapped[list["NetBoxDeviceTypeLibraryItem"]] = relationship(
        back_populates="import_run",
        cascade="all, delete-orphan",
        order_by="NetBoxDeviceTypeLibraryItem.manufacturer, NetBoxDeviceTypeLibraryItem.model",
    )


class NetBoxDeviceTypeLibraryItem(Base):
    """Indeksert device type fra NetBox Device Type Library."""

    __tablename__ = "dcim_netbox_dtl_items"
    __table_args__ = (
        UniqueConstraint("import_id", "manufacturer", "slug", name="uq_dcim_netbox_dtl_item_import_slug"),
        Index("ix_dcim_netbox_dtl_items_import", "import_id"),
        Index("ix_dcim_netbox_dtl_items_lookup", "manufacturer", "slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    import_id: Mapped[int] = mapped_column(ForeignKey("dcim_netbox_dtl_imports.id", ondelete="CASCADE"), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    part_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    u_height: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_full_depth: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    airflow: Mapped[str | None] = mapped_column(String(64), nullable=True)
    front_image_relpath: Mapped[str | None] = mapped_column(String(512), nullable=True)
    rear_image_relpath: Mapped[str | None] = mapped_column(String(512), nullable=True)
    yaml_relpath: Mapped[str] = mapped_column(String(512), nullable=False)
    component_counts_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    import_run: Mapped["NetBoxDeviceTypeLibraryImport"] = relationship(back_populates="items")


class DeviceModelTemplate(Base):
    """NetBox component template bevart på FreeHCI DeviceModel."""

    __tablename__ = "dcim_device_model_templates"
    __table_args__ = (
        UniqueConstraint("device_model_id", "source", "component_type", "name", name="uq_dcim_device_model_template"),
        Index("ix_dcim_device_model_templates_model", "device_model_id"),
        Index("ix_dcim_device_model_templates_type", "component_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_model_id: Mapped[int] = mapped_column(ForeignKey("dcim_device_models.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="netbox_dtl")
    component_type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    normalized_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    quality_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quality_warnings_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device_model: Mapped["DeviceModel"] = relationship(back_populates="templates")


class ComponentChildTemplate(Base):
    """Barn som en bibliotekskomponent består av, f.eks. NIC -> porter."""

    __tablename__ = "dcim_component_child_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_component_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_components.id", ondelete="CASCADE"),
        nullable=False,
    )
    child_class_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_component_classes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    child_component_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_components.id", ondelete="SET NULL"),
        nullable=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    name_pattern: Mapped[str | None] = mapped_column(String(128), nullable=True)
    slot_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    overrides_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    materialize_as: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    parent_component: Mapped["Component"] = relationship(
        "Component",
        back_populates="child_templates",
        foreign_keys=[parent_component_id],
    )
    child_class: Mapped["ComponentClass"] = relationship("ComponentClass")
    child_component: Mapped["Component | None"] = relationship("Component", foreign_keys=[child_component_id])


class DeviceModelComponent(Base):
    __tablename__ = "dcim_device_model_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_model_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_device_models.id", ondelete="CASCADE"),
        nullable=False,
    )
    component_id: Mapped[int] = mapped_column(ForeignKey("dcim_components.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    slot_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    overrides_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    device_model: Mapped["DeviceModel"] = relationship(back_populates="components")
    component: Mapped["Component"] = relationship(back_populates="model_links")


class DeviceInstanceComponent(Base):
    __tablename__ = "dcim_device_instance_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    component_id: Mapped[int] = mapped_column(ForeignKey("dcim_components.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    slot_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    asset_tag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    installed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    overrides_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    device: Mapped["DeviceInstance"] = relationship(back_populates="components")
    component: Mapped["Component"] = relationship(back_populates="instance_links")


class DeviceInterface(Base):
    """Grensesnitt eller port på en enhet (forberedelse for IPAM/VLAN).

    vlan_id er bare et 802.1Q-tall uten global semantikk: samme VLAN-ID kan brukes på
    flere sites. For plasserte enheter er site gitt via rack → rom → site; da er
    (site, vlan_id) den naturlige konteksten — ikke VLAN-ID alene.
    """

    __tablename__ = "dcim_device_interfaces"
    __table_args__ = (UniqueConstraint("device_id", "name", name="uq_dcim_device_interface_device_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(32), nullable=True)
    speed_mbps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mtu: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 802.1Q brukbar rekkevidde 1–4094; NULL = ikke satt (ingen kobling til legacy VLAN-tabell).
    vlan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Logisk underegrensesnitt (f.eks. Juniper me0.0 under fysisk me0); MAC ofte på forelder, VLAN/IP på barn.
    parent_interface_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_interfaces.id", ondelete="CASCADE"),
        nullable=True,
    )

    device: Mapped["DeviceInstance"] = relationship(back_populates="interfaces")
    parent: Mapped["DeviceInterface | None"] = relationship(
        "DeviceInterface",
        remote_side=[id],
        back_populates="subinterfaces",
    )
    subinterfaces: Mapped[list["DeviceInterface"]] = relationship(
        "DeviceInterface",
        back_populates="parent",
    )
    ip_assignments: Mapped[list["InterfaceIpAssignment"]] = relationship(
        back_populates="interface",
        cascade="all, delete-orphan",
        order_by="InterfaceIpAssignment.family, InterfaceIpAssignment.address",
    )


class InterfaceIpAssignment(Base):
    """IPv4/IPv6-adresse på et grensesnitt; kan senere kobles til IPAM-prefiks.

    Overlappende subnet mellom sites (samme privat CIDR flere steder) håndteres i IPAM
    ved at prefiks alltid er knyttet til site — ikke global unikhet på CIDR.
    """

    __tablename__ = "dcim_interface_ip_assignments"
    __table_args__ = (UniqueConstraint("interface_id", "address", name="uq_dcim_iface_ip_addr"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    interface_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_device_interfaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    ipv4_prefix_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_ipv4_prefixes.id", ondelete="SET NULL"),
        nullable=True,
    )
    family: Mapped[str] = mapped_column(String(4), nullable=False)
    address: Mapped[str] = mapped_column(String(45), nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)

    interface: Mapped["DeviceInterface"] = relationship(back_populates="ip_assignments")


class DeviceIpAssignment(Base):
    """IPv4/IPv6 på enheten uten kobling til et bestemt grensesnitt (f.eks. én felles MAC på alle porter)."""

    __tablename__ = "dcim_device_ip_assignments"
    __table_args__ = (UniqueConstraint("device_id", "address", name="uq_dcim_device_ip_addr"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    ipv4_prefix_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_ipv4_prefixes.id", ondelete="SET NULL"),
        nullable=True,
    )
    family: Mapped[str] = mapped_column(String(4), nullable=False)
    address: Mapped[str] = mapped_column(String(45), nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)

    device: Mapped["DeviceInstance"] = relationship(back_populates="device_ip_assignments")


class RackPlacement(Base):
    __tablename__ = "dcim_rack_placements"
    __table_args__ = (UniqueConstraint("device_id", name="uq_dcim_rack_placement_device"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rack_id: Mapped[int] = mapped_column(ForeignKey("dcim_racks.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("dcim_device_instances.id", ondelete="CASCADE"), nullable=False)
    # Laveste RU (1 = nederst i racket)
    u_position: Mapped[int] = mapped_column(Integer, nullable=False)
    mounting: Mapped[str] = mapped_column(String(16), nullable=False, default="front")

    rack: Mapped["Rack"] = relationship(back_populates="placements")
    device: Mapped["DeviceInstance"] = relationship(back_populates="placement")
