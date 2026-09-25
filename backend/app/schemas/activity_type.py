import re
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

_SLUG = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def slugify_activity_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug[:100]


class ActivityUnitLinkWrite(BaseModel):
    unit_type_id: uuid.UUID
    sort_order: int = Field(default=0, ge=0)
    is_required: bool = True
    per_set: bool = False


class ActivityTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str | None = Field(default=None, max_length=100)
    unit_links: list[ActivityUnitLinkWrite] = Field(min_length=1)

    @field_validator("slug")
    @classmethod
    def slug_shape(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not _SLUG.fullmatch(normalized):
            raise ValueError("Slug must use lowercase letters, digits, and underscores")
        return normalized


class UnitTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    unit_label: str | None


class ActivityUnitLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    unit_type_id: uuid.UUID
    sort_order: int
    is_required: bool
    per_set: bool
    unit_type: UnitTypeRead


class ActivityTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    is_system: bool
    user_id: uuid.UUID | None
    unit_links: list[ActivityUnitLinkRead]
