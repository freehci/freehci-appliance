"""Tenant-brukermedlemskap, DCIM-grants og valgfri tenant_id på prefiks/VLAN/rack.

Revision ID: 20260432_tenant_access
Revises: 20260431_tenant_ipam
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260432_tenant_access"
down_revision: Union[str, Sequence[str], None] = "20260431_tenant_ipam"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_user_memberships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_tenant_user_memberships_tenant_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_tenant_user_memberships_user_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user_membership"),
    )
    op.create_index("ix_tenant_user_memberships_tenant_id", "tenant_user_memberships", ["tenant_id"], unique=False)

    op.create_table(
        "tenant_dcim_grants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("scope_type", sa.String(length=16), nullable=False),
        sa.Column("scope_id", sa.Integer(), nullable=False),
        sa.Column("access", sa.String(length=16), nullable=False, server_default="view"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], name="fk_tenant_dcim_grants_tenant_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "scope_type", "scope_id", name="uq_tenant_dcim_grant_scope"),
    )
    op.create_index("ix_tenant_dcim_grants_tenant_id", "tenant_dcim_grants", ["tenant_id"], unique=False)

    op.add_column(
        "ipam_ipv4_prefixes",
        sa.Column("tenant_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_ipam_ipv4_prefixes_tenant_id",
        "ipam_ipv4_prefixes",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "ipam_vlans",
        sa.Column("tenant_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_ipam_vlans_tenant_id",
        "ipam_vlans",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "dcim_racks",
        sa.Column("tenant_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_dcim_racks_tenant_id",
        "dcim_racks",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_dcim_racks_tenant_id", "dcim_racks", type_="foreignkey")
    op.drop_column("dcim_racks", "tenant_id")

    op.drop_constraint("fk_ipam_vlans_tenant_id", "ipam_vlans", type_="foreignkey")
    op.drop_column("ipam_vlans", "tenant_id")

    op.drop_constraint("fk_ipam_ipv4_prefixes_tenant_id", "ipam_ipv4_prefixes", type_="foreignkey")
    op.drop_column("ipam_ipv4_prefixes", "tenant_id")

    op.drop_index("ix_tenant_dcim_grants_tenant_id", table_name="tenant_dcim_grants")
    op.drop_table("tenant_dcim_grants")

    op.drop_index("ix_tenant_user_memberships_tenant_id", table_name="tenant_user_memberships")
    op.drop_table("tenant_user_memberships")
