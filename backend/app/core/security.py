"""Password hashing helpers (bcrypt). No FastAPI or database imports.

Bcrypt only uses the first 72 bytes of a password; longer values are rejected.
"""

import bcrypt

BCRYPT_MAX_PASSWORD_BYTES = 72


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
