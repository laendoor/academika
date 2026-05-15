import uuid
from datetime import datetime

from pydantic import BaseModel


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    doc_id: str
    email: str | None = None
    degree_id: uuid.UUID
    plan_id: uuid.UUID | None = None
    academic_status: str


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    degree_id: uuid.UUID | None = None
    plan_id: uuid.UUID | None = None
    academic_status: str | None = None


class StudentResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    doc_id: str
    email: str | None
    degree_id: uuid.UUID
    plan_id: uuid.UUID | None
    academic_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
