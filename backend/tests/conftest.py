import os

# Use an in-memory SQLite DB for tests so MySQL is not required.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from app.core import database

database.engine.dispose()
database.engine = database.create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
database.SessionLocal.configure(bind=database.engine)

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    database.Base.metadata.drop_all(database.engine)
    with TestClient(app) as c:  # runs lifespan -> init_db()
        yield c
