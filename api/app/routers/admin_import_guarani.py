from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile

from app.auth.dependencies import require_role
from app.db.session import SessionFactoryDep
from app.models.user import User
from app.schemas.imports import ImportAcceptedResponse
from app.services.guarani_upload_service import GuaraniUploadService

router = APIRouter()

AdminRole = Annotated[User, Depends(require_role("admin"))]


def _build_service(session_factory: SessionFactoryDep) -> GuaraniUploadService:
    return GuaraniUploadService.dep(session_factory)


UploadServiceDep = Annotated[GuaraniUploadService, Depends(_build_service)]

_MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("", response_model=ImportAcceptedResponse)
async def accept_upload(
    user: AdminRole,
    service: UploadServiceDep,
    background_tasks: BackgroundTasks,
    files: Annotated[list[UploadFile], File()],
) -> ImportAcceptedResponse:
    payloads: list[tuple[str, bytes]] = []
    for f in files:
        if f.size and f.size > _MAX_FILE_SIZE:
            # Skip oversized files at read time — _process_one re-checks but
            # this prevents loading 2GB into RAM before the background task.
            continue
        payloads.append((f.filename or "", await f.read()))
    background_tasks.add_task(service.process_upload, user.id, payloads)
    return ImportAcceptedResponse(status="processing", count=len(payloads))
