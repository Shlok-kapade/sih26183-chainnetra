"""
Trace Engine — BFS and M3-guided best-first search.
Supports both 'bfs' and 'guided' policies.
'guided' requires an m3_scorer callable: (node, depth, taint_share) -> p_exit float.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from enum import Enum
from typing import Callable, Optional


class TerminationReason(Enum):
    REACHED_VASP_CONFIRMED = "REACHED_VASP_CONFIRMED"
    REACHED_VASP_PROBABLE = "REACHED_VASP_PROBABLE"
    EXIT_P2P_OTC_SUSPECTED = "EXIT_P2P_OTC_SUSPECTED"
    EXIT_MIXER = "EXIT_MIXER"
    EXIT_BRIDGE_UNRESOLVED = "EXIT_BRIDGE_UNRESOLVED"
    EXIT_SANCTIONED = "EXIT_SANCTIONED"
    DORMANT = "DORMANT"
    BELOW_MIN_TAINT = "BELOW_MIN_TAINT"
    DEPTH_LIMIT = "DEPTH_LIMIT"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    CONTRACT_UNKNOWN = "CONTRACT_UNKNOWN"


@dataclass
class TraceResult:
    """Full result of a trace run."""
    graph_nodes: list[str]
    graph_edges: list[tuple[str, str]]
    termination_reasons: dict[str, str]
    api_calls_used: int
    found_exits: list[str]          # nodes labelled as VASP exits during trace
    policy: str
    budget: int


class TraceEngine:
    def __init__(
        self,
        fetch_transfers: Callable[[str], list],
        max_depth: int = 6,
        budget: int = 100,
        min_taint: Decimal = Decimal("0.01"),
        fan_out_cap: int = 10,
        time_window: Optional[timedelta] = None,
        m3_scorer: Optional[Callable[[str, int, float], float]] = None,
        vasp_classifier: Optional[Callable[[str], bool]] = None,
    ):
        """
        Parameters
        ----------
        fetch_transfers: callable address -> list[Transfer]
        m3_scorer: optional (node, depth, taint_share) -> p_exit; enables guided policy
        vasp_classifier: optional address -> bool; marks exits for recall tracking
        """
        self.fetch_transfers = fetch_transfers
        self.max_depth = max_depth
        self.budget = budget
        self.min_taint = min_taint
        self.fan_out_cap = fan_out_cap
        self.time_window = time_window
        self.m3_scorer = m3_scorer
        self.vasp_classifier = vasp_classifier

    def _compute_taint(
        self, transfers: list, seed_address: str, seed_amount: Decimal
    ) -> dict[str, Decimal]:
        """Haircut taint propagation over a transfer list."""
        from collections import defaultdict, deque

        total_out: dict[str, Decimal] = defaultdict(Decimal)
        for t in transfers:
            total_out[t.from_addr] += t.amount

        taint: dict[str, Decimal] = {seed_address: seed_amount}
        q: deque[str] = deque([seed_address])
        visited: set[str] = {seed_address}
        while q:
            node = q.popleft()
            node_taint = taint.get(node, Decimal(0))
            out_total = total_out.get(node, Decimal(0))
            if out_total == 0:
                continue
            for t in transfers:
                if t.from_addr != node:
                    continue
                share = t.amount / out_total
                child_taint = node_taint * share
                if child_taint < self.min_taint:
                    continue
                taint[t.to_addr] = taint.get(t.to_addr, Decimal(0)) + child_taint
                if t.to_addr not in visited:
                    visited.add(t.to_addr)
                    q.append(t.to_addr)
        return taint

    def _priority(
        self, node: str, depth: int, taint_share: float, policy: str
    ) -> float:
        """
        Returns a priority value. **Higher = explored first** (negate for heapq).
        - bfs: priority = -depth (process shallowest first)
        - guided: priority = taint_share * p_exit / (depth + 1)
        - taint_greedy: priority = taint_share
        - dfs: priority = depth (deepest first, negate gives negative depth)
        - random: random float
        """
        if policy == "bfs":
            return -float(depth)
        if policy == "dfs":
            return float(depth)
        if policy == "taint_greedy":
            return taint_share
        if policy == "random":
            import random
            return random.random()
        if policy == "guided":
            p_exit = 0.5  # fallback if no scorer
            if self.m3_scorer is not None:
                p_exit = float(self.m3_scorer(node, depth, taint_share))
            return taint_share * p_exit / max(float(depth + 1), 1.0)
        return -float(depth)  # default bfs

    def run(
        self,
        seed_address: str,
        seed_amount: Decimal,
        policy: str = "bfs",
    ) -> TraceResult:
        """
        Run the trace engine under the given policy and budget.

        Parameters
        ----------
        seed_address: starting address
        seed_amount: initial tainted amount
        policy: one of 'bfs', 'dfs', 'taint_greedy', 'random', 'guided'
        """
        # heap: (-priority, counter, depth, address)  — min-heap, so negate priority
        counter = 0
        initial_priority = self._priority(seed_address, 0, 1.0, policy)
        heap: list[tuple[float, int, int, str]] = [
            (-initial_priority, counter, 0, seed_address)
        ]
        visited: set[str] = set()
        api_calls = 0
        all_transfers: list = []
        termination_reasons: dict[str, str] = {}
        found_exits: list[str] = []
        nodes_seen: list[str] = []
        edges_seen: list[tuple[str, str]] = []

        while heap and api_calls < self.budget:
            _, _, depth, current = heapq.heappop(heap)

            if current in visited:
                continue
            visited.add(current)
            nodes_seen.append(current)

            if depth >= self.max_depth:
                termination_reasons[current] = TerminationReason.DEPTH_LIMIT.value
                continue

            # Check if this node is a VASP exit BEFORE fetching (VASPs may have no out-transfers)
            if self.vasp_classifier is not None and self.vasp_classifier(current):
                found_exits.append(current)
                termination_reasons[current] = TerminationReason.REACHED_VASP_CONFIRMED.value
                continue  # don't expand VASP exits

            transfers = self.fetch_transfers(current)
            api_calls += 1


            if not transfers:
                termination_reasons[current] = TerminationReason.DATA_UNAVAILABLE.value
                continue

            all_transfers.extend(transfers)
            for t in transfers:
                edges_seen.append((t.from_addr, t.to_addr))


            # Compute taint over all seen transfers
            taints = self._compute_taint(all_transfers, seed_address, seed_amount)

            # Build candidate successors, capped by fan_out_cap
            by_dest: dict[str, Decimal] = {}
            for t in transfers:
                by_dest[t.to_addr] = by_dest.get(t.to_addr, Decimal(0)) + t.amount
            top_successors = sorted(
                by_dest.items(), key=lambda kv: kv[1], reverse=True
            )[: self.fan_out_cap]

            for next_addr, _ in top_successors:
                if next_addr in visited:
                    continue
                node_taint = taints.get(next_addr, Decimal(0))
                if node_taint < self.min_taint:
                    termination_reasons[next_addr] = TerminationReason.BELOW_MIN_TAINT.value
                    continue
                taint_share = float(node_taint) / float(seed_amount) if seed_amount > 0 else 0.0
                priority = self._priority(next_addr, depth + 1, taint_share, policy)
                counter += 1
                heapq.heappush(heap, (-priority, counter, depth + 1, next_addr))

        # Mark remaining frontier as budget exhausted
        if api_calls >= self.budget:
            for _, _, _, node in heap:
                if node not in termination_reasons:
                    termination_reasons[node] = TerminationReason.BUDGET_EXHAUSTED.value

        return TraceResult(
            graph_nodes=nodes_seen,
            graph_edges=list(set(edges_seen)),
            termination_reasons=termination_reasons,
            api_calls_used=api_calls,
            found_exits=found_exits,
            policy=policy,
            budget=self.budget,
        )
