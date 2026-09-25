import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.calendar import CalendarSessionRead
from app.services.calendar import list_calendar
from app.services.sessions import InvalidSessionRangeError

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("", response_model=list[CalendarSessionRead])
def list_my_calendar(
    session_from: Annotated[
        datetime | None,
        Query(alias="from", description="Inclusive lower bound on session_at."),
    ] = None,
    session_to: Annotated[
        datetime | None,
        Query(alias="to", description="Inclusive upper bound on session_at."),
    ] = None,
    plan_id: Annotated[
        uuid.UUID | None,
        Query(description="Only this user's dated sessions with this plan_id."),
    ] = None,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> list[CalendarSessionRead]:
    try:
        sessions = list_calendar(
            db,
            current_user,
            starts_at=session_from,
            ends_at=session_to,
            plan_id=plan_id,
        )
    except InvalidSessionRangeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from must not be after to",
        ) from None
    return [CalendarSessionRead.model_validate(session) for session in sessions]
