import uuid
from datetime import datetime

from pydantic import BaseModel


class CourseCreate(BaseModel):
    name: str
    code: str
    abbreviation: str | None = None


class CourseUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    abbreviation: str | None = None


class CourseResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    abbreviation: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
