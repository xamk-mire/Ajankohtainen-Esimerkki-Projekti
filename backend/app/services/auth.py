from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import create_user, get_user_by_email
from app.schemas.auth import RegisterRequest


class DuplicateEmailError(Exception):
    """Raised when register is attempted with an email that already exists."""


def register_user(db: Session, data: RegisterRequest) -> User:
    if get_user_by_email(db, data.email) is not None:
        raise DuplicateEmailError()

    user = create_user(
        db,
        email=data.email,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmailError() from None
    db.refresh(user)
    return user
