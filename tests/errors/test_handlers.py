from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.errors import (
    AuthenticationError,
    ConflictError,
    LimitExceededError,
    NotFoundError,
    PermissionDeniedError,
)
from app.errors.handlers import register_error_handlers


def make_client(exc: Exception) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    def boom():
        raise exc

    return TestClient(app)


def test_service_errors_become_http_errors():
    cases = [
        (NotFoundError("Course not found"), 404),
        (ConflictError("Already enrolled"), 409),
        (LimitExceededError("Course is full"), 422),
    ]

    for exc, status in cases:
        response = make_client(exc).get("/boom")

        assert response.status_code == status
        assert response.json() == {"detail": exc.detail}


def test_permission_and_authentication_errors():
    response = make_client(PermissionDeniedError("Admin role required")).get("/boom")
    assert response.status_code == 403

    response = make_client(AuthenticationError("Invalid token")).get("/boom")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
