from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class GraphNode(BaseModel):
    chain: str
    address: str
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    is_contract: bool = False
    labels: list[str] = []
    role_probs: dict[str, float] = {}
    cluster_id: str | None = None
    taint_share: Decimal = Decimal("0")

class GraphEdge(BaseModel):
    src: str
    dst: str
    asset: str
    total_amount: Decimal
    tx_count: int
    first_ts: datetime
    last_ts: datetime
    taint_share: Decimal = Decimal("0")
    tx_refs: list[str] = []
    kind: str = "transfer"

class Attribution(BaseModel):
    address: str
    tier: Literal["CONFIRMED", "PROBABLE", "POSSIBLE", "UNATTRIBUTED"]
    entity: str | None = None
    entity_type: str | None = None
    confidence: float
    evidence: list[dict] = []
    source: str | None = None

class ExitReport(BaseModel):
    exit_type: Literal["VASP", "P2P_OTC_SUSPECTED", "PRIVATE_WALLET", "MIXER",
                       "BRIDGE", "DEX_SWAP", "SANCTIONED", "UNKNOWN"]
    entity: str | None = None
    tier: Literal["CONFIRMED", "PROBABLE", "POSSIBLE", "UNATTRIBUTED"]
    confidence: float
    path: list[str] = []
    amount_at_risk: Decimal
    eta_hours: float | None = None
    termination_reason: str = ""
    evidence: list[dict] = []
