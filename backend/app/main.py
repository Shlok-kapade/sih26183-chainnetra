from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1.api import api_router
from app.core.errors import setup_error_handlers
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="ChainNetra API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_error_handlers(app)
app.include_router(health_router, tags=["health"])
app.include_router(api_router, prefix="/api/v1")
