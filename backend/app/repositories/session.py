import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem

_session_load = selectinload(WorkoutSession.items).selectinload(
    WorkoutSessionItem.measurements
)


@dataclass(frozen=True)
class SessionListFilters:
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: str | None = None
    activity_type_id: uuid.UUID | None = None
    unscheduled: bool | None = None
    plan_id: uuid.UUID | None = None
    page: int = 1
    limit: int | None = None


def _filtered_sessions(user_id: uuid.UUID, filters: SessionListFilters):
    statement = select(WorkoutSession).where(WorkoutSession.user_id == user_id)
    if filters.starts_at is not None:
        statement = statement.where(WorkoutSession.session_at >= filters.starts_at)
    if filters.ends_at is not None:
        statement = statement.where(WorkoutSession.session_at <= filters.ends_at)
    if filters.status is not None:
        statement = statement.where(WorkoutSession.status == filters.status)
    if filters.activity_type_id is not None:
        statement = statement.where(
            WorkoutSession.items.any(
                WorkoutSessionItem.activity_type_id == filters.activity_type_id
            )
        )
    if filters.unscheduled is True:
        statement = statement.where(WorkoutSession.session_at.is_(None))
    elif filters.unscheduled is False:
        statement = statement.where(WorkoutSession.session_at.is_not(None))
    if filters.plan_id is not None:
        statement = statement.where(WorkoutSession.plan_id == filters.plan_id)
    return statement


def list_sessions_for_user(
    db: Session,
    user_id: uuid.UUID,
    filters: SessionListFilters | None = None,
) -> tuple[list[WorkoutSession], int]:
    filters = filters or SessionListFilters()
    filtered = _filtered_sessions(user_id, filters)
    total = db.scalar(select(func.count()).select_from(filtered.subquery())) or 0
    statement = filtered.options(_session_load).order_by(WorkoutSession.created_at.desc())
    if filters.limit is not None:
        offset = (filters.page - 1) * filters.limit
        statement = statement.offset(offset).limit(filters.limit)
    rows = list(db.scalars(statement).unique().all())
    return rows, total


def get_session_for_user(
    db: Session,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
) -> WorkoutSession | None:
    statement = (
        select(WorkoutSession)
        .where(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
        )
        .options(_session_load)
    )
    return db.scalars(statement).unique().one_or_none()
