"""
M1b Training Script — BTC Illicit Transaction Scorer (Elliptic Dataset)
========================================================================
Usage: backend/.venv/bin/python backend/ml/train/train_m1b.py

Requires the Elliptic Bitcoin Dataset. See instructions below if dataset
is not present — the script exits with clear directions rather than
fabricating data.

DATASET INSTRUCTIONS
--------------------
The Elliptic dataset is available at:
  https://www.kaggle.com/datasets/ellipticco/elliptic-data-set

Download and place files as:
  data/raw/elliptic/elliptic_txs_features.csv
  data/raw/elliptic/elliptic_txs_classes.csv
  data/raw/elliptic/elliptic_txs_edgelist.csv

File layout (from Elliptic paper, Pareja et al. 2019):
  elliptic_txs_features.csv  — 203,769 rows × 167 columns (txId, time_step, f1..f165)
  elliptic_txs_classes.csv   — 203,769 rows × 2 columns (txId, class: 1=illicit, 2=licit, unknown)
  elliptic_txs_edgelist.csv  — edges (not used in M1b)

Temporal split convention (from Elliptic paper):
  Time steps 1–34 → train; steps 35–49 → test.
  This is the STANDARD split used in Pareja et al. 2019.
  Do NOT shuffle — temporal leakage is a serious validity concern.

License: CC BY 4.0 (for research use).
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

ELLIPTIC_DIR = PROJECT_ROOT / "data" / "raw" / "elliptic"
FEATURES_PATH = ELLIPTIC_DIR / "elliptic_txs_features.csv"
CLASSES_PATH = ELLIPTIC_DIR / "elliptic_txs_classes.csv"


def check_dataset() -> bool:
    missing = []
    for p in [FEATURES_PATH, CLASSES_PATH]:
        if not p.exists():
            missing.append(str(p))
    if missing:
        print("=" * 65)
        print("M1b BLOCKED — Elliptic dataset not found.")
        print("=" * 65)
        print("\nMissing files:")
        for m in missing:
            print(f"  {m}")
        print("""
TO OBTAIN THE DATASET:
  1. Go to https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
  2. Accept the CC BY 4.0 licence and click Download.
  3. Extract the ZIP to:
       data/raw/elliptic/
     so that these files exist:
       data/raw/elliptic/elliptic_txs_features.csv
       data/raw/elliptic/elliptic_txs_classes.csv
       data/raw/elliptic/elliptic_txs_edgelist.csv
  4. Re-run: backend/.venv/bin/python backend/ml/train/train_m1b.py

Alternatively, the dataset can be obtained via the Kaggle CLI:
  pip install kaggle
  kaggle datasets download ellipticco/elliptic-data-set -p data/raw/elliptic --unzip

