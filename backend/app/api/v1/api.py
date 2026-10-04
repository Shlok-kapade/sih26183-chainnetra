from fastapi import APIRouter

from app.api.v1.endpoints import auth, complaints, cases
from app.api.v1.endpoints.evidence import router as evidence_router

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["complaints"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(evidence_router, prefix="/cases", tags=["evidence"])
