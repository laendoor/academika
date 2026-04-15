from fastapi import FastAPI

from app.routers import health

app = FastAPI(title="Académika API")

app.include_router(health.router, prefix="/health", tags=["health"])
