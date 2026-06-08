from fastapi import FastAPI

from app.exception_handlers import add_error_handlers
from app.routers import (
    alumnos,
    auth,
    carreras,
    cursadas,
    health,
    lookups,
    materias,
    planes_de_estudio,
)

app = FastAPI(title="Académika API")

add_error_handlers(app)

app.include_router(health.router, prefix="/health", tags=["health"])

api_prefix = "/api/v1"

app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["auth"])

app.include_router(carreras.router, prefix=f"{api_prefix}/carreras", tags=["carreras"])
app.include_router(materias.router, prefix=f"{api_prefix}/materias", tags=["materias"])
app.include_router(planes_de_estudio.router, prefix=f"{api_prefix}/planes", tags=["planes"])
app.include_router(alumnos.router, prefix=f"{api_prefix}/alumnos", tags=["alumnos"])
app.include_router(cursadas.router, prefix=f"{api_prefix}/cursadas", tags=["cursadas"])
app.include_router(lookups.router, prefix=f"{api_prefix}/lookups", tags=["lookups"])
