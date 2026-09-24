"""Allow VPN members without a site so named clients are recorded, not invented sites.

Revision ID: 20260618_ipam_vpn_client_member
Revises: 20260617_dcim_fiber_bundle
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260618_ipam_vpn_client_member"
down_revision: Union[str, Sequence[str], None] = "20260617_dcim_fiber_bundle"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("ipam_vpn_members") as batch_op:
        batch_op.alter_column("site_id", existing_type=sa.Integer(), nullable=True)
        batch_op.add_column(sa.Column("name", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("slug", sa.String(length=128), nullable=True))
        batch_op.create_unique_constraint("uq_ipam_vpn_member_slug", ["vpn_service_id", "slug"])


def downgrade() -> None:
    with op.batch_alter_table("ipam_vpn_members") as batch_op:
        batch_op.drop_constraint("uq_ipam_vpn_member_slug", type_="unique")
        batch_op.drop_column("slug")
        batch_op.drop_column("name")
        batch_op.alter_column("site_id", existing_type=sa.Integer(), nullable=False)
