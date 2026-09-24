"""Named fiber bundles of recorded strands, without invented count or pairs.

Revision ID: 20260617_dcim_fiber_bundle
Revises: 20260616_ipam_circuit_attributes
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260617_dcim_fiber_bundle"
down_revision: Union[str, Sequence[str], None] = "20260616_ipam_circuit_attributes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_fiber_bundles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cable_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cable_id"], ["dcim_cables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cable_id", "slug", name="uq_dcim_fiber_bundle_cable_slug"),
    )
    op.create_table(
        "dcim_fiber_bundle_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bundle_id", sa.Integer(), nullable=False),
        sa.Column("strand_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["bundle_id"], ["dcim_fiber_bundles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["strand_id"], ["dcim_fiber_strands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("strand_id", name="uq_dcim_fiber_bundle_member_strand"),
        sa.UniqueConstraint("bundle_id", "strand_id", name="uq_dcim_fiber_bundle_member_bundle_strand"),
    )


def downgrade() -> None:
    op.drop_table("dcim_fiber_bundle_members")
    op.drop_table("dcim_fiber_bundles")
