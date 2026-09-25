from fastapi import FastAPI

from app.errors.handlers import register_error_handlers
from app.routes import courses, enrollments, users

app = FastAPI(title="BEON High School API")

register_error_handlers(app)

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
