import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AdherenceRead(BaseModel):
    """Planned versus actual for one unit. Sprint 4 can chart ``GET /sessions/adherence``."""

    model_config = ConfigDict(from_attributes=True)

    unit_type_id: uuid.UUID
    compared: int = Field(
        description="Measurements in range where both planned_value and actual_value are set.",
    )
    planned_total: Decimal = Field(description="Sum of planned_value for this unit only.")
    actual_total: Decimal = Field(description="Sum of actual_value for this unit only.")
    hit_count: int = Field(
        description="Compared measurements where actual_value is greater than or equal to planned_value.",
    )
