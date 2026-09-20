"""Autonomous systems, AS assignments and BGP sessions.

Revision ID: 20260523_ipam_as_bgp
Revises: 20260522_ipam_circuits
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260523_ipam_as_bgp"
down_revision: Union[str, Sequence[str], None] = "20260522_ipam_circuits"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_autonomous_systems",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("asn", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("tenant_scope", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_scope", "asn", name="uq_ipam_as_scope_asn"),
    )
    op.create_table(
        "ipam_as_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("autonomous_system_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("vrf_id", sa.Integer(), nullable=True),
        sa.Column("vrf_scope", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["autonomous_system_id"], ["ipam_autonomous_systems.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vrf_id"], ["ipam_vrfs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("autonomous_system_id", "site_id", "vrf_scope", name="uq_ipam_as_assign_site_vrf"),
    )
    op.create_table(
        "ipam_bgp_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("local_as_id", sa.Integer(), nullable=False),
        sa.Column("remote_as_id", sa.Integer(), nullable=True),
        sa.Column("remote_asn", sa.BigInteger(), nullable=False),
        sa.Column("peer_ip", sa.String(length=64), nullable=False),
        sa.Column("vrf_id", sa.Integer(), nullable=True),
        sa.Column("vrf_scope", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("address_families", sa.JSON(), nullable=True),
        sa.Column("desired_status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("observed_status", sa.String(length=32), nullable=True),
        sa.Column("local_device_id", sa.Integer(), nullable=True),
        sa.Column("local_interface_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["local_as_id"], ["ipam_autonomous_systems.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["remote_as_id"], ["ipam_autonomous_systems.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vrf_id"], ["ipam_vrfs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["local_device_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["local_interface_id"], ["dcim_device_interfaces.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "local_as_id", "peer_ip", "vrf_scope", name="uq_ipam_bgp_peer"),
        sa.UniqueConstraint("site_id", "slug", name="uq_ipam_bgp_site_slug"),
    )


def downgrade() -> None:
    op.drop_table("ipam_bgp_sessions")
    op.drop_table("ipam_as_assignments")
    op.drop_table("ipam_autonomous_systems")
