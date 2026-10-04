"""
M1 Training Script
==================
Usage: backend/.venv/bin/python backend/ml/train/train_m1.py

Trains LightGBM multiclass classifier with:
- Temporal split (80/20 by synthetic trace index, preserving time ordering)
- Leave-one-class-out split (one role withheld for generalization test)
- Isotonic calibration on held-out calibration fold
- SHAP top-k feature importance
- Model registry save

All splits are seeded. No data is fabricated — synthetic dataset is generated
deterministically from synth_laundering.py generators.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import hashlib
import warnings

import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    f1_score,
)

from app.ml.datasets import (
    build_synthetic_dataset,
    data_manifest,
    load_all_labels,
)
from app.ml.features import ROLE_CLASSES, ROLE_TO_IDX
from app.ml.registry import ModelRegistry

warnings.filterwarnings("ignore", category=UserWarning)

SEED = 42
VERSION = "v0.1"
N_PER_CLASS = 300  # synthetic samples per class


from app.ml.utils import expected_calibration_error
from app.ml.utils import per_class_pr_auc as _prauc


def per_class_pr_auc(y_prob: np.ndarray, y_true: np.ndarray, n_classes: int) -> dict[str, float]:
    return _prauc(y_prob, y_true, ROLE_CLASSES)


def rules_baseline_predict(X: pd.DataFrame) -> np.ndarray:
    """
    Simple rules baseline using interpretable features.
    Returns predicted class indices.
    """
    preds = np.full(len(X), ROLE_TO_IDX["personal_or_unknown"])
    # Exchange hot: high 24/7 entropy, many counterparties
    mask = (X["hour_entropy"] > 2.5) & (X["n_in_cp"] > 10)
    preds[mask] = ROLE_TO_IDX["exchange_hot_or_collection"]
    # Exchange deposit: many senders, high forward ratio
    mask = (X["n_in_cp"] > 5) & (X["fwd_ratio_24h"] > 0.8)
    preds[mask] = ROLE_TO_IDX["exchange_deposit"]
    # Mixer: rapid forward, high fan-in, round amounts
    mask = (X["fwd_ratio_10m"] > 0.7) & (X["fan_in_ratio"] > 3)
    preds[mask] = ROLE_TO_IDX["mixer"]
    # Structuring/illicit: round amounts, small deposits
    mask = (X["round_amount_share"] > 0.6) & (X["small_deposit_share"] > 0.5)
    preds[mask] = ROLE_TO_IDX["illicit"]
    return preds


def main() -> None:
    print("=" * 60)
    print("ChainNetra M1 — Address Role Classifier Training")
    print("=" * 60)

    # 1. Build dataset
    print("\n[1/7] Building synthetic dataset …")
    X, y, addresses = build_synthetic_dataset(n_per_class=N_PER_CLASS, seed=SEED)
    print(f"  Dataset: {len(X)} samples, {len(X.columns)} features")
    for cls_idx, cls_name in enumerate(ROLE_CLASSES):
        count = (y == cls_idx).sum()
        print(f"  {cls_name}: {count} samples")

    feature_names = list(X.columns)

    # Data manifest
    label_paths = list((PROJECT_ROOT / "data" / "labels").glob("*.csv"))
    dataset_hash = hashlib.sha256(pd.util.hash_pandas_object(X).values.tobytes()).hexdigest()
    manifest = data_manifest(label_paths, dataset_hash)

    # 2. Temporal split (80/20, preserving generation order)
    print("\n[2/7] Temporal split (80/20 by index order) …")
    n = len(X)
    split_idx = int(n * 0.8)
    X_train_full, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train_full, y_test = y[:split_idx], y[split_idx:]

    # Hold out 10% of train as calibration set
    cal_split = int(len(X_train_full) * 0.9)
    X_train, X_cal = X_train_full.iloc[:cal_split], X_train_full.iloc[cal_split:]
    y_train, y_cal = y_train_full[:cal_split], y_train_full[cal_split:]

    print(f"  Train: {len(X_train)} | Cal: {len(X_cal)} | Test: {len(X_test)}")

    # Class weights (inverse frequency)
    class_counts = np.bincount(y_train, minlength=len(ROLE_CLASSES))
    class_weights = {i: float(len(y_train) / max(c * len(ROLE_CLASSES), 1)) for i, c in enumerate(class_counts)}

    # 3. Train LightGBM
    print("\n[3/7] Training LightGBM …")
    lgb_params = {
        "objective": "multiclass",
        "num_class": len(ROLE_CLASSES),
        "metric": "multi_logloss",
        "n_estimators": 200,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_child_samples": 5,
        "class_weight": class_weights,
        "random_state": SEED,
        "n_jobs": -1,
        "verbose": -1,
    }
    lgb_model = lgb.LGBMClassifier(**lgb_params)
    lgb_model.fit(X_train, y_train)

    # Uncalibrated test probs
    y_prob_raw = lgb_model.predict_proba(X_test)

    # 4. Isotonic calibration on held-out calibration fold
    # sklearn 1.9 removed cv='prefit'; implement per-class isotonic calibration manually
    print("\n[4/7] Calibrating with isotonic regression …")
    from sklearn.isotonic import IsotonicRegression  # noqa: PLC0415

    raw_cal_probs = lgb_model.predict_proba(X_cal)
    raw_test_probs = lgb_model.predict_proba(X_test)
    n_classes = len(ROLE_CLASSES)

    # Fit one isotonic regressor per class (one-vs-rest)
    iso_regressors = []
    cal_probs_adj = np.zeros_like(raw_test_probs)
    for c in range(n_classes):
        y_bin_cal = (y_cal == c).astype(float)
        ir = IsotonicRegression(out_of_bounds="clip")
        ir.fit(raw_cal_probs[:, c], y_bin_cal)
        iso_regressors.append(ir)
        cal_probs_adj[:, c] = ir.predict(raw_test_probs[:, c])

    # Renormalize rows to sum to 1
    row_sums = cal_probs_adj.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1.0, row_sums)
    y_prob_cal = cal_probs_adj / row_sums

    ece_raw = expected_calibration_error(raw_test_probs, y_test)
    ece_cal = expected_calibration_error(y_prob_cal, y_test)
    print(f"  ECE before calibration: {ece_raw:.4f}")
    print(f"  ECE after calibration:  {ece_cal:.4f}")

    # 5. Baselines
    print("\n[5/7] Baselines …")
    # Rules baseline
    y_rules = rules_baseline_predict(X_test)
    f1_rules = f1_score(y_test, y_rules, average="macro", zero_division=0)

    # Logistic regression baseline
    lr = LogisticRegression(max_iter=1000, random_state=SEED, class_weight="balanced")
    lr.fit(X_train, y_train)
    y_lr_pred = lr.predict(X_test)
    y_lr_prob = lr.predict_proba(X_test)
    f1_lr = f1_score(y_test, y_lr_pred, average="macro", zero_division=0)

    # LightGBM
    y_lgb_pred = y_prob_cal.argmax(axis=1)
    f1_lgb = f1_score(y_test, y_lgb_pred, average="macro", zero_division=0)

    pr_auc_rules: dict[str, float] = {}
    pr_auc_lr = per_class_pr_auc(y_lr_prob, y_test, len(ROLE_CLASSES))
    pr_auc_lgb = per_class_pr_auc(y_prob_cal, y_test, len(ROLE_CLASSES))

    print(f"  Rules  macro-F1: {f1_rules:.3f}")
    print(f"  LogReg macro-F1: {f1_lr:.3f}")
    print(f"  LightGBM(cal) macro-F1: {f1_lgb:.3f}")

    # 6. Leave-one-class-out (proxy for leave-one-exchange-out with synthetic data)
    print("\n[6/7] Leave-one-class-out evaluation …")
    loeo_results: dict[str, dict] = {}
    for withheld_idx, withheld_cls in enumerate(ROLE_CLASSES):
        mask_train = y_train != withheld_idx
        mask_test = y_test == withheld_idx
        if mask_train.sum() < 10 or mask_test.sum() == 0:
            continue
        Xtr = X_train[mask_train]
        ytr = y_train[mask_train]
        loeo_params = {k: v for k, v in lgb_params.items() if k != "class_weight"}
        loeo_params["class_weight"] = "balanced"
        model_loeo = lgb.LGBMClassifier(**loeo_params)
        model_loeo.fit(Xtr, ytr)
        Xte = X_test[mask_test]
        yte = y_test[mask_test]
        prob_loeo = model_loeo.predict_proba(Xte)
        # Pad probs to full n_classes shape
        n_cls_trained = prob_loeo.shape[1]
        if n_cls_trained < len(ROLE_CLASSES):
            # Model trained without withheld class — recall@withheld is 0 by construction
            recall_withheld = 0.0
        else:
            pred_loeo = prob_loeo.argmax(axis=1)
            recall_withheld = float((pred_loeo == withheld_idx).mean())
        loeo_results[withheld_cls] = {
            "withheld_n_test": int(mask_test.sum()),
            "recall_withheld": round(recall_withheld, 4),
            "note": "Proxy leave-one-class-out (real leave-one-exchange-out requires exchange-level labels)",
        }
        print(f"  Withheld={withheld_cls}: recall={recall_withheld:.3f} (n={mask_test.sum()})")

    # 7. SHAP feature importance
    print("\n[7/7] Computing SHAP values …")
    try:
        explainer = shap.TreeExplainer(lgb_model)
        shap_values = explainer.shap_values(X_test[:50])  # sample for speed
        # shap_values shape: (n_classes, n_samples, n_features) or (n_samples, n_features, n_classes)
        if isinstance(shap_values, list):
            # list of arrays, one per class
            mean_abs_shap = np.array([np.abs(sv).mean(axis=0) for sv in shap_values]).mean(axis=0)
        else:
            mean_abs_shap = np.abs(shap_values).mean(axis=(0, 1)) if shap_values.ndim == 3 else np.abs(shap_values).mean(axis=0)
        top_k = 15
        top_indices = np.argsort(mean_abs_shap)[::-1][:top_k]
        top_features = {feature_names[i]: float(mean_abs_shap[i]) for i in top_indices}
        print("  Top features (mean |SHAP|):")
        for fname, fval in list(top_features.items())[:5]:
            print(f"    {fname}: {fval:.4f}")
    except Exception as e:
        print(f"  SHAP computation failed: {e} — skipping")
        top_features = {}

    # Assemble metrics
    metrics = {
        "dataset": {
            "n_samples": int(len(X)),
            "n_features": int(len(feature_names)),
            "n_train": int(len(X_train)),
            "n_cal": int(len(X_cal)),
            "n_test": int(len(X_test)),
            "note": "Synthetic dataset — real-data metrics will differ. See MODEL_CARD.md.",
        },
        "temporal_split": {
            "lgbm_macro_f1": round(f1_lgb, 4),
            "lgbm_ece": round(ece_cal, 4),
            "lgbm_pr_auc_per_class": {k: (round(v, 4) if not (isinstance(v, float) and v != v) else "n/a") for k, v in pr_auc_lgb.items()},
            "lr_baseline_macro_f1": round(f1_lr, 4),
            "lr_pr_auc_per_class": {k: (round(v, 4) if not (isinstance(v, float) and v != v) else "n/a") for k, v in pr_auc_lr.items()},
            "rules_baseline_macro_f1": round(f1_rules, 4),
            "ece_before_calibration": round(ece_raw, 4),
            "ece_after_calibration": round(ece_cal, 4),
        },
        "leave_one_class_out": loeo_results,
        "shap_top_features": top_features,
        "classification_report_lgbm": classification_report(
            y_test, y_lgb_pred,
            target_names=ROLE_CLASSES,
            zero_division=0,
            output_dict=True,
        ),
    }

    # Build config
    config = {
        "model_id": "m1",
        "model_type": "LightGBMClassifier + IsotonicCalibration",
        "classes": ROLE_CLASSES,
        "n_classes": len(ROLE_CLASSES),
        "lgbm_params": lgb_params,
        "abstain_threshold": 0.4,
        "feature_names": feature_names,
        "seed": SEED,
        "dataset": "synthetic (synth_laundering.py) + data/labels/ CSVs",
        "temporal_split": "80/20 by generation index",
    }

    # Model card
    model_card = f"""# MODEL_CARD — M1 Address Role Classifier

