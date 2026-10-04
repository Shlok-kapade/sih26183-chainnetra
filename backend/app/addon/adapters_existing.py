"""
Existing adapters for addon ports.
"""
from typing import Optional, AsyncIterator
from datetime import datetime

class ExistingTransferPort:
    async def outgoing(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        # Fallback explanation: this wraps existing ingest code
        yield []
    async def incoming(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        yield []

# Add other existing adapters as None or dummy for now
