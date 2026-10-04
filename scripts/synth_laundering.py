import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.ingest.normalize import Transfer


def _make_transfer(tx_hash, ts, frm, to, amt):
    return Transfer(
        chain="SYNTHETIC",
        tx_hash=tx_hash,
        ts=ts,
        from_addr=frm,
        to_addr=to,
        asset="USDT",
        amount=Decimal(str(amt)),
        kind="token",
        block=1000
    )

def generate_layering(seed: int = 42, n_layers: int = 3, width: int = 4) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)

    for i in range(width):
        transfers.append(_make_transfer(f"layering_{seed}_L0_{i}", base_ts, f"seed_{seed}", f"L1_{seed}_{i}", 100))

    for l in range(1, n_layers):
        for i in range(width):
            transfers.append(_make_transfer(f"layering_{seed}_L{l}_{i}", base_ts + timedelta(minutes=l*10), f"L{l}_{seed}_{i}", f"L{l+1}_{seed}_{i}", 100))

    for i in range(width):
        transfers.append(_make_transfer(f"layering_{seed}_collect_{i}", base_ts + timedelta(minutes=n_layers*10), f"L{n_layers}_{seed}_{i}", f"collection_{seed}", 100))

    return transfers

def generate_peel_chain(seed: int = 42, n_hops: int = 5) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)
    current_amount = Decimal(1000)
    curr_addr = f"origin_{seed}"

    for i in range(n_hops):
        peel = current_amount * Decimal("0.1")
        rem = current_amount - peel
        next_addr = f"hop_{seed}_{i+1}"
        peel_addr = f"peel_{seed}_{i}"

        transfers.append(_make_transfer(f"peel_rem_{seed}_{i}", base_ts + timedelta(minutes=i*10), curr_addr, next_addr, rem))
        transfers.append(_make_transfer(f"peel_out_{seed}_{i}", base_ts + timedelta(minutes=i*10), curr_addr, peel_addr, peel))

        curr_addr = next_addr
        current_amount = rem

    return transfers

def generate_rapid_forwarding(seed: int = 42, n_hops: int = 5) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)

    for i in range(n_hops):
        transfers.append(_make_transfer(f"rapid_{seed}_{i}", base_ts + timedelta(minutes=i*2), f"hop_{seed}_{i}", f"hop_{seed}_{i+1}", 100))

    return transfers

def generate_dormancy_burst(seed: int = 42) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)
    addr = f"dormant_{seed}"

    transfers.append(_make_transfer(f"dormant_in_{seed}", base_ts, f"sender_{seed}", addr, 1000))

    burst_ts = base_ts + timedelta(days=40)
    for i in range(5):
        transfers.append(_make_transfer(f"dormant_out_{seed}_{i}", burst_ts + timedelta(minutes=i*10), addr, f"dest_{seed}_{i}", 200))

    return transfers

def generate_structuring(seed: int = 42, n_txs: int = 5) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)
    addr = f"structurer_{seed}"

    for i in range(n_txs):
        amt = 9.8 + random.random() * 0.1
        transfers.append(_make_transfer(f"struct_{seed}_{i}", base_ts + timedelta(hours=i), addr, f"dest_{seed}", amt))

    return transfers

def generate_round_trip(seed: int = 42) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)
    addr = f"origin_{seed}"

    transfers.append(_make_transfer(f"rt_{seed}_1", base_ts, addr, f"hop1_{seed}", 100))
    transfers.append(_make_transfer(f"rt_{seed}_2", base_ts + timedelta(minutes=10), f"hop1_{seed}", f"hop2_{seed}", 100))
    transfers.append(_make_transfer(f"rt_{seed}_3", base_ts + timedelta(minutes=20), f"hop2_{seed}", addr, 100))

    return transfers

def generate_exchange_deposit_funnel(seed: int = 42) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)
    hot_wallet = f"hot_wallet_{seed}"

    for i in range(10):
        transfers.append(_make_transfer(f"dep_{seed}_{i}", base_ts + timedelta(minutes=i), f"user_{seed}_{i}", hot_wallet, 50))

    return transfers

def generate_benign_processor(seed: int = 42) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)
    processor = f"processor_{seed}"

    for i in range(10):
        transfers.append(_make_transfer(f"sal_{seed}_{i}", base_ts + timedelta(minutes=i), processor, f"emp_{seed}_{i}", 5000))

    return transfers

def generate_benign_market_maker(seed: int = 42) -> list[Transfer]:
    random.seed(seed)
    transfers = []
    base_ts = datetime.now(timezone.utc)
    mm = f"mm_{seed}"

    for i in range(5):
        amt = 100 + i*20
        transfers.append(_make_transfer(f"mm_{seed}_{i}", base_ts + timedelta(hours=i), mm, f"exchange_{seed}", amt))

    return transfers
