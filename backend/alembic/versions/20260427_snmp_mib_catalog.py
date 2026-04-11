"""SNMP MIB metadata, IANA enterprises, manufacturer PEN.

Revision ID: 20260427_snmp_mib
Revises: 20260426_rack_meta
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260427_snmp_mib"
down_revision: Union[str, Sequence[str], None] = "20260426_rack_meta"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_manufacturers",
        sa.Column("iana_enterprise_number", sa.Integer(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_dcim_manufacturers_iana_enterprise_number",
        "dcim_manufacturers",
        ["iana_enterprise_number"],
    )

    op.create_table(
        "snmp_iana_enterprises",
        sa.Column("pen", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("organization", sa.String(length=1024), nullable=False),
        sa.PrimaryKeyConstraint("pen"),
    )

    op.create_table(
        "snmp_mib_file_meta",
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("module_name", sa.String(length=255), nullable=True),
        sa.Column("enterprise_number", sa.Integer(), nullable=True),
        sa.Column("compile_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("compile_message", sa.Text(), nullable=True),
        sa.Column("compiled_module_name", sa.String(length=255), nullable=True),
        sa.Column("compiled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("filename"),
    )


def downgrade() -> None:
    op.drop_table("snmp_mib_file_meta")
    op.drop_table("snmp_iana_enterprises")
    op.drop_constraint("uq_dcim_manufacturers_iana_enterprise_number", "dcim_manufacturers", type_="unique")
    op.drop_column("dcim_manufacturers", "iana_enterprise_number")
