import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout_session import WorkoutSession
from app.repositories.session import SessionListFilters
from app.services.sessions import list_sessions


def list_calendar(
    db: Session,
    user: User,
    *,
    starts_at: datetime | None,
    ends_at: datetime | None,
    plan_id: uuid.UUID | None,
) -> list[WorkoutSession]:
    """Dated sessions for this user, ordered by session_at.

    Unscheduled rows are excluded. A plan_id the user does not own matches
    nothing, because the session list is already limited to user_id.
    """
    sessions = list_sessions(
        db,
        user,
        SessionListFilters(
            starts_at=starts_at,
            ends_at=ends_at,
            unscheduled=False,
            plan_id=plan_id,
        ),
    )
    dated = [session for session in sessions if session.session_at is not None]
    dated.sort(key=lambda session: session.session_at)
    return dated
