from fastapi import FastAPI

from app.routes import users

app = FastAPI(title="BEON High School API")

app.include_router(users.router)
