from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from .levers import LeverOption
import itertools

@dataclass
class PlanAction:
    rank: int
    lever: str
    target_ref: str
    expected_secured: Decimal
    expected_secured_lo: Decimal
    expected_secured_hi: Decimal
    deadline_hours: Optional[float]
    eta_hours: float
    illustrative_priors: bool = True
    illustrative_note: str = "Priors are ILLUSTRATIVE assumptions"

@dataclass
class ActionPlan:
    case_id: str
    ev_total: Decimal
    ev_lo: Decimal
    ev_hi: Decimal
    actions: list[PlanAction]
    illustrative_priors: bool = True
    illustrative_note: str = "Priors are ILLUSTRATIVE assumptions"

def greedy_plan(case_id: str, lever_options: list[LeverOption], K: int = 5, survival: float = 1.0) -> ActionPlan:
    scored = []
    for opt in lever_options:
        ev = opt.applicable_value * Decimal(str(opt.p_success)) * Decimal(str(survival))
        scored.append((ev, opt))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = scored[:K]
    
    actions = []
    ev_total = Decimal("0")
    for i, (ev, opt) in enumerate(selected):
        ev_total += ev
        actions.append(PlanAction(
            rank=i+1,
            lever=opt.lever_type,
            target_ref=opt.target_ref,
            expected_secured=ev,
            expected_secured_lo=ev * Decimal("0.5"),
            expected_secured_hi=ev * Decimal("1.2"),
            deadline_hours=opt.latency_hours * 2 if opt.latency_hours else None,
            eta_hours=opt.latency_hours
        ))
        
    return ActionPlan(
        case_id=case_id,
        ev_total=ev_total,
        ev_lo=ev_total * Decimal("0.5"),
        ev_hi=ev_total * Decimal("1.2"),
        actions=actions
    )

def brute_force_plan(lever_options: list[LeverOption], K: int = 5, survival: float = 1.0) -> Decimal:
    max_ev = Decimal("0")
    for k in range(1, K + 1):
        for combo in itertools.combinations(lever_options, k):
            ev = sum(opt.applicable_value * Decimal(str(opt.p_success)) * Decimal(str(survival)) for opt in combo)
            if ev > max_ev:
                max_ev = ev
    return max_ev

def verify_approximation_ratio(lever_options: list[LeverOption], K: int, survival: float = 1.0) -> tuple[Decimal, Decimal, float]:
    brute = brute_force_plan(lever_options, K, survival)
    greedy = greedy_plan("test", lever_options, K, survival).ev_total
    
    ratio = float(greedy / brute) if brute > 0 else 1.0
    return greedy, brute, ratio
