from decimal import Decimal

from app.trace.engine import TerminationReason, TraceEngine, TraceResult
from tests.helpers.synthetic import make_linear_chain


def test_trace_engine_depth_limit():
    transfers = make_linear_chain(10, Decimal("100"))

    def fetch_mock(addr):
        return [t for t in transfers if t.from_addr == addr]

    engine = TraceEngine(fetch_mock, max_depth=3)
    result = engine.run("addr_0", Decimal("100"))

    assert isinstance(result, TraceResult)
    # It should trace up to addr_3
    assert "addr_3" in result.termination_reasons
    assert result.termination_reasons["addr_3"] == TerminationReason.DEPTH_LIMIT.value


def test_trace_engine_budget_limit():
    transfers = make_linear_chain(10, Decimal("100"))

    def fetch_mock(addr):
        return [t for t in transfers if t.from_addr == addr]

    engine = TraceEngine(fetch_mock, budget=2)
    result = engine.run("addr_0", Decimal("100"))

    assert isinstance(result, TraceResult)
    # Should stop after 2 API calls (budget)
    assert any(
        reason == TerminationReason.BUDGET_EXHAUSTED.value
        for reason in result.termination_reasons.values()
    )
