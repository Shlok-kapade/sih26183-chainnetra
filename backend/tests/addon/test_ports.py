import pytest
from app.addon.adapters_fixture import FixtureTransferPort, FixtureLabelPort, FixtureBudgetPort, FixtureNotifyPort, FixtureClockPort, FixtureTracePort

@pytest.mark.asyncio
async def test_fixture_transfer_port_counts_calls():
    port = FixtureTransferPort()
    async for _ in port.outgoing("chain", "addr", "asset", None, None, 1): pass
    async for _ in port.incoming("chain", "addr", "asset", None, None, 1): pass
    assert port.call_count == 2

def test_fixture_label_port_hit_and_miss():
    port = FixtureLabelPort()
    assert port.lookup("chain", "known") is not None
    assert port.lookup("chain", "unknown") is None

def test_fixture_budget_port_limits():
    port = FixtureBudgetPort(100)
    port.charge(10)
    assert port.calls_left("case") == 90
    assert port.calls_used("case") == 10

@pytest.mark.asyncio
async def test_fixture_notify_collects_events():
    port = FixtureNotifyPort()
    await port.emit("case1", "test_event", {"a": 1})
    assert len(port.events) == 1

def test_fixture_clock_advance():
    port = FixtureClockPort()
    t1 = port.now()
    port.advance(10)
    t2 = port.now()
    assert (t2 - t1).total_seconds() == 10

def test_fixture_trace_port_returns_graph():
    port = FixtureTracePort()
    assert isinstance(port.get_case_graph("case1"), dict)
