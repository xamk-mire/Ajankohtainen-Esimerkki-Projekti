import uuid
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.session import SessionListFilters
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate
from app.services.sessions import (
    InvalidSessionRangeError,
    InvalidSessionReferenceError,
    PlanNotFoundError,
    SessionNotFoundError,
    create_session,
    delete_session,
    get_session,
    list_sessions,
    update_session,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionRead])
def list_my_sessions(
    session_from: Annotated[
        datetime | None,
        Query(
            alias="from",
            description="Inclusive lower bound on session_at. Unscheduled sessions are excluded.",
        ),
    ] = None,
    session_to: Annotated[
        datetime | None,
        Query(
            alias="to",
            description="Inclusive upper bound on session_at. Unscheduled sessions are excluded.",
        ),
    ] = None,
    status_filter: Annotated[
        Literal["planned", "in_progress", "completed"] | None,
        Query(alias="status", description="Session status."),
    ] = None,
    activity_type_id: Annotated[
        uuid.UUID | None,
        Query(description="Only sessions that include this exercise."),
    ] = None,
    unscheduled: Annotated[
        bool | None,
        Query(
            description="True: session_at is null. False: session_at is set. Omit to include both.",
        ),
    ] = None,
    plan_id: Annotated[
        uuid.UUID | None,
        Query(description="Only this user's sessions with this plan_id."),
    ] = None,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> list[SessionRead]:
    try:
        sessions = list_sessions(
            db,
            current_user,
            SessionListFilters(
                starts_at=session_from,
                ends_at=session_to,
                status=status_filter,
                activity_type_id=activity_type_id,
                unscheduled=unscheduled,
                plan_id=plan_id,
            ),
        )
    except InvalidSessionRangeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from must not be after to",
        ) from None
    return [SessionRead.model_validate(session) for session in sessions]


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_my_session(
    body: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> SessionRead:
    try:
        session = create_session(db, current_user, body)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        ) from None
    except InvalidSessionReferenceError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.detail,
        ) from None
    return SessionRead.model_validate(session)


@router.get("/{session_id}", response_model=SessionRead)
def get_my_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> SessionRead:
    try:
        session = get_session(db, current_user, session_id)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from None
    return SessionRead.model_validate(session)


@router.patch("/{session_id}", response_model=SessionRead)
def update_my_session(
    session_id: uuid.UUID,
    body: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> SessionRead:
    try:
        session = update_session(db, current_user, session_id, body)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from None
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        ) from None
    except InvalidSessionReferenceError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.detail,
        ) from None
    return SessionRead.model_validate(session)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> None:
    try:
        delete_session(db, current_user, session_id)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from None
