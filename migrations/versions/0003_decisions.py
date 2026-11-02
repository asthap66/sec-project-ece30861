"""Add human materiality decisions and their evidence links (Phase 4).

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-02

Applies to an existing Phase 3 database without touching its rows. Status
and deadline are derived on read, so no column stores them.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Target for decision_evidence's composite key: (evidence, its incident).
    op.create_unique_constraint("evidence_id_incident_key", "evidence", ["id", "incident_id"])
    op.create_table(
        "decisions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "public_id",
            sa.String(32),
            sa.Computed(
                "'DEC-' || CASE WHEN id < 1000 THEN lpad(id::text, 3, '0') ELSE id::text END",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "incident_id",
            sa.BigInteger(),
            sa.ForeignKey("incidents.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("determined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_by", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column(
            "recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("decision IN ('MATERIAL', 'NOT_MATERIAL')", name="decision_valid"),
        sa.UniqueConstraint("public_id", name="decisions_public_id_key"),
        sa.UniqueConstraint("id", "incident_id", name="decisions_id_incident_key"),
    )
    op.create_index("ix_decisions_incident_id", "decisions", ["incident_id"])
    op.create_table(
        "decision_evidence",
        sa.Column("decision_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("incident_id", sa.BigInteger(), nullable=False),
        sa.Column("evidence_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("decision_id", "position"),
        sa.ForeignKeyConstraint(
            ["decision_id", "incident_id"],
            ["decisions.id", "decisions.incident_id"],
            ondelete="RESTRICT",
            name="decision_evidence_decision_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id", "incident_id"],
            ["evidence.id", "evidence.incident_id"],
            ondelete="RESTRICT",
            name="decision_evidence_evidence_fkey",
        ),
        sa.CheckConstraint("position >= 0", name="position_nonnegative"),
    )
    op.create_index("ix_decision_evidence_evidence_id", "decision_evidence", ["evidence_id"])


def downgrade() -> None:
    op.drop_index("ix_decision_evidence_evidence_id", table_name="decision_evidence")
    op.drop_table("decision_evidence")
    op.drop_index("ix_decisions_incident_id", table_name="decisions")
    op.drop_table("decisions")
    op.drop_constraint("evidence_id_incident_key", "evidence", type_="unique")
