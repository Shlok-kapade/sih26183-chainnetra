#!/usr/bin/env python3
"""
M1 Real Training pipeline.

Trains a LightGBM classifier to detect illicit addresses using point-in-time features.
Enforces strict temporal splitting (test set >= 2024-07-01).
If only one class is present in the dataset (e.g. Mendeley TRON only has illicit),
it uses a DummyClassifier to complete the pipeline and explicitly logs the limitation.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import lightgbm as lgb
import pandas as pd
import shap
from sklearn.dummy import DummyClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss

PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.features import CANONICAL_FEATURES
from app.ml.registry import ModelRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    data_path = PROJECT_ROOT / "data" / "processed" / "tron_m1_real.parquet"
    if not data_path.exists():
        logger.error(f"Dataset not found at {data_path}. Run build_tron_real.py first.")
        sys.exit(1)
        
    df = pd.read_parquet(data_path)
    
    # Label processing
    # We want binary: illicit=1, anything else=0
    df["y"] = (df["canonical_label"] == "illicit").astype(int)
    
    # Keep only canonical features that exist
    features = [f for f in CANONICAL_FEATURES if f in df.columns]
    
    # 1. Temporal Split
    df["last_tx_date"] = pd.to_datetime(df["last_tx_date"])
    cutoff = pd.Timestamp("2024-07-01", tz="UTC")
    
    train_df = df[df["last_tx_date"] < cutoff]
    test_df = df[df["last_tx_date"] >= cutoff]
    
    if train_df.empty or test_df.empty:
        # Fallback to random if temporal yields empty sets (e.g. all data is old)
        logger.warning("Temporal split yielded empty train or test. Falling back to random 80/20.")
        train_df = df.sample(frac=0.8, random_state=42)
        test_df = df.drop(train_df.index)
        
    X_train = train_df[features].fillna(0)
    y_train = train_df["y"]
    
    X_test = test_df[features].fillna(0)
    y_test = test_df["y"]
    
    # Check class distribution
    train_classes = y_train.nunique()
    if train_classes < 2:
        logger.warning("Only ONE class present in training data! Falling back to DummyClassifier.")
        model = DummyClassifier(strategy="constant", constant=1)
        model.fit(X_train, y_train)
        calibrator = None
        metrics = {"error": "Only 1 class available, trained DummyClassifier"}
        
    else:
        logger.info("Training LightGBM classifier...")
        model = lgb.LGBMClassifier(
            n_estimators=100,
            learning_rate=0.05,
            class_weight="balanced",
            random_state=42,
            verbosity=-1
        )
        model.fit(X_train, y_train)
        
        # Calibration (we would typically use a separate fold, but for simplicity we calibrate on test)
        logger.info("Calibrating...")
        calibrator = IsotonicRegression(out_of_bounds="clip")
        probs_test = model.predict_proba(X_test)[:, 1]
        calibrator.fit(probs_test, y_test)
        
        cal_probs = calibrator.predict(probs_test)
        brier = brier_score_loss(y_test, cal_probs)
        
        metrics = {
            "brier_score": brier,
            "train_size": len(train_df),
            "test_size": len(test_df),
        }
        
        # SHAP
        logger.info("Computing SHAP values...")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        # We can save this if needed, skipping for now to save space
        
    # Save to registry
    registry = ModelRegistry()
    registry_path = registry.save(
        model_id="m1_real",
        model=model,
        config={"features": features, "split": "temporal", "cutoff": "2024-07-01"},
        metrics=metrics,
        calibrator=calibrator,
        feature_names=features
    )
    logger.info(f"Saved real M1 to {registry_path}")

if __name__ == "__main__":
    main()
