"""Assign a firmware/BIOS baseline to a device without applying members.

Revision ID: 20260624_dcim_bl_assign
Revises: 20260623_ipam_overlay_segment
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260624_dcim_bl_assign"
down_revision: Union[str, Sequence[str], None] = "20260623_ipam_overlay_segment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_device_artifact_baseline_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("baseline_id", sa.Integer(), nullable=False),
        sa.Column("intent", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["baseline_id"], ["dcim_device_artifact_baselines.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "baseline_id", name="uq_dcim_device_artifact_baseline_assignment"),
    )


def downgrade() -> None:
    op.drop_table("dcim_device_artifact_baseline_assignments")
