from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.db import engine, get_db
from app.core.security import create_access_token
from app.main import app
from app.models.courses import Course
from app.models.user import Role, User


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client_for(db):
    app.dependency_overrides[get_db] = lambda: db

    def make(user=None):
        if user is None:
            return TestClient(app)
        token = create_access_token(user.id)
        return TestClient(app, headers={"Authorization": f"Bearer {token}"})

    yield make

    app.dependency_overrides.clear()


@pytest.fixture
def client(client_for, make_user):
    return client_for(make_user(role=Role.ADMIN))


@pytest.fixture
def make_user(db):
    def make(**fields):
        defaults = {
            "first_name": "Lucas",
            "last_name": "Kaminski",
            "email": f"{uuid4().hex}@example.com",
            "hashed_password": "hashed",
        }
        user = User(**{**defaults, **fields})
        db.add(user)
        db.flush()
        return user

    return make


@pytest.fixture
def make_course(db):
    def make(**fields):
        course = Course(**{"title": "Math", "description": "Algebra", **fields})
        db.add(course)
        db.flush()
        return course

    return make
