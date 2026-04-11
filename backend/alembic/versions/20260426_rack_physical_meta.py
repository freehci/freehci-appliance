"""Rack physical dimensions, brand, dates, notes, JSON attributes.

Revision ID: 20260426_rack_meta
Revises: 20260425_dm_product
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260426_rack_meta"
down_revision: Union[str, Sequence[str], None] = "20260425_dm_product"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_racks", sa.Column("height_mm", sa.Integer(), nullable=True))
    op.add_column("dcim_racks", sa.Column("width_mm", sa.Integer(), nullable=True))
    op.add_column("dcim_racks", sa.Column("depth_mm", sa.Integer(), nullable=True))
    op.add_column("dcim_racks", sa.Column("brand", sa.String(length=255), nullable=True))
    op.add_column("dcim_racks", sa.Column("purchase_date", sa.Date(), nullable=True))
    op.add_column("dcim_racks", sa.Column("commissioned_date", sa.Date(), nullable=True))
    op.add_column("dcim_racks", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column("dcim_racks", sa.Column("attributes", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("dcim_racks", "attributes")
    op.drop_column("dcim_racks", "notes")
    op.drop_column("dcim_racks", "commissioned_date")
    op.drop_column("dcim_racks", "purchase_date")
    op.drop_column("dcim_racks", "brand")
    op.drop_column("dcim_racks", "depth_mm")
    op.drop_column("dcim_racks", "width_mm")
    op.drop_column("dcim_racks", "height_mm")
