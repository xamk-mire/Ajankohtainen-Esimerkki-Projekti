import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workout_plan import WorkoutPlan


def list_plans_for_user(db: Session, user_id: uuid.UUID) -> list[WorkoutPlan]:
    statement = (
        select(WorkoutPlan)
        .where(WorkoutPlan.user_id == user_id)
        .order_by(WorkoutPlan.created_at.desc())
    )
    return list(db.scalars(statement).all())


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


def get_plan_detail_for_user(
    db: Session,
    plan_id: uuid.UUID,
    user_id: uuid.UUID,
) -> WorkoutPlan | None:
    statement = (
        select(WorkoutPlan)
        .where(
            WorkoutPlan.id == plan_id,
            WorkoutPlan.user_id == user_id,
        )
        .options(selectinload(WorkoutPlan.sessions))
    )
    return db.scalars(statement).unique().one_or_none()
