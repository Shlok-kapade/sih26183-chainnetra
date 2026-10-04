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
from .validators import validate_btc_address


class BTCAdapter(BaseAdapter):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cache = ResponseCache(session)
        self.limiter = get_limiter("mempool", rate=2.0, capacity=5)
        self.client = httpx.AsyncClient(timeout=30.0)

    def validate_address(self, address: str) -> bool:
        return validate_btc_address(address)

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
            raise ValueError("Invalid BTC address")

        fixture_id = "mempool_txs"
        url = f"https://mempool.space/api/address/{address}/txs"

        data = await self._fetch_with_retry(url, {}, fixture_id)
        if data and isinstance(data, list):
            for tx in data:
                status = tx.get("status", {})
                if not status.get("confirmed", False):
                    continue

                yield Transfer(
                    chain="bitcoin",
                    tx_hash=tx.get("txid", ""),
                    log_index=0,
                    ts=datetime.fromtimestamp(int(status.get("block_time", 0))),
                    from_addr="multiple",
                    to_addr=address,
                    asset="BTC",
                    amount=Decimal(0),
                    kind="native",
                    block=int(status.get("block_height", 0)),
                    raw_ref="mempool_raw"
                )

    async def _fetch_with_retry(self, url: str, params: Dict[str, str], fixture_id: str) -> Optional[Any]:
        if not settings.LIVE_MODE:
            return load_fixture("btc", fixture_id)

        cached = await self.cache.get_cached_response("mempool", url, params)
        if cached:
            import json
            return json.loads(cached)

        retryer = get_retry_policy()

        async def do_request():
            await self.limiter.acquire()
            response = await self.client.get(url, params=params)
            if response.status_code in (429, 403, 503):
                raise RateLimitError("Rate limited")
            response.raise_for_status()

            await self.cache.store_response(
                provider="mempool",
                url=url,
                params=params,
                status=response.status_code,
                body=response.text
            )
            return response.json()

        return await retryer(do_request)
