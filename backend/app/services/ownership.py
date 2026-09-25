"""Load a session, plan, or goal for the current user, or raise.

A missing id and another user's id raise the same error. API routes map these
to **404** with a fixed detail (``Session not found``, ``Plan not found``,
``Goal not found``). Do not use 403: that would reveal that the id exists.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.user import User
from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession
from app.repositories.goal import get_goal_for_user
from app.repositories.plan import get_plan_detail_for_user, get_plan_for_user
from app.repositories.session import get_session_for_user


class SessionNotFoundError(Exception):
    """Raised when the session is missing or belongs to another user."""


class PlanNotFoundError(Exception):
    """Raised when the plan is missing or belongs to another user."""


class GoalNotFoundError(Exception):
    """Raised when the goal is missing or belongs to another user."""


def require_session(db: Session, user: User, session_id: uuid.UUID) -> WorkoutSession:
    session = get_session_for_user(db, session_id, user.id)
    if session is None:
        raise SessionNotFoundError()
    return session


def require_plan(db: Session, user: User, plan_id: uuid.UUID) -> WorkoutPlan:
    plan = get_plan_for_user(db, plan_id, user.id)
    if plan is None:
        raise PlanNotFoundError()
    return plan


def require_plan_detail(db: Session, user: User, plan_id: uuid.UUID) -> WorkoutPlan:
    plan = get_plan_detail_for_user(db, plan_id, user.id)
    if plan is None:
        raise PlanNotFoundError()
    return plan


def require_goal(db: Session, user: User, goal_id: uuid.UUID) -> Goal:
    goal = get_goal_for_user(db, goal_id, user.id)
    if goal is None:
        raise GoalNotFoundError()
    return goal
