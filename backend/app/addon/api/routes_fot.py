from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

from ..fot.service import get_plan, recompute_plan, get_mass_map
from ..adapters_fixture import FixtureTracePort, FixtureClockPort

router = APIRouter()

class RecomputeRequest(BaseModel):
    seed_amount: float
    K: int = 5

@router.get("/cases/{case_id}/plan")
def read_plan(case_id: str):
    plan = get_plan(case_id)
    if not plan:
        return {"message": "No plan found. Recompute first."}
    return plan

@router.post("/cases/{case_id}/plan/recompute")
def post_recompute(case_id: str, req: RecomputeRequest):
    trace_port = FixtureTracePort()
    clock_port = FixtureClockPort()
    graph = trace_port.get_case_graph(case_id)
    plan = recompute_plan(case_id, Decimal(str(req.seed_amount)), graph, clock_port.now(), req.K)
    return plan

@router.get("/cases/{case_id}/mass-map")
def read_mass_map(case_id: str):
    mmap = get_mass_map(case_id)
    if not mmap:
        raise HTTPException(status_code=404, detail="Mass map not found")
    return mmap
