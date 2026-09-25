import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal


def list_goals_for_user(
    db: Session,
    user_id: uuid.UUID,
    *,
    active: bool | None = None,
) -> list[Goal]:
    statement = select(Goal).where(Goal.user_id == user_id)
    if active is not None:
        statement = statement.where(Goal.active.is_(active))
    statement = statement.order_by(Goal.created_at.desc())
    return list(db.scalars(statement).all())


def get_goal_for_user(
    db: Session,
    goal_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Goal | None:
    statement = select(Goal).where(
        Goal.id == goal_id,
        Goal.user_id == user_id,
    )
    return db.scalars(statement).one_or_none()
