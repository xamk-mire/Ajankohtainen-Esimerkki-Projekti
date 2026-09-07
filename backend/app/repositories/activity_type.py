from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType


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
