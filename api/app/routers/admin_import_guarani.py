from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.auth.dependencies import require_role
from app.schemas.imports import ImportResponse
from app.services.guarani_upload_service import GuaraniUploadService

router = APIRouter()

UploadServiceDep = Annotated[GuaraniUploadService, Depends(GuaraniUploadService.dep)]
AdminRole = Depends(require_role("admin"))


@router.post("", response_model=ImportResponse, dependencies=[AdminRole])
async def import_guarani_sheets(
    service: UploadServiceDep,
    files: Annotated[list[UploadFile], File()],
) -> ImportResponse:
    return await service.upload(files)
