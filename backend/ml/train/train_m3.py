"""
M3 — Guided Tracing Policy Classifier
======================================
Task: binary classifier — P(labeled VASP reachable within remaining budget)
Model: LightGBM binary + isotonic calibration
Split: group-based by seed_id (no seed appears in both train and test)

Usage:
    backend/.venv/bin/python backend/ml/train/train_m3.py
    (also: make train-m3)

Outputs to: ml/artifacts/m3/v0.1/
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import lightgbm as lgb
import numpy as np
import shap
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit

PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.m3_dataset import M3_FEATURE_NAMES, build_m3_dataset  # noqa: E402
from app.ml.registry import ModelRegistry  # noqa: E402
from app.ml.utils import expected_calibration_error  # noqa: E402

warnings.filterwarnings("ignore", category=UserWarning)

SEED = 42
VERSION = "v0.1"
N_TRACES = 120       # synthetic trace graphs (each produces multiple node rows)
MAX_BUDGET = 10      # max hop budget for label computation


def main() -> None:
    print("=" * 60)
    print("ChainNetra M3 — Guided Tracing Policy Training")
    print("=" * 60)

    # 1. Build dataset
    print("\n[1/6] Building trace-labeled dataset …")
    X, y, groups = build_m3_dataset(n_traces=N_TRACES, max_budget=MAX_BUDGET, seed=SEED)
    n_pos = int(y.sum())
    n_neg = int((y == 0).sum())
    print(f"  Total nodes: {len(X)} | Positive (VASP reachable): {n_pos} | Negative: {n_neg}")
    print(f"  Features: {X.shape[1]}")
    print(f"  Unique seeds (traces): {len(np.unique(groups))}")

    if n_pos == 0 or n_neg == 0:
        print("ERROR: Dataset has no positive or no negative examples. Aborting.")
        sys.exit(1)

    # 2. Group-based train/cal/test split (80/10/10 by seed group)
    print("\n[2/6] Group split by seed_id (80 / 10 / 10) …")
    gss_outer = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    train_idx, temp_idx = next(gss_outer.split(X, y, groups))
    gss_inner = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=SEED)
    cal_rel, test_rel = next(gss_inner.split(
        X.iloc[temp_idx], y[temp_idx], groups[temp_idx]
    ))
    cal_idx = temp_idx[cal_rel]
    test_idx = temp_idx[test_rel]

    X_train, y_train = X.iloc[train_idx].values, y[train_idx]
    X_cal, y_cal = X.iloc[cal_idx].values, y[cal_idx]
    X_test, y_test = X.iloc[test_idx].values, y[test_idx]

    # Verify group disjointness
    train_seeds = set(groups[train_idx])
    test_seeds = set(groups[test_idx])
    assert len(train_seeds & test_seeds) == 0, "Seed leakage between train and test!"
    print(f"  Train: {len(X_train)} rows ({len(train_seeds)} seeds)")
    print(f"  Cal:   {len(X_cal)} rows")
    print(f"  Test:  {len(X_test)} rows ({len(test_seeds)} seeds)")

    # 3. Train LightGBM
    print("\n[3/6] Training LightGBM …")
    pos_weight = n_neg / max(n_pos, 1)
    lgb_params = {
        "objective": "binary",
        "metric": "binary_logloss",
        "n_estimators": 200,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_child_samples": 5,
        "scale_pos_weight": pos_weight,
        "random_state": SEED,
        "verbose": -1,
    }
    model = lgb.LGBMClassifier(**lgb_params)
    model.fit(X_train, y_train)
    raw_prob_cal = model.predict_proba(X_cal)[:, 1]
    raw_prob_test = model.predict_proba(X_test)[:, 1]

    # 4. Isotonic calibration on cal fold
    print("\n[4/6] Isotonic calibration …")
    ir = IsotonicRegression(out_of_bounds="clip")
    ir.fit(raw_prob_cal, y_cal.astype(float))
    cal_prob_test = ir.predict(raw_prob_test)

    # Metrics
    threshold = 0.5
    y_pred = (cal_prob_test >= threshold).astype(int)
    pr_auc = average_precision_score(y_test, cal_prob_test)
    roc_auc = roc_auc_score(y_test, cal_prob_test)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    ece = expected_calibration_error(
        np.column_stack([1 - cal_prob_test, cal_prob_test]), y_test
    )

    print(f"  PR-AUC:  {pr_auc:.4f}")
    print(f"  ROC-AUC: {roc_auc:.4f}")
    print(f"  F1 @ 0.5: {f1:.4f}")
    print(f"  ECE:     {ece:.4f}")

    # 5. SHAP
    print("\n[5/6] Computing SHAP values …")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test[:min(200, len(X_test))])
    if isinstance(shap_values, list):
        shap_arr = shap_values[1]
    else:
        shap_arr = shap_values
    mean_abs_shap = np.abs(shap_arr).mean(axis=0)
    top_idx = np.argsort(mean_abs_shap)[::-1][:5]
    top_features = [(M3_FEATURE_NAMES[i], float(mean_abs_shap[i])) for i in top_idx]
    print("  Top features (mean |SHAP|):")
    for fname, fval in top_features:
        print(f"    {fname}: {fval:.4f}")

    # 6. Save to registry
    print("\n[6/6] Saving to registry …")
    config = {
        "model_type": "lightgbm_binary",
        "calibration": "isotonic",
        "n_traces": N_TRACES,
        "max_budget": MAX_BUDGET,
        "threshold": threshold,
        "seed": SEED,
        "feature_names": M3_FEATURE_NAMES,
        "note": (
            "Trained on synthetic graphs only (synth_laundering.py). "
            "Real-world performance unknown. Ground-truth bias: only labeled VASPs counted. "
            "See MODEL_CARD.md."
        ),
    }
    metrics = {
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "f1_at_threshold_0_5": f1,
        "ece": ece,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_positive_test": int(y_test.sum()),
        "top_shap_features": top_features,
        "data_note": (
            "SYNTHETIC DATA ONLY. Metrics do not reflect real-world investigative recall. "
            "Ground-truth only includes exits to labeled VASPs; unlabeled exchanges are invisible."
        ),
    }
    model_card = f"""# M3 Model Card — Guided Tracing Policy

