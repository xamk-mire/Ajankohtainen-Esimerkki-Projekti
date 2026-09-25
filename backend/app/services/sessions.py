import uuid

from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType
from app.models.unit_type import UnitType
from app.models.user import User
from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem
from app.models.workout_session_measurement import WorkoutSessionMeasurement
from app.repositories.session import (
    get_plan_for_user,
    get_session_for_user,
    list_sessions_for_user,
)
from app.schemas.session import SessionCreate, SessionItemWrite, SessionUpdate


class SessionNotFoundError(Exception):
    """Raised when the session is missing or belongs to another user."""


class PlanNotFoundError(Exception):
    """Raised when plan_id is missing or belongs to another user."""


class InvalidSessionReferenceError(Exception):
    """Raised when an activity or unit id does not exist."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def list_sessions(db: Session, user: User) -> list[WorkoutSession]:
    return list_sessions_for_user(db, user.id)


def get_session(db: Session, user: User, session_id: uuid.UUID) -> WorkoutSession:
    session = get_session_for_user(db, session_id, user.id)
    if session is None:
        raise SessionNotFoundError()
    return session


def create_session(db: Session, user: User, data: SessionCreate) -> WorkoutSession:
    _require_owned_plan(db, user.id, data.plan_id)
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
        _require_owned_plan(db, user.id, data.plan_id)
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


def _require_owned_plan(
    db: Session,
    user_id: uuid.UUID,
    plan_id: uuid.UUID | None,
) -> None:
    if plan_id is None:
        return
    if get_plan_for_user(db, plan_id, user_id) is None:
        raise PlanNotFoundError()


def _build_item(db: Session, data: SessionItemWrite) -> WorkoutSessionItem:
    # Link, per-set, and empty-value rules are S3-05. This only checks that
    # the referenced catalog rows exist so the write does not hit a raw FK error.
    if db.get(ActivityType, data.activity_type_id) is None:
        raise InvalidSessionReferenceError("Unknown activity type")
    measurements = []
    for measurement in data.measurements:
        if db.get(UnitType, measurement.unit_type_id) is None:
            raise InvalidSessionReferenceError("Unknown unit type")
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
