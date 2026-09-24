"""Record explicit L2 stretch between VLANs so membership is never inferred from VID.

Revision ID: 20260625_ipam_vlan_stretch
Revises: 20260624_dcim_bl_assign
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260625_ipam_vlan_stretch"
down_revision: Union[str, Sequence[str], None] = "20260624_dcim_bl_assign"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_vlan_stretches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vlan_low_id", sa.Integer(), nullable=False),
        sa.Column("vlan_high_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vlan_low_id"], ["ipam_vlans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vlan_high_id"], ["ipam_vlans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vlan_low_id", "vlan_high_id", name="uq_ipam_vlan_stretch_pair"),
        sa.UniqueConstraint("slug", name="uq_ipam_vlan_stretch_slug"),
    )


def downgrade() -> None:
    op.drop_table("ipam_vlan_stretches")
