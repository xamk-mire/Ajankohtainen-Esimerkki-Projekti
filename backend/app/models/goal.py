import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.activity_type import ActivityType
from app.models.unit_type import UnitType
from app.models.user import User

GOAL_PERIODS = ("week", "month")


class Goal(Base):
    """Week or month target for a unit type.

    This is not a session measurement. Planned set values stay on
    ``workout_session_measurements.planned_value``.
    """

    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint(
            "period IN ('week', 'month')",
            name="ck_goals_period",
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
    unit_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("unit_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    activity_type_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("activity_types.id", ondelete="RESTRICT"),
        nullable=True,
    )
    target_value: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    period: Mapped[str] = mapped_column(String(10), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    user: Mapped[User] = relationship()
    unit_type: Mapped[UnitType] = relationship()
    activity_type: Mapped[ActivityType | None] = relationship()

    def __repr__(self) -> str:
        return (
            f"Goal(id={self.id!r}, period={self.period!r}, "
            f"target_value={self.target_value!r})"
        )
