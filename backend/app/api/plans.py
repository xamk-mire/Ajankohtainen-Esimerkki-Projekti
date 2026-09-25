import uuid

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.plan import PlanCreate, PlanDetail, PlanRead, PlanUpdate
from app.services.plans import (
    InvalidPlanError,
    PlanNotFoundError,
    SessionNotFoundError,
    attach_session,
    create_plan,
    delete_plan,
    detach_session,
    get_plan,
    list_plans,
    update_plan,
)

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanRead])
def list_my_plans(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> list[PlanRead]:
    return [PlanRead.model_validate(plan) for plan in list_plans(db, current_user)]


@router.post("", response_model=PlanDetail, status_code=status.HTTP_201_CREATED)
def create_my_plan(
    body: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> PlanDetail:
    return PlanDetail.model_validate(create_plan(db, current_user, body))


@router.get("/{plan_id}", response_model=PlanDetail)
def get_my_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> PlanDetail:
    try:
        plan = get_plan(db, current_user, plan_id)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        ) from None
    return PlanDetail.model_validate(plan)


@router.patch("/{plan_id}", response_model=PlanDetail)
def update_my_plan(
    plan_id: uuid.UUID,
    body: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> PlanDetail:
    try:
        plan = update_plan(db, current_user, plan_id, body)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        ) from None
    except InvalidPlanError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.detail,
        ) from None
    return PlanDetail.model_validate(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> None:
    try:
        delete_plan(db, current_user, plan_id)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        ) from None


@router.post("/{plan_id}/sessions/{session_id}", response_model=PlanDetail)
def attach_my_session(
    plan_id: uuid.UUID,
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> PlanDetail:
    try:
        plan = attach_session(db, current_user, plan_id, session_id)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        ) from None
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from None
    return PlanDetail.model_validate(plan)


@router.delete("/{plan_id}/sessions/{session_id}", response_model=PlanDetail)
def detach_my_session(
    plan_id: uuid.UUID,
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> PlanDetail:
    try:
        plan = detach_session(db, current_user, plan_id, session_id)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        ) from None
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from None
    return PlanDetail.model_validate(plan)
