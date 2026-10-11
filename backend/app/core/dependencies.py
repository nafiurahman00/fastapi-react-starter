"""Reusable FastAPI dependencies (the "security filter" of this app)."""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories import user_repository

# auto_error=False so *we* return our JSON 401 instead of FastAPI's default 403.
# It also adds the "Authorize" button to Swagger UI.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve `Authorization: Bearer <jwt>` to a User, or raise 401."""
    if credentials is None:
        raise UnauthorizedError("Authentication required")
    email = decode_access_token(credentials.credentials)
    if email is None:
        raise UnauthorizedError("Invalid or expired token")
    user = user_repository.find_by_email(db, email)
    if user is None:
        raise UnauthorizedError("Invalid or expired token")
    return user
