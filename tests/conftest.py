from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.db import engine, get_db
from app.main import app
from app.models.courses import Course
from app.models.user import User


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
def client(db):
    app.dependency_overrides[get_db] = lambda: db

    yield TestClient(app)

    app.dependency_overrides.clear()


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
