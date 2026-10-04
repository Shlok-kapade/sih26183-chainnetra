#!/usr/bin/env python3
"""
Instructions for fetching BitcoinHeist dataset.
"""
from pathlib import Path

def main():
    dest = Path(__file__).parents[1] / "data" / "raw" / "dataset-raw" / "BitcoinHeist"
    dest.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("BITCOINHEIST DATASET DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print(f"Destination: {dest}")
    print("1. Go to: https://archive.ics.uci.edu/dataset/514/bitcoinheistransomwareaddressdataset")
    print("2. Click Download or use the UCI Python API.")
    print("3. Place BitcoinHeistData.csv in the destination folder.")
    print("="*60)

if __name__ == "__main__":
    main()
