"""Manufacturer logo on disk (not in DB).

Revision ID: 20260412_mfr_logo_file
Revises: 20260411_mfr_logo

Merk: Eksisterende logo-bytes i databasen slettes; last opp logo på nytt etter migrering.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260412_mfr_logo_file"
down_revision: Union[str, Sequence[str], None] = "20260411_mfr_logo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_manufacturers",
        sa.Column("logo_relpath", sa.String(length=512), nullable=True),
    )
    op.drop_column("dcim_manufacturers", "logo_data")


def downgrade() -> None:
    op.add_column(
        "dcim_manufacturers",
        sa.Column("logo_data", sa.LargeBinary(), nullable=True),
    )
    op.drop_column("dcim_manufacturers", "logo_relpath")
