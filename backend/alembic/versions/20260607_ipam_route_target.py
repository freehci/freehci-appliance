"""Route target som eget objekt, ikke RD.

Revision ID: 20260607_ipam_route_target
Revises: 20260606_ipam_vrf_instance
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260607_ipam_route_target"
down_revision: Union[str, Sequence[str], None] = "20260606_ipam_vrf_instance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_route_targets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("value", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_ipam_route_target_slug"),
        sa.UniqueConstraint("value", name="uq_ipam_route_target_value"),
    )
    op.create_table(
        "ipam_vrf_route_targets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vrf_id", sa.Integer(), nullable=False),
        sa.Column("route_target_id", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["vrf_id"], ["ipam_vrfs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["route_target_id"], ["ipam_route_targets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vrf_id", "route_target_id", "direction", name="uq_ipam_vrf_rt_dir"),
    )


def downgrade() -> None:
    op.drop_table("ipam_vrf_route_targets")
    op.drop_table("ipam_route_targets")
