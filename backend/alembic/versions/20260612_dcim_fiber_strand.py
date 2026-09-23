"""Fiber strands on optical cables, without invented loss or count.

Revision ID: 20260612_dcim_fiber_strand
Revises: 20260611_ipam_circuit_capacity
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260612_dcim_fiber_strand"
down_revision: Union[str, Sequence[str], None] = "20260611_ipam_circuit_capacity"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_fiber_strands",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cable_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cable_id"], ["dcim_cables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cable_id", "position", name="uq_dcim_fiber_strand_cable_position"),
    )


def downgrade() -> None:
    op.drop_table("dcim_fiber_strands")
