"""Device model template images (front/back URLs).

Revision ID: 20260410_model_img
Revises: 20260409_dcim
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260410_model_img"
down_revision: Union[str, Sequence[str], None] = "20260409_dcim"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_device_models",
        sa.Column("image_front_url", sa.String(length=1024), nullable=True),
    )
    op.add_column(
        "dcim_device_models",
        sa.Column("image_back_url", sa.String(length=1024), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dcim_device_models", "image_back_url")
    op.drop_column("dcim_device_models", "image_front_url")
