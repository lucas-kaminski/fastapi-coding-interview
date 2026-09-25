from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.main import app
from app.core.db import engine


@pytest.fixture
def client():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    app.dependency_overrides[get_db] = lambda: session

    yield TestClient(app)

    app.dependency_overrides.clear()
    session.close()
    transaction.rollback()
    connection.close()
