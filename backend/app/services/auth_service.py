"""Business logic for registration and login."""
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.role import Role
from app.models.user import User
from app.repositories import user_repository
from app.views.auth import AuthResponse, LoginRequest, RegisterRequest


def register(db: Session, data: RegisterRequest) -> AuthResponse:
    email = data.email.lower()
    if user_repository.exists_by_email(db, email):
        raise EmailAlreadyExistsError(email)
    user = User(
        name=data.name,
        email=email,
        password=hash_password(data.password),  # never store the raw password
        role=Role.USER,
    )
    user_repository.save(db, user)
    return _build_response(user)


def login(db: Session, data: LoginRequest) -> AuthResponse:
    user = user_repository.find_by_email(db, data.email.lower())
    # Same error for "no such user" and "wrong password" (don't leak which).
    if user is None or not verify_password(data.password, user.password):
        raise InvalidCredentialsError()
    return _build_response(user)


def _build_response(user: User) -> AuthResponse:
    return AuthResponse(
        token=create_access_token(user.email),
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
    )
