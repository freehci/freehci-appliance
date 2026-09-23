"""VRF-instans på enhet uten påføring av routing.

Revision ID: 20260606_ipam_vrf_instance
Revises: 20260605_ipam_ipv4_range
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260606_ipam_vrf_instance"
down_revision: Union[str, Sequence[str], None] = "20260605_ipam_ipv4_range"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_vrf_instances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vrf_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("intent", sa.String(length=32), nullable=False, server_default="recorded"),
        sa.Column("route_distinguisher", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vrf_id"], ["ipam_vrfs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vrf_id", "device_id", name="uq_ipam_vrf_instance_vrf_device"),
        sa.UniqueConstraint("vrf_id", "slug", name="uq_ipam_vrf_instance_vrf_slug"),
    )


def downgrade() -> None:
    op.drop_table("ipam_vrf_instances")
