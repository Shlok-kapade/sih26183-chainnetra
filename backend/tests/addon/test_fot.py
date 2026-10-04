import pytest
from decimal import Decimal
from datetime import datetime
from app.addon.fot.mass_map import build_mass_map
from app.addon.fot.levers import get_lever_options, LeverOption
from app.addon.fot.planner import greedy_plan, brute_force_plan, verify_approximation_ratio
from app.addon.fot.voi import voi_priority, should_act_now

SAMPLE_GRAPH = {
    "elements": [
        {"data": {"id": "victim", "label": "Victim", "role": "victim", "taint": 1.0, "type": "wallet"}},
        {"data": {"id": "hop1", "label": "Hop1", "role": "intermediary", "taint": 0.9, "type": "wallet"}},
        {"data": {"id": "exchange", "label": "Binance", "role": "exchange", "taint": 0.85, "type": "exchange"}},
        {"data": {"source": "victim", "target": "hop1", "amount": "9000"}},
        {"data": {"source": "hop1", "target": "exchange", "amount": "8500"}},
    ]
}

def test_mass_map_builds():
    mmap = build_mass_map("c1", datetime.now(), SAMPLE_GRAPH, Decimal("9000"))
    assert len(mmap.positions) > 0

def test_mass_map_invariant():
    mmap = build_mass_map("c1", datetime.now(), SAMPLE_GRAPH, Decimal("9000"))
    assert mmap.invariant_ok()

def test_mass_map_exchange_exited():
    mmap = build_mass_map("c1", datetime.now(), SAMPLE_GRAPH, Decimal("9000"))
    exc_pos = next(p for p in mmap.positions if p.position_ref == "exchange")
    assert exc_pos.status == "EXITED_VASP"

def test_mass_map_held():
    # Make a leaf node
    g = {
        "elements": [
            {"data": {"id": "victim", "role": "victim"}},
            {"data": {"id": "leaf1", "role": "wallet"}},
            {"data": {"source": "victim", "target": "leaf1", "amount": "100"}},
        ]
    }
    mmap = build_mass_map("c1", datetime.now(), g, Decimal("100"))
    leaf_pos = next(p for p in mmap.positions if p.position_ref == "leaf1")
    assert leaf_pos.status == "HELD"

def test_lever_vasp_hold_created():
    mmap = build_mass_map("c1", datetime.now(), SAMPLE_GRAPH, Decimal("9000"))
    levers = get_lever_options(mmap)
    vasp_lever = next((L for L in levers if L.lever_type == "VASP_HOLD"), None)
    assert vasp_lever is not None

def test_greedy_plan_returns_plan():
    l1 = LeverOption("VASP_HOLD", "t1", 0.5, 24.0, 7, Decimal("100"))
    l2 = LeverOption("ISSUER_BLACKLIST", "t2", 0.8, 48.0, 365, Decimal("50"))
    l3 = LeverOption("WATCH", "t3", 0.1, 0.0, 0, Decimal("200"))
    plan = greedy_plan("c1", [l1, l2, l3], K=2)
    assert len(plan.actions) == 2
    # Wait, l1 ev = 100 * 0.5 = 50. So l1 is first.
    assert plan.actions[0].lever == "VASP_HOLD"

def test_greedy_approximation_ratio():
    levers = [
        LeverOption("L1", "t1", 0.5, 24, 7, Decimal("100")),
        LeverOption("L2", "t2", 0.4, 24, 7, Decimal("120")),
        LeverOption("L3", "t3", 0.9, 24, 7, Decimal("20")),
        LeverOption("L4", "t4", 0.1, 24, 7, Decimal("500")),
        LeverOption("L5", "t5", 0.2, 24, 7, Decimal("300")),
        LeverOption("L6", "t6", 0.8, 24, 7, Decimal("80")),
    ]
    greedy, brute, ratio = verify_approximation_ratio(levers, K=4)
    assert ratio >= 0.60

def test_brute_force_small():
    levers = [
        LeverOption("L1", "t1", 0.5, 24, 7, Decimal("100")),
        LeverOption("L2", "t2", 0.4, 24, 7, Decimal("120")),
    ]
    assert brute_force_plan(levers, K=2) == greedy_plan("c1", levers, K=2).ev_total

def test_plan_intervals():
    l1 = LeverOption("VASP_HOLD", "t1", 0.5, 24.0, 7, Decimal("100"))
    plan = greedy_plan("c1", [l1], K=1)
    a = plan.actions[0]
    assert a.expected_secured_lo <= a.expected_secured <= a.expected_secured_hi

def test_illustrative_always_true():
    l1 = LeverOption("VASP_HOLD", "t1", 0.5, 24.0, 7, Decimal("100"))
    plan = greedy_plan("c1", [l1], K=1)
    assert plan.illustrative_priors is True

def test_voi_priority_ordering():
    p1 = voi_priority("r1", Decimal("100"), 0.5, Decimal("20"), 1)
    p2 = voi_priority("r2", Decimal("50"), 0.5, Decimal("20"), 1)
    assert p1 > p2

def test_act_now_threshold():
    assert should_act_now(Decimal("1000"), 5.0, 3600.0, 0.2) # opportunity_cost = 1000 * 1 * 0.3 = 300, 300 > 5 * 0.2 = 1.0 -> True
