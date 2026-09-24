"""Record explicit overlay stretch so membership is never inferred from VNI.

Revision ID: 20260626_ipam_overlay_stretch
Revises: 20260625_ipam_vlan_stretch
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260626_ipam_overlay_stretch"
down_revision: Union[str, Sequence[str], None] = "20260625_ipam_vlan_stretch"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_overlay_stretches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("overlay_low_id", sa.Integer(), nullable=False),
        sa.Column("overlay_high_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["overlay_low_id"], ["ipam_overlay_segments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["overlay_high_id"], ["ipam_overlay_segments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("overlay_low_id", "overlay_high_id", name="uq_ipam_overlay_stretch_pair"),
        sa.UniqueConstraint("slug", name="uq_ipam_overlay_stretch_slug"),
    )


def downgrade() -> None:
    op.drop_table("ipam_overlay_stretches")
