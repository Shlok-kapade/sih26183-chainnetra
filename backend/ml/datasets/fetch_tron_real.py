#!/usr/bin/env python3
"""
CLI driver to fetch TRON TRC20 transfers for Mendeley addresses.

Reads usable TRON addresses from the Mendeley dataset adapter,
fetches their historical transfers via the TRONSCAN/TronGrid adapter,
and saves the raw responses to data/cache/tronscan/.

Writes a fetch manifest to data/cache/tronscan/fetch_manifest.csv.
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

# Add backend to path so we can import app
PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.provenance import FetchRecord, write_fetch_manifest_csv
from ml.datasets.mendeley_tron import load_all_mendeley_tron
from ml.datasets.tronscan_fetcher import fetch_trc20_transfers_cached, _save_cache, _load_cache

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Loading Mendeley TRON addresses...")
    records, _ = load_all_mendeley_tron(dedup=True)
    logger.info(f"Loaded {len(records)} unique TRON addresses.")

    manifest: list[FetchRecord] = []
    manifest_path = PROJECT_ROOT / "data" / "cache" / "tronscan" / "fetch_manifest.csv"

    # Only fetch if we need to (or if we want to refresh)
    # We will limit max_pages=10 (2000 txs) to avoid taking forever on massive addresses
    # during this pipeline build.
    for rec in tqdm(records, desc="Fetching TRONSCAN history"):
        address = rec.address
        # valid_to is date, we need datetime
        until_ts = None
        if rec.valid_to:
            until_ts = datetime.combine(rec.valid_to, datetime.max.time(), tzinfo=timezone.utc)

        # Check cache first to avoid hitting API unnecessarily during retries
        cached = _load_cache(address)
        if cached:
            txs = cached.get("txs", [])
            pages = cached.get("pages", 0)
            manifest.append(FetchRecord(
                address=address,
                api_source="tronscan_cache",
                status="CACHED",
                n_transfers=len(txs),
                n_pages=pages,
                fetched_at=datetime.fromisoformat(cached.get("fetched_at", datetime.now(timezone.utc).isoformat())),
                cache_hit=True
            ))
            continue

        try:
            txs, status, cache_hit = fetch_trc20_transfers_cached(
                address,
                until_ts=None,  # We fetch all, and filter during build
                max_pages=10    # Limit pages for reasonable time
            )
            
            manifest.append(FetchRecord(
                address=address,
                api_source="tronscan_trongrid",
                status=status,
                n_transfers=len(txs),
                n_pages=len(txs) // 200 + 1,
                fetched_at=datetime.now(timezone.utc),
                cache_hit=cache_hit
            ))
        except Exception as e:
            logger.error(f"Failed to fetch {address}: {e}")
            manifest.append(FetchRecord(
                address=address,
                api_source="tronscan_trongrid",
                status="API_FAILURE",
                error_msg=str(e),
                fetched_at=datetime.now(timezone.utc)
            ))

    write_fetch_manifest_csv(manifest, manifest_path)
    logger.info(f"Wrote fetch manifest to {manifest_path}")

    successes = sum(1 for m in manifest if m.status in ("OK", "CACHED", "NO_TRANSFERS"))
    logger.info(f"Fetch complete. Success: {successes}/{len(manifest)}")

if __name__ == "__main__":
    main()
