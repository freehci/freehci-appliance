"""DCIM rom: etasje (floor) og plantegning (fil).

Revision ID: dcim_room_floorplan
Revises: dcim_dt_fa_icon
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "dcim_room_floorplan"
down_revision: Union[str, Sequence[str], None] = "dcim_dt_fa_icon"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_rooms", sa.Column("floor", sa.String(length=128), nullable=True))
    op.add_column("dcim_rooms", sa.Column("floorplan_relpath", sa.String(length=512), nullable=True))
    op.add_column("dcim_rooms", sa.Column("floorplan_mime_type", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("dcim_rooms", "floorplan_mime_type")
    op.drop_column("dcim_rooms", "floorplan_relpath")
    op.drop_column("dcim_rooms", "floor")
