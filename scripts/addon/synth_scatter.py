from datetime import datetime, timedelta
import random

class SynthTransfer:
    def __init__(self, chain, from_addr, to_addr, asset, amount, ts, kind, raw_ref):
        self.chain = chain
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.asset = asset
        self.amount = amount
        self.ts = ts
        self.kind = kind
        self.raw_ref = raw_ref

def generate_scatter(seed: int, n_recipients: int, n_collectors: int, seed_amount: float):
    random.seed(seed)
    transfers = []
    collectors = [f"collector_{i}" for i in range(n_collectors)]
    
    t_start = datetime(2025, 1, 1, 12, 0)
    
    amount_per = seed_amount / n_recipients
    for i in range(n_recipients):
        recipient = f"wallet_{i}"
        
        # Outgoing from origin
        transfers.append(SynthTransfer(
            chain="ETH",
            from_addr="origin_wallet",
            to_addr=recipient,
            asset="USDT",
            amount=amount_per,
            ts=t_start + timedelta(seconds=i),
            kind="transfer",
            raw_ref="SYNTHETIC"
        ))
        
        # Gathering to collectors
        if n_collectors > 0:
            collector = random.choice(collectors)
            transfers.append(SynthTransfer(
                chain="ETH",
                from_addr=recipient,
                to_addr=collector,
                asset="USDT",
                amount=amount_per * 0.99, # slightly less to simulate fees
                ts=t_start + timedelta(hours=1, seconds=i),
                kind="transfer",
                raw_ref="SYNTHETIC"
            ))
            
    return transfers, collectors

def generate_benign_airdrop(seed: int, n: int):
    random.seed(seed)
    transfers = []
    t_start = datetime(2025, 1, 1, 12, 0)
    for i in range(n):
        transfers.append(SynthTransfer(
            chain="ETH",
            from_addr="airdrop_contract",
            to_addr=f"user_{i}",
            asset="TOKEN",
            amount=100.0,
            ts=t_start + timedelta(seconds=i),
            kind="transfer",
            raw_ref="SYNTHETIC"
        ))
    return transfers

def generate_dust_attack(seed: int, n: int):
    random.seed(seed)
    transfers = []
    t_start = datetime(2025, 1, 1, 12, 0)
    for i in range(n):
        transfers.append(SynthTransfer(
            chain="ETH",
            from_addr="attacker_wallet",
            to_addr=f"victim_{i}",
            asset="ETH",
            amount=0.0001,
            ts=t_start + timedelta(seconds=i),
            kind="transfer",
            raw_ref="SYNTHETIC"
        ))
    return transfers
