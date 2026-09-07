import uuid

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UnitType(Base):
    """Reusable measurement kind (duration, distance, reps, weight, …)."""

    __tablename__ = "unit_types"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    unit_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    activity_links: Mapped[list["ActivityTypeUnitType"]] = relationship(
        back_populates="unit_type",
    )

    def __str__(self) -> str:
        if self.unit_label:
            return f"{self.name} ({self.unit_label})"
        return f"{self.name} ({self.slug})"

    def __repr__(self) -> str:
        return f"UnitType(id={self.id!r}, slug={self.slug!r})"
