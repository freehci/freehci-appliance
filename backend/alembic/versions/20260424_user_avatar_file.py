"""user_avatar_file

Revision ID: 20260424_uava
Revises: 20260434_ipam_vrf
Create Date: 2026-04-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260424_uava"
down_revision: Union[str, Sequence[str], None] = "20260434_ipam_prefix_vrf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_file", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_file")

