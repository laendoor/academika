import uuid
from datetime import datetime

from pydantic import BaseModel


class StudyPlanCreate(BaseModel):
    degree_id: uuid.UUID
    name: str
    year: int
    is_active: bool = True
    course_ids: list[uuid.UUID] = []


class StudyPlanUpdate(BaseModel):
    name: str | None = None
    year: int | None = None
    is_active: bool | None = None
    course_ids: list[uuid.UUID] | None = None


class StudyPlanResponse(BaseModel):
    id: uuid.UUID
    degree_id: uuid.UUID
    name: str
    year: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
