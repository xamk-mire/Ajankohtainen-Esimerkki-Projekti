"""session tables: workout_sessions, items, measurements

plan_id is deferred to S3-03 (workout_plans does not exist yet).
No workout_plan_sessions table and no template flag.

Revision ID: s301_sessions
Revises: s205_initial
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "s301_sessions"
down_revision: Union[str, Sequence[str], None] = "s205_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workout_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("session_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="planned",
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("intensity", sa.Integer(), nullable=True),
        sa.Column("source_session_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('planned', 'in_progress', 'completed')",
            name="ck_workout_sessions_status",
        ),
        sa.CheckConstraint(
            "intensity IS NULL OR (intensity >= 1 AND intensity <= 10)",
            name="ck_workout_sessions_intensity",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_workout_sessions_user_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_session_id"],
            ["workout_sessions.id"],
            name="fk_workout_sessions_source_session_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_workout_sessions_user_id_session_at",
        "workout_sessions",
        ["user_id", "session_at"],
    )
    op.create_table(
        "workout_session_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("activity_type_id", sa.Uuid(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["workout_sessions.id"],
            name="fk_workout_session_items_session_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["activity_type_id"],
            ["activity_types.id"],
            name="fk_workout_session_items_activity_type_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "workout_session_measurements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_item_id", sa.Uuid(), nullable=False),
        sa.Column("unit_type_id", sa.Uuid(), nullable=False),
        sa.Column("planned_value", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("actual_value", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("set_index", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_item_id"],
            ["workout_session_items.id"],
            name="fk_workout_session_measurements_session_item_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["unit_type_id"],
            ["unit_types.id"],
            name="fk_workout_session_measurements_unit_type_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("workout_session_measurements")
    op.drop_table("workout_session_items")
    op.drop_index(
        "ix_workout_sessions_user_id_session_at",
        table_name="workout_sessions",
    )
    op.drop_table("workout_sessions")
