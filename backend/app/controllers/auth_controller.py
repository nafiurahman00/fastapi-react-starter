from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import auth_service
from app.views.auth import AuthResponse, LoginRequest, RegisterRequest


def register(data: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Create an account and return a JWT."""
    return auth_service.register(db, data)


def login(data: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Exchange email + password for a JWT."""
    return auth_service.login(db, data)
