from analytika.errors import MetricaError, MetricaNotFoundError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import AcademikaError


async def academika_error_handler(request: Request, exc: AcademikaError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def metrica_error_handler(request: Request, exc: MetricaError) -> JSONResponse:
    """Traduce la familia de errores de métrica; el router no captura nada."""
    status_code = 404 if isinstance(exc, MetricaNotFoundError) else 422
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AcademikaError, academika_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(MetricaError, metrica_error_handler)  # type: ignore[arg-type]
