"""IPAM (IPv4 først): prefiks er alltid scoped til én DCIM-site.

Samme CIDR (f.eks. 192.168.1.0/24) kan finnes på flere sites — typisk avdelingskontor
med identisk adresseplan. Unikhet er (site_id, cidr), ikke globalt på CIDR alene.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IpamIpv4Prefix(Base):
    __tablename__ = "ipam_ipv4_prefixes"
    __table_args__ = (UniqueConstraint("site_id", "cidr", name="uq_ipam_ipv4_site_cidr"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Kanonisk IPv4 CIDR-streng, f.eks. 192.168.1.0/24 (normaliseres i tjenestelaget).
    cidr: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
