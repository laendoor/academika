import analytika
from fastapi import APIRouter, Request

from app.auth.dependencies import DirectorOrAdminRole
from app.errors import NotFoundError
from app.schemas.analytics import MetricaInfo
from app.session import SessionDep

router = APIRouter(dependencies=[DirectorOrAdminRole])


@router.get("", response_model=list[MetricaInfo])
async def list_metrics() -> list[MetricaInfo]:
    return [MetricaInfo(key=m.key, name=m.name) for m in analytika.list_metrics()]


@router.get("/{nombre}")
async def run_metric(nombre: str, request: Request, session: SessionDep) -> dict:
    metrica = analytika.find_metric(nombre)
    if metrica is None:
        raise NotFoundError("metrica", nombre)
    return await metrica.run(session, _query_params(request))


def _query_params(request: Request) -> dict[str, str | list[str]]:
    params: dict[str, str | list[str]] = {}
    for key in request.query_params:
        values = request.query_params.getlist(key)
        params[key] = values[0] if len(values) == 1 else values
    return params
