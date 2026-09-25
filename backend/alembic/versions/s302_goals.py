"""period goals table

Revision ID: s302_goals
Revises: s301_sessions
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "s302_goals"
down_revision: Union[str, Sequence[str], None] = "s301_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "goals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("unit_type_id", sa.Uuid(), nullable=False),
        sa.Column("activity_type_id", sa.Uuid(), nullable=True),
        sa.Column("target_value", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("period", sa.String(length=10), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "period IN ('week', 'month')",
            name="ck_goals_period",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_goals_user_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["unit_type_id"],
            ["unit_types.id"],
            name="fk_goals_unit_type_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["activity_type_id"],
            ["activity_types.id"],
            name="fk_goals_activity_type_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("goals")
