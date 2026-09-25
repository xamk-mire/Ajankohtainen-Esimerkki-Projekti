import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType


def get_system_activity_type_by_slug(db: Session, slug: str) -> ActivityType | None:
    return db.scalars(
        select(ActivityType).where(
            ActivityType.slug == slug,
            ActivityType.user_id.is_(None),
        )
    ).first()


def get_or_create_system_activity_type(
    db: Session,
    *,
    slug: str,
    name: str,
) -> ActivityType:
    existing = get_system_activity_type_by_slug(db, slug)
    if existing is not None:
        return existing

    activity = ActivityType(
        name=name,
        slug=slug,
        is_system=True,
        user_id=None,
    )
    db.add(activity)
    db.flush()
    return activity


def _with_unit_links(statement):
    return statement.options(
        selectinload(ActivityType.unit_links).selectinload(
            ActivityTypeUnitType.unit_type
        )
    )


def list_visible_activity_types(db: Session, user_id: uuid.UUID) -> list[ActivityType]:
    """System catalog plus this user's custom types."""
    statement = _with_unit_links(
        select(ActivityType)
        .where(
            or_(
                ActivityType.user_id.is_(None),
                ActivityType.user_id == user_id,
            )
        )
        .order_by(ActivityType.is_system.desc(), ActivityType.name.asc())
    )
    activities = list(db.scalars(statement).unique().all())
    for activity in activities:
        activity.unit_links.sort(key=lambda link: (link.sort_order, str(link.id)))
    return activities


def get_user_activity_by_slug(
    db: Session,
    user_id: uuid.UUID,
    slug: str,
) -> ActivityType | None:
    return db.scalars(
        select(ActivityType).where(
            ActivityType.user_id == user_id,
            ActivityType.slug == slug,
        )
    ).first()
