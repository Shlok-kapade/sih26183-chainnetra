#!/usr/bin/env python3
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

import lightgbm as lgb
import pandas as pd
import shap
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss, precision_score, recall_score, f1_score, roc_auc_score

PROJECT_ROOT = Path("/home/finex/Desktop/projects/uncompleted/chainnetra-sih26138")
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
from app.ml.registry import ModelRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    data_path = PROJECT_ROOT / "data/processed/elliptic_m1_real.parquet"
    if not data_path.exists():
        logger.error(f"Dataset not found at {data_path}.")
        sys.exit(1)
        
    df = pd.read_parquet(data_path)
    
    # Elliptic dataset uses 'timestep' (1 to 49) representing ~2 weeks each.
    # Temporal split: train on timesteps < 35, test on timesteps >= 35
    train_df = df[df["timestep"] < 35]
    test_df = df[df["timestep"] >= 35]
    
    features = [c for c in df.columns if c.startswith("feature_")]
    
    X_train, y_train = train_df[features], train_df["y"]
    X_test, y_test = test_df[features], test_df["y"]
    
    logger.info(f"Train size: {len(train_df)} (Illicit: {y_train.sum()})")
    logger.info(f"Test size: {len(test_df)} (Illicit: {y_test.sum()})")
    
    model = lgb.LGBMClassifier(
        n_estimators=100,
        learning_rate=0.05,
        class_weight="balanced",
        random_state=42,
        verbosity=-1
    )
    logger.info("Training LightGBM on Elliptic dataset...")
    model.fit(X_train, y_train)
    
    logger.info("Calibrating...")
    calibrator = IsotonicRegression(out_of_bounds="clip")
    probs_test = model.predict_proba(X_test)[:, 1]
    calibrator.fit(probs_test, y_test)
    
    cal_probs = calibrator.predict(probs_test)
    preds = (cal_probs > 0.5).astype(int)
    
    metrics = {
        "brier_score": brier_score_loss(y_test, cal_probs),
        "precision": precision_score(y_test, preds),
        "recall": recall_score(y_test, preds),
        "f1": f1_score(y_test, preds),
        "roc_auc": roc_auc_score(y_test, cal_probs),
        "train_size": len(train_df),
        "test_size": len(test_df),
    }
    
    logger.info(f"Metrics: {metrics}")
    
    # SHAP
    logger.info("Computing SHAP values on subset of test data...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test.head(1000))
    
    version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    registry = ModelRegistry()
    registry_path = registry.save(
        model_id="m1_elliptic_real",
        version=version,
        model=model,
        config={"features": features, "split": "temporal_timestep", "cutoff": 35},
        metrics=metrics,
        data_manifest={"dataset": "elliptic++", "note": "trained on real data"},
        model_card="# M1 Elliptic Real\nLightGBM model trained on Elliptic++.",
        extra_files={
            "calibrator.pkl": calibrator,
            "feature_names.json": features
        }
    )
    logger.info(f"Saved real M1 (Elliptic) to {registry_path}")

if __name__ == "__main__":
    main()
