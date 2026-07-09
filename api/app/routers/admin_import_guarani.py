from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile

from app.auth.dependencies import require_role
from app.db.session import SessionFactoryDep
from app.errors import BusinessError
from app.models.user import User
from app.schemas.imports import ImportAcceptedResponse
from app.services.guarani_upload_service import GuaraniUploadService

router = APIRouter()

AdminRole = Annotated[User, Depends(require_role("admin"))]


def _build_service(session_factory: SessionFactoryDep) -> GuaraniUploadService:
    return GuaraniUploadService.dep(session_factory)


UploadServiceDep = Annotated[GuaraniUploadService, Depends(_build_service)]


@router.post("", response_model=ImportAcceptedResponse)
async def accept_upload(
    user: AdminRole,
    service: UploadServiceDep,
    background_tasks: BackgroundTasks,
    files: Annotated[list[UploadFile], File()],
) -> ImportAcceptedResponse:
    if not files:
        raise BusinessError("no se recibieron archivos")
    payloads = [(f.filename or "", await f.read()) for f in files]
    background_tasks.add_task(service.process_upload, user.id, payloads)
    return ImportAcceptedResponse(status="processing", count=len(payloads))
