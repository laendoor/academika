from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.auth.dependencies import AdminRole
from app.auth.domains import ALLOWED_DOMAINS_KEY, normalize_domains
from app.schemas.settings import SettingResponse, SettingUpdate
from app.services.settings import SettingService

router = APIRouter()

ServiceDep = Annotated[SettingService, Depends(SettingService.dep)]


@router.get("", response_model=list[SettingResponse], dependencies=[AdminRole])
async def list_settings(service: ServiceDep):
    return await service.list_all()


@router.put("/{key}", response_model=SettingResponse, dependencies=[AdminRole])
async def update_setting(key: Annotated[str, Path(max_length=100)], body: SettingUpdate, service: ServiceDep):
    if key == ALLOWED_DOMAINS_KEY:
        body = SettingUpdate(value=normalize_domains(body.value))
    return await service.update_value(key, body)
