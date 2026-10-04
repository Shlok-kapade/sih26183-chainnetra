from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.ingest.normalize import Transfer


def make_linear_chain(n_hops: int, amount: Decimal):
    transfers = []
    base_ts = datetime.now(timezone.utc)
    for i in range(n_hops):
        transfers.append(Transfer(
            chain="ETH",
            tx_hash=f"tx_{i}",
            ts=base_ts + timedelta(minutes=i),
            from_addr=f"addr_{i}",
            to_addr=f"addr_{i+1}",
            asset="ETH",
            amount=amount,
            kind="native",
            block=1000 + i
        ))
    return transfers

def make_fan_out(n_branches: int, amount: Decimal):
    transfers = []
    base_ts = datetime.now(timezone.utc)
    split_amount = amount / Decimal(n_branches)
    for i in range(n_branches):
        transfers.append(Transfer(
            chain="ETH",
            tx_hash=f"tx_{i}",
            ts=base_ts,
            from_addr="addr_0",
            to_addr=f"addr_{i+1}",
            asset="ETH",
            amount=split_amount,
            kind="native",
            block=1000
        ))
    return transfers

def make_fan_in(n_sources: int, amount: Decimal):
    transfers = []
    base_ts = datetime.now(timezone.utc)
    split_amount = amount / Decimal(n_sources)
    for i in range(n_sources):
        transfers.append(Transfer(
            chain="ETH",
            tx_hash=f"tx_{i}",
            ts=base_ts,
            from_addr=f"addr_{i+1}",
            to_addr="addr_0",
            asset="ETH",
            amount=split_amount,
            kind="native",
            block=1000
        ))
    return transfers

def make_peel_chain(n_hops: int, peel_pct: Decimal):
    transfers = []
    base_ts = datetime.now(timezone.utc)
    current_amount = Decimal("100")
    for i in range(n_hops):
        peel_amount = current_amount * peel_pct
        keep_amount = current_amount - peel_amount
        transfers.append(Transfer(
            chain="ETH",
            tx_hash=f"tx_{i}_a",
            ts=base_ts + timedelta(minutes=i),
            from_addr=f"addr_{i}",
            to_addr=f"peel_{i+1}",
            asset="ETH",
            amount=peel_amount,
            kind="native",
            block=1000 + i
        ))
        transfers.append(Transfer(
            chain="ETH",
            tx_hash=f"tx_{i}_b",
            ts=base_ts + timedelta(minutes=i),
            from_addr=f"addr_{i}",
            to_addr=f"addr_{i+1}",
            asset="ETH",
            amount=keep_amount,
            kind="native",
            block=1000 + i
        ))
        current_amount = keep_amount
    return transfers

def make_layering(depth: int, width: int):
    # Just an example wrapper combining fan_out and fan_in concepts
    # In practice, would build a specific diamond/layering structure
    pass
