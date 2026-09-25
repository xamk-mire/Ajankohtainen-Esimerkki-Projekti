import uuid

from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType
from app.models.user import User
from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem
from app.models.workout_session_measurement import WorkoutSessionMeasurement
from app.repositories.session import SessionListFilters, list_sessions_for_user
from app.repositories.unit_type import get_activity_unit_link
from app.schemas.session import SessionClone, SessionCreate, SessionItemWrite, SessionUpdate
from app.services.ownership import (
    PlanNotFoundError,
    SessionNotFoundError,
    require_plan,
    require_session,
)


class InvalidSessionRangeError(Exception):
    """Raised when a list filter has from later than to."""


class InvalidSessionReferenceError(Exception):
    """Raised when an activity or unit id does not exist."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def list_sessions(
    db: Session,
    user: User,
    filters: SessionListFilters | None = None,
) -> list[WorkoutSession]:
    filters = filters or SessionListFilters()
    if (
        filters.starts_at is not None
        and filters.ends_at is not None
        and filters.starts_at > filters.ends_at
    ):
        raise InvalidSessionRangeError()
    return list_sessions_for_user(db, user.id, filters)


def get_session(db: Session, user: User, session_id: uuid.UUID) -> WorkoutSession:
    return require_session(db, user, session_id)


def create_session(db: Session, user: User, data: SessionCreate) -> WorkoutSession:
    _require_owned_plan(db, user, data.plan_id)
    session = WorkoutSession(
        user_id=user.id,
        name=data.name,
        session_at=data.session_at,
        status=data.status,
        notes=data.notes,
        intensity=data.intensity,
        plan_id=data.plan_id,
        items=[_build_item(db, item) for item in data.items],
    )
    db.add(session)
    db.commit()
    return get_session(db, user, session.id)


def update_session(
    db: Session,
    user: User,
    session_id: uuid.UUID,
    data: SessionUpdate,
) -> WorkoutSession:
    session = get_session(db, user, session_id)
    fields = data.model_fields_set

    if "name" in fields:
        if data.name is None:
            raise InvalidSessionReferenceError("Name is required")
        session.name = data.name
    if "session_at" in fields:
        session.session_at = data.session_at
    if "status" in fields:
        if data.status is None:
            raise InvalidSessionReferenceError("Status is required")
        session.status = data.status
    if "notes" in fields:
        session.notes = data.notes
    if "intensity" in fields:
        session.intensity = data.intensity
    if "plan_id" in fields:
        _require_owned_plan(db, user, data.plan_id)
        session.plan_id = data.plan_id
    if "items" in fields:
        session.items.clear()
        for item in data.items or []:
            session.items.append(_build_item(db, item))

    db.commit()
    return get_session(db, user, session.id)


def delete_session(db: Session, user: User, session_id: uuid.UUID) -> None:
    session = get_session(db, user, session_id)
    db.delete(session)
    db.commit()


def clone_session(
    db: Session,
    user: User,
    session_id: uuid.UUID,
    data: SessionClone | None = None,
) -> WorkoutSession:
    source = get_session(db, user, session_id)
    data = data or SessionClone()
    plan_id = data.plan_id if "plan_id" in data.model_fields_set else None
    _require_owned_plan(db, user, plan_id)
    clone = WorkoutSession(
        user_id=user.id,
        name=data.name or source.name,
        session_at=data.session_at if "session_at" in data.model_fields_set else None,
        status="planned",
        notes=source.notes,
        intensity=source.intensity,
        plan_id=plan_id,
        source_session_id=source.id,
        items=[_copy_item(item) for item in source.items],
    )
    db.add(clone)
    db.commit()
    return get_session(db, user, clone.id)


def _copy_item(item: WorkoutSessionItem) -> WorkoutSessionItem:
    return WorkoutSessionItem(
        activity_type_id=item.activity_type_id,
        sort_order=item.sort_order,
        notes=item.notes,
        measurements=[
            WorkoutSessionMeasurement(
                unit_type_id=measurement.unit_type_id,
                planned_value=measurement.planned_value,
                actual_value=None,
                set_index=measurement.set_index,
            )
            for measurement in item.measurements
        ],
    )


def _require_owned_plan(
    db: Session,
    user: User,
    plan_id: uuid.UUID | None,
) -> None:
    if plan_id is None:
        return
    require_plan(db, user, plan_id)


def _build_item(db: Session, data: SessionItemWrite) -> WorkoutSessionItem:
    if db.get(ActivityType, data.activity_type_id) is None:
        raise InvalidSessionReferenceError("Unknown activity type")
    measurements = []
    for measurement in data.measurements:
        if measurement.planned_value is None and measurement.actual_value is None:
            raise InvalidSessionReferenceError(
                "Measurement needs a planned value, an actual value, or both"
            )
        link = get_activity_unit_link(
            db,
            data.activity_type_id,
            measurement.unit_type_id,
        )
        if link is None:
            raise InvalidSessionReferenceError("Unit is not allowed for this activity")
        if link.per_set and measurement.set_index is None:
            raise InvalidSessionReferenceError(
                "set_index is required for per-set units"
            )
        # Clone copies planned_value and clears actual_value in clone_session.
        measurements.append(
            WorkoutSessionMeasurement(
                unit_type_id=measurement.unit_type_id,
                planned_value=measurement.planned_value,
                actual_value=measurement.actual_value,
                set_index=measurement.set_index,
            )
        )
    return WorkoutSessionItem(
        activity_type_id=data.activity_type_id,
        sort_order=data.sort_order,
        notes=data.notes,
        measurements=measurements,
    )
