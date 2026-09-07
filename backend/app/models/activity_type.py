import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User


class ActivityType(Base):
    """Catalog of individual exercises (running, bench press, …).

    System rows use ``is_system=True`` and ``user_id=NULL`` with a unique
    ``slug``. Custom rows use ``is_system=False`` and a owning ``user_id``;
    ``(user_id, slug)`` is unique so two users may reuse the same slug.
    Measurement kinds live on ``UnitType``, not on this table.
    """

    __tablename__ = "activity_types"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "slug",
            name="uq_activity_types_user_id_slug",
        ),
        Index(
            "uq_activity_types_system_slug",
            "slug",
            unique=True,
            postgresql_where=text("user_id IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    user: Mapped[User | None] = relationship()
    unit_links: Mapped[list["ActivityTypeUnitType"]] = relationship(
        back_populates="activity_type",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"

    def __repr__(self) -> str:
        return (
            f"ActivityType(id={self.id!r}, slug={self.slug!r}, "
            f"is_system={self.is_system!r})"
        )
