import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout_plan import WorkoutPlan
from app.repositories.plan import (
    get_plan_detail_for_user,
    get_plan_for_user,
    list_plans_for_user,
)
from app.repositories.session import get_session_for_user
from app.schemas.plan import PlanCreate, PlanUpdate


class PlanNotFoundError(Exception):
    """Raised when the plan is missing or belongs to another user."""


class SessionNotFoundError(Exception):
    """Raised when the session is missing, not owned, or not on this plan."""


class InvalidPlanError(Exception):
    """Raised when a plan update omits a required field."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def list_plans(db: Session, user: User) -> list[WorkoutPlan]:
    return list_plans_for_user(db, user.id)


def get_plan(db: Session, user: User, plan_id: uuid.UUID) -> WorkoutPlan:
    plan = get_plan_detail_for_user(db, plan_id, user.id)
    if plan is None:
        raise PlanNotFoundError()
    return plan


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
    plan = get_plan_for_user(db, plan_id, user.id)
    if plan is None:
        raise PlanNotFoundError()
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
    plan = get_plan_for_user(db, plan_id, user.id)
    if plan is None:
        raise PlanNotFoundError()
    db.delete(plan)
    db.commit()


def attach_session(
    db: Session,
    user: User,
    plan_id: uuid.UUID,
    session_id: uuid.UUID,
) -> WorkoutPlan:
    if get_plan_for_user(db, plan_id, user.id) is None:
        raise PlanNotFoundError()
    session = get_session_for_user(db, session_id, user.id)
    if session is None:
        raise SessionNotFoundError()
    session.plan_id = plan_id
    db.commit()
    return get_plan(db, user, plan_id)


def detach_session(
    db: Session,
    user: User,
    plan_id: uuid.UUID,
    session_id: uuid.UUID,
) -> WorkoutPlan:
    if get_plan_for_user(db, plan_id, user.id) is None:
        raise PlanNotFoundError()
    session = get_session_for_user(db, session_id, user.id)
    if session is None or session.plan_id != plan_id:
        raise SessionNotFoundError()
    session.plan_id = None
    db.commit()
    return get_plan(db, user, plan_id)
