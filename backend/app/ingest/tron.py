from datetime import datetime
from decimal import Decimal
from typing import Any, AsyncIterator, Dict, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from .base import BaseAdapter
from .cache import ResponseCache
from .fixtures import load_fixture
from .normalize import Transfer
from .ratelimit import RateLimitError, get_limiter, get_retry_policy
from .validators import validate_tron_address


class TronAdapter(BaseAdapter):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cache = ResponseCache(session)
        self.limiter = get_limiter("trongrid", rate=3.0, capacity=10)
        self.client = httpx.AsyncClient(timeout=30.0)

    def validate_address(self, address: str) -> bool:
        return validate_tron_address(address)

    async def fetch_transfers(
        self,
        address: str,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        asset: str | None = None,
        max_pages: int = 10
    ) -> AsyncIterator[Transfer]:
        if not self.validate_address(address):
            raise ValueError("Invalid TRON address")

        fixture_id = "trongrid_txs"
        url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
        params = {"limit": "50"}

        headers = {}
        if settings.TRONGRID_API_KEY:
            headers["TRON-PRO-API-KEY"] = settings.TRONGRID_API_KEY

        data = await self._fetch_with_retry(url, params, headers, fixture_id)
        if data and "data" in data:
            for tx in data["data"]:
                yield Transfer(
                    chain="tron",
                    tx_hash=tx.get("transaction_id", ""),
                    log_index=0,
                    ts=datetime.fromtimestamp(int(tx.get("block_timestamp", 0))/1000),
                    from_addr=tx.get("from", ""),
                    to_addr=tx.get("to", ""),
                    asset=tx.get("token_info", {}).get("symbol", "USDT-TRC20"),
                    amount=Decimal(tx.get("value", 0)) / Decimal(10**int(tx.get("token_info", {}).get("decimals", 6))),
                    kind="token",
                    block=int(tx.get("block_timestamp", 0)),
                    raw_ref="trongrid_raw"
                )

    async def _fetch_with_retry(self, url: str, params: Dict[str, str], headers: Dict[str, str], fixture_id: str) -> Optional[Dict[str, Any]]:
        if not settings.LIVE_MODE:
            return load_fixture("tron", fixture_id)

        cached = await self.cache.get_cached_response("trongrid", url, params)
        if cached:
            import json
            return json.loads(cached)

        retryer = get_retry_policy()

        async def do_request():
            await self.limiter.acquire()
            response = await self.client.get(url, params=params, headers=headers)
            if response.status_code in (429, 403, 503):
                raise RateLimitError("Rate limited")
            response.raise_for_status()

            await self.cache.store_response(
                provider="trongrid",
                url=url,
                params=params,
                status=response.status_code,
                body=response.text
            )
            return response.json()

        return await retryer(do_request)
