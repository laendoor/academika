from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import AdminRole
from app.schemas.settings import SettingResponse, SettingUpdate
from app.services.settings import SettingService

router = APIRouter()

ServiceDep = Annotated[SettingService, Depends(SettingService.dep)]


@router.get("", response_model=list[SettingResponse], dependencies=[AdminRole])
async def list_settings(service: ServiceDep):
    return await service.list_all()


@router.put("/{key}", response_model=SettingResponse, dependencies=[AdminRole])
async def update_setting(key: str, body: SettingUpdate, service: ServiceDep):
    return await service.update_value(key, body)
