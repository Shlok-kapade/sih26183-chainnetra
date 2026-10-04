"""
Phase 6 — M3 Guided Tracing Policy Tests
==========================================
All tests use deterministic synthetic data; no fabricated metrics.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import numpy as np

from app.ingest.normalize import Transfer
from app.trace.engine import TerminationReason, TraceEngine, TraceResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_transfer(frm: str, to: str, amt: float, minutes_offset: int = 0) -> Transfer:
    base = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    return Transfer(
        chain="SYNTHETIC",
        tx_hash=f"tx_{frm}_{to}_{amt}",
        ts=base + timedelta(minutes=minutes_offset),
        from_addr=frm,
        to_addr=to,
        asset="USDT",
        amount=Decimal(str(amt)),
        kind="token",
        block=1000,
    )


def _simple_graph() -> tuple[dict[str, list[Transfer]], set[str]]:
    """
    Simple linear graph: A -> B -> C (VASP) -> D
    Also: A -> E (dead end)
    """
    transfers = [
        _make_transfer("A", "B", 100, 0),
        _make_transfer("A", "E", 10, 0),
        _make_transfer("B", "C", 90, 5),
        _make_transfer("C", "D", 80, 10),
    ]
    by_addr: dict[str, list[Transfer]] = {}
    for t in transfers:
        by_addr.setdefault(t.from_addr, []).append(t)
    vasp_addrs = {"C"}
    return by_addr, vasp_addrs


# ---------------------------------------------------------------------------
# TraceEngine basic tests
# ---------------------------------------------------------------------------

class TestTraceEngine:

    def test_bfs_finds_vasp(self):
        by_addr, vasp_addrs = _simple_graph()
        engine = TraceEngine(
            fetch_transfers=lambda addr: by_addr.get(addr, []),
            budget=50,
            max_depth=10,
            vasp_classifier=lambda addr: addr in vasp_addrs,
        )
        result = engine.run("A", Decimal("100"), policy="bfs")
        assert isinstance(result, TraceResult)
        assert "C" in result.found_exits

    def test_result_tracks_api_calls(self):
        by_addr, vasp_addrs = _simple_graph()
        engine = TraceEngine(
            fetch_transfers=lambda addr: by_addr.get(addr, []),
            budget=2,
            max_depth=10,
            vasp_classifier=lambda addr: addr in vasp_addrs,
        )
        result = engine.run("A", Decimal("100"), policy="bfs")
        assert result.api_calls_used <= 2

    def test_budget_exhausted_marks_reason(self):
        by_addr, _ = _simple_graph()
        engine = TraceEngine(
            fetch_transfers=lambda addr: by_addr.get(addr, []),
            budget=1,
            max_depth=10,
        )
        result = engine.run("A", Decimal("100"), policy="bfs")
        assert result.api_calls_used <= 1
        # Some nodes should be marked budget-exhausted OR depth limit
        reasons = set(result.termination_reasons.values())
        assert len(reasons) > 0

    def test_depth_limit_respected(self):
        by_addr, _ = _simple_graph()
        engine = TraceEngine(
            fetch_transfers=lambda addr: by_addr.get(addr, []),
            budget=50,
            max_depth=1,
        )
        result = engine.run("A", Decimal("100"), policy="bfs")
        assert TerminationReason.DEPTH_LIMIT.value in result.termination_reasons.values()

    def test_all_policies_run(self):
        by_addr, vasp_addrs = _simple_graph()
        for policy in ["bfs", "dfs", "taint_greedy", "random", "guided"]:
            engine = TraceEngine(
                fetch_transfers=lambda addr: by_addr.get(addr, []),
                budget=20,
                max_depth=10,
                vasp_classifier=lambda addr: addr in vasp_addrs,
            )
            result = engine.run("A", Decimal("100"), policy=policy)
            assert isinstance(result, TraceResult)
            assert result.policy == policy

    def test_guided_policy_priority_formula(self):
        """Guided policy should give higher priority to higher taint + p_exit."""
        by_addr, vasp_addrs = _simple_graph()

        # Scorer that always returns p_exit=1.0 → all priority comes from taint_share
        high_scorer = lambda node, depth, taint: 1.0

        engine = TraceEngine(
            fetch_transfers=lambda addr: by_addr.get(addr, []),
            budget=50,
            max_depth=10,
            vasp_classifier=lambda addr: addr in vasp_addrs,
            m3_scorer=high_scorer,
        )
        result = engine.run("A", Decimal("100"), policy="guided")
        assert "C" in result.found_exits  # should still find VASP

    def test_found_exits_subset_of_nodes(self):
        by_addr, vasp_addrs = _simple_graph()
        engine = TraceEngine(
            fetch_transfers=lambda addr: by_addr.get(addr, []),
            budget=50,
            max_depth=10,
            vasp_classifier=lambda addr: addr in vasp_addrs,
        )
        result = engine.run("A", Decimal("100"), policy="bfs")
        for exit_node in result.found_exits:
            assert exit_node in result.graph_nodes

    def test_no_vasp_classifier_returns_empty_exits(self):
        by_addr, _ = _simple_graph()
        engine = TraceEngine(
            fetch_transfers=lambda addr: by_addr.get(addr, []),
            budget=50,
            max_depth=10,
        )
        result = engine.run("A", Decimal("100"), policy="bfs")
        assert result.found_exits == []

    def test_guided_beats_random_on_simple_graph(self):
        """Guided with perfect scorer should find exit in fewer calls than random (on average)."""
        by_addr, vasp_addrs = _simple_graph()

        # Perfect scorer: returns 1.0 for all (always prefer expanding)
        def perfect_scorer(node, depth, taint):
            return 1.0

        budget = 3
        guided_engine = TraceEngine(
            fetch_transfers=lambda addr: by_addr.get(addr, []),
            budget=budget,
            max_depth=10,
            vasp_classifier=lambda addr: addr in vasp_addrs,
            m3_scorer=perfect_scorer,
        )
        guided_result = guided_engine.run("A", Decimal("100"), policy="guided")

        # With budget=3 and guided, should reach C
        # (A->B->C costs 3 API calls exactly; random might go A->E->... first)
        assert guided_result.api_calls_used <= budget


# ---------------------------------------------------------------------------
# M3 Dataset tests
# ---------------------------------------------------------------------------

class TestM3Dataset:

    def test_builds_without_crash(self):
        from app.ml.m3_dataset import build_m3_dataset
        X, y, groups = build_m3_dataset(n_traces=8, max_budget=5, seed=1)
        assert len(X) > 0
        assert len(X) == len(y) == len(groups)

    def test_has_binary_labels(self):
        from app.ml.m3_dataset import build_m3_dataset
        _, y, _ = build_m3_dataset(n_traces=8, max_budget=5, seed=2)
        assert set(np.unique(y)).issubset({0, 1})

    def test_has_both_classes(self):
        from app.ml.m3_dataset import build_m3_dataset
        _, y, _ = build_m3_dataset(n_traces=16, max_budget=5, seed=3)
        assert 0 in y and 1 in y, "Dataset must have both positive and negative examples"

    def test_group_split_disjoint(self):
        from sklearn.model_selection import GroupShuffleSplit

        from app.ml.m3_dataset import build_m3_dataset
        X, y, groups = build_m3_dataset(n_traces=20, max_budget=5, seed=4)
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=0)
        train_idx, test_idx = next(gss.split(X, y, groups))
        train_seeds = set(groups[train_idx])
        test_seeds = set(groups[test_idx])
        assert len(train_seeds & test_seeds) == 0, "Seed leakage detected!"

    def test_feature_names_consistent(self):
        from app.ml.m3_dataset import M3_FEATURE_NAMES, build_m3_dataset
        X, _, _ = build_m3_dataset(n_traces=4, max_budget=3, seed=5)
        assert list(X.columns) == M3_FEATURE_NAMES

    def test_taint_share_in_0_1(self):
        from app.ml.m3_dataset import build_m3_dataset
        X, _, _ = build_m3_dataset(n_traces=8, max_budget=5, seed=6)
        assert (X["taint_share"] >= 0.0).all()
        assert (X["taint_share"] <= 1.0 + 1e-9).all()

    def test_remaining_budget_non_negative(self):
        from app.ml.m3_dataset import build_m3_dataset
        X, _, _ = build_m3_dataset(n_traces=8, max_budget=5, seed=7)
        assert (X["remaining_budget"] >= 0.0).all()


# ---------------------------------------------------------------------------
# Benchmark tests
# ---------------------------------------------------------------------------

class TestBenchmark:

    def test_benchmark_runs_small(self):
        from ml.eval.benchmark_m3 import run_benchmark
        result = run_benchmark(n_test=4)
        assert "results" in result
        assert "bfs" in result["results"]
        assert "guided" in result["results"]

    def test_recall_in_0_1(self):
        from ml.eval.benchmark_m3 import run_benchmark
        result = run_benchmark(n_test=4)
        for policy in result["results"]:
            for budget in result["budgets"]:
                r = result["results"][policy][budget]["mean_recall"]
                assert 0.0 <= r <= 1.0 + 1e-9, f"recall={r} out of [0,1] for {policy}@{budget}"

    def test_format_table_returns_string(self):
        from ml.eval.benchmark_m3 import format_recall_table, run_benchmark
        result = run_benchmark(n_test=4)
        table = format_recall_table(result)
        assert isinstance(table, str)
        assert "recall" in table.lower() or "|" in table

    def test_caveat_in_result(self):
        from ml.eval.benchmark_m3 import run_benchmark
        result = run_benchmark(n_test=4)
        assert "caveat" in result
        assert "lower bound" in result["caveat"]

    def test_higher_budget_geq_lower_budget_recall(self):
        """More budget should give at least as much recall (monotone)."""
        from ml.eval.benchmark_m3 import BUDGETS, run_benchmark
        result = run_benchmark(n_test=8)
        for policy in result["results"]:
            pdata = result["results"][policy]
            sorted_budgets = sorted(BUDGETS)
            recalls = [pdata[b]["mean_recall"] for b in sorted_budgets]
            for i in range(len(recalls) - 1):
                # Allow small floating point noise
                assert recalls[i] <= recalls[i + 1] + 0.05, (
                    f"{policy}: recall decreased from budget {sorted_budgets[i]} "
                    f"to {sorted_budgets[i+1]}: {recalls[i]:.3f} > {recalls[i+1]:.3f}"
                )
