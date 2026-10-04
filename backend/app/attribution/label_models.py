from datetime import datetime
from typing import Literal

from pydantic import BaseModel

EntityType = Literal[
    'exchange_hot', 'exchange_deposit', 'exchange_cold',
    'mixer', 'bridge', 'dex', 'sanctioned', 'scam', 'phishing',
    'service', 'unknown'
]

class AddressLabel(BaseModel):
    address: str
    chain: str
    entity: str
    entity_type: EntityType
    source: str  # e.g. 'ofac_sdn', 'por_binance', 'community'
    source_url: str = ''
    retrieved_at: datetime | None = None
    license: str = ''
    label_confidence: Literal['strong', 'weak'] = 'strong'
