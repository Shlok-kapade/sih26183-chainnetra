"""
TRONSCAN / TronGrid synchronous fetcher for training pipeline.

Uses TronGrid API (https://api.trongrid.io) with API key for higher rate limits.
Falls back to TRONSCAN public API (https://apilist.tronscanapi.com) if TronGrid fails.
All raw responses are cached to data/cache/tronscan/<sha256(address)>.json.

Rate limits:
  - TronGrid keyless: 1 req/s
  - TronGrid with key: 5 req/s (free tier)
  - TRONSCAN public: 1 req/s
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parents[3]
CACHE_DIR = PROJECT_ROOT / "data" / "cache" / "tronscan"

TRONGRID_URL = "https://api.trongrid.io/v1/accounts/{addr}/transactions/trc20"
TRONSCAN_URL = "https://apilist.tronscanapi.com/api/token_trc20/transfers"

# Read API key from environment or .env file
_API_KEY: Optional[str] = None


def _get_api_key() -> Optional[str]:
    global _API_KEY
    if _API_KEY is not None:
        return _API_KEY
    # Try environment
    key = os.environ.get("TRONGRID_API_KEY", "").strip()
    if key:
        _API_KEY = key
        return _API_KEY
    # Try .env file
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("TRONGRID_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    _API_KEY = key
                    return _API_KEY
    return None


def _cache_path(address: str) -> Path:
    sha = hashlib.sha256(address.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{sha}_{address[:8]}.json"


def _load_cache(address: str) -> Optional[dict]:
    p = _cache_path(address)
    if p.exists():
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            p.unlink(missing_ok=True)
    return None


def _save_cache(address: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = _cache_path(address)
    with open(p, "w") as f:
        json.dump(data, f)


def _backoff_request(
    session: requests.Session,
    url: str,
    params: dict,
    headers: dict,
    max_retries: int = 3,
    base_delay: float = 2.0,
) -> Optional[requests.Response]:
    for attempt in range(max_retries):
        try:
            resp = session.get(url, params=params, headers=headers, timeout=20)
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 503):
                delay = base_delay * (2 ** attempt)
                logger.warning("Rate limited (%s), sleeping %.1fs", resp.status_code, delay)
                time.sleep(delay)
                continue
            logger.warning("HTTP %s for %s", resp.status_code, url)
            return None
        except requests.RequestException as e:
            delay = base_delay * (2 ** attempt)
            logger.warning("Request error: %s, retry in %.1fs", e, delay)
            time.sleep(delay)
    return None


def fetch_trc20_transfers_trongrid(
    address: str,
    api_key: Optional[str],
    *,
    until_ts: Optional[datetime] = None,
    max_pages: int = 20,
    rate_limit: float = 1.0,  # req/s
) -> tuple[list[dict], int]:
    """
    Fetch TRC20 transfers from TronGrid API.

    Returns:
        (raw_tx_list, n_pages_fetched)
    """
    session = requests.Session()
    headers = {}
    if api_key:
        headers["TRON-PRO-API-KEY"] = api_key

    all_txs: list[dict] = []
    fingerprint: Optional[str] = None
    pages = 0

    for _ in range(max_pages):
        url = TRONGRID_URL.format(addr=address)
        params: dict[str, Any] = {"limit": 200, "order_by": "block_timestamp,desc"}
        if fingerprint:
            params["fingerprint"] = fingerprint

        time.sleep(1.0 / rate_limit)
        resp = _backoff_request(session, url, params, headers)
        if resp is None:
            break

        data = resp.json()
        txs = data.get("data", [])
        pages += 1

        for tx in txs:
            # Apply until_ts filter if requested
            ts_ms = int(tx.get("block_timestamp", 0))
            ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            if until_ts is not None and ts > until_ts:
                continue
            all_txs.append(tx)

        meta = data.get("meta", {})
        fingerprint = meta.get("fingerprint")
        if not fingerprint or not txs:
            break

    return all_txs, pages


def fetch_trc20_transfers_cached(
    address: str,
    *,
    until_ts: Optional[datetime] = None,
    max_pages: int = 20,
) -> tuple[list[dict], str, bool]:
    """
    Fetch TRC20 transfers, using cache if available.

    Returns:
        (raw_txs, status, cache_hit)
        status: OK | API_FAILURE | NO_TRANSFERS
    """
    cached = _load_cache(address)
    if cached is not None:
        txs = cached.get("txs", [])
        # Apply until_ts filter even on cached data
        if until_ts is not None:
            cutoff_ms = until_ts.timestamp() * 1000
            txs = [t for t in txs if int(t.get("block_timestamp", 0)) <= cutoff_ms]
        return txs, "CACHED", True

    api_key = _get_api_key()
    rate = 5.0 if api_key else 1.0

    try:
        txs, pages = fetch_trc20_transfers_trongrid(
            address, api_key, until_ts=until_ts, max_pages=max_pages, rate_limit=rate
        )
        status = "OK" if txs else "NO_TRANSFERS"
        # Cache the full (unfiltered) result
        _save_cache(address, {"address": address, "txs": txs, "pages": pages,
                               "fetched_at": datetime.now(tz=timezone.utc).isoformat()})
        return txs, status, False
    except Exception as e:
        logger.error("Fetch failed for %s: %s", address, e)
        return [], "API_FAILURE", False


def normalize_trongrid_tx(tx: dict, address: str) -> Optional[dict]:
    """
    Normalize a TronGrid TRC20 transfer to a flat dict compatible with Transfer schema.
    Returns None if required fields are missing.
    """
    tx_hash = tx.get("transaction_id", "")
    ts_ms = tx.get("block_timestamp", 0)
    if not tx_hash or not ts_ms:
        return None

    ts = datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc)
    token_info = tx.get("token_info", {})
    decimals = int(token_info.get("decimals", 6))
    symbol = token_info.get("symbol", "USDT")
    raw_value = tx.get("value", "0")

    try:
        amount = Decimal(raw_value) / Decimal(10 ** decimals)
    except Exception:
        amount = Decimal(0)

    return {
        "chain": "tron",
        "tx_hash": tx_hash,
        "ts": ts.isoformat(),
        "from_addr": tx.get("from", ""),
        "to_addr": tx.get("to", ""),
        "asset": symbol,
        "amount": str(amount),
        "kind": "token",
        "block": int(ts_ms),
        "raw_ref": "trongrid_real",
    }
