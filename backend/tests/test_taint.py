from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from app.graph.builder import GraphBuilder
from app.graph.taint import compute_taint
from tests.helpers.synthetic import make_fan_out, make_linear_chain


@given(st.decimals(min_value=1, max_value=1000000))
def test_taint_conservation_linear(amount):
    builder = GraphBuilder()
    transfers = make_linear_chain(3, amount)
    builder.add_transfers(transfers)

    graph = builder.get_graph()
    taints = compute_taint(graph, "addr_0", amount, mode="haircut")

    # Total taint at any node should be <= seed amount (with small precision tolerance)
    for node, taint in taints.items():
        assert taint <= amount + Decimal("1e-8")
        assert taint >= Decimal("-1e-8")

@given(st.decimals(min_value=1, max_value=1000000))
def test_taint_conservation_fan_out(amount):
    builder = GraphBuilder()
    transfers = make_fan_out(4, amount)
    builder.add_transfers(transfers)

    graph = builder.get_graph()
    taints = compute_taint(graph, "addr_0", amount, mode="haircut")

    # Total taint at any node should be <= seed amount
    for node, taint in taints.items():
        assert taint <= amount + Decimal("1e-8")
        assert taint >= Decimal("-1e-8")

    # Sum of leaf taints should equal seed amount for haircut in simple fan out
    # Actually, in haircut, taint passes entirely to outputs if they sum to total
    leaf_taint_sum = sum(taints[n] for n in ["addr_1", "addr_2", "addr_3", "addr_4"])
    # allow small float precision issues with decimal? Decimal is exact, but division might truncate
    # since we just do simple divisions, it should be close
    assert abs(leaf_taint_sum - amount) < Decimal("0.0001")

def test_poison_mode():
    builder = GraphBuilder()
    transfers = make_fan_out(2, Decimal("100"))
    builder.add_transfers(transfers)

    graph = builder.get_graph()
    taints = compute_taint(graph, "addr_0", Decimal("100"), mode="poison")

    # Total taint at any node <= seed amount
    # addr_1 gets min(50, 100) = 50. Remaining current_taint = 50.
    # addr_2 gets min(50, 50) = 50. Remaining = 0.
    # Total conserved.
    assert taints["addr_1"] == Decimal("50")
    assert taints["addr_2"] == Decimal("50")
