from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.models.goal import Goal
from app.models.unit_type import UnitType
from app.models.user import User
from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem
from app.models.workout_session_measurement import WorkoutSessionMeasurement
from app.repositories.activity_type import (
    get_or_create_system_activity_type,
    get_system_activity_type_by_slug,
)
from app.repositories.unit_type import (
    create_activity_unit_link_if_missing,
    get_or_create_unit_type,
    get_unit_type_by_slug,
)
from app.repositories.user import create_user

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo-pass-1"
DEMO_DISPLAY_NAME = "Demo user"

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


def clear_seed_data(db: Session) -> None:
    """Remove app rows. Does not drop tables or touch Alembic.

    Measurements and goals reference units with RESTRICT, and goals also
    reference activities, so those rows go before the catalog.
    """
    db.execute(update(WorkoutSession).values(source_session_id=None, plan_id=None))
    db.execute(delete(WorkoutSessionMeasurement))
    db.execute(delete(WorkoutSessionItem))
    db.execute(delete(WorkoutSession))
    db.execute(delete(WorkoutPlan))
    db.execute(delete(Goal))
    db.execute(delete(ActivityTypeUnitType))
    db.execute(delete(ActivityType))
    db.execute(delete(UnitType))
    db.execute(delete(User))
    db.flush()


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


def _require_activity(db: Session, slug: str) -> ActivityType:
    activity = get_system_activity_type_by_slug(db, slug)
    if activity is None:
        raise RuntimeError(f"{slug} is missing; seed the catalog first.")
    return activity


def _require_unit(db: Session, slug: str) -> UnitType:
    unit = get_unit_type_by_slug(db, slug)
    if unit is None:
        raise RuntimeError(f"{slug} is missing; seed the catalog first.")
    return unit


def _add_session(
    db: Session,
    user: User,
    plan: WorkoutPlan | None,
    *,
    name: str,
    session_at: datetime | None,
    status: str,
    exercises: list[tuple[ActivityType, list[tuple[UnitType, Decimal | None, Decimal | None, int | None]]]],
) -> WorkoutSession:
    session = WorkoutSession(
        user_id=user.id,
        plan_id=None if plan is None else plan.id,
        name=name,
        session_at=session_at,
        status=status,
    )
    db.add(session)
    db.flush()
    for sort_order, (activity, measurements) in enumerate(exercises):
        item = WorkoutSessionItem(
            session_id=session.id,
            activity_type_id=activity.id,
            sort_order=sort_order,
        )
        db.add(item)
        db.flush()
        for unit, planned, actual, set_index in measurements:
            db.add(
                WorkoutSessionMeasurement(
                    session_item_id=item.id,
                    unit_type_id=unit.id,
                    planned_value=planned,
                    actual_value=actual,
                    set_index=set_index,
                )
            )
    return session


def seed_demo_history(db: Session, user: User) -> None:
    """Dated sessions, a plan, and period goals owned by the demo user.

    Dates are relative to today so the dashboard and the current calendar month
    include them. Strength rows use ``set_index`` because those unit links are
    ``per_set``.
    """
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    running = _require_activity(db, "running")
    bench = _require_activity(db, "bench_press")
    stretch = db.scalars(
        select(ActivityType).where(
            ActivityType.slug == "demo_stretch",
            ActivityType.user_id == user.id,
        )
    ).one()
    duration = _require_unit(db, "duration_min")
    distance = _require_unit(db, "distance_km")
    reps = _require_unit(db, "reps")
    weight = _require_unit(db, "weight_kg")

    plan = WorkoutPlan(
        user_id=user.id,
        name="Demo block",
        notes="Seeded plan. Dated sessions are attached through plan_id.",
        start_date=date.today() - timedelta(days=7),
        length_weeks=4,
    )
    db.add(plan)
    db.flush()

    _add_session(
        db,
        user,
        plan,
        name="Easy run",
        session_at=now - timedelta(days=6),
        status="completed",
        exercises=[
            (
                running,
                [
                    (duration, Decimal("30"), Decimal("28"), None),
                    (distance, Decimal("5"), Decimal("4.8"), None),
                ],
            )
        ],
    )
    _add_session(
        db,
        user,
        plan,
        name="Bench press",
        session_at=now - timedelta(days=3),
        status="completed",
        exercises=[
            (
                bench,
                [
                    (reps, Decimal("8"), Decimal("8"), 1),
                    (weight, Decimal("40"), Decimal("40"), 1),
                    (reps, Decimal("8"), Decimal("6"), 2),
                    (weight, Decimal("40"), Decimal("40"), 2),
                ],
            )
        ],
    )
    _add_session(
        db,
        user,
        plan,
        name="Long run",
        session_at=now + timedelta(days=1),
        status="planned",
        exercises=[
            (
                running,
                [
                    (duration, Decimal("45"), None, None),
                    (distance, Decimal("8"), None, None),
                ],
            )
        ],
    )
    _add_session(
        db,
        user,
        None,
        name="Stretch",
        session_at=None,
        status="planned",
        exercises=[(stretch, [(duration, Decimal("10"), None, None)])],
    )

    db.add_all(
        [
            Goal(
                user_id=user.id,
                unit_type_id=distance.id,
                activity_type_id=running.id,
                target_value=Decimal("20"),
                period="week",
                active=True,
            ),
            Goal(
                user_id=user.id,
                unit_type_id=duration.id,
                target_value=Decimal("150"),
                period="month",
                active=True,
            ),
        ]
    )


def seed_demo_user(db: Session) -> User:
    """One login and a custom exercise. Call after ``seed_catalog``."""
    user = create_user(
        db,
        email=DEMO_EMAIL,
        password_hash=hash_password(DEMO_PASSWORD),
        display_name=DEMO_DISPLAY_NAME,
    )
    duration = get_unit_type_by_slug(db, "duration_min")
    if duration is None:
        raise RuntimeError("duration_min is missing; seed the catalog first.")
    stretch = ActivityType(
        name="Demo stretch",
        slug="demo_stretch",
        is_system=False,
        user_id=user.id,
    )
    db.add(stretch)
    db.flush()
    create_activity_unit_link_if_missing(
        db,
        stretch,
        duration,
        sort_order=0,
        is_required=True,
        per_set=False,
    )
    return user


def reset_and_seed(db: Session) -> User:
    """Wipe app data, then insert a fresh demonstration set."""
    clear_seed_data(db)
    seed_catalog(db)
    user = seed_demo_user(db)
    seed_demo_history(db, user)
    return user
