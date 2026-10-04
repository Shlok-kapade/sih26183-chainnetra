"""Dataset builder for M1 — loads labels, builds feature matrix from synthetic transfers."""
from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.ingest.normalize import Transfer
from app.ml.features import (
    ENTITY_TYPE_TO_ROLE,
    ROLE_TO_IDX,
    compute_features,
    features_to_df,
)

PROJECT_ROOT = Path(__file__).parents[3]
LABEL_DIR = PROJECT_ROOT / "data" / "labels"


def load_label_csv(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_all_labels(label_dir: Path = LABEL_DIR) -> list[dict]:
    """Load all label CSV files from label_dir."""
    rows = []
    for p in label_dir.glob("*.csv"):
        if p.name.startswith("contracts_"):
            continue  # contract lists, not address labels
        rows.extend(load_label_csv(p))
    return rows


def labels_to_role_map(labels: list[dict]) -> dict[tuple[str, str], str]:
    """Returns {(address, chain): role_class}."""
    mapping: dict[tuple[str, str], str] = {}
    for row in labels:
        etype = row.get("entity_type", "unknown")
        role = ENTITY_TYPE_TO_ROLE.get(etype, "personal_or_unknown")
        mapping[(row["address"], row.get("chain", ""))] = role
    return mapping


def build_dataset_from_labels_and_synthetics(
    labels: list[dict],
    synthetic_transfers_by_address: dict[str, list[Transfer]] | None = None,
    window_end: datetime | None = None,
) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """
    Build (X, y, addresses) from label rows + optional synthetic transfer dicts.

    For each labeled address, compute features from synthetic_transfers_by_address
    (or an empty list if none available), then add the label.

    Returns X (DataFrame), y (int array of class indices), addresses (list of str).
    """
    if window_end is None:
        window_end = datetime.now(timezone.utc)

    role_map = labels_to_role_map(labels)
    feature_rows = []
    y_list: list[int] = []
    addr_list: list[str] = []

    synthetic_transfers_by_address = synthetic_transfers_by_address or {}

    for (address, chain), role in role_map.items():
        transfers = synthetic_transfers_by_address.get(address, [])
        feats = compute_features(
            address=address,
            all_transfers=transfers,
            window_end=window_end,
            neighbor_labels=None,
            chain=chain,
        )
        feature_rows.append(feats)
        y_list.append(ROLE_TO_IDX[role])
        addr_list.append(address)

    if not feature_rows:
        # Return empty frame with correct columns
        dummy = compute_features("x", [], window_end)
        X = pd.DataFrame(columns=list(dummy.keys()))
        return X, np.array([], dtype=int), []

    X = features_to_df(feature_rows)
    y = np.array(y_list, dtype=int)
    return X, y, addr_list


def build_synthetic_dataset(
    n_per_class: int = 200,
    seed: int = 42,
) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """
    Build a purely synthetic dataset using scripts/synth_laundering.py generators.
    Used when real labeled data is insufficient (< 50 samples/class).
    Tags: all rows flagged SYNTHETIC in provenance.
    Returns (X, y, addresses).
    """
    import importlib.util
    _spec = importlib.util.spec_from_file_location(
        "synth_laundering", PROJECT_ROOT / "scripts" / "synth_laundering.py"
    )
    sl = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
    _spec.loader.exec_module(sl)  # type: ignore[union-attr]

    rng = np.random.default_rng(seed)

    # Map generator → role class
    generators = [
        (sl.generate_layering, "exchange_hot_or_collection"),
        (sl.generate_rapid_forwarding, "exchange_deposit"),
        (sl.generate_peel_chain, "mixer"),
        (sl.generate_round_trip, "bridge"),
        (sl.generate_benign_processor, "dex_or_contract"),
        (sl.generate_structuring, "illicit"),
        (sl.generate_dormancy_burst, "personal_or_unknown"),
    ]

    feature_rows: list[dict] = []
    y_list: list[int] = []
    addr_list: list[str] = []
    window_end = datetime.now(timezone.utc) + timedelta(days=365)  # include all synthetic transfers

    for i in range(n_per_class):
        for gen_fn, role in generators:
            seed_i = int(rng.integers(0, 100000))
            transfers = gen_fn(seed=seed_i)
            if not transfers:
                continue

            # Find hub address: most-connected by combined in+out degree
            from collections import Counter  # noqa: PLC0415
            degree: Counter = Counter()
            for t in transfers:
                degree[t.from_addr] += 1
                degree[t.to_addr] += 1
            address = degree.most_common(1)[0][0]

            feats = compute_features(
                address=address,
                all_transfers=transfers,
                window_end=window_end,
                neighbor_labels=None,
                chain=transfers[0].chain,
            )
            feature_rows.append(feats)
            y_list.append(ROLE_TO_IDX[role])
            addr_list.append(f"SYNTHETIC_{role}_{i}")

    X = features_to_df(feature_rows)
    y = np.array(y_list, dtype=int)
    return X, y, addr_list


def data_manifest(label_paths: list[Path], dataset_hash: str) -> dict[str, Any]:
    """Build data provenance manifest."""
    files = []
    for p in label_paths:
        if p.exists():
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            files.append({"path": str(p), "sha256": h})
    return {
        "label_files": files,
        "dataset_sha256": dataset_hash,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "note": "Synthetic dataset generated by scripts/synth_laundering.py; real labels from data/labels/",
    }
