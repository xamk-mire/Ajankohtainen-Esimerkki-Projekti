import uuid

from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.user import User
from app.repositories.activity_type import get_visible_activity_type
from app.repositories.goal import get_goal_for_user, list_goals_for_user
from app.repositories.unit_type import get_unit_type_by_id
from app.schemas.goal import GoalCreate, GoalUpdate


class GoalNotFoundError(Exception):
    """Raised when the goal is missing or belongs to another user."""


class InvalidGoalError(Exception):
    """Raised when a goal references an unknown unit or activity, or clears a required field."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def list_goals(db: Session, user: User, *, active: bool | None = None) -> list[Goal]:
    return list_goals_for_user(db, user.id, active=active)


def get_goal(db: Session, user: User, goal_id: uuid.UUID) -> Goal:
    goal = get_goal_for_user(db, goal_id, user.id)
    if goal is None:
        raise GoalNotFoundError()
    return goal


def _require_unit(db: Session, unit_type_id: uuid.UUID) -> None:
    if get_unit_type_by_id(db, unit_type_id) is None:
        raise InvalidGoalError("Unknown unit type")


def _require_visible_activity(
    db: Session,
    user: User,
    activity_type_id: uuid.UUID | None,
) -> None:
    if activity_type_id is None:
        return
    if get_visible_activity_type(db, activity_type_id, user.id) is None:
        raise InvalidGoalError("Unknown activity type")


def create_goal(db: Session, user: User, data: GoalCreate) -> Goal:
    _require_unit(db, data.unit_type_id)
    _require_visible_activity(db, user, data.activity_type_id)
    goal = Goal(
        user_id=user.id,
        unit_type_id=data.unit_type_id,
        activity_type_id=data.activity_type_id,
        target_value=data.target_value,
        period=data.period,
        active=data.active,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def update_goal(
    db: Session,
    user: User,
    goal_id: uuid.UUID,
    data: GoalUpdate,
) -> Goal:
    goal = get_goal_for_user(db, goal_id, user.id)
    if goal is None:
        raise GoalNotFoundError()
    fields = data.model_fields_set
    if "unit_type_id" in fields:
        if data.unit_type_id is None:
            raise InvalidGoalError("Unit type is required")
        _require_unit(db, data.unit_type_id)
        goal.unit_type_id = data.unit_type_id
    if "activity_type_id" in fields:
        _require_visible_activity(db, user, data.activity_type_id)
        goal.activity_type_id = data.activity_type_id
    if "target_value" in fields:
        if data.target_value is None:
            raise InvalidGoalError("Target value is required")
        goal.target_value = data.target_value
    if "period" in fields:
        if data.period is None:
            raise InvalidGoalError("Period is required")
        goal.period = data.period
    if "active" in fields:
        if data.active is None:
            raise InvalidGoalError("Active is required")
        goal.active = data.active
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, user: User, goal_id: uuid.UUID) -> None:
    goal = get_goal_for_user(db, goal_id, user.id)
    if goal is None:
        raise GoalNotFoundError()
    db.delete(goal)
    db.commit()
