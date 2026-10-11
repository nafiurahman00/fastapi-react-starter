# Backend (FastAPI REST API)

A REST API built with FastAPI using a strict **MVC** layout and JWT
authentication. This document explains how the code is organized and how a
request flows through the layers. For installation and how to run the whole
project, see the [root README](../README.md).

## Technology

- Python 3.10+, FastAPI (routing, dependency injection, OpenAPI docs)
- SQLAlchemy 2.0 (ORM) + PyMySQL, MySQL
- Pydantic v2 (validation and serialization)
- PyJWT + bcrypt (authentication)
- Uvicorn (ASGI server), pytest (tests)

## Folder structure

```
backend/
├── app/
│   ├── main.py                 Entry point: creates the app, CORS, routers, handlers
│   │
│   ├── models/                 M - SQLAlchemy tables
│   │   ├── user.py               User
│   │   ├── role.py               Role enum (USER, ADMIN)
│   │   └── task.py               Task
│   │
│   ├── views/                  V - Pydantic schemas: the JSON going in and out
│   │   ├── auth.py               RegisterRequest, LoginRequest, AuthResponse
│   │   ├── task.py               TaskRequest, TaskResponse
│   │   └── error.py              ApiError (documents the error shape)
│   │
│   ├── controllers/            C - request handlers (thin)
│   │   ├── auth_controller.py    register, login
│   │   └── task_controller.py    list / get / create / update / delete
│   │
│   ├── routes/                 URL paths wired to controllers
│   │   ├── paths.py              the route catalog (every path string)
│   │   ├── auth_routes.py        /api/auth/*
│   │   └── task_routes.py        /api/tasks/*
│   │
│   ├── services/               Business logic
│   │   ├── auth_service.py
│   │   └── task_service.py
│   │
│   ├── repositories/           Database queries
│   │   ├── user_repository.py
│   │   └── task_repository.py
│   │
│   └── core/                   Cross-cutting infrastructure
│       ├── config.py             settings from env / .env
│       ├── database.py           engine, session, get_db, init_db
│       ├── security.py           bcrypt + JWT create/decode
│       ├── dependencies.py       get_current_user (the auth guard)
│       └── exceptions.py         domain errors + JSON error handlers
│
├── tests/                      pytest suite (uses in-memory SQLite)
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

### What each layer is responsible for

| Layer        | Responsibility                                                    | Must not do                               |
|--------------|-------------------------------------------------------------------|-------------------------------------------|
| Model        | Describe database tables                                          | Be returned directly over the API         |
| View         | Define exactly what goes in/out over HTTP, with validation        | Hold persistence or business logic        |
| Controller   | Receive the request, call a service, return a view               | Contain business logic or database code   |
| Routes       | Map HTTP method + path to a controller, set status codes/tags     | Contain any logic                         |
| Service      | Business rules and orchestration                                  | Know about HTTP (requests, status codes)  |
| Repository   | Read/write the database                                           | Contain business rules                    |
| Core         | Settings, DB session, security, error handling                    | Depend on controllers or services         |

Dependencies point one way: `routes -> controllers -> services -> repositories
-> models`, with `views` shared by routes/controllers/services and `core`
available to everyone. Keep it that way and each layer can change independently.

### If you come from Node / Express

| Express        | Here                                          |
|----------------|-----------------------------------------------|
| `routes/`      | `routes/` (`router.add_api_route(path, handler)`) |
| `controllers/` | `controllers/` (plain functions)              |
| `models/`      | `models/` + `repositories/`                   |
| `joi`/`zod`    | `views/` (Pydantic)                           |
| middleware     | `core/dependencies.py` (`Depends(...)`)       |

Just like Express, a route file wires a path to a handler:

```python
router.add_api_route(paths.LOGIN, auth_controller.login, methods=["POST"], ...)
```

## Request flow

```
Client (browser / curl / React)
   |  HTTP request (JSON)
   v
CORS middleware
   v
Route          routes/task_routes.py      matches method + path
   v
Dependencies   get_db, get_current_user   open DB session, validate JWT -> User
   v
View (in)      TaskRequest                Pydantic validates the body (422 on failure)
   v
Controller     task_controller.create_task
   v
Service        task_service.create       business logic
   v
Repository     task_repository.save      SQLAlchemy -> SQL
   v
Database       (MySQL)
   ^
   |  Task model comes back up
   v
