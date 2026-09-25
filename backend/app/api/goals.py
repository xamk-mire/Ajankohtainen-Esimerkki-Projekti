import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.services.goals import (
    GoalNotFoundError,
    InvalidGoalError,
    create_goal,
    delete_goal,
    get_goal,
    list_goals,
    update_goal,
)

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalRead])
def list_my_goals(
    active: Annotated[
        bool | None,
        Query(description="When set, only goals with this active flag."),
    ] = None,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> list[GoalRead]:
    return [
        GoalRead.model_validate(goal)
        for goal in list_goals(db, current_user, active=active)
    ]


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_my_goal(
    body: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> GoalRead:
    try:
        goal = create_goal(db, current_user, body)
    except InvalidGoalError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.detail,
        ) from None
    return GoalRead.model_validate(goal)


@router.get("/{goal_id}", response_model=GoalRead)
def get_my_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> GoalRead:
    try:
        goal = get_goal(db, current_user, goal_id)
    except GoalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        ) from None
    return GoalRead.model_validate(goal)


@router.patch("/{goal_id}", response_model=GoalRead)
def update_my_goal(
    goal_id: uuid.UUID,
    body: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> GoalRead:
    try:
        goal = update_goal(db, current_user, goal_id, body)
    except GoalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        ) from None
    except InvalidGoalError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.detail,
        ) from None
    return GoalRead.model_validate(goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> None:
    try:
        delete_goal(db, current_user, goal_id)
    except GoalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        ) from None
