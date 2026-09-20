"""Site dashboard banner image.

Revision ID: 20260518_site_banner
Revises: 20260517_rack_elev
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260518_site_banner"
down_revision: Union[str, Sequence[str], None] = "20260517_rack_elev"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_sites", sa.Column("banner_relpath", sa.String(length=512), nullable=True))
    op.add_column("dcim_sites", sa.Column("banner_mime_type", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("dcim_sites", "banner_mime_type")
    op.drop_column("dcim_sites", "banner_relpath")
