from decimal import Decimal

from app.graph.builder import GraphBuilder
from tests.helpers.synthetic import make_linear_chain


def test_graph_builder():
    builder = GraphBuilder()
    transfers = make_linear_chain(3, Decimal("100"))
    builder.add_transfers(transfers)

    graph = builder.get_graph()
    assert len(graph.nodes) == 4
    assert len(graph.edges) == 3

    node = builder.get_node("addr_0")
    assert node.address == "addr_0"

    neighbors = builder.get_neighbors("addr_0")
    assert neighbors == ["addr_1"]
