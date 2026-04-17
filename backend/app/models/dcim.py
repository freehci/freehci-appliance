"""DCIM: sites, rooms, racks, modeller og plassering."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Site(Base):
    __tablename__ = "dcim_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
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
    # relationship til IAM User deklareres som string for å unngå import-syklus.
    user: Mapped["User"] = relationship("User")  # type: ignore[name-defined]


class Room(Base):
    __tablename__ = "dcim_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("dcim_sites.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    site: Mapped["Site"] = relationship(back_populates="rooms")
    racks: Mapped[list["Rack"]] = relationship(back_populates="room", cascade="all, delete-orphan")


class Rack(Base):
    __tablename__ = "dcim_racks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("dcim_rooms.id", ondelete="CASCADE"), nullable=False)
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


class DeviceType(Base):
    """Logisk klasse utstyr (switch, server, router, …) — grunnlag for attributter og plugin-kobling."""

    __tablename__ = "dcim_device_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


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
