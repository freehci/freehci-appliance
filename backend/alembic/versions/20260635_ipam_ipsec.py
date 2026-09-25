"""Record IPsec profiles without inventing IKE, mode, keys or selectors.

Revision ID: 20260635_ipam_ipsec
Revises: 20260634_ipam_wg_iface
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260635_ipam_ipsec"
down_revision: Union[str, Sequence[str], None] = "20260634_ipam_wg_iface"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_ipsec_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("ike_version", sa.String(length=32), nullable=True),
        sa.Column("mode", sa.String(length=32), nullable=True),
        sa.Column("psk_ref", sa.String(length=255), nullable=True),
        sa.Column("local_id", sa.String(length=255), nullable=True),
        sa.Column("remote_id", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_ipam_ipsec_profile_slug"),
    )
    op.create_table(
        "ipam_ipsec_tunnels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tunnel_id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tunnel_id"], ["ipam_tunnels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["ipam_ipsec_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tunnel_id", name="uq_ipam_ipsec_tunnel"),
    )
    op.create_table(
        "ipam_ipsec_selectors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("local_cidr", sa.String(length=64), nullable=True),
        sa.Column("remote_cidr", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["ipam_ipsec_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "slug", name="uq_ipam_ipsec_selector_slug"),
    )


def downgrade() -> None:
    op.drop_table("ipam_ipsec_selectors")
    op.drop_table("ipam_ipsec_tunnels")
    op.drop_table("ipam_ipsec_profiles")
