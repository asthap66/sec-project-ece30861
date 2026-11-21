"""Create incidents and evidence (Phase 3).

Revision ID: 0001
Revises:
Create Date: 2026-10-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _public_id(prefix: str) -> sa.Computed:
    return sa.Computed(
        f"'{prefix}-' || CASE WHEN id < 1000 THEN lpad(id::text, 3, '0') ELSE id::text END",
        persisted=True,
    )


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("public_id", sa.String(32), _public_id("INC"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(5000), nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reporter_name", sa.String(500), nullable=False),
        sa.Column("status", sa.String(32), server_default="OPEN", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "status IN ('OPEN', 'NOT_MATERIAL', 'MATERIAL_PENDING_FILING', 'FILED')",
            name="status_valid",
        ),
        sa.UniqueConstraint("public_id", name="incidents_public_id_key"),
    )
    op.create_table(
        "evidence",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("public_id", sa.String(32), _public_id("EVD"), nullable=False),
        sa.Column(
            "incident_id",
            sa.BigInteger(),
            sa.ForeignKey("incidents.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("source", sa.String(500), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "category IN ('TECHNICAL', 'BUSINESS_IMPACT', 'LEGAL', 'OTHER')",
            name="category_valid",
        ),
        sa.UniqueConstraint("public_id", name="evidence_public_id_key"),
    )
    op.create_index("ix_evidence_incident_id", "evidence", ["incident_id"])


def downgrade() -> None:
    op.drop_index("ix_evidence_incident_id", table_name="evidence")
    op.drop_table("evidence")
    op.drop_table("incidents")
