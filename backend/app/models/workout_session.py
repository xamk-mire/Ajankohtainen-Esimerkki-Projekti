import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User

SESSION_STATUSES = ("planned", "in_progress", "completed")


class WorkoutSession(Base):
    """One training outing: metadata plus ordered exercises.

    ``plan_id`` is optional and points at one ``WorkoutPlan``. A session cannot
    belong to two plans. Deleting the plan sets ``plan_id`` to null.
    There is no template flag and no ``workout_plan_sessions`` table.
    """

    __tablename__ = "workout_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('planned', 'in_progress', 'completed')",
            name="ck_workout_sessions_status",
        ),
        CheckConstraint(
            "intensity IS NULL OR (intensity >= 1 AND intensity <= 10)",
            name="ck_workout_sessions_intensity",
        ),
        Index(
            "ix_workout_sessions_user_id_session_at",
            "user_id",
            "session_at",
        ),
        Index(
            "ix_workout_sessions_plan_id_session_at",
            "plan_id",
            "session_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    session_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="planned",
        server_default="planned",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    intensity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workout_plans.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workout_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped[User] = relationship()
    plan: Mapped["WorkoutPlan | None"] = relationship(back_populates="sessions")
    items: Mapped[list["WorkoutSessionItem"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutSessionItem.sort_order",
    )
    source_session: Mapped["WorkoutSession | None"] = relationship(
        remote_side="WorkoutSession.id",
        foreign_keys="WorkoutSession.source_session_id",
        back_populates="cloned_sessions",
    )
    cloned_sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="source_session",
        foreign_keys="WorkoutSession.source_session_id",
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"WorkoutSession(id={self.id!r}, name={self.name!r})"
