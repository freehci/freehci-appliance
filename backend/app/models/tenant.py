"""Multi-tenant: organisasjoner som eier DCIM-sites (og dermed IPAM-kontekst)."""

from __future__ import annotations

import datetime as dt
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sites: Mapped[list["Site"]] = relationship("Site", back_populates="tenant")
    circuits: Mapped[list["IpamCircuit"]] = relationship("IpamCircuit", back_populates="tenant")
