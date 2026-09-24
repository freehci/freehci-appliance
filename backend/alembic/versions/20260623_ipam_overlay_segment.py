"""Record overlay VNIs so they stay distinct from VLAN IDs and are never applied.

Revision ID: 20260623_ipam_overlay_segment
Revises: 20260622_ipam_circuit_ownership
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260623_ipam_overlay_segment"
down_revision: Union[str, Sequence[str], None] = "20260622_ipam_circuit_ownership"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_overlay_segments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("vni", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("vlan_id", sa.Integer(), nullable=True),
        sa.Column("vrf_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vlan_id"], ["ipam_vlans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vrf_id"], ["ipam_vrfs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "vni", name="uq_ipam_overlay_segment_site_vni"),
        sa.UniqueConstraint("site_id", "slug", name="uq_ipam_overlay_segment_site_slug"),
    )


def downgrade() -> None:
    op.drop_table("ipam_overlay_segments")