## Intended Use
Classify blockchain addresses into one of {len(ROLE_CLASSES)} roles to support
investigative leads for law enforcement. **Outputs are investigative leads, not
proof of wrongdoing.**

## Classes
{chr(10).join(f"- {c}" for c in ROLE_CLASSES)}

## Training Data
- **Real labels**: {len(load_all_labels())} rows from data/labels/ (OFAC SDN, PoR disclosures)
- **Synthetic data**: {N_PER_CLASS} samples/class from scripts/synth_laundering.py (seed={SEED})
- **WARNING**: Model is currently trained primarily on synthetic data due to
  insufficient real labeled addresses. Metrics below are on synthetic test data and
  will NOT generalize to real-world performance. Real-world performance is unknown
  until real labeled data is added.

## Splits
- Temporal: 80% train / 10% calibration / 20% test (by generation index)
- Leave-one-class-out: see metrics.json

## Metrics (synthetic test set — see warning above)
- Macro-F1 (LightGBM, calibrated): {f1_lgb:.3f}
- Macro-F1 (LogReg baseline): {f1_lr:.3f}
- Macro-F1 (Rules baseline): {f1_rules:.3f}
- ECE (before cal): {ece_raw:.4f} | ECE (after cal): {ece_cal:.4f}

## Calibration
Isotonic calibration on held-out calibration fold. Abstain (→ UNATTRIBUTED)
when max probability < {config["abstain_threshold"]}.

## Failure Modes
- Payment processors look like exchange_hot (FP)
- OTC desks look like exchange_deposit (FP)
- Shared deposit addresses across users reduce precision
- Stale labels (VASP changes custodian) cause misclassification
- Synthetic training → real-world distribution shift is unknown

## Label Bias
Labels biased to large exchanges (Binance PoR), OFAC-listed addresses.
Under-represents DeFi, DEX, regional exchanges.

## Fairness / Harms Note
Misattribution risk: model may incorrectly flag legitimate personal wallets
as illicit. All outputs must be reviewed by a human analyst before any action.

## Version
{VERSION} — {config.get("saved_at", "see config.json")}
"""

    # Save to registry
    registry = ModelRegistry()
    saved_path = registry.save(
        model_id="m1",
        version=VERSION,
        model=lgb_model,
        config=config,
        metrics=metrics,
        data_manifest=manifest,
        model_card=model_card,
        extra_files={
            "calibrator.pkl": iso_regressors,
            "feature_names.json": feature_names,
        },
    )
    print(f"\n✓ Model saved to: {saved_path}")
    print("  Run 'make eval' to generate docs/evaluation/RESULTS.md")


if __name__ == "__main__":
    main()
