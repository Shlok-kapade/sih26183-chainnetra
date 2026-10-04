from typing import Protocol, AsyncIterator, Optional, runtime_checkable
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Label:
    address: str
    chain: str
    entity: str
    entity_type: str
    source: str
    confidence: str

@dataclass
class ClusterRef:
    cluster_id: str
    size: int
    entity: Optional[str]

@dataclass
class Entity:
    name: str
    entity_type: str

class TransferPort(Protocol):
    async def outgoing(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator: ...
    async def incoming(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator: ...

class LabelPort(Protocol):
    def lookup(self, chain: str, address: str) -> Optional[Label]: ...
    def cluster_of(self, chain: str, address: str) -> Optional[ClusterRef]: ...
    def entity_of(self, chain: str, address: str) -> Optional[Entity]: ...

class RolePort(Protocol):
    def role_probs(self, chain: str, address: str, as_of_ts: Optional[datetime]) -> Optional[dict]: ...

class TracePort(Protocol):
    def get_case_graph(self, case_id: str) -> dict: ...
    async def enqueue_expand(self, case_id: str, address: str, priority: float, budget: int) -> None: ...
    def seed_info(self, case_id: str) -> dict: ...

class ExitPolicyPort(Protocol):
    def p_exit(self, case_id: str, address: str) -> Optional[float]: ...

class ClockPort(Protocol):
    def now(self) -> datetime: ...

class BudgetPort(Protocol):
    def calls_used(self, case_id: str) -> int: ...
    def calls_left(self, case_id: str) -> int: ...
    def charge(self, n: int) -> None: ...

class NotifyPort(Protocol):
    async def emit(self, case_id: str, event_type: str, payload: dict) -> None: ...
