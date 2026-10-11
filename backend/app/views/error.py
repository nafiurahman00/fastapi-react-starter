from datetime import datetime

from pydantic import Field

from app.views.auth import CamelModel


class ApiError(CamelModel):
    """Documents the JSON error shape (see core/exceptions.py)."""

    timestamp: datetime
    status: int
    error: str
    message: str
    path: str
    field_errors: dict[str, str] | None = Field(default=None)
