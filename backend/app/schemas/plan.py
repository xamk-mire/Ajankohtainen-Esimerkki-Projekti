import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    notes: str | None = None
    start_date: date | None = None
    length_weeks: int | None = Field(default=None, ge=1)


class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None
    start_date: date | None = None
    length_weeks: int | None = Field(default=None, ge=1)


class PlanSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    session_at: datetime | None
    status: str


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    notes: str | None
    start_date: date | None
    length_weeks: int | None
    created_at: datetime
    updated_at: datetime


class PlanDetail(PlanRead):
    sessions: list[PlanSessionRead]
