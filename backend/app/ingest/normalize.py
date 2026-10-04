from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class Transfer(BaseModel):
    chain: str
    tx_hash: str
    log_index: int | None = None
    ts: datetime
    from_addr: str
    to_addr: str
    asset: str
    amount: Decimal
    kind: Literal["native", "token", "internal"]
    block: int
    raw_ref: str = ''
