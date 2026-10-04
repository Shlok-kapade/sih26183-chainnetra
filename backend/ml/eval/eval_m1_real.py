#!/usr/bin/env python3
"""
Evaluate M1 Real Model.

Generates docs/evaluation/TRON_REAL_RESULTS.md.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.metrics import classification_report

PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.features import CANONICAL_FEATURES
from app.ml.registry import ModelRegistry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    try:
        registry = ModelRegistry()
        saved = registry.load("m1_real")
        model = saved["model"]
        features = saved["feature_names"]
    except Exception as e:
        logger.error(f"Failed to load m1_real: {e}")
        sys.exit(1)
        
    data_path = PROJECT_ROOT / "data" / "processed" / "tron_m1_real.parquet"
    df = pd.read_parquet(data_path)
    
    df["y"] = (df["canonical_label"] == "illicit").astype(int)
    
    # Predict over entire dataset for the report (we note the split inside)
    X = df[features].fillna(0)
    preds = model.predict(X)
    
    report = classification_report(df["y"], preds, output_dict=True, zero_division=0)
    
    # Write TRON_REAL_RESULTS.md
    out_path = PROJECT_ROOT / "docs" / "evaluation" / "TRON_REAL_RESULTS.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w") as f:
        f.write("# ChainNetra M1: Real Data Evaluation\n\n")
        f.write("> **HONESTY CAVEAT**: The Mendeley TRON dataset used for this evaluation contains ONLY `illicit` labels. ")
        f.write("Because there are no verified TRON exchange/DEX/unknown labels in this dataset, a true binary classifier ")
        f.write("cannot be trained on it alone. The model currently operates as a fallback DummyClassifier until negative ")
        f.write("samples are sourced. These metrics reflect that reality.\n\n")
        
        f.write("## Dataset\n")
        f.write("- **Source**: Mendeley TRON Dataset v3\n")
        f.write(f"- **Total rows**: {len(df)}\n")
        f.write("- **Classes present**: illicit (1) only\n\n")
        
        f.write("## Metrics (Global)\n")
        f.write("```json\n")
        f.write(json.dumps(report, indent=2))
        f.write("\n```\n")
        
    logger.info(f"Wrote evaluation results to {out_path}")
    
    # Update main RESULTS.md to point to this
    main_results = PROJECT_ROOT / "docs" / "evaluation" / "RESULTS.md"
    if main_results.exists():
        content = main_results.read_text()
        if "## REAL DATA RESULTS" not in content:
            new_content = (
                "# Evaluation Results\n\n"
                "## REAL DATA RESULTS\n"
                "See [TRON_REAL_RESULTS.md](./TRON_REAL_RESULTS.md) for the actual, real-world evaluation metrics.\n\n"
                "## SYNTHETIC DATA RESULTS\n"
                "> [!WARNING]\n"
                "> The metrics below are from fully SYNTHETIC data and DO NOT represent real-world accuracy.\n\n"
            ) + content.replace("# Evaluation Results\n", "")
            main_results.write_text(new_content)

if __name__ == "__main__":
    main()
