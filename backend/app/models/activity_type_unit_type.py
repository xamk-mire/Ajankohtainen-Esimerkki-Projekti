import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.activity_type import ActivityType
from app.models.unit_type import UnitType


class ActivityTypeUnitType(Base):
    """Association: which measurement units an activity accepts."""

    __tablename__ = "activity_type_unit_types"
    __table_args__ = (
        UniqueConstraint(
            "activity_type_id",
            "unit_type_id",
            name="uq_activity_type_unit_types_pair",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    activity_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("activity_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    unit_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("unit_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    per_set: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    activity_type: Mapped[ActivityType] = relationship(back_populates="unit_links")
    unit_type: Mapped[UnitType] = relationship(back_populates="activity_links")

    def __str__(self) -> str:
        return f"{self.activity_type} → {self.unit_type}"

    def __repr__(self) -> str:
        return (
            f"ActivityTypeUnitType(activity_type_id={self.activity_type_id!r}, "
            f"unit_type_id={self.unit_type_id!r}, per_set={self.per_set!r})"
        )
