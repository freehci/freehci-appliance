"""DCIM: 0U-modeller, SNMP sysObjectID-prefiks på modell, enhets-IP uten grensesnitt.

Revision ID: 20260430_dcim_enh
Revises: 20260429_mib_deps
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260430_dcim_enh"
down_revision: Union[str, Sequence[str], None] = "20260429_mib_deps"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_device_models",
        sa.Column("snmp_sys_object_id_prefix", sa.String(length=512), nullable=True),
    )

    op.create_table(
        "dcim_device_ip_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("ipv4_prefix_id", sa.Integer(), nullable=True),
        sa.Column("family", sa.String(length=4), nullable=False),
        sa.Column("address", sa.String(length=45), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ipv4_prefix_id"], ["ipam_ipv4_prefixes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "address", name="uq_dcim_device_ip_addr"),
    )


def downgrade() -> None:
    op.drop_table("dcim_device_ip_assignments")
    op.drop_column("dcim_device_models", "snmp_sys_object_id_prefix")
