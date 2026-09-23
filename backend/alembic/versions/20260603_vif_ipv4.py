"""IPv4-tildeling på virtuelt grensesnitt uten oppfunnet MAC.

Revision ID: 20260603_vif_ipv4
Revises: 20260602_dcim_device_role
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260603_vif_ipv4"
down_revision: Union[str, Sequence[str], None] = "20260602_dcim_device_role"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("ipam_ipv4_addresses") as batch:
        batch.add_column(sa.Column("virtual_interface_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_ipam_ipv4_virtual_interface",
            "platform_virtual_interfaces",
            ["virtual_interface_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("ipam_ipv4_addresses") as batch:
        batch.drop_constraint("fk_ipam_ipv4_virtual_interface", type_="foreignkey")
        batch.drop_column("virtual_interface_id")
