import os

os.makedirs('backend/app/addon', exist_ok=True)
os.makedirs('backend/app/addon/db', exist_ok=True)
os.makedirs('backend/app/addon/api', exist_ok=True)
os.makedirs('backend/config/addon', exist_ok=True)
os.makedirs('backend/tests/addon', exist_ok=True)

with open('backend/app/addon/__init__.py', 'w') as f:
    pass

with open('backend/app/addon/db/__init__.py', 'w') as f:
    pass

with open('backend/app/addon/api/__init__.py', 'w') as f:
    pass

with open('backend/tests/addon/__init__.py', 'w') as f:
    pass

with open('backend/app/addon/ports.py', 'w') as f:
    f.write("""from typing import Protocol, AsyncIterator, Optional, runtime_checkable
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
""")

with open('backend/app/addon/adapters_existing.py', 'w') as f:
    f.write('''"""
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
''')

with open('backend/app/addon/adapters_fixture.py', 'w') as f:
    f.write('''"""
Fixture adapters for tests.
"""
from typing import Optional, AsyncIterator
from datetime import datetime, timedelta
from .ports import Label, ClusterRef, Entity

class FixtureTransferPort:
    def __init__(self):
        self.call_count = 0
    async def outgoing(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        self.call_count += 1
        yield {}
    async def incoming(self, chain: str, address: str, asset: str, since: Optional[datetime], until: Optional[datetime], max_pages: int) -> AsyncIterator:
        self.call_count += 1
        yield {}

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
    def get_case_graph(self, case_id: str) -> dict: return {"nodes": [], "edges": []}
    async def enqueue_expand(self, case_id: str, address: str, priority: float, budget: int) -> None: pass
    def seed_info(self, case_id: str) -> dict: return {}
''')

with open('backend/config/addon/levers.yaml', 'w') as f:
    f.write('''levers:
  VASP_HOLD:
    binance: {p_success: 0.60, latency_hours: 4, hold_validity_days: 30}
    okx: {p_success: 0.50, latency_hours: 8, hold_validity_days: 30}
    default: {p_success: 0.40, latency_hours: 12, hold_validity_days: 14}
  ISSUER_BLACKLIST:
    usdt: {p_success: 0.80, latency_hours: 2}
    usdc: {p_success: 0.85, latency_hours: 1}
  LEGAL_ESCALATION:
    default: {p_success: 0.10, latency_hours: 720}
''')

with open('backend/config/addon/convergence.yaml', 'w') as f:
    f.write('''weights:
  coverage_value: 0.40
  coverage_breadth: 0.20
  time_compactness: 0.15
  conservation: 0.15
  collector_novelty: 0.10
tiers:
  CONVERGENCE_CONFIRMED: {min_score: 0.80, requires_verification: true}
  CONVERGENCE_PROBABLE: {min_score: 0.50}
  NONE: {min_score: 0.0}
''')

with open('backend/config/addon/fot.yaml', 'w') as f:
    f.write('''hazard:
  default_daily_rate: 0.30
budget:
  default_api_calls: 500
  max_pages_per_address: 5
planner:
  max_actions: 5
  act_now_threshold: 0.20
watch:
  poll_interval_seconds: 300
  high_hazard_interval_seconds: 60
''')

