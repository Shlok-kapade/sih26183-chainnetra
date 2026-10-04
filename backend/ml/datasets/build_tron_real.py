#!/usr/bin/env python3
"""
Build the point-in-time feature dataset for M1 real training.

Reads Mendeley LabelRecords, loads cached TRON transfers, applies temporal cutoff,
computes features, runs leakage tests, and outputs a Parquet dataset and manifest.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ingest.normalize import Transfer
from app.ml.features import compute_features
from app.ml.provenance import write_provenance_csv
from ml.datasets.mendeley_tron import load_all_mendeley_tron
from ml.datasets.tronscan_fetcher import _load_cache, normalize_trongrid_tx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Loading Mendeley TRON addresses...")
    records, group_ids = load_all_mendeley_tron(dedup=True)
    
    # Optional: we can filter to only CONFIRMED tier if we had multiple tiers
    
    dataset_rows = []
    
    for rec in tqdm(records, desc="Building features"):
        addr = rec.address
        cached = _load_cache(addr)
        if not cached:
            continue
            
        raw_txs = cached.get("txs", [])
        
        # 1. Normalize transfers
        transfers: list[Transfer] = []
        for rtx in raw_txs:
            norm = normalize_trongrid_tx(rtx, addr)
            if norm:
                try:
                    transfers.append(Transfer(**norm))
                except Exception as e:
                    pass
                    
        if not transfers:
            continue
            
        # 2. Point-in-time cutoff
        # We must NOT use any transfer after valid_to.
        # If valid_to is None, we use the max timestamp in the data (but warn).
        if rec.valid_to:
            cutoff_dt = datetime.combine(rec.valid_to, datetime.max.time(), tzinfo=timezone.utc)
        else:
            cutoff_dt = datetime.now(timezone.utc) # fallback
            
        filtered_transfers = [t for t in transfers if t.ts <= cutoff_dt]
        
        # Guard: Check leakage
        if any(t.ts > cutoff_dt for t in filtered_transfers):
            raise ValueError(f"LEAKAGE DETECTED: {addr} has transfers after valid_to")
            
        if not filtered_transfers:
            continue
            
        # 3. Compute features
        feats = compute_features(addr, filtered_transfers, window_end=cutoff_dt)
        
        # 4. Append row
        row = {
            "address": addr,
            "address_release_id": rec.address_release_id,
            "original_label": rec.original_label,
            "canonical_label": rec.canonical_label,
            "label_tier": rec.label_tier,
            "source": rec.source,
            "dataset_identity": rec.dataset_identity,
            "validation_group_id": group_ids.get(addr, ""),
            "first_tx_date": rec.valid_from.isoformat() if rec.valid_from else None,
            "last_tx_date": rec.valid_to.isoformat() if rec.valid_to else None,
            "n_transfers_used": len(filtered_transfers),
        }
        row.update(feats)
        dataset_rows.append(row)
        
    df = pd.DataFrame(dataset_rows)
    logger.info(f"Built dataset with {len(df)} rows.")
    
    # Run Leakage Checks before saving
    _run_leakage_checks(df)
    
    out_dir = PROJECT_ROOT / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    parquet_path = out_dir / "tron_m1_real.parquet"
    df.to_parquet(parquet_path, index=False)
    
    # Save provenance
    prov_path = out_dir.parent / "labels" / "provenance_tron_real.csv"
    write_provenance_csv(records, prov_path)
    
    # Save manifest
    manifest = {
        "dataset_identity": "REAL",
        "source": "Mendeley TRON v3",
        "row_count": len(df),
        "address_count": df["address"].nunique(),
        "class_distribution": df["canonical_label"].value_counts().to_dict(),
        "feature_count": len([c for c in df.columns if c not in ["address", "address_release_id", "original_label", "canonical_label", "label_tier", "source", "dataset_identity", "validation_group_id", "first_tx_date", "last_tx_date", "n_transfers_used"]]),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    with open(out_dir / "tron_m1_real_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    logger.info(f"Saved dataset to {parquet_path}")

def _run_leakage_checks(df: pd.DataFrame):
    logger.info("Running leakage checks...")
    # 1. No synthetic rows
    if (df["dataset_identity"] != "REAL").any():
        raise ValueError("LEAKAGE: Synthetic rows found in real dataset.")
    # 2. No duplicate addresses
    if df["address"].duplicated().any():
        raise ValueError("LEAKAGE: Duplicate addresses found.")
    logger.info("Leakage checks passed.")

if __name__ == "__main__":
    main()
