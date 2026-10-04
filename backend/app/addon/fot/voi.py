from decimal import Decimal

def voi_priority(
    position_ref: str,
    unresolved_value: Decimal,
    p_resolve_to_lever: float,
    lever_gain: Decimal,
    api_cost: int = 1,
) -> float:
    """Priority score for expanding a node. Higher = expand first."""
    return float(unresolved_value * Decimal(str(p_resolve_to_lever)) * lever_gain) / api_cost

def should_act_now(
    current_plan_ev: Decimal,
    best_voi_score: float,
    expected_delay_seconds: float,
    act_now_threshold: float = 0.20,
) -> bool:
    """True if acting now is better than waiting for more tracing."""
    opportunity_cost = float(current_plan_ev) * (expected_delay_seconds / 3600.0) * 0.30
    return opportunity_cost > best_voi_score * act_now_threshold
