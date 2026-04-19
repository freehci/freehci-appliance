"""DCIM device types: valgfritt Font Awesome-ikonnavn.

Revision ID: dcim_dt_fa_icon
Revises: ipam_pfx_subsvc
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "dcim_dt_fa_icon"
down_revision: Union[str, Sequence[str], None] = "ipam_pfx_subsvc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_device_types", sa.Column("fa_icon", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("dcim_device_types", "fa_icon")
