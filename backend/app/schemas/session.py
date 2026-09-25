import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SessionStatus = Literal["planned", "in_progress", "completed"]


class MeasurementWrite(BaseModel):
    unit_type_id: uuid.UUID
    planned_value: Decimal | None = None
    actual_value: Decimal | None = None
    set_index: int | None = Field(default=None, ge=0)


class SessionItemWrite(BaseModel):
    activity_type_id: uuid.UUID
    sort_order: int = Field(default=0, ge=0)
    notes: str | None = None
    measurements: list[MeasurementWrite] = Field(default_factory=list)


class SessionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    session_at: datetime | None = None
    status: SessionStatus = "planned"
    notes: str | None = None
    intensity: int | None = Field(default=None, ge=1, le=10)
    plan_id: uuid.UUID | None = None
    items: list[SessionItemWrite] = Field(default_factory=list)


class SessionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    session_at: datetime | None = None
    status: SessionStatus | None = None
    notes: str | None = None
    intensity: int | None = Field(default=None, ge=1, le=10)
    plan_id: uuid.UUID | None = None
    items: list[SessionItemWrite] | None = None


class SessionClone(BaseModel):
    """Optional overrides. Omitted ``plan_id`` does not copy the source plan."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    session_at: datetime | None = None
    plan_id: uuid.UUID | None = None


class MeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    unit_type_id: uuid.UUID
    planned_value: Decimal | None
    actual_value: Decimal | None
    set_index: int | None


class SessionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    activity_type_id: uuid.UUID
    sort_order: int
    notes: str | None
    measurements: list[MeasurementRead]


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    session_at: datetime | None
    status: str
    notes: str | None
    intensity: int | None
    plan_id: uuid.UUID | None
    source_session_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    items: list[SessionItemRead]
