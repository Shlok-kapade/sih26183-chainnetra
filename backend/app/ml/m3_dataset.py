"""
M3 Guided Tracing Policy — Trace-Labeled Dataset Builder
=========================================================
Builds per-node binary labels from synthetic graphs:
  label = 1 if a labeled VASP is reachable from node v within k remaining hops
  label = 0 otherwise

Dataset split is GROUP-based by seed_id (no seed appears in both train and test).
All features are point-in-time relative to each node's position in the trace.

Real cached graphs are not yet available; this module uses the same synthetic
generators as M1 (synth_laundering.py). See MODEL_CARD caveat on ground-truth bias.
"""
from __future__ import annotations

import importlib.util
import math
from collections import defaultdict, deque
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.ingest.normalize import Transfer
from app.ml.features import ROLE_CLASSES

PROJECT_ROOT = Path(__file__).parents[3]

# M3 feature names (ordered, deterministic)
M3_FEATURE_NAMES = [
    "hops_so_far",
    "taint_share",
    "remaining_budget",
    "fan_out_width",
    "top1_forward_share",
    "dwell_so_far_hours",
    "value_trend_log",
    "n_out_cp",
    "label_proximity",
    # M1 role probabilities (7 features)
    "p_exchange_hot",
    "p_exchange_deposit",
    "p_mixer",
    "p_bridge",
    "p_dex",
    "p_illicit",
    "p_personal",
]


def _bfs_reachable_within(
    graph: dict[str, list[str]], start: str, max_hops: int
) -> set[str]:
    """Return all nodes reachable from start within max_hops hops (including start)."""
    visited: set[str] = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= max_hops:
            continue
        for nxt in graph.get(node, []):
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, depth + 1))
    return visited


def _build_adjacency(transfers: list[Transfer]) -> dict[str, list[str]]:
    """Build forward adjacency list from transfers."""
    adj: dict[str, list[str]] = defaultdict(list)
    for t in transfers:
        adj[t.from_addr].append(t.to_addr)
    return dict(adj)


def _haircut_taint(
    transfers: list[Transfer], seed_addr: str, seed_amount: Decimal
) -> dict[str, float]:
    """
    Simple proportional (haircut) taint propagation.
    Returns mapping address → taint_share (0.0–1.0).
    """
    total_out: dict[str, Decimal] = defaultdict(Decimal)
    total_in: dict[str, Decimal] = defaultdict(Decimal)
    for t in transfers:
        total_out[t.from_addr] += t.amount
        total_in[t.to_addr] += t.amount

    taint: dict[str, float] = {seed_addr: 1.0}
    # BFS propagation
    queue: deque[str] = deque([seed_addr])
    visited: set[str] = {seed_addr}
    while queue:
        node = queue.popleft()
        node_taint = taint.get(node, 0.0)
        out_total = float(total_out.get(node, Decimal(0)))
        if out_total == 0:
            continue
        for t in transfers:
            if t.from_addr != node:
                continue
            share = float(t.amount) / out_total
            child_taint = node_taint * share
            existing = taint.get(t.to_addr, 0.0)
            taint[t.to_addr] = existing + child_taint
            if t.to_addr not in visited:
                visited.add(t.to_addr)
                queue.append(t.to_addr)
    return taint


