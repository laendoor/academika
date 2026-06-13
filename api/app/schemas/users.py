from pydantic import BaseModel

from app.schemas.auth import UserRole


class UserCreate(BaseModel):
    email: str
    role: UserRole
    hashed_password: str
