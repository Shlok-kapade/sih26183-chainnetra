#!/usr/bin/env python3
"""
Instructions for fetching Forta EVM dataset.
"""
from pathlib import Path

def main():
    dest = Path(__file__).parents[1] / "data" / "raw" / "dataset-raw" / "Forta"
    dest.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("FORTA EVM DATASET DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print(f"Destination: {dest}")
    print("1. Go to Forta Network's public labels repository or API.")
    print("2. Download the labeled dataset.")
    print("3. Place the CSV file in the destination folder.")
    print("="*60)

if __name__ == "__main__":
    main()
