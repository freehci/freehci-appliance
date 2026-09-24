"""Record explicit VRF stretch so membership is never inferred from name or RD.

Revision ID: 20260627_ipam_vrf_stretch
Revises: 20260626_ipam_overlay_stretch
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260627_ipam_vrf_stretch"
down_revision: Union[str, Sequence[str], None] = "20260626_ipam_overlay_stretch"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_vrf_stretches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vrf_low_id", sa.Integer(), nullable=False),
        sa.Column("vrf_high_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vrf_low_id"], ["ipam_vrfs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vrf_high_id"], ["ipam_vrfs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vrf_low_id", "vrf_high_id", name="uq_ipam_vrf_stretch_pair"),
        sa.UniqueConstraint("slug", name="uq_ipam_vrf_stretch_slug"),
    )


def downgrade() -> None:
    op.drop_table("ipam_vrf_stretches")
