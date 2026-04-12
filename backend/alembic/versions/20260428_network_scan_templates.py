"""Network scan templates, jobs, host JSON results, DCIM discovery queue.

Revision ID: 20260428_netscan
Revises: 20260427_snmp_mib
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260428_netscan"
down_revision: Union[str, Sequence[str], None] = "20260427_snmp_mib"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "network_scan_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("default_config", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_network_scan_template_slug"),
    )
    op.create_table(
        "network_scan_prefix_bindings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("ipv4_prefix_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["ipv4_prefix_id"], ["ipam_ipv4_prefixes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["network_scan_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("template_id", "ipv4_prefix_id", name="uq_netscan_bind_template_prefix"),
    )
    op.create_table(
        "network_scan_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("ipv4_prefix_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("cidr", sa.String(length=32), nullable=False),
        sa.Column("parent_job_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("options_json", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("hosts_scanned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hosts_matched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["ipv4_prefix_id"], ["ipam_ipv4_prefixes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_job_id"], ["network_scan_jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["network_scan_templates.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "network_scan_host_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(length=45), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["network_scan_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", "address", name="uq_netscan_host_job_addr"),
    )
    op.create_table(
        "network_scan_discoveries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(length=45), nullable=False),
        sa.Column("name_candidates_json", sa.JSON(), nullable=False),
        sa.Column("chosen_name_source", sa.String(length=32), nullable=True),
        sa.Column("chosen_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("dcim_device_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dcim_device_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_id"], ["network_scan_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("network_scan_discoveries")
    op.drop_table("network_scan_host_results")
    op.drop_table("network_scan_jobs")
    op.drop_table("network_scan_prefix_bindings")
    op.drop_table("network_scan_templates")