## Intended Use
Priority function for best-first search over blockchain transaction graphs.
Predicts P(labeled VASP reachable within remaining hop budget) for a frontier node.
Used to rank which node to expand next, minimizing API calls needed to find exits.

## Training Data
- **Source**: Synthetic graphs from `scripts/synth_laundering.py`
- **Size**: {len(X)} node observations from {N_TRACES} trace graphs
- **Features**: {len(M3_FEATURE_NAMES)} (path features + M1 role probs + label proximity)
- **Split**: Group-based by seed_id; no seed in both train and test

## ⚠️ Ground-Truth Bias (MUST READ)
Ground truth only includes exits to **labeled** VASPs (exchange addresses in
`data/labels/*.csv`). Unlabeled exchanges are invisible to the evaluation.
Published recall metrics are **lower bounds** on true coverage. In production,
the engine will find more exits than the metrics suggest — but those extra exits
cannot be verified against ground truth without broader labeling.

## Metrics (synthetic test set)
| Metric | Value |
|--------|-------|
| PR-AUC | {pr_auc:.4f} |
| ROC-AUC | {roc_auc:.4f} |
| F1 @ threshold=0.5 | {f1:.4f} |
| ECE | {ece:.4f} |

## Top SHAP Features
{chr(10).join(f"- {n}: {v:.4f}" for n, v in top_features)}

## Failure Modes
- Synthetic distribution differs from real-world (sparse, heterogeneous) graphs
- M1 role probs injected as uniform (M1 not integrated at dataset build time)
- LOEO not applicable here (group split by trace seed serves same purpose)
- Assumes labeled VASP addresses are in `data/labels/`; fresh VASPs invisible

## Version
{VERSION} | seed={SEED}
"""

    registry = ModelRegistry()
    saved_path = registry.save(
        model_id="m3",
        version=VERSION,
        model=model,
        config=config,
        metrics=metrics,
        data_manifest={"built_at": __import__("datetime").datetime.utcnow().isoformat(), "synthetic": True},
        model_card=model_card,
        extra_files={"calibrator.pkl": ir, "feature_names.json": M3_FEATURE_NAMES},
    )
    print(f"\n✓ M3 model saved to: {saved_path}")
    print("  Run 'make eval' to regenerate docs/evaluation/RESULTS.md")


if __name__ == "__main__":
    main()
