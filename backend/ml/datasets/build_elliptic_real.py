#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

def build():
    root = Path("/home/finex/Desktop/projects/uncompleted/chainnetra-sih26138")
    raw_dir = root / "data/raw/elliptic"
    out_dir = root / "data/processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading classes...")
    df_classes = pd.read_csv(raw_dir / "elliptic_txs_classes.csv")
    
    print("Loading features...")
    # Features has no header. Col 0 is txId, Col 1 is timestep, Col 2-167 are features.
    df_features = pd.read_csv(raw_dir / "elliptic_txs_features.csv", header=None)
    
    # Rename first two columns
    cols = list(df_features.columns)
    cols[0] = 'txId'
    cols[1] = 'timestep'
    for i in range(2, 167):
        cols[i] = f'feature_{i}'
    df_features.columns = cols
    
    print("Merging...")
    df = df_features.merge(df_classes, on='txId')
    
    # Map classes: '1' is illicit, '2' is licit, 'unknown'
    # We only train on known labels.
    df_known = df[df['class'] != 'unknown'].copy()
    df_known['y'] = (df_known['class'] == '1').astype(int)
    
    out_path = out_dir / "elliptic_m1_real.parquet"
    print(f"Saving to {out_path}...")
    df_known.to_parquet(out_path)
    print("Done!")

if __name__ == "__main__":
    build()
