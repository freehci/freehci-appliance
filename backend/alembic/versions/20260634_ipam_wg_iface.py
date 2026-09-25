"""Record WireGuard interfaces and peers without inventing keys or BGP.

Revision ID: 20260634_ipam_wg_iface
Revises: 20260633_dcim_ipv6_pfx
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260634_ipam_wg_iface"
down_revision: Union[str, Sequence[str], None] = "20260633_dcim_ipv6_pfx"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_wireguard_interfaces",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("interface_id", sa.Integer(), nullable=True),
        sa.Column("listen_port", sa.Integer(), nullable=True),
        sa.Column("address", sa.String(length=64), nullable=True),
        sa.Column("private_key_ref", sa.String(length=255), nullable=True),
        sa.Column("tunnel_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tunnel_id"], ["ipam_tunnels.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "slug", name="uq_ipam_wg_iface_device_slug"),
    )
    op.create_table(
        "ipam_wireguard_peers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("wg_interface_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("public_key_ref", sa.String(length=255), nullable=True),
        sa.Column("psk_ref", sa.String(length=255), nullable=True),
        sa.Column("endpoint_host", sa.String(length=255), nullable=True),
        sa.Column("endpoint_port", sa.Integer(), nullable=True),
        sa.Column("allowed_ips", sa.JSON(), nullable=True),
        sa.Column("persistent_keepalive", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["wg_interface_id"], ["ipam_wireguard_interfaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("wg_interface_id", "slug", name="uq_ipam_wg_peer_iface_slug"),
    )


def downgrade() -> None:
    op.drop_table("ipam_wireguard_peers")
    op.drop_table("ipam_wireguard_interfaces")
