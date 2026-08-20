import os

os.environ["DATABASE_URL"] = "sqlite:///./test_two_do_notes.db"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, SessionLocal, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_client(client):
    response = client.post("/api/v1/auth/register", json={"name": "Asha", "email": "asha@example.com", "password": "password123"})
    client.headers.update({"Authorization": f"Bearer {response.json()['access_token']}"})
    return client

