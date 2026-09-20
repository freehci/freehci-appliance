"""Provider, circuit layer, VPN/tunnel. No circuit_type backfill.

Revision ID: 20260522_ipam_circuits
Revises: 20260521_ipam_scope
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260522_ipam_circuits"
down_revision: Union[str, Sequence[str], None] = "20260521_ipam_scope"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_providers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("asn", sa.Integer(), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_ipam_provider_slug"),
    )
    op.create_table(
        "ipam_provider_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("account_number", sa.String(length=128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["ipam_providers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_id", "slug", name="uq_ipam_provider_account_slug"),
    )

    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.add_column(sa.Column("layer", sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column("provider_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("provider_account_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_ipam_circuit_provider_id",
            "ipam_providers",
            ["provider_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_ipam_circuit_provider_account_id",
            "ipam_provider_accounts",
            ["provider_account_id"],
            ["id"],
            ondelete="SET NULL",
        )

    with op.batch_alter_table("ipam_circuit_terminations") as batch_op:
        batch_op.add_column(sa.Column("device_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_ipam_circuit_term_device_id",
            "dcim_device_instances",
            ["device_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_table(
        "ipam_vpn_services",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("tenant_scope", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("vpn_type", sa.String(length=32), nullable=False),
        sa.Column("source_circuit_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_circuit_id"], ["ipam_circuits.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_scope", "slug", name="uq_ipam_vpn_service_scope_slug"),
    )
    op.create_table(
        "ipam_tunnel_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("vpn_type", sa.String(length=32), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_ipam_tunnel_profile_slug"),
    )
    op.create_table(
        "ipam_tunnels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vpn_service_id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vpn_service_id"], ["ipam_vpn_services.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["ipam_tunnel_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vpn_service_id", "slug", name="uq_ipam_tunnel_vpn_slug"),
    )
    op.create_table(
        "ipam_tunnel_endpoints",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tunnel_id", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.String(length=1), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("interface_id", sa.Integer(), nullable=True),
        sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["tunnel_id"], ["ipam_tunnels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tunnel_id", "endpoint", name="uq_ipam_tunnel_endpoint"),
    )
    op.create_table(
        "ipam_tunnel_peers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tunnel_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("public_key_ref", sa.String(length=255), nullable=True),
        sa.Column("allowed_ips", sa.JSON(), nullable=True),
        sa.Column("endpoint_host", sa.String(length=255), nullable=True),
        sa.Column("endpoint_port", sa.Integer(), nullable=True),
        sa.Column("persistent_keepalive", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("interface_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tunnel_id"], ["ipam_tunnels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ipam_tunnel_peers")
    op.drop_table("ipam_tunnel_endpoints")
    op.drop_table("ipam_tunnels")
    op.drop_table("ipam_tunnel_profiles")
    op.drop_table("ipam_vpn_services")
    with op.batch_alter_table("ipam_circuit_terminations") as batch_op:
        batch_op.drop_constraint("fk_ipam_circuit_term_device_id", type_="foreignkey")
        batch_op.drop_column("device_id")
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.drop_constraint("fk_ipam_circuit_provider_account_id", type_="foreignkey")
        batch_op.drop_constraint("fk_ipam_circuit_provider_id", type_="foreignkey")
        batch_op.drop_column("provider_account_id")
        batch_op.drop_column("provider_id")
        batch_op.drop_column("layer")
    op.drop_table("ipam_provider_accounts")
    op.drop_table("ipam_providers")
