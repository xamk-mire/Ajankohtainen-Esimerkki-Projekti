import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CalendarSessionRead(BaseModel):
    """Dated session shown on the calendar. Unscheduled sessions are omitted."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    session_at: datetime
    status: str
    plan_id: uuid.UUID | None
