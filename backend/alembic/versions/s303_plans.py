"""workout plans and session plan_id

One session references at most one plan. No workout_plan_sessions table.

Revision ID: s303_plans
Revises: s302_goals
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "s303_plans"
down_revision: Union[str, Sequence[str], None] = "s302_goals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workout_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("length_weeks", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_workout_plans_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "workout_sessions",
        sa.Column("plan_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_workout_sessions_plan_id",
        "workout_sessions",
        "workout_plans",
        ["plan_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_workout_sessions_plan_id_session_at",
        "workout_sessions",
        ["plan_id", "session_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_workout_sessions_plan_id_session_at",
        table_name="workout_sessions",
    )
    op.drop_constraint(
        "fk_workout_sessions_plan_id",
        "workout_sessions",
        type_="foreignkey",
    )
    op.drop_column("workout_sessions", "plan_id")
    op.drop_table("workout_plans")
