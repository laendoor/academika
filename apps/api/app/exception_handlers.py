from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import AcademikaError


async def academika_error_handler(request: Request, exc: AcademikaError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AcademikaError, academika_error_handler)  # type: ignore[arg-type]
