from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.errors import ConflictError, NotFoundError
from app.models.setting import Setting
from app.schemas.settings import SettingUpdate
from app.services.base import BaseService


class SettingService(BaseService[Setting, SettingUpdate, SettingUpdate]):
    model = Setting

    async def list_all(self) -> list[Setting]:
        result = await self.session.execute(select(Setting).order_by(Setting.key))
        return list(result.scalars().all())

    async def find_by_key(self, key: str) -> Setting | None:
        result = await self.session.execute(select(Setting).where(Setting.key == key))
        return result.scalar_one_or_none()

    async def get_by_key(self, key: str) -> Setting:
        setting = await self.find_by_key(key)
        if setting is None:
            raise NotFoundError("settings", key)
        return setting

    async def update_value(self, key: str, data: SettingUpdate) -> Setting:
        setting = await self.get_by_key(key)
        setting.value = data.value
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(str(e.orig)) from e
        await self.session.refresh(setting)
        return setting
