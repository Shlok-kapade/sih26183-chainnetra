from fastapi import APIRouter
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/cases", tags=["addon-watch"])

_watcher_store: dict = {}  # case_id -> FrontierWatcher

class WatchRequest(BaseModel):
    position_ref: str
    value: float
    seed_amount: float

@router.post("/{case_id}/watch")
async def start_watch(case_id: str, req: WatchRequest):
    from app.addon.fot.watch import FrontierWatcher
    from app.addon.adapters_existing import ExistingTracePort, RealClockPort
    from app.addon.adapters_fixture import FixtureBudgetPort, FixtureNotifyPort
    watcher = FrontierWatcher(
        trace=ExistingTracePort(),
        clock=RealClockPort(),
        budget=FixtureBudgetPort(limit=200),
        notify=FixtureNotifyPort(),
        seed_amount=Decimal(str(req.seed_amount)),
    )
    watcher.add_watch(case_id, req.position_ref, Decimal(str(req.value)))
    _watcher_store[case_id] = watcher
    return {"status": "watching", "case_id": case_id, "position": req.position_ref, "illustrative": True}

@router.get("/{case_id}/watch")
def get_watch_status(case_id: str):
    watcher = _watcher_store.get(case_id)
    if not watcher:
        return {"case_id": case_id, "watching": False}
    w = watcher.get_watch(case_id)
    if not w:
        return {"case_id": case_id, "watching": False}
    return {
        "case_id": case_id, "watching": True,
        "position_ref": w.position_ref,
        "status": w.status,
        "last_hazard": w.last_hazard,
        "illustrative": True,
        "note": "Hazard estimate uses ILLUSTRATIVE model coefficients.",
    }
