#!/usr/bin/env python3
"""
Instructions for fetching Elliptic Data Set.
"""
import os
from pathlib import Path

def main():
    dest = Path(__file__).parents[1] / "data" / "raw" / "dataset-raw" / "Elliptic"
    dest.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("ELLIPTIC DATASET DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print(f"Destination: {dest}")
    print("The Elliptic dataset requires a Kaggle account to download.")
    print("1. Go to: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set")
    print("2. Download the archive.zip")
    print("3. Extract it into the destination folder so that the following files exist:")
    print("   - elliptic_txs_classes.csv")
    print("   - elliptic_txs_edgelist.csv")
    print("   - elliptic_txs_features.csv")
    print("="*60)

if __name__ == "__main__":
    main()
