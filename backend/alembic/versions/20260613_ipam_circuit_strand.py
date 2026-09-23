"""Bind circuits to recorded fiber strands without inventing pairs or loss.

Revision ID: 20260613_ipam_circuit_strand
Revises: 20260612_dcim_fiber_strand
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260613_ipam_circuit_strand"
down_revision: Union[str, Sequence[str], None] = "20260612_dcim_fiber_strand"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_circuit_strands",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("circuit_id", sa.Integer(), nullable=False),
        sa.Column("strand_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["circuit_id"], ["ipam_circuits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["strand_id"], ["dcim_fiber_strands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("strand_id", name="uq_ipam_circuit_strand_strand"),
    )


def downgrade() -> None:
    op.drop_table("ipam_circuit_strands")
