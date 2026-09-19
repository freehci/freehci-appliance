"""Child prefix allocate, idempotency keys, device site_id.

Revision ID: 20260512_ipam_cluster2
Revises: 20260511_ipam_gitops
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260512_ipam_cluster2"
down_revision: Union[str, Sequence[str], None] = "20260511_ipam_gitops"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dcim_device_instances") as batch_op:
        batch_op.add_column(sa.Column("site_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_dcim_device_instances_site_id",
            "dcim_sites",
            ["site_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.execute(
        sa.text(
            """
            UPDATE dcim_device_instances
            SET site_id = (
                SELECT dcim_rooms.site_id
                FROM dcim_rack_placements
                JOIN dcim_racks ON dcim_racks.id = dcim_rack_placements.rack_id
                JOIN dcim_rooms ON dcim_rooms.id = dcim_racks.room_id
                WHERE dcim_rack_placements.device_id = dcim_device_instances.id
                LIMIT 1
            )
            WHERE site_id IS NULL
            """
        ),
    )

    op.create_table(
        "ipam_idempotency_keys",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("response_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", name="uq_ipam_idempotency_key"),
    )


def downgrade() -> None:
    op.drop_table("ipam_idempotency_keys")
    with op.batch_alter_table("dcim_device_instances") as batch_op:
        batch_op.drop_constraint("fk_dcim_device_instances_site_id", type_="foreignkey")
        batch_op.drop_column("site_id")