with open('backend/app/addon/db/models_addon.py', 'w') as f:
    f.write('''from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from app.db.base import Base

class AddonCohort(Base):
    __tablename__ = "addon_cohorts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    origin_addr: Mapped[str] = mapped_column(String(255))
    chain: Mapped[str] = mapped_column(String(50))
    asset: Mapped[str] = mapped_column(String(50))
    n_members: Mapped[int] = mapped_column(Integer)
    s_total: Mapped[float] = mapped_column(Float)
    amount_median: Mapped[float] = mapped_column(Float)
    amount_cv: Mapped[float] = mapped_column(Float)
    t_start: Mapped[datetime] = mapped_column(DateTime)
    t_end: Mapped[datetime] = mapped_column(DateTime)
    layer: Mapped[int] = mapped_column(Integer)
    truncated: Mapped[bool] = mapped_column(Boolean)
    kind: Mapped[str] = mapped_column(String(50))

class AddonCohortMember(Base):
    __tablename__ = "addon_cohort_members"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cohort_id: Mapped[int] = mapped_column(ForeignKey("addon_cohorts.id"))
    address: Mapped[str] = mapped_column(String(255), index=True)
    received_amount: Mapped[float] = mapped_column(Float)
    ts: Mapped[datetime] = mapped_column(DateTime)
    # Note: Alembic / manual indices on (cohort_id, address) will be generated.

class AddonCohortEdge(Base):
    __tablename__ = "addon_cohort_edges"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cohort_id: Mapped[int] = mapped_column(ForeignKey("addon_cohorts.id"))
    dst_ref: Mapped[str] = mapped_column(String(255))
    dst_kind: Mapped[str] = mapped_column(String(50))
    votes: Mapped[int] = mapped_column(Integer)
    value: Mapped[float] = mapped_column(Float)
    coverage_value: Mapped[float] = mapped_column(Float)
    coverage_breadth: Mapped[float] = mapped_column(Float)
    time_compactness: Mapped[float] = mapped_column(Float)
    conservation_error: Mapped[float] = mapped_column(Float)
    score: Mapped[float] = mapped_column(Float)
    tier: Mapped[str] = mapped_column(String(50))
    verified: Mapped[bool] = mapped_column(Boolean)

class AddonMassSnapshot(Base):
    __tablename__ = "addon_mass_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    t: Mapped[datetime] = mapped_column(DateTime)
    position_ref: Mapped[str] = mapped_column(String(255))
    kind: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50))
    value_est: Mapped[float] = mapped_column(Float)
    value_lo: Mapped[float] = mapped_column(Float)
    value_hi: Mapped[float] = mapped_column(Float)

class AddonPlan(Base):
    __tablename__ = "addon_plans"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    t: Mapped[datetime] = mapped_column(DateTime)
    ev_total: Mapped[float] = mapped_column(Float)
    ev_lo: Mapped[float] = mapped_column(Float)
    ev_hi: Mapped[float] = mapped_column(Float)
    params_hash: Mapped[str] = mapped_column(String(255))
    illustrative_priors: Mapped[bool] = mapped_column(Boolean)

class AddonPlanAction(Base):
    __tablename__ = "addon_plan_actions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("addon_plans.id"))
    rank: Mapped[int] = mapped_column(Integer)
    lever: Mapped[str] = mapped_column(String(100))
    target_ref: Mapped[str] = mapped_column(String(255))
    expected_secured: Mapped[float] = mapped_column(Float)
    lo: Mapped[float] = mapped_column(Float)
    hi: Mapped[float] = mapped_column(Float)
    deadline: Mapped[datetime] = mapped_column(DateTime)
    eta_hours: Mapped[float] = mapped_column(Float)
    prereqs_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    doc_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

class AddonWatch(Base):
    __tablename__ = "addon_watches"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    position_ref: Mapped[str] = mapped_column(String(255))
    hazard: Mapped[float] = mapped_column(Float)
    next_check: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50))

class AddonActionOutcome(Base):
    __tablename__ = "addon_action_outcomes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_action_id: Mapped[int] = mapped_column(ForeignKey("addon_plan_actions.id"))
    outcome: Mapped[str] = mapped_column(String(50))
    ts: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
''')

with open('backend/app/addon/api/routes_addon.py', 'w') as f:
    f.write('''from fastapi import APIRouter

router = APIRouter(prefix="/addon", tags=["addon"])

@router.get("/health")
def addon_health():
    return {"status": "ok", "features": ["cohorts", "fot"]}
''')

with open('backend/tests/addon/test_ports.py', 'w') as f:
    f.write('''import pytest
from app.addon.adapters_fixture import FixtureTransferPort, FixtureLabelPort, FixtureBudgetPort, FixtureNotifyPort, FixtureClockPort, FixtureTracePort

@pytest.mark.asyncio
async def test_fixture_transfer_port_counts_calls():
    port = FixtureTransferPort()
    async for _ in port.outgoing("chain", "addr", "asset", None, None, 1): pass
    async for _ in port.incoming("chain", "addr", "asset", None, None, 1): pass
    assert port.call_count == 2

def test_fixture_label_port_hit_and_miss():
    port = FixtureLabelPort()
    assert port.lookup("chain", "known") is not None
    assert port.lookup("chain", "unknown") is None

def test_fixture_budget_port_limits():
    port = FixtureBudgetPort(100)
    port.charge(10)
    assert port.calls_left("case") == 90
    assert port.calls_used("case") == 10

@pytest.mark.asyncio
async def test_fixture_notify_collects_events():
    port = FixtureNotifyPort()
    await port.emit("case1", "test_event", {"a": 1})
    assert len(port.events) == 1

def test_fixture_clock_advance():
    port = FixtureClockPort()
    t1 = port.now()
    port.advance(10)
    t2 = port.now()
    assert (t2 - t1).total_seconds() == 10

def test_fixture_trace_port_returns_graph():
    port = FixtureTracePort()
    assert isinstance(port.get_case_graph("case1"), dict)
''')
