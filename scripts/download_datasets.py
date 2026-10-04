#!/usr/bin/env python3
import os
import subprocess
import urllib.request
import zipfile
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"

def check_kaggle():
    try:
        subprocess.run(["kaggle", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def download_elliptic():
    dest_dir = DATA_DIR / "elliptic"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    if (dest_dir / "elliptic_txs_features.csv").exists():
        print("[Elliptic] Dataset already exists.")
        return

    print("[Elliptic] Attempting to download via Kaggle API...")
    if check_kaggle():
        try:
            subprocess.run([
                "kaggle", "datasets", "download", "-d", "ellipticco/elliptic-data-set", "-p", str(dest_dir)
            ], check=True)
            
            zip_path = dest_dir / "elliptic-data-set.zip"
            if zip_path.exists():
                print("[Elliptic] Extracting...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(dest_dir)
                zip_path.unlink()
                print("[Elliptic] Download complete.")
            return
        except subprocess.CalledProcessError as e:
            print(f"[Elliptic] Kaggle download failed: {e}")

    print("\n" + "="*80)
    print("ACTION REQUIRED: Elliptic Dataset")
    print("="*80)
    print("Kaggle API key missing or download failed.")
    print("Please manually download the dataset:")
    print("1. Go to: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set")
    print("2. Download the archive.")
    print("3. Extract the contents into:")
    print(f"   {dest_dir.absolute()}")
    print("Ensure the following files are present:")
    print("   - elliptic_txs_features.csv")
    print("   - elliptic_txs_classes.csv")
    print("   - elliptic_txs_edgelist.csv")
    print("="*80 + "\n")

def download_bitcoinheist():
    dest_dir = DATA_DIR / "bitcoinheist"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = dest_dir / "BitcoinHeistData.csv"
    if file_path.exists():
        print("[BitcoinHeist] Dataset already exists.")
        return

    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00526/BitcoinHeistData.csv"
    print(f"[BitcoinHeist] Downloading from {url}...")
    try:
        urllib.request.urlretrieve(url, file_path)
        print("[BitcoinHeist] Download complete.")
    except Exception as e:
        print(f"[BitcoinHeist] Download failed: {e}")
        print("\n" + "="*80)
        print("ACTION REQUIRED: BitcoinHeist Dataset")
        print("="*80)
        print("Please manually download the dataset:")
        print(f"1. Go to: {url}")
        print("2. Save the file as:")
        print(f"   {file_path.absolute()}")
        print("="*80 + "\n")

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Starting dataset downloads...")
    download_bitcoinheist()
    download_elliptic()
    
    print("\nDataset checking complete. See action required messages above if any.")

if __name__ == "__main__":
    main()
