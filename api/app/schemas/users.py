import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.auth import UserRole


class UserCreate(BaseModel):
    email: str
    role: UserRole
    hashed_password: str


class UserUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
