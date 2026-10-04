from .routes_cohorts import router as cohorts_router
from fastapi import APIRouter
from .routes_fot import router as fot_router
from .routes_watch import router as watch_router

router = APIRouter(prefix="/addon", tags=["addon"])
router.include_router(fot_router)
router.include_router(watch_router)

@router.get("/health")
def addon_health():
    return {"status": "ok", "features": ["cohorts", "fot"]}

router.include_router(cohorts_router, prefix="/cohorts", tags=["cohorts"])
