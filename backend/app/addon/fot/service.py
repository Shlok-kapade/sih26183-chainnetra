from decimal import Decimal
from datetime import datetime
from .mass_map import build_mass_map
from .levers import get_lever_options
from .planner import greedy_plan, ActionPlan

_plan_cache = {}
_mass_map_cache = {}

def recompute_plan(case_id: str, seed_amount: Decimal, graph: dict, t: datetime, K: int = 5) -> ActionPlan:
    mass_map = build_mass_map(case_id, t, graph, seed_amount)
    _mass_map_cache[case_id] = mass_map
    
    levers = get_lever_options(mass_map)
    plan = greedy_plan(case_id, levers, K=K)
    _plan_cache[case_id] = plan
    return plan

def get_plan(case_id: str) -> ActionPlan | None:
    return _plan_cache.get(case_id)
    
def get_mass_map(case_id: str):
    return _mass_map_cache.get(case_id)
