"""Subnet ping scans and discovered hosts (MAC from ARP where available).

Revision ID: 20260420_ipam_scan
Revises: 20260419_iface_ip_pfx
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260420_ipam_scan"
down_revision: Union[str, Sequence[str], None] = "20260419_iface_ip_pfx"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_subnet_scans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("ipv4_prefix_id", sa.Integer(), nullable=True),
        sa.Column("cidr", sa.String(length=32), nullable=False),
        sa.Column("method", sa.String(length=32), nullable=False, server_default="ping"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("hosts_scanned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hosts_responding", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["ipv4_prefix_id"], ["ipam_ipv4_prefixes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ipam_scan_hosts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scan_id", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(length=45), nullable=False),
        sa.Column("mac_address", sa.String(length=32), nullable=True),
        sa.Column("ping_responded", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["scan_id"], ["ipam_subnet_scans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scan_id", "address", name="uq_ipam_scan_host_scan_addr"),
    )


def downgrade() -> None:
    op.drop_table("ipam_scan_hosts")
    op.drop_table("ipam_subnet_scans")
