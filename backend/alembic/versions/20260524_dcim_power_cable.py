"""Power panels, electrical circuits, feeds, device ports and cables.

Revision ID: 20260524_dcim_power
Revises: 20260523_ipam_as_bgp
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260524_dcim_power"
down_revision: Union[str, Sequence[str], None] = "20260523_ipam_as_bgp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_power_panels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["room_id"], ["dcim_rooms.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "slug", name="uq_dcim_power_panel_site_slug"),
    )
    op.create_table(
        "dcim_power_circuits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("panel_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("breaker_label", sa.String(length=64), nullable=True),
        sa.Column("rating_amps", sa.Integer(), nullable=True),
        sa.Column("voltage", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["panel_id"], ["dcim_power_panels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("panel_id", "name", name="uq_dcim_power_circuit_panel_name"),
    )
    op.create_table(
        "dcim_power_feeds",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("circuit_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("rack_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("supply", sa.String(length=8), nullable=True),
        sa.Column("phase", sa.String(length=16), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["circuit_id"], ["dcim_power_circuits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rack_id"], ["dcim_racks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("circuit_id", "slug", name="uq_dcim_power_feed_circuit_slug"),
    )
    op.create_table(
        "dcim_device_ports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("label", sa.String(length=128), nullable=True),
        sa.Column("connector", sa.String(length=64), nullable=True),
        sa.Column("rear_port_id", sa.Integer(), nullable=True),
        sa.Column("power_port_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rear_port_id"], ["dcim_device_ports.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["power_port_id"], ["dcim_device_ports.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "kind", "name", name="uq_dcim_device_port_kind_name"),
    )
    op.create_table(
        "dcim_cables",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("cable_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="connected"),
        sa.Column("color", sa.String(length=32), nullable=True),
        sa.Column("length_m", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "slug", name="uq_dcim_cable_site_slug"),
    )
    op.create_table(
        "dcim_cable_terminations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cable_id", sa.Integer(), nullable=False),
        sa.Column("end", sa.String(length=1), nullable=False),
        sa.Column("object_type", sa.String(length=32), nullable=False),
        sa.Column("object_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["cable_id"], ["dcim_cables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cable_id", "end", name="uq_dcim_cable_term_end"),
        sa.UniqueConstraint("object_type", "object_id", name="uq_dcim_cable_term_object"),
    )


def downgrade() -> None:
    op.drop_table("dcim_cable_terminations")
    op.drop_table("dcim_cables")
    op.drop_table("dcim_device_ports")
    op.drop_table("dcim_power_feeds")
    op.drop_table("dcim_power_circuits")
    op.drop_table("dcim_power_panels")
