from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.models.unit_type import UnitType


def get_unit_type_by_slug(db: Session, slug: str) -> UnitType | None:
    return db.scalars(select(UnitType).where(UnitType.slug == slug)).first()


def get_or_create_unit_type(
    db: Session,
    *,
    slug: str,
    name: str,
    unit_label: str | None = None,
    is_system: bool = True,
) -> UnitType:
    existing = get_unit_type_by_slug(db, slug)
    if existing is not None:
        return existing

    unit = UnitType(
        slug=slug,
        name=name,
        unit_label=unit_label,
        is_system=is_system,
    )
    db.add(unit)
    db.flush()
    return unit


def create_activity_unit_link_if_missing(
    db: Session,
    activity_type: ActivityType,
    unit_type: UnitType,
    *,
    sort_order: int,
    is_required: bool = True,
    per_set: bool = False,
) -> ActivityTypeUnitType:
    existing = db.scalars(
        select(ActivityTypeUnitType).where(
            ActivityTypeUnitType.activity_type_id == activity_type.id,
            ActivityTypeUnitType.unit_type_id == unit_type.id,
        )
    ).first()
    if existing is not None:
        return existing

    link = ActivityTypeUnitType(
        activity_type=activity_type,
        unit_type=unit_type,
        sort_order=sort_order,
        is_required=is_required,
        per_set=per_set,
    )
    db.add(link)
    return link
