"""Record circuit service type, medium and operational status without guessing.

Revision ID: 20260616_ipam_circuit_attributes
Revises: 20260615_ipam_vpn_member
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260616_ipam_circuit_attributes"
down_revision: Union[str, Sequence[str], None] = "20260615_ipam_vpn_member"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ipam_circuits", sa.Column("service_type", sa.String(length=32), nullable=True))
    op.add_column("ipam_circuits", sa.Column("medium", sa.String(length=32), nullable=True))
    op.add_column("ipam_circuits", sa.Column("operational_status", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("ipam_circuits", "operational_status")
    op.drop_column("ipam_circuits", "medium")
    op.drop_column("ipam_circuits", "service_type")
