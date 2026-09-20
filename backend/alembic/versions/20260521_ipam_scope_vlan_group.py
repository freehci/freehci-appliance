"""VLAN groups, VID unique in group, prefix role vs status.

Revision ID: 20260521_ipam_scope
Revises: 20260520_dcim_bldg_floor
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260521_ipam_scope"
down_revision: Union[str, Sequence[str], None] = "20260520_dcim_bldg_floor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_vlan_groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "slug", name="uq_ipam_vlan_group_site_slug"),
        sa.UniqueConstraint("site_id", "name", name="uq_ipam_vlan_group_site_name"),
    )

    conn = op.get_bind()
    site_ids = [int(r[0]) for r in conn.execute(sa.text("SELECT DISTINCT site_id FROM ipam_vlans")).fetchall()]
    for site_id in site_ids:
        conn.execute(
            sa.text(
                "INSERT INTO ipam_vlan_groups (site_id, name, slug) VALUES (:site_id, 'Default', 'default')",
            ),
            {"site_id": site_id},
        )

    with op.batch_alter_table("ipam_vlans") as batch_op:
        batch_op.add_column(sa.Column("vlan_group_id", sa.Integer(), nullable=True))

    conn.execute(
        sa.text(
            """
            UPDATE ipam_vlans
            SET vlan_group_id = (
                SELECT g.id FROM ipam_vlan_groups g
                WHERE g.site_id = ipam_vlans.site_id AND g.slug = 'default'
            )
            """,
        ),
    )

    with op.batch_alter_table("ipam_vlans") as batch_op:
        batch_op.drop_constraint("uq_ipam_vlan_site_vid", type_="unique")
        batch_op.alter_column("vlan_group_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_ipam_vlan_group_id",
            "ipam_vlan_groups",
            ["vlan_group_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_unique_constraint("uq_ipam_vlan_group_vid", ["vlan_group_id", "vid"])

    for table in ("ipam_ipv4_prefixes", "ipam_ipv6_prefixes"):
        conn.execute(sa.text(f"UPDATE {table} SET role = 'access' WHERE role = 'active'"))
        conn.execute(sa.text(f"UPDATE {table} SET role = 'container' WHERE role = 'reserved'"))


def downgrade() -> None:
    conn = op.get_bind()
    for table in ("ipam_ipv4_prefixes", "ipam_ipv6_prefixes"):
        conn.execute(sa.text(f"UPDATE {table} SET role = 'active' WHERE role = 'access'"))

    with op.batch_alter_table("ipam_vlans") as batch_op:
        batch_op.drop_constraint("uq_ipam_vlan_group_vid", type_="unique")
        batch_op.drop_constraint("fk_ipam_vlan_group_id", type_="foreignkey")
        batch_op.drop_column("vlan_group_id")
        batch_op.create_unique_constraint("uq_ipam_vlan_site_vid", ["site_id", "vid"])

    op.drop_table("ipam_vlan_groups")
