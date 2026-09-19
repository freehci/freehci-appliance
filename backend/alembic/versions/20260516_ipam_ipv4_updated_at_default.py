"""IPv4 prefix updated_at: server_default so INSERT does not fail as prefix_conflict.

Revision ID: 20260516_ipam_v4_updated_at
Revises: 20260515_ipam_ipv6_grid
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260516_ipam_v4_updated_at"
down_revision: Union[str, Sequence[str], None] = "20260515_ipam_ipv6_grid"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.func.now(),
        )


def downgrade() -> None:
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=None,
        )
