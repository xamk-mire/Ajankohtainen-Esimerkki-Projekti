import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.unit_type import UnitType


class WorkoutSessionMeasurement(Base):
    """Planned and/or actual value for one unit on a session item.

    Both value columns are nullable. There is no single ``value`` column.
    ``set_index`` is set when the activity's unit link is ``per_set``.
    """

    __tablename__ = "workout_session_measurements"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workout_session_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    unit_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("unit_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    planned_value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )
    actual_value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )
    set_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    session_item: Mapped["WorkoutSessionItem"] = relationship(
        back_populates="measurements",
    )
    unit_type: Mapped[UnitType] = relationship()

    def __repr__(self) -> str:
        return (
            f"WorkoutSessionMeasurement(id={self.id!r}, "
            f"unit_type_id={self.unit_type_id!r}, set_index={self.set_index!r})"
        )
