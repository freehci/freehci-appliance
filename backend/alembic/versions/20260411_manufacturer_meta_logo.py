"""Manufacturer description, website, logo blob.

Revision ID: 20260411_mfr_logo
Revises: 20260410_model_img
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260411_mfr_logo"
down_revision: Union[str, Sequence[str], None] = "20260410_model_img"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_manufacturers", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "dcim_manufacturers",
        sa.Column("website_url", sa.String(length=1024), nullable=True),
    )
    op.add_column(
        "dcim_manufacturers",
        sa.Column("logo_mime_type", sa.String(length=64), nullable=True),
    )
    op.add_column("dcim_manufacturers", sa.Column("logo_data", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("dcim_manufacturers", "logo_data")
    op.drop_column("dcim_manufacturers", "logo_mime_type")
    op.drop_column("dcim_manufacturers", "website_url")
    op.drop_column("dcim_manufacturers", "description")
