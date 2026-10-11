from datetime import datetime

from pydantic import Field, field_validator

from app.views.auth import CamelModel


class TaskRequest(CamelModel):
    """Body for creating / updating a task."""

    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title is required")
        return v


class TaskResponse(CamelModel):
    """Outgoing task. A view, not the model, so internals never leak."""

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