No API key substitution will be made. Metrics in RESULTS.md will show
M1b=BLOCKED until the dataset is placed correctly.
""")
        return False
    return True


def train_m1b() -> dict:
    import warnings

    import lightgbm as lgb
    import pandas as pd
    from sklearn.metrics import (
        average_precision_score,
        classification_report,
        f1_score,
        precision_recall_curve,
    )

    from app.ml.registry import ModelRegistry

    warnings.filterwarnings("ignore", category=UserWarning)

    SEED = 42
    TRAIN_STEPS_MAX = 34  # Standard Elliptic temporal split

    print("Loading Elliptic dataset …")
    features_df = pd.read_csv(FEATURES_PATH, header=None)
    classes_df = pd.read_csv(CLASSES_PATH)

    # Column names: txId, time_step, f1..f165
    n_feats = features_df.shape[1] - 2
    feat_cols = [f"f{i}" for i in range(1, n_feats + 1)]
    features_df.columns = ["txId", "time_step"] + feat_cols
    classes_df.columns = ["txId", "class"]

    merged = features_df.merge(classes_df, on="txId")
    # Drop unknowns (class == "unknown")
    labeled = merged[merged["class"] != "unknown"].copy()
    labeled["label"] = (labeled["class"] == "1").astype(int)  # 1=illicit, 0=licit

    print(f"  Labeled: {len(labeled)} rows")
    print(f"  Illicit: {labeled['label'].sum()} | Licit: {(labeled['label']==0).sum()}")

    # Temporal split
    train_mask = labeled["time_step"].astype(int) <= TRAIN_STEPS_MAX
    test_mask = ~train_mask
    X_train = labeled.loc[train_mask, feat_cols]
    y_train = labeled.loc[train_mask, "label"]
    X_test = labeled.loc[test_mask, feat_cols]
    y_test = labeled.loc[test_mask, "label"]

    print(f"  Train steps 1-{TRAIN_STEPS_MAX}: {len(X_train)} | Test steps 35-49: {len(X_test)}")

    # Class weight
    pos_weight = float((y_train == 0).sum()) / max((y_train == 1).sum(), 1)

    params = {
        "objective": "binary",
        "metric": "binary_logloss",
        "n_estimators": 300,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "scale_pos_weight": pos_weight,
        "random_state": SEED,
        "n_jobs": -1,
        "verbose": -1,
    }
    model = lgb.LGBMClassifier(**params)
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    pr_auc = float(average_precision_score(y_test, y_prob))
    f1_ill = float(f1_score(y_test, y_pred, pos_label=1, zero_division=0))
    prec, rec, _ = precision_recall_curve(y_test, y_prob)

    report = classification_report(y_test, y_pred, target_names=["licit", "illicit"],
                                   zero_division=0, output_dict=True)

    metrics = {
        "dataset": "Elliptic Bitcoin Dataset (Pareja et al. 2019)",
        "split": f"temporal: train steps 1-{TRAIN_STEPS_MAX}, test steps 35-49",
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "illicit_pr_auc": round(pr_auc, 4),
        "illicit_f1": round(f1_ill, 4),
        "illicit_precision": round(float(report["illicit"]["precision"]), 4),
        "illicit_recall": round(float(report["illicit"]["recall"]), 4),
        "classification_report": report,
        "note": "Standard temporal split per Pareja et al. 2019 convention.",
    }

    print(f"\n  Illicit PR-AUC: {pr_auc:.4f}")
    print(f"  Illicit F1:     {f1_ill:.4f}")
    print(f"  Illicit Prec:   {report['illicit']['precision']:.4f}")
    print(f"  Illicit Recall: {report['illicit']['recall']:.4f}")

    registry = ModelRegistry()
    model_card = f"""# MODEL_CARD — M1b BTC Illicit Transaction Scorer

## Intended Use
Score Bitcoin transactions for illicit activity (1=illicit, 0=licit) to
supplement M1 role classification on the Bitcoin chain.
**Outputs are investigative leads, not proof of wrongdoing.**

## Training Data
Elliptic Bitcoin Dataset (Pareja et al. 2019, CC BY 4.0).
203,769 transactions, 49 time steps.
Labeled: {len(labeled)} (illicit: {labeled['label'].sum()}, licit: {(labeled['label']==0).sum()}).

## Split
Standard temporal: time steps 1–{TRAIN_STEPS_MAX} → train, 35–49 → test.
No shuffle (temporal leakage guard).

## Metrics (test set, steps 35–49)
- Illicit PR-AUC: {pr_auc:.4f}
- Illicit F1: {f1_ill:.4f}

## Failure Modes
- Coverage: Elliptic covers only transactions, not addresses.
- Temporal drift: illicit patterns evolve after dataset cutoff.
- Dataset skew: licit class dominates (~10:1 ratio).

## License
Model trained on CC BY 4.0 data. Attribution: Pareja et al. 2019.
"""
    saved = registry.save(
        model_id="m1b",
        version="v0.1",
        model=model,
        config={"model_id": "m1b", "params": params, "train_steps_max": TRAIN_STEPS_MAX},
        metrics=metrics,
        data_manifest={"elliptic_features": str(FEATURES_PATH), "elliptic_classes": str(CLASSES_PATH)},
        model_card=model_card,
        extra_files={"feature_names.json": feat_cols},
    )
    print(f"\n✓ M1b saved to: {saved}")
    return metrics


def main() -> None:
    print("=" * 65)
    print("ChainNetra M1b — BTC Illicit Transaction Scorer (Elliptic)")
    print("=" * 65)
    if not check_dataset():
        sys.exit(1)
    train_m1b()


if __name__ == "__main__":
    main()
