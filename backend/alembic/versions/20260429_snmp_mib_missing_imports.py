"""SNMP MIB: missing IMPORTS detection (JSON cache).

Revision ID: 20260429_mib_deps
Revises: 20260428_netscan
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260429_mib_deps"
down_revision: Union[str, Sequence[str], None] = "20260428_netscan"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "snmp_mib_file_meta",
        sa.Column(
            "missing_import_modules_json",
            sa.Text(),
            nullable=False,
            server_default="[]",
        ),
    )


def downgrade() -> None:
    op.drop_column("snmp_mib_file_meta", "missing_import_modules_json")
