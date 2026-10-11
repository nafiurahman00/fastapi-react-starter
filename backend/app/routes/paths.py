"""The route catalog: every URL path of the API in one place."""

API_PREFIX = "/api"

# ---- Authentication (base: /api/auth) ----
AUTH = "/auth"
REGISTER = "/register"  # POST /api/auth/register
LOGIN = "/login"        # POST /api/auth/login

# ---- Tasks (base: /api/tasks) ----
TASKS = "/tasks"
TASK_BY_ID = "/{task_id}"  # GET/PUT/DELETE /api/tasks/{task_id}
