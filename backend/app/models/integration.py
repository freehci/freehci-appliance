"""Tilkoblinger mot plugin-pakker. Plugin-kode lever under Extensions, ikke her."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class IntegrationConnection(Base):
    """Én tilkobling mot en installert/innebygd plugin. Hemmeligheter er secret:-referanser."""

    __tablename__ = "integration_connections"
    __table_args__ = (UniqueConstraint("slug", name="uq_integration_connection_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    plugin_id: Mapped[str] = mapped_column(String(128), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    credential_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    last_sync_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mapping_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    claims: Mapped[list["DeviceIdentityClaim"]] = relationship(back_populates="connection", cascade="all, delete-orphan")


class DeviceIdentity(Base):
    """Kanonisk ekstern identitet på én Device. Samme verdi kan ikke eies av to enheter."""

    __tablename__ = "dcim_device_identities"
    __table_args__ = (
        UniqueConstraint("identity_type", "namespace", "normalized_value", name="uq_dcim_device_identity_value"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("dcim_device_instances.id", ondelete="CASCADE"), nullable=False)
    identity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    namespace: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    claims: Mapped[list["DeviceIdentityClaim"]] = relationship(back_populates="identity", cascade="all, delete-orphan")


class DeviceIdentityClaim(Base):
    """En tilkobling hevder at denne identiteten er denne enheten."""

    __tablename__ = "dcim_device_identity_claims"
    __table_args__ = (UniqueConstraint("connection_id", "identity_id", name="uq_dcim_device_identity_claim"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connection_id: Mapped[int] = mapped_column(
        ForeignKey("integration_connections.id", ondelete="CASCADE"),
        nullable=False,
    )
    identity_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_device_identities.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    connection: Mapped["IntegrationConnection"] = relationship(back_populates="claims")
    identity: Mapped["DeviceIdentity"] = relationship(back_populates="claims")


class IdentityConflict(Base):
    """To kilder peker på ulike enheter for samme identitet. Ingen auto-merge."""

    __tablename__ = "integration_identity_conflicts"
    __table_args__ = (
        UniqueConstraint(
            "identity_type",
            "namespace",
            "normalized_value",
            "device_a_id",
            "device_b_id",
            name="uq_integration_identity_conflict",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    identity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    namespace: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(255), nullable=False)
    connection_a_id: Mapped[int | None] = mapped_column(
        ForeignKey("integration_connections.id", ondelete="SET NULL"),
        nullable=True,
    )
    connection_b_id: Mapped[int | None] = mapped_column(
        ForeignKey("integration_connections.id", ondelete="SET NULL"),
        nullable=True,
    )
    device_a_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    device_b_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
