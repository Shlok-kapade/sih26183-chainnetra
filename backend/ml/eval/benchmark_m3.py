"""
M3 Benchmark — recall-vs-API-calls across 5 policies
======================================================
Policies compared: BFS, DFS, taint_greedy, random, M3-guided

Metric (headline): recall of labeled VASP exits vs number of API calls used.
Reports:
  - recall@B table for B in {50, 100, 200, 500} (but budgets capped to graph size)
  - Mean calls-to-first-exit
  - Per-policy JSON results

Usage:
    backend/.venv/bin/python backend/ml/eval/benchmark_m3.py
    (called by eval_m1.py via make eval)

All numbers computed from held-out seeds — nothing is hand-typed.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Callable, Optional

import numpy as np

PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.registry import ModelRegistry  # noqa: E402
from app.trace.engine import TraceEngine  # noqa: E402

POLICIES = ["bfs", "dfs", "taint_greedy", "random", "guided"]
BUDGETS = [20, 50, 100, 200, 500]  # includes small budgets for synthetic graphs
SEED = 42
N_TEST_TRACES = 40  # held-out traces


def _load_m3_scorer() -> Optional[Callable[[str, int, float], float]]:
    """Load M3 model from registry; return None if not available."""
    try:
        from app.ml.m3_dataset import M3_FEATURE_NAMES  # noqa: PLC0415
        registry = ModelRegistry()
        artifact = registry.load("m3", version="latest")
        model = artifact["model"]
        config = artifact["config"]
        ir = artifact.get("calibrator")

        def scorer(node: str, depth: int, taint_share: float) -> float:
            # Minimal feature vector: path features only (M1 probs = uniform)
            feats = {
                "hops_so_far": float(depth),
                "taint_share": taint_share,
                "remaining_budget": float(max(0, config.get("max_budget", 10) - depth)),
                "fan_out_width": 1.0,
                "top1_forward_share": 0.5,
                "dwell_so_far_hours": 0.0,
                "value_trend_log": 0.0,
                "n_out_cp": 1.0,
                "label_proximity": 0.0,
                "p_exchange_hot": 1.0 / 7,
                "p_exchange_deposit": 1.0 / 7,
                "p_mixer": 1.0 / 7,
                "p_bridge": 1.0 / 7,
                "p_dex": 1.0 / 7,
                "p_illicit": 1.0 / 7,
                "p_personal": 1.0 / 7,
            }
            row = [[feats[f] for f in M3_FEATURE_NAMES]]
            raw = float(model.predict_proba(row)[0][1])
            if ir is not None:
                return float(ir.predict([raw])[0])
            return raw

        return scorer
    except Exception as exc:
        print(f"  [warn] M3 model not loaded ({exc}); guided policy uses taint fallback")
        return None


def run_policy_on_graph(
    transfers: list,
    seed_addr: str,
    vasp_addresses: set[str],
    policy: str,
    budget: int,
    m3_scorer: Optional[Callable],
    seed_amount: Decimal = Decimal("100"),
) -> dict:
    """
    Run one policy on a single synthetic graph.

    Returns:
        api_calls_used: int
        exits_found: list[str]
        recall: float (exits_found / total_vasp exits in graph)
        calls_to_first_exit: int | None
    """
    # Build a fetch_transfers function backed by the known graph
    by_address: dict[str, list] = defaultdict(list)
    for t in transfers:
        by_address[t.from_addr].append(t)

    def fetch(addr: str) -> list:
        return by_address.get(addr, [])

    vasp_set = vasp_addresses.copy()

    engine = TraceEngine(
        fetch_transfers=fetch,
        max_depth=20,
        budget=budget,
        min_taint=Decimal("0.001"),
        fan_out_cap=20,
        m3_scorer=m3_scorer if policy == "guided" else None,
        vasp_classifier=lambda addr: addr in vasp_set,
    )

    result = engine.run(seed_addr, seed_amount, policy=policy)

    total_exits = len(vasp_addresses)
    exits_found = len(result.found_exits)
    recall = exits_found / max(total_exits, 1)
    calls_to_first = result.api_calls_used if exits_found > 0 else None

    return {
        "api_calls_used": result.api_calls_used,
        "exits_found": exits_found,
        "total_exits": total_exits,
        "recall": recall,
        "calls_to_first_exit": calls_to_first,
    }


def run_benchmark(n_test: int = N_TEST_TRACES) -> dict:
    """
    Run the full benchmark. Returns nested dict:
        results[policy][budget] -> {mean_recall, mean_calls_to_first, ...}
    """
    # Load synthetic generator
    sl_path = PROJECT_ROOT / "scripts" / "synth_laundering.py"
    _spec = importlib.util.spec_from_file_location("synth_laundering", sl_path)
    sl = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
    _spec.loader.exec_module(sl)  # type: ignore[union-attr]

    rng = np.random.default_rng(SEED + 999)  # different seed from training

    # Same generators as m3_dataset but with test seeds
    gen_configs = [
        (sl.generate_exchange_deposit_funnel,
         lambda s: f"user_{s}_0",
         lambda s: {f"hot_wallet_{s}"}),
        (sl.generate_layering,
         lambda s: f"seed_{s}",
         lambda s: {f"collection_{s}"}),
        (sl.generate_benign_processor,
         lambda s: f"processor_{s}",
         lambda s: {f"emp_{s}_0", f"emp_{s}_1"}),
        (sl.generate_rapid_forwarding,
         lambda s: f"hop_{s}_0",
         lambda s: {f"hop_{s}_5"}),
    ]

    m3_scorer = _load_m3_scorer()

    # Collect per-trace results
    per_trace: list[dict] = []

    per_gen = max(1, n_test // len(gen_configs))
    for gen_fn, get_seed, get_vasps in gen_configs:
        for _ in range(per_gen):
            s = int(rng.integers(0, 100_000))
            transfers = gen_fn(seed=s)
            if not transfers:
                continue
            seed_addr = get_seed(s)
            vasp_addresses = get_vasps(s)
            # Skip if VASP address doesn't exist in graph
            all_addrs = {t.from_addr for t in transfers} | {t.to_addr for t in transfers}
            vasp_addresses &= all_addrs
            if not vasp_addresses:
                continue

            trace_result: dict = {"seed": s}
            for policy in POLICIES:
                trace_result[policy] = {}
                for budget in BUDGETS:
                    r = run_policy_on_graph(
                        transfers, seed_addr, vasp_addresses,
                        policy, budget, m3_scorer,
                    )
                    trace_result[policy][budget] = r
            per_trace.append(trace_result)

    if not per_trace:
        return {"error": "No valid test traces generated"}

    # Aggregate
    results: dict = {}
    for policy in POLICIES:
        results[policy] = {}
        for budget in BUDGETS:
            recalls = [t[policy][budget]["recall"] for t in per_trace if policy in t]
            ctfe_vals = [
                t[policy][budget]["calls_to_first_exit"]
                for t in per_trace
                if policy in t and t[policy][budget]["calls_to_first_exit"] is not None
            ]
            results[policy][budget] = {
                "mean_recall": float(np.mean(recalls)) if recalls else 0.0,
                "std_recall": float(np.std(recalls)) if recalls else 0.0,
                "mean_calls_to_first_exit": float(np.mean(ctfe_vals)) if ctfe_vals else None,
                "n_traces": len(recalls),
            }

    return {
        "policies": POLICIES,
        "budgets": BUDGETS,
        "n_test_traces": len(per_trace),
        "results": results,
        "caveat": (
            "Ground truth only includes exits to labeled VASPs. "
            "Unlabeled exchanges are invisible → recall is a lower bound. "
            "All graphs are synthetic; real-world topology differs."
        ),
    }


def format_recall_table(benchmark: dict) -> str:
    """Format recall@B table as Markdown."""
    if "error" in benchmark:
        return f"Benchmark error: {benchmark['error']}\n"

    results = benchmark["results"]
    budgets = benchmark["budgets"]
    policies = benchmark["policies"]

    # Header
    header = "| Policy | " + " | ".join(f"Recall@{b}" for b in budgets) + " | Mean calls-to-1st |"
    sep = "|--------|" + "--------|" * len(budgets) + "------------------|"
    rows = [header, sep]

    for policy in policies:
        pdata = results[policy]
        cells = []
        for b in budgets:
            v = pdata[b]["mean_recall"]
            cells.append(f"{v:.3f}")
        ctfe_vals = [
            pdata[b]["mean_calls_to_first_exit"]
            for b in budgets
            if pdata[b]["mean_calls_to_first_exit"] is not None
        ]
        mean_ctfe = f"{np.mean(ctfe_vals):.1f}" if ctfe_vals else "N/A"
        display = "**M3-guided**" if policy == "guided" else policy
        rows.append(f"| {display} | " + " | ".join(cells) + f" | {mean_ctfe} |")

    return "\n".join(rows) + "\n"


if __name__ == "__main__":
    print("Running M3 benchmark …")
    bench = run_benchmark()
    print("\n--- recall@B table ---")
    print(format_recall_table(bench))
    out = PROJECT_ROOT / "ml" / "artifacts" / "m3" / "benchmark.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bench, indent=2))
    print(f"Full results: {out}")
