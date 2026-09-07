import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 72

# Small local blocklist for demos — not a full breach list.
COMMON_PASSWORDS = frozenset(
    {
        "password",
        "password1",
        "12345678",
        "123456789",
        "qwerty123",
        "letmein1",
    }
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        description=(
            f"At least {PASSWORD_MIN_LENGTH} characters, at most "
            f"{PASSWORD_MAX_LENGTH}. Must not be a common password."
        ),
    )
    display_name: str = Field(min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def reject_common_passwords(cls, value: str) -> str:
        if value.lower() in COMMON_PASSWORDS:
            raise ValueError(
                "Password is too common. Choose a longer unique password."
            )
        return value


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    display_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
