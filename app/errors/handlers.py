from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import AuthenticationError, ServiceError


def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    headers = (
        {"WWW-Authenticate": "Bearer"} if isinstance(exc, AuthenticationError) else None
    )
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}, headers=headers
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ServiceError, service_error_handler)
