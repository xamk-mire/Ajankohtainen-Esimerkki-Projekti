from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.models.user import User
from app.repositories.activity_type import (
    get_user_activity_by_slug,
    list_visible_activity_types,
)
from app.repositories.unit_type import get_unit_types_by_ids
from app.schemas.activity_type import ActivityTypeCreate, slugify_activity_name


class DuplicateActivitySlugError(Exception):
    """Raised when this user already has a custom type with the slug."""


class InvalidActivityTypeError(Exception):
    """Raised when a custom type cannot be created from the request."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def list_activity_types(db: Session, user: User) -> list[ActivityType]:
    return list_visible_activity_types(db, user.id)


def create_custom_activity_type(
    db: Session,
    user: User,
    data: ActivityTypeCreate,
) -> ActivityType:
    slug = data.slug or slugify_activity_name(data.name)
    if not slug:
        raise InvalidActivityTypeError("Slug is required")

    unit_ids = [link.unit_type_id for link in data.unit_links]
    if len(unit_ids) != len(set(unit_ids)):
        raise InvalidActivityTypeError("Each unit type can be linked only once")

    found = get_unit_types_by_ids(db, unit_ids)
    if len(found) != len(set(unit_ids)):
        raise InvalidActivityTypeError("Unknown unit type")

    if get_user_activity_by_slug(db, user.id, slug) is not None:
        raise DuplicateActivitySlugError()

    activity = ActivityType(
        name=data.name,
        slug=slug,
        is_system=False,
        user_id=user.id,
    )
    for link in data.unit_links:
        activity.unit_links.append(
            ActivityTypeUnitType(
                unit_type_id=link.unit_type_id,
                sort_order=link.sort_order,
                is_required=link.is_required,
                per_set=link.per_set,
            )
        )
    db.add(activity)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateActivitySlugError() from None

    created = next(
        (
            row
            for row in list_visible_activity_types(db, user.id)
            if row.id == activity.id
        ),
        None,
    )
    if created is None:
        raise InvalidActivityTypeError("Activity type was not created")
    return created
