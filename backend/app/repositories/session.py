import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem

_session_load = selectinload(WorkoutSession.items).selectinload(
    WorkoutSessionItem.measurements
)


def list_sessions_for_user(db: Session, user_id: uuid.UUID) -> list[WorkoutSession]:
    statement = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .options(_session_load)
        .order_by(WorkoutSession.created_at.desc())
    )
    return list(db.scalars(statement).unique().all())


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


def get_plan_for_user(
    db: Session,
    plan_id: uuid.UUID,
    user_id: uuid.UUID,
) -> WorkoutPlan | None:
    statement = select(WorkoutPlan).where(
        WorkoutPlan.id == plan_id,
        WorkoutPlan.user_id == user_id,
    )
    return db.scalars(statement).one_or_none()
