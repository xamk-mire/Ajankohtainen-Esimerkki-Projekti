import uuid
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.session import SessionListFilters
from app.schemas.adherence import AdherenceRead
from app.schemas.session import SessionClone, SessionCreate, SessionListPage, SessionRead, SessionUpdate
from app.services.sessions import (
    InvalidSessionRangeError,
    InvalidSessionReferenceError,
    PlanNotFoundError,
    SessionNotFoundError,
    adherence_for_user,
    clone_session,
    create_session,
    delete_session,
    get_session,
    list_sessions,
    update_session,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=SessionListPage)
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
    page: Annotated[
        int,
        Query(ge=1, description="1-based page. Applies when limit is set."),
    ] = 1,
    limit: Annotated[
        int | None,
        Query(
            ge=1,
            le=100,
            description="Page size. Omit to return every matching session.",
        ),
    ] = None,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> SessionListPage:
    try:
        sessions, total = list_sessions(
            db,
            current_user,
            SessionListFilters(
                starts_at=session_from,
                ends_at=session_to,
                status=status_filter,
                activity_type_id=activity_type_id,
                unscheduled=unscheduled,
                plan_id=plan_id,
                page=page,
                limit=limit,
            ),
        )
    except InvalidSessionRangeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from must not be after to",
        ) from None
    return SessionListPage(
        items=[SessionRead.model_validate(session) for session in sessions],
        total=total,
        page=page if limit is not None else 1,
        limit=limit,
    )


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


@router.post(
    "/{session_id}/clone",
    response_model=SessionRead,
    status_code=status.HTTP_201_CREATED,
)
def clone_my_session(
    session_id: uuid.UUID,
    body: SessionClone | None = None,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> SessionRead:
    try:
        session = clone_session(db, current_user, session_id, body)
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
    return SessionRead.model_validate(session)


@router.get(
    "/adherence",
    response_model=list[AdherenceRead],
    summary="Planned versus actual preview",
)
def adherence_preview(
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
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> list[AdherenceRead]:
    """Sprint 4 preview: this user's planned versus actual totals, one row per unit.

    Measurements missing planned or actual are skipped. Units are not added together.
    """
    try:
        rows = adherence_for_user(
            db,
            current_user,
            starts_at=session_from,
            ends_at=session_to,
        )
    except InvalidSessionRangeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from must not be after to",
        ) from None
    return [AdherenceRead.model_validate(row, from_attributes=True) for row in rows]


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
