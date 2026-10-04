"""
Fixture adapters for tests.
"""
from typing import Optional, AsyncIterator
from datetime import datetime, timedelta
from .ports import Label, ClusterRef, Entity

class FixtureTransferPort:
    def __init__(self):
        self.call_count = 0
        self.transfers = [] # list of Transfer objects
    async def outgoing(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        self.call_count += 1
        for t in self.transfers:
            if t.from_addr == address and t.chain == chain and t.asset == asset:
                if since and t.ts < since: continue
                if until and t.ts > until: continue
                yield t
    async def incoming(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        self.call_count += 1
        for t in self.transfers:
            if t.to_addr == address and t.chain == chain and t.asset == asset:
                if since and t.ts < since: continue
                if until and t.ts > until: continue
                yield t



class FixtureLabelPort:
    def lookup(self, chain: str, address: str) -> Optional[Label]:
        if address == "known":
            return Label(address, chain, "e1", "vasp", "src", "high")
        return None
    def cluster_of(self, chain: str, address: str) -> Optional[ClusterRef]: return None
    def entity_of(self, chain: str, address: str) -> Optional[Entity]: return None

class FixtureClockPort:
    def __init__(self):
        self._now = datetime(2025, 1, 1)
    def now(self) -> datetime:
        return self._now
    def advance(self, seconds: int):
        self._now += timedelta(seconds=seconds)
    def set_time(self, ts: datetime):
        self._now = ts

class FixtureBudgetPort:
    def __init__(self, limit: int):
        self.limit = limit
        self.used = 0
    def calls_used(self, case_id: str) -> int: return self.used
    def calls_left(self, case_id: str) -> int: return self.limit - self.used
    def charge(self, n: int) -> None: self.used += n

class FixtureNotifyPort:
    def __init__(self):
        self.events = []
    async def emit(self, case_id: str, event_type: str, payload: dict) -> None:
        self.events.append((case_id, event_type, payload))

class FixtureTracePort:
    def __init__(self, graph: dict = None):
        self._graph = graph or {'elements': []}
        self._expanded = []
    def get_case_graph(self, case_id: str) -> dict: return self._graph
    async def enqueue_expand(self, case_id: str, address: str, priority: float, budget: int) -> None:
        self._expanded.append(address)
    def seed_info(self, case_id: str) -> dict: return {}
    @property
    def expanded_addresses(self):
        return self._expanded
