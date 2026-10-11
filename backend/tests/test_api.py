def register(client, email="ada@example.com"):
    r = client.post("/api/auth/register", json={"name": "Ada", "email": email, "password": "secret123"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_login_and_duplicate(client):
    register(client)
    assert client.post("/api/auth/register", json={"name": "A", "email": "ada@example.com", "password": "secret123"}).status_code == 409
    ok = client.post("/api/auth/login", json={"email": "ada@example.com", "password": "secret123"})
    assert ok.status_code == 200 and ok.json()["role"] == "USER"
    bad = client.post("/api/auth/login", json={"email": "ada@example.com", "password": "nope"})
    assert bad.status_code == 401 and bad.json()["message"] == "Invalid email or password"


def test_validation_error_shape(client):
    r = client.post("/api/auth/register", json={"name": "A", "email": "bad", "password": "1"})
    body = r.json()
    assert r.status_code == 422 and body["message"] == "Validation failed"
    assert {"email", "password"} <= set(body["fieldErrors"])


def test_tasks_require_auth(client):
    r = client.get("/api/tasks")
    assert r.status_code == 401 and r.json()["status"] == 401
    assert client.get("/api/tasks", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_task_crud_and_ownership(client):
    h = register(client)
    created = client.post("/api/tasks", json={"title": "Do it", "description": "now", "completed": False}, headers=h)
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Do it" and "createdAt" in task

    assert len(client.get("/api/tasks", headers=h).json()) == 1
    upd = client.put(f"/api/tasks/{task['id']}", json={"title": "Done", "description": "x", "completed": True}, headers=h)
    assert upd.json()["completed"] is True

    other = register(client, "bob@example.com")
    assert client.get(f"/api/tasks/{task['id']}", headers=other).status_code == 404
    assert client.get("/api/tasks", headers=other).json() == []

    assert client.delete(f"/api/tasks/{task['id']}", headers=h).status_code == 204
    assert client.get(f"/api/tasks/{task['id']}", headers=h).status_code == 404
