import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

GoalPeriod = Literal["week", "month"]


class GoalCreate(BaseModel):
    unit_type_id: uuid.UUID
    activity_type_id: uuid.UUID | None = None
    target_value: Decimal = Field(gt=0)
    period: GoalPeriod
    active: bool = True


class GoalUpdate(BaseModel):
    unit_type_id: uuid.UUID | None = None
    activity_type_id: uuid.UUID | None = None
    target_value: Decimal | None = Field(default=None, gt=0)
    period: GoalPeriod | None = None
    active: bool | None = None


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    unit_type_id: uuid.UUID
    activity_type_id: uuid.UUID | None
    target_value: Decimal
    period: str
    active: bool
    created_at: datetime
