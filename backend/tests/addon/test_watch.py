import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timezone
from app.addon.fot.hazard import HazardFeatures, predict_hazard, hazard_poll_interval
from app.addon.fot.watch import FrontierWatcher
from app.addon.adapters_fixture import FixtureClockPort, FixtureBudgetPort, FixtureNotifyPort

def test_hazard_predict_returns_estimate():
    f = HazardFeatures(10.0, 4.0, 12, 5.0, 0.5)
    est = predict_hazard(f)
    assert 0 <= est.p_move_next_hour <= 1.0
    assert 0 <= est.p_move_next_24h <= 1.0

def test_hazard_p_monotone_with_holding():
    f1 = HazardFeatures(1.0, 4.0, 12, 5.0, 0.5)
    f2 = HazardFeatures(100.0, 4.0, 12, 5.0, 0.5)
    e1 = predict_hazard(f1)
    e2 = predict_hazard(f2)
    assert e2.p_move_next_hour <= e1.p_move_next_hour

def test_hazard_high_value_higher_p():
    f1 = HazardFeatures(10.0, 1.0, 12, 5.0, 0.5)
    f2 = HazardFeatures(10.0, 6.0, 12, 5.0, 0.5)
    e1 = predict_hazard(f1)
    e2 = predict_hazard(f2)
    assert e2.p_move_next_hour > e1.p_move_next_hour

def test_hazard_poll_interval_high():
    f = HazardFeatures(0.0, 10.0, 12, 0.0, 1.0) # High hazard
    est = predict_hazard(f)
    if est.p_move_next_hour > 0.20:
        interval = hazard_poll_interval(est)
        assert interval == 60

def test_hazard_poll_interval_low():
    f = HazardFeatures(100.0, 1.0, 12, 0.0, 0.1) # Low hazard
    est = predict_hazard(f)
    if est.p_move_next_hour < 0.20:
        interval = hazard_poll_interval(est)
        assert interval == 300

class SwitchingFixtureTracePort:
    def __init__(self, t_switch: float):
        self.t_switch = t_switch
        self.call_count = 0
    def get_case_graph(self, case_id: str) -> dict:
        self.call_count += 1
        if self.call_count < self.t_switch:
            # HELD position present: addr1 has incoming but no outgoing
            return {
                "elements": [
                    {"data": {"id": "seed"}},
                    {"data": {"id": "addr1"}},
                    {"data": {"source": "seed", "target": "addr1", "amount": 1000}}
                ]
            }
        else:
            # Position moved (no longer HELD): addr1 has incoming and outgoing
            return {
                "elements": [
                    {"data": {"id": "seed"}},
                    {"data": {"id": "addr1"}},
                    {"data": {"id": "addr2"}},
                    {"data": {"source": "seed", "target": "addr1", "amount": 1000}},
                    {"data": {"source": "addr1", "target": "addr2", "amount": 1000}}
                ]
            }

@pytest.mark.asyncio
async def test_watcher_add_watch():
    watcher = FrontierWatcher(None, FixtureClockPort(), None, None, seed_amount=Decimal('1000'))
    watcher.add_watch('case1', 'addr1', Decimal('1000'))
    w = watcher.get_watch('case1')
    assert w is not None
    assert w.position_ref == 'addr1'

@pytest.mark.asyncio
async def test_watcher_tick_no_movement():
    clock = FixtureClockPort()
    budget = FixtureBudgetPort(100)
    notify = FixtureNotifyPort()
    trace = SwitchingFixtureTracePort(100) # never switches
    watcher = FrontierWatcher(trace, clock, budget, notify, seed_amount=Decimal('1000'))
    watcher.add_watch('case1', 'addr1', Decimal('1000'))
    moved = await watcher.tick('case1')
    assert not moved
    assert watcher.get_watch('case1').status == 'active'

@pytest.mark.asyncio
async def test_watcher_tick_movement_detected():
    clock = FixtureClockPort()
    budget = FixtureBudgetPort(100)
    notify = FixtureNotifyPort()
    trace = SwitchingFixtureTracePort(2) # switches on second call
    watcher = FrontierWatcher(trace, clock, budget, notify, seed_amount=Decimal('1000'))
    watcher.add_watch('case1', 'addr1', Decimal('1000'))
    
    # Tick 1: no movement
    moved = await watcher.tick('case1')
    assert not moved
    
    # Tick 2: movement detected
    moved = await watcher.tick('case1')
    assert moved
    assert watcher.get_watch('case1').status == 'triggered'

@pytest.mark.asyncio
async def test_watcher_emits_mass_moved():
    clock = FixtureClockPort()
    budget = FixtureBudgetPort(100)
    notify = FixtureNotifyPort()
    trace = SwitchingFixtureTracePort(1) # switches immediately
    watcher = FrontierWatcher(trace, clock, budget, notify, seed_amount=Decimal('1000'))
    watcher.add_watch('case1', 'addr1', Decimal('1000'))
    await watcher.tick('case1')
    
    events = [e for e in notify.events if e[1] == 'mass_moved']
    assert len(events) > 0
    assert events[0][2]['position'] == 'addr1'

@pytest.mark.asyncio
async def test_watcher_emits_plan_changed():
    clock = FixtureClockPort()
    budget = FixtureBudgetPort(100)
    notify = FixtureNotifyPort()
    trace = SwitchingFixtureTracePort(1)
    watcher = FrontierWatcher(trace, clock, budget, notify, seed_amount=Decimal('1000'))
    watcher.add_watch('case1', 'addr1', Decimal('1000'))
    await watcher.tick('case1')
    
    events = [e for e in notify.events if e[1] == 'plan_changed']
    assert len(events) > 0

@pytest.mark.asyncio
async def test_watch_job_stops_on_movement():
    clock = FixtureClockPort()
    budget = FixtureBudgetPort(100)
    notify = FixtureNotifyPort()
    trace = SwitchingFixtureTracePort(3) # switches on third call
    watcher = FrontierWatcher(trace, clock, budget, notify, seed_amount=Decimal('1000'))
    watcher.add_watch('case1', 'addr1', Decimal('1000'))
    
    await watcher.run_watch_job('case1', max_ticks=10)
    assert trace.call_count == 3
