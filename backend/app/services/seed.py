from sqlalchemy.orm import Session

from app.repositories.activity_type import get_or_create_system_activity_type
from app.repositories.unit_type import (
    create_activity_unit_link_if_missing,
    get_or_create_unit_type,
)

SYSTEM_UNIT_TYPES: list[tuple[str, str, str]] = [
    ("duration_min", "Duration", "min"),
    ("distance_km", "Distance", "km"),
    ("reps", "Reps", "reps"),
    ("weight_kg", "Weight", "kg"),
]

CARDIO_ACTIVITIES: list[tuple[str, str]] = [
    ("running", "Running"),
    ("cycling", "Cycling"),
    ("swimming", "Swimming"),
    ("hiking", "Hiking"),
]

STRENGTH_ACTIVITIES: list[tuple[str, str]] = [
    ("bench_press", "Bench press"),
    ("barbell_curl", "Barbell curl"),
    ("hammer_curl", "Hammer curl"),
    ("incline_curl", "Incline curl"),
    ("face_pull", "Face pull"),
]

OTHER_ACTIVITY = ("other", "Other")


def seed_catalog(db: Session) -> None:
    units = {
        slug: get_or_create_unit_type(
            db,
            slug=slug,
            name=name,
            unit_label=label,
            is_system=True,
        )
        for slug, name, label in SYSTEM_UNIT_TYPES
    }

    for slug, name in CARDIO_ACTIVITIES:
        activity = get_or_create_system_activity_type(db, slug=slug, name=name)
        create_activity_unit_link_if_missing(
            db,
            activity,
            units["duration_min"],
            sort_order=0,
            is_required=True,
            per_set=False,
        )
        create_activity_unit_link_if_missing(
            db,
            activity,
            units["distance_km"],
            sort_order=1,
            is_required=True,
            per_set=False,
        )

    for slug, name in STRENGTH_ACTIVITIES:
        activity = get_or_create_system_activity_type(db, slug=slug, name=name)
        create_activity_unit_link_if_missing(
            db,
            activity,
            units["reps"],
            sort_order=0,
            is_required=True,
            per_set=True,
        )
        create_activity_unit_link_if_missing(
            db,
            activity,
            units["weight_kg"],
            sort_order=1,
            is_required=True,
            per_set=True,
        )

    other = get_or_create_system_activity_type(
        db,
        slug=OTHER_ACTIVITY[0],
        name=OTHER_ACTIVITY[1],
    )
    create_activity_unit_link_if_missing(
        db,
        other,
        units["duration_min"],
        sort_order=0,
        is_required=True,
        per_set=False,
    )
