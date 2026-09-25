import uuid

from sqlalchemy import ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.activity_type import ActivityType


class WorkoutSessionItem(Base):
    """One exercise line on a session, ordered by ``sort_order``."""

    __tablename__ = "workout_session_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("activity_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    session: Mapped["WorkoutSession"] = relationship(back_populates="items")
    activity_type: Mapped[ActivityType] = relationship()
    measurements: Mapped[list["WorkoutSessionMeasurement"]] = relationship(
        back_populates="session_item",
        cascade="all, delete-orphan",
        order_by="WorkoutSessionMeasurement.set_index",
    )

    def __repr__(self) -> str:
        return (
            f"WorkoutSessionItem(id={self.id!r}, "
            f"activity_type_id={self.activity_type_id!r})"
        )
