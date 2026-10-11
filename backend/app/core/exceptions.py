"""Domain exceptions + handlers that turn them into one JSON error shape.

    {
      "timestamp": "2026-01-01T10:00:00Z",
      "status": 404,
      "error": "Not Found",
      "message": "Task not found with id 5",
      "path": "/api/tasks/5"
    }

`fieldErrors` is added for validation failures (HTTP 422).
"""
from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Base class: subclasses set the HTTP status and a message."""

    status_code = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ResourceNotFoundError(AppError):
    status_code = 404

    def __init__(self, resource: str, identifier: object):
        super().__init__(f"{resource} not found with id {identifier}")


class EmailAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, email: str):
        super().__init__(f"Email already registered: {email}")


class InvalidCredentialsError(AppError):
    status_code = 401

    def __init__(self):
        super().__init__("Invalid email or password")


class UnauthorizedError(AppError):
    status_code = 401


def _body(status: int, message: str, path: str, field_errors: dict | None = None) -> dict:
    body = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "error": HTTPStatus(status).phrase,
        "message": message,
        "path": path,
    }
    if field_errors:
        body["fieldErrors"] = field_errors
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse(
            _body(exc.status_code, exc.message, request.url.path),
            status_code=exc.status_code,
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError):
        field_errors = {}
        for err in exc.errors():
            # loc looks like ("body", "email"); keep the field name.
            field = ".".join(str(p) for p in err["loc"][1:]) or str(err["loc"][0])
            field_errors[field] = err["msg"]
        return JSONResponse(
            _body(422, "Validation failed", request.url.path, field_errors),
            status_code=422,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            _body(exc.status_code, str(exc.detail), request.url.path),
            status_code=exc.status_code,
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        # In a real app, log the full stack trace here.
        return JSONResponse(
            _body(500, "Something went wrong", request.url.path), status_code=500
        )
