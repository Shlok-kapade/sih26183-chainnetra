from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator

from .normalize import Transfer


class BaseAdapter(ABC):
    @abstractmethod
    async def fetch_transfers(
        self,
        address: str,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        asset: str | None = None,
        max_pages: int = 10
    ) -> AsyncIterator[Transfer]: ...

    @abstractmethod
    def validate_address(self, address: str) -> bool: ...
