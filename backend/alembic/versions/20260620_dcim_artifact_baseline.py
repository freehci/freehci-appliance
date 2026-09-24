"""Record firmware baselines and BIOS profiles without flashing or scoring compliance.

Revision ID: 20260620_dcim_artifact_baseline
Revises: 20260619_ipam_circuit_term_kind
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260620_dcim_artifact_baseline"
down_revision: Union[str, Sequence[str], None] = "20260619_ipam_circuit_term_kind"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_device_artifact_baselines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_dcim_device_artifact_baseline_slug"),
    )
    op.create_table(
        "dcim_device_artifact_baseline_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("baseline_id", sa.Integer(), nullable=False),
        sa.Column("artifact_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["baseline_id"], ["dcim_device_artifact_baselines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["artifact_id"], ["dcim_device_artifacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("baseline_id", "artifact_id", name="uq_dcim_device_artifact_baseline_member"),
    )


def downgrade() -> None:
    op.drop_table("dcim_device_artifact_baseline_members")
    op.drop_table("dcim_device_artifact_baselines")
