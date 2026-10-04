from fastapi import APIRouter
from typing import Dict, List, Any

router = APIRouter()

_cohort_store: Dict[str, List[Any]] = {}

def register_cohort(case_id: str, report: Any):
    if case_id not in _cohort_store:
        _cohort_store[case_id] = []
    _cohort_store[case_id].append(report)

@router.get("/cases/{case_id}/cohorts")
def get_cohorts(case_id: str):
    return {"case_id": case_id, "cohorts": _cohort_store.get(case_id, [])}
