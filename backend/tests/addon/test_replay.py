import pytest
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from app.addon.fot.replay import ReplayRunner, ReplayEvent
from app.addon.fot.voi import voi_priority, should_act_now
from app.addon.adapters_fixture import FixtureTracePort, FixtureBudgetPort, FixtureClockPort, FixtureNotifyPort

def generate_simple_timeline():
    t0 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return [
        ReplayEvent(ts=t0, event_type='case_start', address='addr1', detail={'amount': 100}),
        ReplayEvent(ts=t0, event_type='movement', address='addr1', detail={})
    ]

@pytest.mark.asyncio
async def test_replay_runner_runs():
    events = generate_simple_timeline()
    trace = FixtureTracePort()
    budget = FixtureBudgetPort(100)
    clock = FixtureClockPort()
    notify = FixtureNotifyPort()
    runner = ReplayRunner('c1', events, trace, clock, budget, notify, Decimal('100'))
    result = await runner.run('B1')
    assert result.case_id == 'c1'
    assert result.baseline_name == 'B1'
    assert result.plans_computed == 2

@pytest.mark.asyncio
async def test_replay_computes_plans():
    events = generate_simple_timeline()
    trace = FixtureTracePort()
    budget = FixtureBudgetPort(100)
    clock = FixtureClockPort()
    notify = FixtureNotifyPort()
    runner = ReplayRunner('c1', events, trace, clock, budget, notify, Decimal('100'))
    result = await runner.run('B1')
    assert result.plans_computed == len(events)

@pytest.mark.asyncio
async def test_replay_time_to_action():
    events = generate_simple_timeline()
    # graph with exchange to ensure plan has actions
    graph = {
        'elements': [
            {'data': {'id': 'victim', 'role': 'victim'}},
            {'data': {'id': 'exchange', 'role': 'exchange', 'type': 'exchange'}},
            {'data': {'source': 'victim', 'target': 'exchange', 'amount': '100'}}
        ]
    }
    trace = FixtureTracePort(graph)
    budget = FixtureBudgetPort(100)
    clock = FixtureClockPort()
    notify = FixtureNotifyPort()
    runner = ReplayRunner('c1', events, trace, clock, budget, notify, Decimal('100'))
    result = await runner.run('B1')
    assert result.time_to_first_action_hours is not None

def test_voi_priority_positive():
    score = voi_priority('lever1', Decimal('1000'), 0.5, Decimal('500'), 1)
    assert score > 0

def test_act_now_high_opportunity():
    # ev_total = 1000, best_voi = 10
    assert should_act_now(Decimal('1000'), 10.0, 300) == True

def test_act_now_low_opportunity():
    assert should_act_now(Decimal('10'), 1000.0, 300) == False

@pytest.mark.asyncio
async def test_notify_emits_act_now():
    events = generate_simple_timeline()
    # Provide a graph that triggers act_now
    graph = {
        'elements': [
            {'data': {'id': 'victim', 'role': 'victim'}},
            {'data': {'id': 'exchange', 'role': 'exchange', 'type': 'exchange'}},
            {'data': {'source': 'victim', 'target': 'exchange', 'amount': '1000000'}}
        ]
    }
    trace = FixtureTracePort(graph)
    budget = FixtureBudgetPort(100)
    clock = FixtureClockPort()
    notify = FixtureNotifyPort()
    runner = ReplayRunner('c1', events, trace, clock, budget, notify, Decimal('1000000'))
    result = await runner.run('B1')
    
    assert result.act_now_triggered is True
    assert len(notify.events) > 0
    assert notify.events[0][1] == 'act_now'

def test_clock_set_time():
    clock = FixtureClockPort()
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock.set_time(t)
    assert clock.now() == t
