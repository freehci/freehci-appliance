"""IAM: personkatalog (users), globale roller og grupper med nestede undergrupper.

Eksterne IdP-er (f.eks. Active Directory) kan kobles via plugin med capability
`iam.directory_provider` — se `app.integrations.iam_directory_provider`.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", name="uq_users_username"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Vanlige verdier: `person`, `service_account` (for tjeneste-/maskinidentiteter); plugins kan bruke egne prefiks.
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="person")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Synkronisering fra ekstern IAM (AD/LDAP m.m.); fylles av plugins, ikke hardkodet logikk i kjernen.
    external_subject_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    identity_provider: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tenant_memberships: Mapped[list["TenantUserMembership"]] = relationship(
        "TenantUserMembership",
        back_populates="user",
    )


class IamRole(Base):
    """Global applikasjonsrolle (utenfor DCIM site-spesifikke roller)."""

    __tablename__ = "iam_roles"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_iam_roles_slug"),
        UniqueConstraint("name", name="uq_iam_roles_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class IamGroup(Base):
    __tablename__ = "iam_groups"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_iam_groups_slug"),
        UniqueConstraint("name", name="uq_iam_groups_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_subject_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    identity_provider: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user_memberships: Mapped[list["IamGroupUserMember"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )
    child_links: Mapped[list["IamGroupSubgroup"]] = relationship(
        back_populates="group",
        foreign_keys="IamGroupSubgroup.group_id",
        cascade="all, delete-orphan",
    )


class IamGroupUserMember(Base):
    __tablename__ = "iam_group_users"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_iam_group_users"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("iam_groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    group: Mapped[IamGroup] = relationship(back_populates="user_memberships")


class IamGroupSubgroup(Base):
    """Undergruppe: parent-gruppe (group_id) inneholder child_group_id."""

    __tablename__ = "iam_group_subgroups"
    __table_args__ = (UniqueConstraint("group_id", "child_group_id", name="uq_iam_group_subgroups"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("iam_groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    child_group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("iam_groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    group: Mapped[IamGroup] = relationship(
        back_populates="child_links",
        foreign_keys=[group_id],
    )


class IamUserRole(Base):
    __tablename__ = "iam_user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_iam_user_roles"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("iam_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
