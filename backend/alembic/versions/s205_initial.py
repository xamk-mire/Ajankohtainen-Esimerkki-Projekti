"""initial schema: users, activity types, unit types, links

Revision ID: s205_initial
Revises:
Create Date: 2026-09-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "s205_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "unit_types",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("unit_label", sa.String(length=20), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_unit_types_slug"),
    )
    op.create_table(
        "activity_types",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_activity_types_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "slug",
            name="uq_activity_types_user_id_slug",
        ),
    )
    op.create_index(
        "uq_activity_types_system_slug",
        "activity_types",
        ["slug"],
        unique=True,
        postgresql_where=sa.text("user_id IS NULL"),
    )
    op.create_table(
        "activity_type_unit_types",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("activity_type_id", sa.Uuid(), nullable=False),
        sa.Column("unit_type_id", sa.Uuid(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("per_set", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_type_id"],
            ["activity_types.id"],
            name="fk_activity_type_unit_types_activity_type_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["unit_type_id"],
            ["unit_types.id"],
            name="fk_activity_type_unit_types_unit_type_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "activity_type_id",
            "unit_type_id",
            name="uq_activity_type_unit_types_pair",
        ),
    )


def downgrade() -> None:
    op.drop_table("activity_type_unit_types")
    op.drop_index(
        "uq_activity_types_system_slug",
        table_name="activity_types",
        postgresql_where=sa.text("user_id IS NULL"),
    )
    op.drop_table("activity_types")
    op.drop_table("unit_types")
    op.drop_table("users")
