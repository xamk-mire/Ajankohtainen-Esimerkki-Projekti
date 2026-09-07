"""Password hashing (bcrypt) and JWT helpers.

Bcrypt only uses the first 72 bytes of a password; longer values are rejected.
JWT payload is minimal: ``sub`` (user id) and ``exp``. Password hashes never
go into tokens.
"""

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import get_settings

BCRYPT_MAX_PASSWORD_BYTES = 72
JWT_ALGORITHM = "HS256"


def _password_bytes(plain: str) -> bytes:
    encoded = plain.encode("utf-8")
    if len(encoded) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError(
            f"Password exceeds bcrypt's {BCRYPT_MAX_PASSWORD_BYTES}-byte limit."
        )
    return encoded


def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(_password_bytes(plain), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    try:
        encoded = plain.encode("utf-8")
        if len(encoded) > BCRYPT_MAX_PASSWORD_BYTES:
            return False
        return bcrypt.checkpw(encoded, password_hash.encode("utf-8"))
    except (TypeError, ValueError):
        return False


def create_access_token(subject: uuid.UUID | str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """Return the token subject (user id string). Raises InvalidTokenError."""
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[JWT_ALGORITHM],
    )
    subject = payload.get("sub")
    if not subject:
        raise InvalidTokenError("Token is missing subject")
    return str(subject)