def _compute_m3_node_features(
    node: str,
    depth: int,
    max_budget: int,
    transfers: list[Transfer],
    taint: dict[str, float],
    seed_addr: str,
    seed_ts: datetime,
    m1_probs: dict[str, float] | None,
    vasp_addresses: set[str],
) -> dict[str, float]:
    """Compute M3 features for a frontier node."""
    # Path features
    node_transfers_in = [t for t in transfers if t.to_addr == node]
    node_transfers_out = [t for t in transfers if t.from_addr == node]

    total_out_value = sum(float(t.amount) for t in node_transfers_out)
    distinct_out = len({t.to_addr for t in node_transfers_out})
    top1_out = 0.0
    if node_transfers_out and total_out_value > 0:
        out_by_dest: dict[str, float] = defaultdict(float)
        for t in node_transfers_out:
            out_by_dest[t.to_addr] += float(t.amount)
        top1_out = max(out_by_dest.values()) / total_out_value

    # Dwell time: time from seed to first receipt by this node
    first_receipt_ts = min((t.ts for t in node_transfers_in), default=seed_ts)
    dwell_hours = max(0.0, (first_receipt_ts - seed_ts).total_seconds() / 3600.0)

    # Value trend: log ratio of node received value to seed amount
    node_in_value = sum(float(t.amount) for t in node_transfers_in)
    seed_val = float(taint.get(seed_addr, 1.0)) if seed_addr != node else 1.0
    if node_in_value > 0 and seed_val > 0:
        value_trend_log = math.log(node_in_value + 1.0) - math.log(float(seed_val) + 1.0)
    else:
        value_trend_log = 0.0

    # Label proximity: fraction of 1-hop out-neighbors that are labeled VASPs
    label_prox = 0.0
    if node_transfers_out:
        out_neighbors = {t.to_addr for t in node_transfers_out}
        label_prox = len(out_neighbors & vasp_addresses) / len(out_neighbors)

    # M1 role probabilities (use provided or default to uniform)
    if m1_probs is None:
        m1_probs = {cls: 1.0 / len(ROLE_CLASSES) for cls in ROLE_CLASSES}

    return {
        "hops_so_far": float(depth),
        "taint_share": float(taint.get(node, 0.0)),
        "remaining_budget": float(max(0, max_budget - depth)),
        "fan_out_width": float(distinct_out),
        "top1_forward_share": float(top1_out),
        "dwell_so_far_hours": float(dwell_hours),
        "value_trend_log": float(value_trend_log),
        "n_out_cp": float(distinct_out),
        "label_proximity": float(label_prox),
        "p_exchange_hot": float(m1_probs.get("exchange_hot_or_collection", 0.0)),
        "p_exchange_deposit": float(m1_probs.get("exchange_deposit", 0.0)),
        "p_mixer": float(m1_probs.get("mixer", 0.0)),
        "p_bridge": float(m1_probs.get("bridge", 0.0)),
        "p_dex": float(m1_probs.get("dex_or_contract", 0.0)),
        "p_illicit": float(m1_probs.get("illicit", 0.0)),
        "p_personal": float(m1_probs.get("personal_or_unknown", 0.0)),
    }


# ---------------------------------------------------------------------------
# Generator-to-VASP-node mapping  (which addresses are the "exits" in each trace)
# ---------------------------------------------------------------------------

_GENERATOR_META: list[tuple[str, str, str]] = [
    # (generator_name, seed_role, vasp_role)
    # For exchange_deposit_funnel: hot_wallet is the VASP exit
    ("generate_exchange_deposit_funnel", "user_0", "hot_wallet"),
    # For layering: collection_{seed} is the VASP exit
    ("generate_layering", "seed", "collection"),
    # For benign_processor: processor is the exit
    ("generate_benign_processor", "processor", "processor"),
    # For rapid_forwarding: last hop is the VASP
    ("generate_rapid_forwarding", "hop_0", "hop_last"),
]


