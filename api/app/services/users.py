import uuid

from sqlalchemy import select

from app.models.user import User
from app.schemas.users import UserCreate
from app.services.base import BaseService


class UserService(BaseService[User, UserCreate, None]):
    model = User

    async def find_by_id(self, id: uuid.UUID) -> User | None:
        return await self.session.get(User, id)

    async def find_active_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email, User.is_active))
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
