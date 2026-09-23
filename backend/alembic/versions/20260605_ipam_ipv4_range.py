"""Førsteklasses IPv4-område/pool uten DHCP-tjeneste.

Revision ID: 20260605_ipam_ipv4_range
Revises: 20260604_dcim_artifact
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260605_ipam_ipv4_range"
down_revision: Union[str, Sequence[str], None] = "20260604_dcim_artifact"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_ipv4_ranges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ipv4_prefix_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="allocation"),
        sa.Column("start_address", sa.String(length=45), nullable=False),
        sa.Column("end_address", sa.String(length=45), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["ipv4_prefix_id"], ["ipam_ipv4_prefixes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ipv4_prefix_id", "slug", name="uq_ipam_ipv4_range_prefix_slug"),
        sa.UniqueConstraint("ipv4_prefix_id", "start_address", "end_address", name="uq_ipam_ipv4_range_prefix_span"),
    )


def downgrade() -> None:
    op.drop_table("ipam_ipv4_ranges")