View (out)     TaskResponse              response_model serializes the model to JSON
```

### Worked example: `POST /api/tasks`

1. `task_routes.py` matches `POST /api/tasks` and runs its dependencies first.
2. `get_current_user` (`core/dependencies.py`) reads `Authorization: Bearer
   <token>`, validates it with `decode_access_token`, and loads the `User`. A
   missing/invalid token raises `UnauthorizedError`, rendered as a JSON 401.
3. FastAPI parses the body into a `TaskRequest` view. If validation fails, the
   handler in `core/exceptions.py` returns a 422 with per-field messages.
4. `task_controller.create_task` receives the view, the DB session, and the
   user, and calls `task_service.create(...)`.
5. `task_service.create` builds a `Task` model owned by that user and passes it
   to `task_repository.save`, which commits it.
6. The controller returns the `Task` model; because the route declares
   `response_model=TaskResponse`, FastAPI converts it to that view (camelCase
   JSON) with status `201 Created`.

### How authentication works

1. Register or log in -> the server verifies credentials and returns a **JWT**.
2. The client sends that token on every request: `Authorization: Bearer <token>`.
3. `get_current_user` validates the signature and expiry and identifies the user
   for that single request. No session is stored on the server ("stateless").
4. Passwords are hashed with **bcrypt**; raw passwords are never stored.
5. Task routes are protected by depending on `get_current_user`; auth routes are
   public.

## Configuration

Settings are read from environment variables or `backend/.env`
(see `.env.example`):

| Variable                 | Meaning                                       |
|--------------------------|-----------------------------------------------|
| `DATABASE_URL`           | SQLAlchemy URL of the database                |
| `JWT_SECRET`             | Signing key for JWTs (min 32 chars)           |
| `JWT_EXPIRATION_MINUTES` | Token lifetime (default 1440 = 24h)           |
| `CORS_ALLOWED_ORIGINS`   | Comma-separated frontend origins              |
| `ECHO_SQL`               | `true` to print every SQL statement           |

Secrets and credentials should come from environment variables in real
deployments, not be committed (`.env` is git-ignored).

## Run and test

```bash
# From the backend/ directory, with the virtualenv active:
uvicorn app.main:app --reload     # start the app (needs MySQL)
pip install -r requirements-dev.txt
pytest                            # run tests (no MySQL needed: uses SQLite)
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Adding a new feature

The Task feature is a complete template. To add, for example, a `Note` feature,
add one file in each layer and keep the same responsibilities:

1. `routes/paths.py` - add `NOTES = "/notes"`.
2. `models/note.py` - the SQLAlchemy model; export it in `models/__init__.py`.
3. `repositories/note_repository.py` - queries.
4. `views/note.py` - `NoteRequest` and `NoteResponse`.
5. `services/note_service.py` - business logic.
6. `controllers/note_controller.py` - handler functions.
7. `routes/note_routes.py` - wire paths to controllers (copy `task_routes.py`),
   then add `api_router.include_router(note_routes.router)` in
   `routes/__init__.py`.

New tables are created on the next startup.

## Extending the backend further

Add these incrementally, only when a project actually needs them:

- **Database migrations** - [Alembic](https://alembic.sqlalchemy.org/) instead of
  `create_all`, so schema changes are versioned. Recommended before any real
  deployment.
- **Pagination and sorting** - accept `skip`/`limit` query parameters in
  controllers and apply `.offset().limit()` in repositories.
- **Role-based authorization** - add a dependency like
  `require_role(Role.ADMIN)` that wraps `get_current_user`; the `Role` enum and
  `User.role` already exist.
- **Refresh tokens** - a short-lived access token plus a long-lived refresh
  token and a `/api/auth/refresh` endpoint.
- **Async database access** - SQLAlchemy async engine + `asyncmy`/`asyncpg` and
  `async def` handlers for higher concurrency.
- **Background jobs** - FastAPI `BackgroundTasks` for small jobs; Celery/ARQ for
  heavier ones (emails, reports).
- **Caching and rate limiting** - Redis with `fastapi-cache2` / `slowapi`.
- **File uploads** - `UploadFile` with disk or S3 storage.
- **Structured logging & environments** - the `logging` module with JSON output
  and a separate `.env` per environment.
- **Containerization** - a `Dockerfile` and `docker-compose.yml` to run the API
  and database together.
