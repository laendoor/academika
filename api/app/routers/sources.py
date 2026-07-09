from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_role
from app.schemas.common import PaginatedResponse
from app.schemas.log_events import SourceResponse
from app.services.log_events import LogEventService

router = APIRouter()

DirectorOrAdminRole = Depends(require_role("director", "admin"))
ServiceDep = Annotated[LogEventService, Depends(LogEventService.dep)]


@router.get("", response_model=PaginatedResponse[SourceResponse], dependencies=[DirectorOrAdminRole])
async def list_sources(service: ServiceDep, skip: int = 0, limit: int = Query(default=20, le=100)):
    total, items = await service.list_import_guarani(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)
