from datetime import datetime

from pydantic import BaseModel


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
