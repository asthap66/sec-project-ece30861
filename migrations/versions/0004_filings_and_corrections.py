"""Add filings and decision corrections (Phase 5).

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-21

Applies to an existing Phase 4 database without touching its rows:

- filings: one row per incident (the unique incident_id makes a second filing
  impossible even if two requests race). Timeliness and businessDaysLate are
  stored as classified when the filing was recorded, so the record never
  changes if the holiday list is updated later (append-only, REQ-07).
- decisions.corrects_decision_id: a correction is a new decision row that
  points at the one it replaces. The composite key keeps it inside the same
  incident, and the unique constraint means a decision is superseded at most
  once, so the history is a single chain. Existing Phase 4 decisions are
  original decisions (NULL).
- recorded_at/created_at defaults change from now() to clock_timestamp().
  now() is the start of the transaction, and a decision or filing transaction
  starts by waiting for the incident lock, so with now() a write that waited
  could get an earlier timestamp than the write it waited behind and appear
  out of order in the timeline. clock_timestamp() is the time of the insert.
  Existing rows keep their values.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RECORDING_COLUMNS = (
    ("incidents", "created_at"),
    ("evidence", "recorded_at"),
    ("decisions", "recorded_at"),
)


def upgrade() -> None:
    op.add_column("decisions", sa.Column("corrects_decision_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "decisions_corrects_fkey",
        "decisions",
        "decisions",
        ["corrects_decision_id", "incident_id"],
        ["id", "incident_id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "decisions_corrects_decision_id_key", "decisions", ["corrects_decision_id"]
    )
    op.create_check_constraint(
        "corrects_other_decision",
        "decisions",
        "corrects_decision_id IS NULL OR corrects_decision_id <> id",
    )

    op.create_table(
        "filings",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "public_id",
            sa.String(32),
            sa.Computed(
                "'FIL-' || CASE WHEN id < 1000 THEN lpad(id::text, 3, '0') ELSE id::text END",
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
        sa.Column("filed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accession_number", sa.Text(), nullable=False),
        sa.Column("timeliness", sa.String(16), nullable=False),
        sa.Column("business_days_late", sa.Integer(), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("clock_timestamp()"),
            nullable=False,
        ),
        sa.CheckConstraint("timeliness IN ('ON_TIME', 'LATE')", name="timeliness_valid"),
        sa.CheckConstraint("business_days_late >= 0", name="business_days_late_nonnegative"),
        sa.CheckConstraint("length(btrim(accession_number)) > 0", name="accession_not_blank"),
        sa.UniqueConstraint("public_id", name="filings_public_id_key"),
        sa.UniqueConstraint("incident_id", name="filings_incident_id_key"),
    )

    for table, column in RECORDING_COLUMNS:
        op.alter_column(table, column, server_default=sa.text("clock_timestamp()"))


def downgrade() -> None:
    for table, column in RECORDING_COLUMNS:
        op.alter_column(table, column, server_default=sa.func.now())
    op.drop_table("filings")
    op.drop_constraint("corrects_other_decision", "decisions", type_="check")
    op.drop_constraint("decisions_corrects_decision_id_key", "decisions", type_="unique")
    op.drop_constraint("decisions_corrects_fkey", "decisions", type_="foreignkey")
    op.drop_column("decisions", "corrects_decision_id")
