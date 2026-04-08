"""DCIM-tabeller (sites, rooms, racks, modeller, enheter, plassering).

Revision ID: 20260409_dcim
Revises: 20260408_0001
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260409_dcim"
down_revision: Union[str, Sequence[str], None] = "20260408_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_sites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "dcim_manufacturers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "dcim_rooms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dcim_racks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("u_height", sa.Integer(), nullable=False, server_default=sa.text("42")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(["room_id"], ["dcim_rooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dcim_device_models",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("manufacturer_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("u_height", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("form_factor", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["manufacturer_id"], ["dcim_manufacturers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dcim_device_instances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_model_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("serial_number", sa.String(length=128), nullable=True),
        sa.Column("asset_tag", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(["device_model_id"], ["dcim_device_models.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dcim_rack_placements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rack_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("u_position", sa.Integer(), nullable=False),
        sa.Column("mounting", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rack_id"], ["dcim_racks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", name="uq_dcim_rack_placement_device"),
    )


def downgrade() -> None:
    op.drop_table("dcim_rack_placements")
    op.drop_table("dcim_device_instances")
    op.drop_table("dcim_device_models")
    op.drop_table("dcim_racks")
    op.drop_table("dcim_rooms")
    op.drop_table("dcim_manufacturers")
    op.drop_table("dcim_sites")
