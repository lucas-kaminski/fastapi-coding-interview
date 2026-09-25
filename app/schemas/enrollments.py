from datetime import datetime

from pydantic import BaseModel


class EnrollmentRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int
