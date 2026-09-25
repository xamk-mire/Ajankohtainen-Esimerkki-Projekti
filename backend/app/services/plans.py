import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout_plan import WorkoutPlan
from app.repositories.plan import list_plans_for_user
from app.schemas.plan import PlanCreate, PlanUpdate
from app.services.ownership import (
    PlanNotFoundError,
    SessionNotFoundError,
    require_plan,
    require_plan_detail,
    require_session,
)


class InvalidPlanError(Exception):
    """Raised when a plan update omits a required field."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def list_plans(db: Session, user: User) -> list[WorkoutPlan]:
    return list_plans_for_user(db, user.id)


def get_plan(db: Session, user: User, plan_id: uuid.UUID) -> WorkoutPlan:
    return require_plan_detail(db, user, plan_id)


def create_plan(db: Session, user: User, data: PlanCreate) -> WorkoutPlan:
    plan = WorkoutPlan(
        user_id=user.id,
        name=data.name,
        notes=data.notes,
        start_date=data.start_date,
        length_weeks=data.length_weeks,
    )
    db.add(plan)
    db.commit()
    return get_plan(db, user, plan.id)


def update_plan(
    db: Session,
    user: User,
    plan_id: uuid.UUID,
    data: PlanUpdate,
) -> WorkoutPlan:
    plan = require_plan(db, user, plan_id)
    fields = data.model_fields_set
    if "name" in fields:
        if data.name is None:
            raise InvalidPlanError("Name is required")
        plan.name = data.name
    if "notes" in fields:
        plan.notes = data.notes
    if "start_date" in fields:
        plan.start_date = data.start_date
    if "length_weeks" in fields:
        plan.length_weeks = data.length_weeks
    db.commit()
    return get_plan(db, user, plan.id)


def delete_plan(db: Session, user: User, plan_id: uuid.UUID) -> None:
    plan = require_plan(db, user, plan_id)
    db.delete(plan)
    db.commit()


def attach_session(
    db: Session,
    user: User,
    plan_id: uuid.UUID,
    session_id: uuid.UUID,
) -> WorkoutPlan:
    require_plan(db, user, plan_id)
    session = require_session(db, user, session_id)
    session.plan_id = plan_id
    db.commit()
    return get_plan(db, user, plan_id)


def detach_session(
    db: Session,
    user: User,
    plan_id: uuid.UUID,
    session_id: uuid.UUID,
) -> WorkoutPlan:
    require_plan(db, user, plan_id)
    session = require_session(db, user, session_id)
    if session.plan_id != plan_id:
        raise SessionNotFoundError()
    session.plan_id = None
    db.commit()
    return get_plan(db, user, plan_id)
