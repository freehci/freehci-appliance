"""Device model product image (non rack front/back).

Revision ID: 20260425_dm_product
Revises: 20260424_admin_acc
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260425_dm_product"
down_revision: Union[str, Sequence[str], None] = "20260424_admin_acc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_device_models", sa.Column("image_product_url", sa.String(length=1024), nullable=True))
    op.add_column("dcim_device_models", sa.Column("image_product_relpath", sa.String(length=512), nullable=True))
    op.add_column("dcim_device_models", sa.Column("image_product_mime_type", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("dcim_device_models", "image_product_mime_type")
    op.drop_column("dcim_device_models", "image_product_relpath")
    op.drop_column("dcim_device_models", "image_product_url")
