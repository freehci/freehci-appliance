"""Rack mounting (floor/wall) and elevation above floor.

Revision ID: 20260517_rack_elev
Revises: 20260516_ipam_v4_updated_at
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260517_rack_elev"
down_revision: Union[str, Sequence[str], None] = "20260516_ipam_v4_updated_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_racks",
        sa.Column("mounting", sa.String(length=16), nullable=False, server_default="floor"),
    )
    op.add_column("dcim_racks", sa.Column("elevation_mm", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("dcim_racks", "elevation_mm")
    op.drop_column("dcim_racks", "mounting")
