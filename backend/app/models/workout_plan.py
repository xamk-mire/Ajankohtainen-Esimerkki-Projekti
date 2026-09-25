import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Uuid, func, nulls_last
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User


def _sessions_by_session_at():
    from app.models.workout_session import WorkoutSession

    return nulls_last(WorkoutSession.session_at.asc())


class WorkoutPlan(Base):
    """Named program. Sessions belong through ``workout_sessions.plan_id``.

    One session has at most one plan: ``plan_id`` is a single nullable column,
    not a ``workout_plan_sessions`` junction. ``start_date`` and
    ``length_weeks`` are metadata only.
    """

    __tablename__ = "workout_plans"

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
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    length_weeks: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
    sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="plan",
        order_by=lambda: _sessions_by_session_at(),
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"WorkoutPlan(id={self.id!r}, name={self.name!r})"
