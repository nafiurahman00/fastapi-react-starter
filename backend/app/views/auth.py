from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base view: snake_case in Python, camelCase on the wire (React-friendly)."""

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class RegisterRequest(CamelModel):
    name: str = Field(min_length=1, description="Display name")
    email: EmailStr
    password: str = Field(min_length=6, description="At least 6 characters")


class LoginRequest(CamelModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AuthResponse(CamelModel):
    """Returned by register/login. Send `token` back as `Authorization: Bearer <token>`."""

    token: str
    user_id: int
    name: str
    email: str
    role: str
