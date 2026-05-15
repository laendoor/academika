import uuid
from datetime import datetime

from pydantic import BaseModel


class DegreeCreate(BaseModel):
    name: str
    code: str


class DegreeUpdate(BaseModel):
    name: str | None = None
    code: str | None = None


class DegreeResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
