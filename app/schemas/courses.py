from datetime import datetime

from pydantic import BaseModel


class CoursesRead(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CoursesCreate(BaseModel):
    title: str
    description: str


class CoursesUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
