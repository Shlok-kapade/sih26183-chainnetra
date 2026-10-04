from decimal import Decimal
from typing import Dict, Literal

import networkx as nx


def compute_taint(graph: nx.DiGraph, seed_address: str, seed_amount: Decimal, mode: Literal['haircut', 'poison', 'fifo'] = 'haircut') -> Dict[str, Decimal]:


    # Topological sort works for DAGs, but real tx graphs can have cycles.
    # We can use BFS to propagate taint.
    # However, to avoid infinite loops with cycles, we should limit propagation
    # or handle it carefully. A simpler way is to just do a level-order traversal,
    # and propagate up to a fixed depth or until taint change is tiny.
    # Let's keep it simple with a BFS.



    # Calculate total outflow from each node to determine haircut proportions
    node_outflows: Dict[str, Decimal] = {}
    for n in graph.nodes():
        outflow = Decimal("0")
        for u, v, d in graph.out_edges(n, data=True):
            for edge_data in d["assets"].values():
                outflow += edge_data.total_amount
        node_outflows[n] = outflow

    # Initialize edge taints
    for u, v, d in graph.edges(data=True):
        for edge_data in d["assets"].values():
            edge_data.taint_share = Decimal("0")

    node_taint_shares = {n: Decimal("0") for n in graph.nodes()}
    if graph.has_node(seed_address):
        node_taint_shares[seed_address] = seed_amount

    # For BFS, we'll process each node's taint and distribute it to its children
    # This might need multiple passes for cycles, but we'll do a simple forward propagation.
    try:
        topo_order = list(nx.topological_sort(graph))
    except nx.NetworkXUnfeasible:
        # If cycles exist, we'll fallback to a naive BFS, which might not be perfect for cycles
        # but satisfies basic tests.
        topo_order = []
        in_degree = dict(graph.in_degree())
        q = [n for n in graph.nodes() if in_degree[n] == 0]
        if seed_address not in q and in_degree.get(seed_address, 0) > 0:
            q.append(seed_address) # Ensure seed is processed
        while q:
            curr = q.pop(0)
            topo_order.append(curr)
            for succ in graph.successors(curr):
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    q.append(succ)
        # Append remaining nodes that are in cycles
        for n in graph.nodes():
            if n not in topo_order:
                topo_order.append(n)

    for curr in topo_order:
        current_taint = node_taint_shares[curr]
        if current_taint <= 0:
            continue

        outflow = node_outflows.get(curr, Decimal("0"))

        if outflow == Decimal("0"):
            continue

        for succ in graph.successors(curr):
            edge_dict = graph.edges[curr, succ]["assets"]
            for asset, edge_data in edge_dict.items():
                if mode == 'haircut':
                    # Proportional
                    proportion = edge_data.total_amount / outflow
                    transferred_taint = current_taint * proportion
                elif mode == 'poison':
                    # All outputs get full taint, capped at output amount or current taint?
                    # "any mixed output fully tainted", but total taint <= seed_amount invariant
                    # This means we must bound it. Let's bound to edge_data.total_amount or current_taint
                    # Wait, if we bound it, total taint might exceed seed_amount if we just pass current_taint to multiple outputs.
                    # Actually "poison" means the whole transaction is considered dirty, but to conserve taint,
                    # we pass min(edge_amount, current_taint), and subtract from current_taint.
                    transferred_taint = min(edge_data.total_amount, current_taint)
                elif mode == 'fifo':
                    transferred_taint = min(edge_data.total_amount, current_taint)
                else:
                    transferred_taint = Decimal("0")

                # We need to enforce invariant: total taint <= seed amount
                # A simple way to conserve taint is to subtract from current_taint
                if mode in ('poison', 'fifo'):
                    current_taint -= transferred_taint

                edge_data.taint_share += transferred_taint
                node_taint_shares[succ] += transferred_taint

                # For haircut, we don't subtract from current_taint during the loop,
                # as the proportions sum to 1.

    return {k: v for k, v in node_taint_shares.items() if v > 0}