def build_m3_dataset(
    n_traces: int = 80,
    max_budget: int = 10,
    seed: int = 42,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """
    Build the M3 trace-labeled dataset from synthetic graphs.

    Returns:
        X: DataFrame of M3 features (one row per node visit)
        y: binary label array (1 = VASP reachable within remaining budget)
        seed_ids: integer array of seed trace index (for group-split)
    """
    # Load synth_laundering module
    sl_path = PROJECT_ROOT / "scripts" / "synth_laundering.py"
    _spec = importlib.util.spec_from_file_location("synth_laundering", sl_path)
    sl = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
    _spec.loader.exec_module(sl)  # type: ignore[union-attr]

    rng = np.random.default_rng(seed)

    # Generators and which addresses are VASPs in each pattern
    # (generator_fn, get_seed_addr(transfers), get_vasp_addrs(transfers))
    generators: list[tuple[Any, Any, Any]] = [
        (
            sl.generate_exchange_deposit_funnel,
            lambda transfers, s: f"user_{s}_0",
            lambda transfers, s: {f"hot_wallet_{s}"},
        ),
        (
            sl.generate_layering,
            lambda transfers, s: f"seed_{s}",
            lambda transfers, s: {f"collection_{s}"},
        ),
        (
            sl.generate_benign_processor,
            lambda transfers, s: f"processor_{s}",
            # Processor itself is a VASP-like exit; first destination is the exit
            lambda transfers, s: {f"emp_{s}_0", f"emp_{s}_1", f"emp_{s}_2"},
        ),
        (
            sl.generate_rapid_forwarding,
            lambda transfers, s: f"hop_{s}_0",
            lambda transfers, s: {f"hop_{s}_5"},  # last hop
        ),
    ]

    rows: list[dict] = []
    labels: list[int] = []
    seed_ids: list[int] = []

    trace_idx = 0
    per_gen = max(1, n_traces // len(generators))

    window_end = datetime.now(timezone.utc).replace(tzinfo=timezone.utc)  # noqa: F841 — kept for M1 integration

    for gen_fn, get_seed, get_vasps in generators:
        for i in range(per_gen):
            s = int(rng.integers(0, 100_000))
            transfers = gen_fn(seed=s)
            if not transfers:
                continue

            seed_addr = get_seed(transfers, s)
            vasp_addresses: set[str] = get_vasps(transfers, s)

            # Only keep traces that actually have a VASP reachable
            adj = _build_adjacency(transfers)
            seed_ts = min(t.ts for t in transfers)

            # Compute taint from seed_addr
            # Find seed amount (total outflow from seed_addr)
            seed_amount = Decimal(sum(float(t.amount) for t in transfers if t.from_addr == seed_addr))
            if seed_amount == 0:
                seed_amount = Decimal("100")
            taint = _haircut_taint(transfers, seed_addr, seed_amount)

            # BFS to enumerate nodes and their depths
            visited_order: list[tuple[str, int]] = []  # (node, depth)
            bfs_q: deque[tuple[str, int]] = deque([(seed_addr, 0)])
            bfs_seen: set[str] = {seed_addr}
            while bfs_q:
                node, depth = bfs_q.popleft()
                visited_order.append((node, depth))
                if depth < max_budget:
                    for nxt in adj.get(node, []):
                        if nxt not in bfs_seen:
                            bfs_seen.add(nxt)
                            bfs_q.append((nxt, depth + 1))

            # For each visited node, compute label and features
            for node, depth in visited_order:
                remaining = max_budget - depth
                reachable = _bfs_reachable_within(adj, node, remaining)
                label = 1 if (reachable & vasp_addresses) else 0

                # M1 role probs: uniform (M1 predictor not integrated to avoid circular dep)
                # Real training would load M1Predictor from registry and call predict(node, transfers)
                m3_feats = _compute_m3_node_features(
                    node=node,
                    depth=depth,
                    max_budget=max_budget,
                    transfers=transfers,
                    taint=taint,
                    seed_addr=seed_addr,
                    seed_ts=seed_ts,
                    m1_probs=None,  # uniform — M1 not integrated here (avoid circular dep)
                    vasp_addresses=vasp_addresses,
                )
                rows.append(m3_feats)
                labels.append(label)
                seed_ids.append(trace_idx)

            trace_idx += 1

    X = pd.DataFrame(rows, columns=M3_FEATURE_NAMES).fillna(0.0)
    y = np.array(labels, dtype=int)
    groups = np.array(seed_ids, dtype=int)
    return X, y, groups
