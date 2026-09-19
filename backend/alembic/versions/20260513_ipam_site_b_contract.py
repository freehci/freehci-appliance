"""Overlap policy, IPv6, circuits without tenant, audit, token scopes.

Revision ID: 20260513_ipam_site_b
Revises: 20260512_ipam_cluster2
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260513_ipam_site_b"
down_revision: Union[str, Sequence[str], None] = "20260512_ipam_cluster2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.add_column(sa.Column("overlap_policy", sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column("dual_stack_group_id", sa.Integer(), nullable=True))

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE ipam_ipv4_prefixes SET overlap_policy = CASE "
            "WHEN role IN ('overlay-pod', 'overlay-service', 'lb-pool', 'p2p') THEN 'global-unique' "
            "ELSE 'site-local' END"
        ),
    )
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.alter_column("overlap_policy", existing_type=sa.String(length=16), nullable=False)

    with op.batch_alter_table("ipam_ipv4_addresses") as batch_op:
        batch_op.add_column(sa.Column("owner_type", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("owner_ref", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.add_column(sa.Column("tenant_scope", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("a_site_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("z_site_id", sa.Integer(), nullable=True))

    conn.execute(sa.text("UPDATE ipam_circuits SET tenant_scope = COALESCE(tenant_id, 0)"))

    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.alter_column("tenant_scope", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("tenant_id", existing_type=sa.Integer(), nullable=True)
        batch_op.drop_constraint("uq_ipam_circuit_tenant_number", type_="unique")
        batch_op.create_unique_constraint("uq_ipam_circuit_tenant_scope_number", ["tenant_scope", "circuit_number"])
        batch_op.create_foreign_key("fk_ipam_circuits_a_site", "dcim_sites", ["a_site_id"], ["id"], ondelete="SET NULL")
        batch_op.create_foreign_key("fk_ipam_circuits_z_site", "dcim_sites", ["z_site_id"], ["id"], ondelete="SET NULL")

    with op.batch_alter_table("ipam_circuit_terminations") as batch_op:
        batch_op.add_column(sa.Column("site_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_ipam_circuit_term_site",
            "dcim_sites",
            ["site_id"],
            ["id"],
            ondelete="SET NULL",
        )

    with op.batch_alter_table("api_tokens") as batch_op:
        batch_op.add_column(sa.Column("scopes", sa.JSON(), nullable=True))

    op.create_table(
        "ipam_ipv6_prefixes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("vlan_id", sa.Integer(), nullable=True),
        sa.Column("vrf_id", sa.Integer(), nullable=True),
        sa.Column("vrf_scope", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("overlap_policy", sa.String(length=16), nullable=False),
        sa.Column("dual_stack_group_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cidr", sa.String(length=64), nullable=False),
        sa.Column("subnet_services", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vlan_id"], ["ipam_vlans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vrf_id"], ["ipam_vrfs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "vrf_scope", "cidr", name="uq_ipam_ipv6_site_vrf_cidr"),
        sa.UniqueConstraint("site_id", "slug", name="uq_ipam_ipv6_site_slug"),
    )
    op.create_table(
        "ipam_ipv6_addresses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("ipv6_prefix_id", sa.Integer(), nullable=True),
        sa.Column("address", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("fqdn", sa.String(length=255), nullable=True),
        sa.Column("dns_name", sa.String(length=255), nullable=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("owner_type", sa.String(length=32), nullable=True),
        sa.Column("owner_ref", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("mac_address", sa.String(length=32), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("interface_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ipv6_prefix_id"], ["ipam_ipv6_prefixes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "address", name="uq_ipam_ipv6_addr_site_address"),
    )
    op.create_table(
        "ipam_audit_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor_type", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("actor_name", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("resource_type", sa.String(length=32), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ipam_audit_events")
    op.drop_table("ipam_ipv6_addresses")
    op.drop_table("ipam_ipv6_prefixes")
    with op.batch_alter_table("api_tokens") as batch_op:
        batch_op.drop_column("scopes")
    with op.batch_alter_table("ipam_circuit_terminations") as batch_op:
        batch_op.drop_constraint("fk_ipam_circuit_term_site", type_="foreignkey")
        batch_op.drop_column("site_id")
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.drop_constraint("fk_ipam_circuits_a_site", type_="foreignkey")
        batch_op.drop_constraint("fk_ipam_circuits_z_site", type_="foreignkey")
        batch_op.drop_constraint("uq_ipam_circuit_tenant_scope_number", type_="unique")
        batch_op.create_unique_constraint("uq_ipam_circuit_tenant_number", ["tenant_id", "circuit_number"])
        batch_op.drop_column("z_site_id")
        batch_op.drop_column("a_site_id")
        batch_op.drop_column("tenant_scope")
    with op.batch_alter_table("ipam_ipv4_addresses") as batch_op:
        batch_op.drop_column("expires_at")
        batch_op.drop_column("owner_ref")
        batch_op.drop_column("owner_type")
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.drop_column("dual_stack_group_id")
        batch_op.drop_column("overlap_policy")
