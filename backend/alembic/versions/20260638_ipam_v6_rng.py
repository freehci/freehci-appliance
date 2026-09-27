"""Record IPv6 ranges so free CIDRs never invent an inventory window.

Revision ID: 20260638_ipam_v6_rng
Revises: 20260637_ipam_ds_grp
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260638_ipam_v6_rng"
down_revision: Union[str, Sequence[str], None] = "20260637_ipam_ds_grp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_ipv6_ranges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ipv6_prefix_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("start_address", sa.String(length=64), nullable=False),
        sa.Column("end_address", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["ipv6_prefix_id"], ["ipam_ipv6_prefixes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ipv6_prefix_id", "slug", name="uq_ipam_ipv6_range_prefix_slug"),
        sa.UniqueConstraint("ipv6_prefix_id", "start_address", "end_address", name="uq_ipam_ipv6_range_prefix_span"),
    )


def downgrade() -> None:
    op.drop_table("ipam_ipv6_ranges")
