import uuid

from sqlalchemy import select

from app.errors import BusinessError
from app.models.user import User
from app.schemas.users import UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    model = User

    async def find_by_id(self, id: uuid.UUID) -> User | None:
        return await self.session.get(User, id)

    async def find_active_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email, User.is_active))
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update(self, id: uuid.UUID, data: UserUpdate, requester_id: uuid.UUID | None = None) -> User:
        instance = await self.get_by_id(id)
        self._ensure_no_self_lockout(instance, data, requester_id)
        return await super().update(id, data)

    def _ensure_no_self_lockout(self, instance: User, data: UserUpdate, requester_id: uuid.UUID | None) -> None:
        if requester_id != instance.id or instance.role != "admin":
            return
        new_role = data.role or instance.role
        new_active = instance.is_active if data.is_active is None else data.is_active
        if new_role == "admin" and new_active:
            return
        raise BusinessError("Un admin no puede quitarse el rol admin ni desactivarse a sí mismo")
