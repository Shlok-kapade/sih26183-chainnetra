from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    tx_hash: str
    chain: str
    from_address: str
    to_address: str
    asset: str
    amount: str
    timestamp: datetime
    evidence_type: str  # "hop", "deposit", "withdrawal"
    notes: Optional[str] = None

class LabelRecord(BaseModel):
    address: str
    chain: str
    label: str
    confidence: str
    source: str
    source_url: Optional[str] = None

class EvidenceManifest(BaseModel):
    case_id: str
    generated_at: datetime
    generator_version: str = "1.0.0"
    target_address: str
    target_chain: str

    # Core Evidence
    traces: List[EvidenceRecord] = Field(default_factory=list)
    labels: List[LabelRecord] = Field(default_factory=list)

    # Triage/Risk Output
    urgency_score: float = 0.0
    severity_level: str = "UNKNOWN"

    # Verification
    manifest_hash: Optional[str] = None

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)
