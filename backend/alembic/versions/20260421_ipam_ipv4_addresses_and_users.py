"""Users table and IPAM IPv4 address inventory.

Revision ID: 20260421_ipam_ipv4_addr
Revises: 20260420_ipam_scan
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260421_ipam_ipv4_addr"
down_revision: Union[str, Sequence[str], None] = "20260420_ipam_scan"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    op.create_table(
        "ipam_ipv4_addresses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("ipv4_prefix_id", sa.Integer(), nullable=True),
        sa.Column("address", sa.String(length=45), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="discovered"),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("mac_address", sa.String(length=32), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("device_type_id", sa.Integer(), nullable=True),
        sa.Column("device_model_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("interface_id", sa.Integer(), nullable=True),
        sa.Column("interface_ip_assignment_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ipv4_prefix_id"], ["ipam_ipv4_prefixes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["device_type_id"], ["dcim_device_types.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["device_model_id"], ["dcim_device_models.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["interface_ip_assignment_id"], ["dcim_interface_ip_assignments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "address", name="uq_ipam_ipv4_addr_site_address"),
        sa.UniqueConstraint("interface_ip_assignment_id", name="uq_ipam_ipv4_addr_iface_assign"),
    )

    op.create_index("ix_ipam_ipv4_addr_site", "ipam_ipv4_addresses", ["site_id"])
    op.create_index("ix_ipam_ipv4_addr_prefix", "ipam_ipv4_addresses", ["ipv4_prefix_id"])
    op.create_index("ix_ipam_ipv4_addr_status", "ipam_ipv4_addresses", ["status"])


def downgrade() -> None:
    op.drop_index("ix_ipam_ipv4_addr_status", table_name="ipam_ipv4_addresses")
    op.drop_index("ix_ipam_ipv4_addr_prefix", table_name="ipam_ipv4_addresses")
    op.drop_index("ix_ipam_ipv4_addr_site", table_name="ipam_ipv4_addresses")
    op.drop_table("ipam_ipv4_addresses")
    op.drop_table("users")

