"""
M1 Address Role Classifier — Feature Engineering
Point-in-time features computed from Transfer lists.
All features use only transactions with ts <= window_end.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import numpy as np
import pandas as pd

from app.ingest.normalize import Transfer

# Class labels (M1 multiclass)
ROLE_CLASSES = [
    "exchange_hot_or_collection",
    "exchange_deposit",
    "mixer",
    "bridge",
    "dex_or_contract",
    "illicit",
    "personal_or_unknown",
]

ROLE_TO_IDX = {r: i for i, r in enumerate(ROLE_CLASSES)}

# Map from entity_type in label CSVs → M1 class
ENTITY_TYPE_TO_ROLE: dict[str, str] = {
    "exchange_hot": "exchange_hot_or_collection",
    "exchange_cold": "exchange_hot_or_collection",
    "exchange_deposit": "exchange_deposit",
    "mixer": "mixer",
    "bridge": "bridge",
    "dex": "dex_or_contract",
    "sanctioned": "illicit",
    "scam": "illicit",
    "phishing": "illicit",
    "service": "personal_or_unknown",
    "unknown": "personal_or_unknown",
}


def _safe_log1p(x: float) -> float:
    return math.log1p(max(x, 0.0))


def compute_features(
    address: str,
    all_transfers: list[Transfer],
    window_end: datetime,
    neighbor_labels: dict[str, str] | None = None,
    chain: str | None = None,
) -> dict[str, float]:
    """
    Compute M1 point-in-time features for `address`.

    Parameters
    ----------
    address:
        Target address.
    all_transfers:
        All known transfers visible at window_end (ts <= window_end).
        May include transfers not involving address (for label proximity).
    window_end:
        Evaluation timestamp. Only transfers with ts <= window_end are used.
    neighbor_labels:
        Pre-computed {addr: role_class} for 1-hop neighbors from label store,
        as of window_end (never use future labels).
    chain:
        Chain identifier string (encoded as feature).
    """
    # Filter point-in-time
    pit = [t for t in all_transfers if t.ts <= window_end]
    inflows = [t for t in pit if t.to_addr == address]
    outflows = [t for t in pit if t.from_addr == address]

    total_in = float(sum(t.amount for t in inflows))
    total_out = float(sum(t.amount for t in outflows))
    n_in_tx = len(inflows)
    n_out_tx = len(outflows)
    n_in_cp = len({t.from_addr for t in inflows})
    n_out_cp = len({t.to_addr for t in outflows})

    eps = 1e-9

    # --- Degree features ---
    feats: dict[str, float] = {
        "n_in_cp": float(n_in_cp),
        "n_out_cp": float(n_out_cp),
        "log_n_in_cp": _safe_log1p(n_in_cp),
        "log_n_out_cp": _safe_log1p(n_out_cp),
        "n_in_tx": float(n_in_tx),
        "n_out_tx": float(n_out_tx),
        "log_total_in": _safe_log1p(total_in),
        "log_total_out": _safe_log1p(total_out),
    }

    # --- Balance dynamics ---
    avg_balance = max(total_in - total_out, 0.0)
    turnover = total_out / max(avg_balance, eps)
    feats["turnover"] = min(turnover, 1000.0)
    feats["balance_ratio"] = avg_balance / max(total_in, eps)

    # --- Forwarding behavior ---
    # For each inflow, check if address sent out within fixed windows
    fwd_10m = fwd_1h = fwd_24h = 0.0
    dwell_times: list[float] = []
    for inf in inflows:
        following = [
            o for o in outflows
            if o.ts >= inf.ts
        ]
        if not following:
            continue
        first_out = min(following, key=lambda o: o.ts)
        delta_s = (first_out.ts - inf.ts).total_seconds()
        dwell_times.append(delta_s)
        amt = float(inf.amount)
        if delta_s <= 600:
            fwd_10m += amt
        if delta_s <= 3600:
            fwd_1h += amt
        if delta_s <= 86400:
            fwd_24h += amt

    feats["fwd_ratio_10m"] = fwd_10m / max(total_in, eps)
    feats["fwd_ratio_1h"] = fwd_1h / max(total_in, eps)
    feats["fwd_ratio_24h"] = fwd_24h / max(total_in, eps)
    feats["median_dwell_s"] = float(np.median(dwell_times)) if dwell_times else 0.0
    feats["log_median_dwell_s"] = _safe_log1p(feats["median_dwell_s"])

    # Amount-match ratio: out ≈ in − fee (single-hop pass-through)
    if n_in_tx == 1 and n_out_tx == 1 and total_in > 0:
        ratio = total_out / total_in
        feats["amount_match_ratio"] = float(ratio)
    else:
        feats["amount_match_ratio"] = 0.0

    # Single-target forwarding share (top-1 out counterparty)
    out_by_dest: dict[str, float] = defaultdict(float)
    for o in outflows:
        out_by_dest[o.to_addr] += float(o.amount)
    if out_by_dest:
        top1_out = max(out_by_dest.values())
        feats["top1_out_share"] = top1_out / max(total_out, eps)
    else:
        feats["top1_out_share"] = 0.0

    # --- Fan structure ---
    fan_in_ratio = n_in_cp / max(n_out_cp, 1)
    feats["fan_in_ratio"] = float(fan_in_ratio)

    def gini(values: list[float]) -> float:
        if not values:
            return 0.0
        arr = sorted(values)
        n = len(arr)
        s = sum(arr)
        if s == 0:
            return 0.0
        cum = sum(v * (i + 1) for i, v in enumerate(arr))
        return (2 * cum / (n * s)) - (n + 1) / n

    in_amounts = [float(t.amount) for t in inflows]
    out_amounts = [float(t.amount) for t in outflows]
    feats["gini_in"] = gini(in_amounts)
    feats["gini_out"] = gini(out_amounts)

    # --- Temporal features ---
    all_ts = sorted(t.ts for t in pit if t.from_addr == address or t.to_addr == address)
    if len(all_ts) >= 2:
        intervals = [(all_ts[i+1] - all_ts[i]).total_seconds() for i in range(len(all_ts)-1)]
        feats["inter_arrival_mean"] = float(np.mean(intervals))
        feats["inter_arrival_cv"] = float(np.std(intervals) / max(np.mean(intervals), eps))
        # Burstiness: (std - mean) / (std + mean)
        std_ia = float(np.std(intervals))
        mean_ia = float(np.mean(intervals))
        feats["burstiness"] = (std_ia - mean_ia) / max(std_ia + mean_ia, eps)
    else:
        feats["inter_arrival_mean"] = 0.0
        feats["inter_arrival_cv"] = 0.0
        feats["burstiness"] = 0.0

    if all_ts:
        account_age_days = (window_end - all_ts[0]).total_seconds() / 86400.0
        feats["account_age_days"] = max(account_age_days, 0.0)
        n_days = max(account_age_days, 1.0)
        active_days = len({t.ts.date() for t in pit if t.from_addr == address or t.to_addr == address})
        feats["days_active_ratio"] = float(active_days) / n_days
    else:
        feats["account_age_days"] = 0.0
        feats["days_active_ratio"] = 0.0

    # Hourly entropy (24/7 activity → high entropy)
    hour_counts: list[int] = [0] * 24
    for t in pit:
        if t.from_addr == address or t.to_addr == address:
            hour_counts[t.ts.hour] += 1
    total_tx = sum(hour_counts)
    if total_tx > 0:
        probs = [c / total_tx for c in hour_counts if c > 0]
        feats["hour_entropy"] = -sum(p * math.log(p) for p in probs)
    else:
        feats["hour_entropy"] = 0.0

    # --- Value shape ---
    def is_round(v: Decimal) -> bool:
        f = float(v)
        return f > 0 and (f % 100 < 1 or f % 10 < 0.01 or f % 1000 < 1)

    round_count = sum(1 for t in pit if (t.from_addr == address or t.to_addr == address) and is_round(t.amount))
    total_tx_count = n_in_tx + n_out_tx
    feats["round_amount_share"] = round_count / max(total_tx_count, 1)

    if in_amounts:
        in_log = [math.log(v + eps) for v in in_amounts if v > 0]
        feats["amount_entropy"] = float(-sum((1/len(in_log)) * v for v in in_log)) if in_log else 0.0
    else:
        feats["amount_entropy"] = 0.0

    small_threshold = 10.0  # $10 or equivalent
    small_count = sum(1 for t in inflows if float(t.amount) < small_threshold)
    feats["small_deposit_share"] = small_count / max(n_in_tx, 1)

    # --- Counterparty label proximity (1-hop, point-in-time) ---
    neighbor_roles: dict[str, int] = defaultdict(int)
    all_neighbors = {t.from_addr for t in inflows} | {t.to_addr for t in outflows}
    all_neighbors.discard(address)

    if neighbor_labels:
        for nb in all_neighbors:
            role = neighbor_labels.get(nb)
            if role:
                neighbor_roles[role] += 1

    n_nb = max(len(all_neighbors), 1)
    for role in ROLE_CLASSES:
        feats[f"nb_share_{role}"] = neighbor_roles.get(role, 0) / n_nb

    # --- Chain encoding ---
    chain_map = {"ethereum": 0, "tron": 1, "bitcoin": 2, "bsc": 3, "polygon": 4}
    feats["chain_id"] = float(chain_map.get((chain or "").lower(), 99))

    return feats


def features_to_df(feature_dicts: list[dict[str, float]]) -> pd.DataFrame:
    """Convert list of feature dicts to DataFrame with consistent column order."""
    return pd.DataFrame(feature_dicts).fillna(0.0)
