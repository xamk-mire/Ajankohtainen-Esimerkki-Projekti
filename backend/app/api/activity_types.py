from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.activity_type import ActivityTypeCreate, ActivityTypeRead
from app.services.activity_types import (
    DuplicateActivitySlugError,
    InvalidActivityTypeError,
    create_custom_activity_type,
    list_activity_types,
)

router = APIRouter(prefix="/activity-types", tags=["activity-types"])


@router.get("", response_model=list[ActivityTypeRead])
def list_my_activity_types(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> list[ActivityTypeRead]:
    return [
        ActivityTypeRead.model_validate(activity)
        for activity in list_activity_types(db, current_user)
    ]


@router.post("", response_model=ActivityTypeRead, status_code=status.HTTP_201_CREATED)
def create_my_activity_type(
    body: ActivityTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
) -> ActivityTypeRead:
    try:
        activity = create_custom_activity_type(db, current_user, body)
    except DuplicateActivitySlugError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Activity type slug already exists",
        ) from None
    except InvalidActivityTypeError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.detail,
        ) from None
    return ActivityTypeRead.model_validate(activity)
