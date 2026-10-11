# FastAPI + React Starter

A full-stack starter project for building web applications. The **backend** is a
FastAPI REST API organized in a strict **MVC** layout with JWT authentication.
The **frontend** is a minimal React (Vite) application that consumes the API.
Clone it, rename things, and start building your own features.

The database is **MySQL**. You can later switch to PostgreSQL, Supabase, or
MongoDB; see [Switching databases](#switching-databases).

## Contents

- [Project structure](#project-structure)
- [Prerequisites and installation](#prerequisites-and-installation)
- [Getting started](#getting-started)
- [API reference](#api-reference)
- [Frontend overview](#frontend-overview)
- [Switching databases](#switching-databases)
- [Troubleshooting](#troubleshooting)
- [Building for production](#building-for-production)

## Project structure

```
fastapi-react-starter/
├── backend/      FastAPI REST API (Python 3.10+) - see backend/README.md
└── frontend/     React + Vite single-page application
```

The backend follows **Model - View - Controller**, plus the supporting layers a
real API needs:

| MVC part       | Folder                      | What lives there                         |
|----------------|-----------------------------|------------------------------------------|
| **Model**      | `app/models/`               | SQLAlchemy tables (`User`, `Task`)       |
| **View**       | `app/views/`                | Pydantic schemas = the JSON in and out   |
| **Controller** | `app/controllers/`          | Request handlers, no business logic      |
| Routes         | `app/routes/`               | URL paths wired to controllers           |
| Services       | `app/services/`             | Business logic                           |
| Repositories   | `app/repositories/`         | Database queries                         |
| Core           | `app/core/`                 | Settings, DB session, JWT, error handling|

The full layout and a step-by-step request flow are in the
**[backend README](backend/README.md)**.

```
frontend/src/
├── api/          fetch() wrapper (attaches the JWT automatically)
├── auth/         AuthContext (login / register / logout state)
├── components/   NavBar, ProtectedRoute
└── pages/        Login, Register, Tasks
```

## Prerequisites and installation

| Tool    | Version | Purpose                  | Check              |
|---------|---------|--------------------------|--------------------|
| Python  | 3.10+   | Run the backend          | `python3 --version`|
| Node.js | 18+     | Run the frontend         | `node -v`          |
| MySQL   | 8+      | Database                 | `mysql --version`  |

### Download pages

- Python: https://www.python.org/downloads/
- Node.js (LTS): https://nodejs.org/en/download
- MySQL Community Server: https://dev.mysql.com/downloads/mysql/

### Install commands

**Linux (Debian / Ubuntu)**

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip mysql-server
# Node.js 20 LTS (via NodeSource):
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

**macOS (Homebrew)** - install Homebrew first from https://brew.sh

```bash
brew install python node mysql
brew services start mysql        # start the MySQL server
```

**Windows (winget)** - or use the download pages above

```powershell
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
winget install Oracle.MySQL
```

After installing, open a new terminal and confirm each `Check` command above
prints a version.

## Getting started

### 1. Backend

Make sure MySQL is installed and running, then create the database and an
application user:

```bash
sudo mysql          # on Windows/macOS: mysql -u root -p
```

```sql
CREATE DATABASE app_db;
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'apppass';
GRANT ALL PRIVILEGES ON app_db.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Create a virtual environment, install dependencies, and configure:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # defaults match the SQL above
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The backend starts on http://localhost:8000. Tables are created automatically on
startup. Interactive API docs (Swagger UI) are at http://localhost:8000/docs and
ReDoc at http://localhost:8000/redoc.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend starts on http://localhost:5173. Open it, register an account, and
manage your tasks. The Vite dev server proxies `/api/*` to the backend, so you
do not deal with CORS during development.

## API reference

| Method | Endpoint             | Auth | Description                   |
|--------|----------------------|------|-------------------------------|
| POST   | `/api/auth/register` | No   | Create an account, get JWT    |
| POST   | `/api/auth/login`    | No   | Log in, get a JWT             |
| GET    | `/api/tasks`         | Yes  | List the current user's tasks |
| GET    | `/api/tasks/{id}`    | Yes  | Get one task                  |
| POST   | `/api/tasks`         | Yes  | Create a task                 |
| PUT    | `/api/tasks/{id}`    | Yes  | Update a task                 |
| DELETE | `/api/tasks/{id}`    | Yes  | Delete a task                 |
| GET    | `/health`            | No   | Liveness check                |

Errors always have the same JSON shape (`status`, `error`, `message`, `path`,
and `fieldErrors` for validation failures, which return HTTP 422).

### Example with curl

```bash
# Register (returns { "token": "...", ... })
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada","email":"ada@example.com","password":"secret123"}'

# Save the token, then create a task:
TOKEN=paste-the-token-here
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Finish assignment","description":"Due Friday","completed":false}'

# List your tasks:
curl http://localhost:8000/api/tasks -H "Authorization: Bearer $TOKEN"
```

Prefer a UI? Open http://localhost:8000/docs, call `/api/auth/login`, click
**Authorize**, paste the token, and try every endpoint.

## Frontend overview

The frontend is intentionally small so it is easy to read:

- `api/client.js` - a thin wrapper around `fetch` that sets the base URL, JSON
  headers, and the `Authorization: Bearer <token>` header automatically.
- `auth/AuthContext.jsx` - React context holding the logged-in user; exposes
  `login`, `register`, and `logout`. The token is kept in `localStorage`.
- `components/ProtectedRoute.jsx` - redirects to `/login` when there is no user.
- `pages/` - `LoginPage`, `RegisterPage`, and `TasksPage` (full CRUD demo).

To point the built frontend at a deployed backend, copy `.env.example` to `.env`
and set `VITE_API_URL`.

## Switching databases

The project uses MySQL, but SQLAlchemy hides most differences. In most cases you
change only `DATABASE_URL` in `backend/.env` and install the matching driver.

### PostgreSQL

```bash
pip install "psycopg[binary]"
```

```env
DATABASE_URL=postgresql+psycopg://postgres:your-password@localhost:5432/app_db
```

### Supabase (hosted PostgreSQL)

Supabase is PostgreSQL, so install the same driver and use the connection string
from the dashboard (Project -> Settings -> Database -> Connection string),
changing the scheme to `postgresql+psycopg://`:

```env
DATABASE_URL=postgresql+psycopg://postgres:your-supabase-password@db.<project-ref>.supabase.co:5432/postgres
```

Keep real passwords in `.env` (git-ignored) or real environment variables.

### SQLite (zero setup, handy for experiments)

```env
DATABASE_URL=sqlite:///./app.db
```

### MongoDB (different data model, more than a config change)

MongoDB is a document database and does not use SQLAlchemy:

1. Replace `sqlalchemy`/`pymysql` with a Mongo library such as
   [Beanie](https://beanie-odm.dev/) (async ODM) or `pymongo`.
2. Rewrite `app/models/` as documents (ids are usually strings) and
   `app/repositories/` to use that library.
3. Keep `app/views/`, `app/controllers/`, `app/routes/` and the service
   structure; only the id types in the views change from `int` to `str`.

That the upper layers barely change is the benefit of keeping business logic out
of the data layer.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Can't connect to MySQL server` | MySQL is not running, or `DATABASE_URL` in `backend/.env` is wrong. Start MySQL and verify the database and user exist. |
| `Access denied for user` | Wrong username/password in `DATABASE_URL`, or the user lacks privileges on `app_db`. Re-check the `CREATE USER` / `GRANT` step. |
| `RuntimeError: 'cryptography' package is required` | Run `pip install -r requirements.txt` (MySQL 8 auth needs it). |
| `ModuleNotFoundError: No module named 'app'` | Run `uvicorn` from inside the `backend/` folder. |
| Port 8000 already in use | `uvicorn app.main:app --reload --port 8001` and update the proxy `target` in `frontend/vite.config.js`. |
| `npm run dev` fails | Run `npm install` first; Node 18+ is required. |
| Tasks return 401 | The token is missing or expired - log in again. Tokens last 24h by default. |
| CORS error (only if not using the proxy) | Add your frontend origin to `CORS_ALLOWED_ORIGINS` in `backend/.env`. |

## Building for production

```bash
# Backend: run with several workers, no --reload
cd backend && pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend -> static files in frontend/dist/
cd frontend && npm run build
```

Before deploying: set a strong `JWT_SECRET`, provide `DATABASE_URL` through
environment variables, and replace the create-tables-on-startup call
(`init_db()` in `app/main.py`) with [Alembic](https://alembic.sqlalchemy.org/)
migrations.
