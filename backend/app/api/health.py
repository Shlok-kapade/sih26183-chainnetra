from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    mode: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    mode = "live" if settings.LIVE_MODE else "fixture"
    return HealthResponse(status="ok", mode=mode, version=settings.VERSION)

@router.get("/version", response_model=HealthResponse)
async def version() -> HealthResponse:
    mode = "live" if settings.LIVE_MODE else "fixture"
    return HealthResponse(status="ok", mode=mode, version=settings.VERSION)
