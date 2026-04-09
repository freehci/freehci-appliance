"""Device interface parent (subinterfaces / logical units).

Revision ID: 20260422_iface_parent
Revises: 20260421_ipam_ipv4_addr
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260422_iface_parent"
down_revision: Union[str, Sequence[str], None] = "20260421_ipam_ipv4_addr"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_device_interfaces",
        sa.Column("parent_interface_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_dcim_iface_parent_iface",
        "dcim_device_interfaces",
        "dcim_device_interfaces",
        ["parent_interface_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_dcim_device_interfaces_parent_interface_id",
        "dcim_device_interfaces",
        ["parent_interface_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_dcim_device_interfaces_parent_interface_id", table_name="dcim_device_interfaces")
    op.drop_constraint("fk_dcim_iface_parent_iface", "dcim_device_interfaces", type_="foreignkey")
    op.drop_column("dcim_device_interfaces", "parent_interface_id")
