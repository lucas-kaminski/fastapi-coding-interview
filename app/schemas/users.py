from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import Role


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: Role
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    role: Role | None = None
