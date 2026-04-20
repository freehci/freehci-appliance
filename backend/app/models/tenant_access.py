"""Kobling mellom tenants og IAM-brukere, samt tenant-scoped DCIM-tilganger."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.iam import User
    from app.models.tenant import Tenant


class TenantUserMembership(Base):
    """Bruker som er medlem av en tenant (f.eks. kundeorganisasjon)."""

    __tablename__ = "tenant_user_memberships"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user_membership"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="member")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="user_memberships")
    user: Mapped["User"] = relationship("User", back_populates="tenant_memberships")


class TenantDcimGrant(Base):
    """Gir en tenant eksplisitt tilgang til et DCIM-omfang (site, rom eller rack)."""

    __tablename__ = "tenant_dcim_grants"
    __table_args__ = (
        UniqueConstraint("tenant_id", "scope_type", "scope_id", name="uq_tenant_dcim_grant_scope"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scope_type: Mapped[str] = mapped_column(String(16), nullable=False)
    scope_id: Mapped[int] = mapped_column(Integer, nullable=False)
    access: Mapped[str] = mapped_column(String(16), nullable=False, default="view")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="dcim_grants")
