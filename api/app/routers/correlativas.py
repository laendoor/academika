import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import DirectorOrAdminRole
from app.schemas.common import PaginatedResponse
from app.schemas.correlativas import CorrelativaResponse
from app.services.correlativas import CorrelativaService

router = APIRouter(dependencies=[DirectorOrAdminRole])

ServiceDep = Annotated[CorrelativaService, Depends(CorrelativaService.dep)]


@router.get("", response_model=PaginatedResponse[CorrelativaResponse])
async def list_correlativas(
    service: ServiceDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    materia_id: uuid.UUID | None = None,
):
    total, items = await service.list_filtered(skip=skip, limit=limit, materia_id=materia_id)
    return PaginatedResponse(total=total, items=items)
