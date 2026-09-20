"""DCIM building, wing and floor hierarchy.

Revision ID: 20260520_dcim_bldg_floor
Revises: 20260519_federation
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260520_dcim_bldg_floor"
down_revision: Union[str, Sequence[str], None] = "20260519_federation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_buildings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "slug", name="uq_dcim_building_site_slug"),
    )
    op.create_table(
        "dcim_wings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["building_id"], ["dcim_buildings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("building_id", "slug", name="uq_dcim_wing_building_slug"),
    )
    op.create_table(
        "dcim_floors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.Column("wing_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["building_id"], ["dcim_buildings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["wing_id"], ["dcim_wings.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("building_id", "slug", name="uq_dcim_floor_building_slug"),
    )
    op.add_column("dcim_rooms", sa.Column("building_id", sa.Integer(), nullable=True))
    op.add_column("dcim_rooms", sa.Column("wing_id", sa.Integer(), nullable=True))
    op.add_column("dcim_rooms", sa.Column("floor_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_dcim_rooms_building_id",
        "dcim_rooms",
        "dcim_buildings",
        ["building_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dcim_rooms_wing_id",
        "dcim_rooms",
        "dcim_wings",
        ["wing_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dcim_rooms_floor_id",
        "dcim_rooms",
        "dcim_floors",
        ["floor_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_dcim_rooms_floor_id", "dcim_rooms", type_="foreignkey")
    op.drop_constraint("fk_dcim_rooms_wing_id", "dcim_rooms", type_="foreignkey")
    op.drop_constraint("fk_dcim_rooms_building_id", "dcim_rooms", type_="foreignkey")
    op.drop_column("dcim_rooms", "floor_id")
    op.drop_column("dcim_rooms", "wing_id")
    op.drop_column("dcim_rooms", "building_id")
    op.drop_table("dcim_floors")
    op.drop_table("dcim_wings")
    op.drop_table("dcim_buildings")
