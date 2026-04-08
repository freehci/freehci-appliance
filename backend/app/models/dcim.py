"""DCIM: sites, rooms, racks, modeller og plassering."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Site(Base):
    __tablename__ = "dcim_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    rooms: Mapped[list["Room"]] = relationship(back_populates="site", cascade="all, delete-orphan")


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
