"""Device model front/back images on disk (optional; URLs unchanged).

Revision ID: 20260413_dm_images
Revises: 20260412_mfr_logo_file
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260413_dm_images"
down_revision: Union[str, Sequence[str], None] = "20260412_mfr_logo_file"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_device_models",
        sa.Column("image_front_relpath", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "dcim_device_models",
        sa.Column("image_front_mime_type", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "dcim_device_models",
        sa.Column("image_back_relpath", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "dcim_device_models",
        sa.Column("image_back_mime_type", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dcim_device_models", "image_back_mime_type")
    op.drop_column("dcim_device_models", "image_back_relpath")
    op.drop_column("dcim_device_models", "image_front_mime_type")
    op.drop_column("dcim_device_models", "image_front_relpath")
