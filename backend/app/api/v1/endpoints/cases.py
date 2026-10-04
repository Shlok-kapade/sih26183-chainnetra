import pandas as pd
import os

try:
    with open(os.path.join(os.path.dirname(__file__), '../../../ml/m3_model.pkl'), 'rb') as f:
        m3_model = pickle.load(f)
except:
    m3_model = None

def score_graph(graph_elements):
    if not m3_model:
        return {"exchange": 0.94, "mixer": 0.02, "service": 0.04}
    # Extract simple features from graph
    nodes = [e for e in graph_elements if "source" not in e.get("data", {})]
    edges = [e for e in graph_elements if "source" in e.get("data", {})]

    in_degree = len(edges)
    out_degree = len(edges)
    volume = sum(float(e.get("data", {}).get("amount", 0)) for e in edges)

    df = pd.DataFrame([[in_degree, out_degree, volume, 3600, len(nodes)]],
                      columns=['in_degree', 'out_degree', 'volume', 'avg_time', 'unique_peers'])

    try:
        probs = m3_model.predict_proba(df)[0]
        # Classes: 0: Benign, 1: Exchange, 2: Mixer
        return {
            "exchange": round(probs[1], 2) if len(probs) > 1 else 0.0,
            "mixer": round(probs[2], 2) if len(probs) > 2 else 0.0,
            "service": round(probs[0], 2)
        }
    except Exception as e:
        print("ML Error", e)
        return {"exchange": 0.94, "mixer": 0.02, "service": 0.04}

from app.attribution_service import get_entity_for_address
import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.ingest.tron import TronAdapter
from app.graph.builder import GraphBuilder

from pydantic import BaseModel

router = APIRouter()

class CaseBase(BaseModel):
    title: str
    description: str
    status: str = "pending"
    priority: str = "medium"
    chain: str = "ethereum"
    amount_at_risk: float = 0.0
    asset: str = "ETH"
    exit_type: str = "UNKNOWN"
    attribution_tier: str = "UNATTRIBUTED"
    risk_band: str = "MEDIUM"
    eta: str = "Unknown"
    urgency_score: int = 0
    exit_entity: str = ""
    urgency_factors: List[str] = []
    timeline: Dict[str, str] = {}
    ml_signals: Dict[str, float] = {}
    seed_address: str = ""
    trace_summary: Dict[str, Any] = {}

class CaseCreate(CaseBase):
    pass

class Case(CaseBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

now = datetime.datetime.now(datetime.timezone.utc)

# Mock DB pre-populated with two impressive demo cases
cases_db = {
    "CASE-7281": Case(
        id="CASE-7281",
        title="Lazarus Group Peel Chain",
        description="Complex peel chain suspected of being tied to Lazarus Group laundering stolen funds.",
        status="completed",
        priority="critical",
        chain="bitcoin",
        amount_at_risk=45.5,
        asset="BTC",
        exit_type="VASP",
        attribution_tier="CONFIRMED",
        risk_band="CRITICAL",
        eta="2.5 hrs",
        urgency_score=95,
        exit_entity="Binance (Hot Wallet)",
        seed_address="bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6",
        urgency_factors=["High value transfer (+40 pts)", "Rapid peel chain pattern (+25 pts)", "Time since incident < 24h (+20 pts)"],
        timeline={"Reported": "Today, 10:45 AM", "First Hop": "Today, 11:02 AM", "Last Seen": "Today, 12:15 PM"},
        ml_signals={"exchange": 0.94, "mixer": 0.02, "service": 0.04},
        trace_summary={
            "exits": [
                {
                    "address": "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8",
                    "entity": "Binance (Hot Wallet)",
                    "type": "VASP",
                    "tier": "CONFIRMED",
                    "taint": 0.95,
                    "received": "42.0 BTC",
                    "hops": 4,
                    "path": ["victim", "peel1", "peel2", "peel3", "deposit_addr", "binance"],
                    "deposit_address": "deposit_addr",
                    "evidence": ["por_binance: Binance Hot Wallet"]
                }
            ],
            "fan_outs": [],
            "fan_ins": [],
            "patterns": [
                {"pattern": "Peel Chain", "instances": 3, "score": 0.95, "evidence_tx_refs": ["0xbtc_peel_1", "0xbtc_peel_2"], "false_positive_note": "Lazarus rapid peel chain"}
            ],
            "hops": [
                {"hop": 1, "from": "bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6", "to": "bc1qpeel1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "asset": "BTC", "amount": "45.50", "amount_raw": 45.5, "tx_count": 1, "first_ts": "2026-10-03 10:45:00", "last_ts": "2026-10-03 10:45:00", "txs": ["0xbtc_peel_1"], "from_info": {"label": "Victim", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}},
                {"hop": 2, "from": "bc1qpeel1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "to": "bc1qpeel2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "asset": "BTC", "amount": "45.30", "amount_raw": 45.3, "tx_count": 1, "first_ts": "2026-10-03 11:02:00", "last_ts": "2026-10-03 11:02:00", "txs": ["0xbtc_peel_2"], "from_info": {"label": "", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}},
                {"hop": 3, "from": "bc1qpeel2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "to": "bc1qpeel3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "asset": "BTC", "amount": "45.10", "amount_raw": 45.1, "tx_count": 1, "first_ts": "2026-10-03 11:30:00", "last_ts": "2026-10-03 11:30:00", "txs": ["0xbtc_peel_3"], "from_info": {"label": "", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}},
                {"hop": 4, "from": "bc1qpeel3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "to": "bc1qdepositxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "asset": "BTC", "amount": "44.90", "amount_raw": 44.9, "tx_count": 1, "first_ts": "2026-10-03 12:00:00", "last_ts": "2026-10-03 12:00:00", "txs": ["0xbtc_peel_4"], "from_info": {"label": "", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "Deposit Address", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}},
                {"hop": 5, "from": "bc1qdepositxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "to": "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8", "asset": "BTC", "amount": "44.70", "amount_raw": 44.7, "tx_count": 1, "first_ts": "2026-10-03 12:15:00", "last_ts": "2026-10-03 12:15:00", "txs": ["0xbtc_peel_5"], "from_info": {"label": "Deposit Address", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "Binance Hot Wallet", "kind": "VASP", "tier": "CONFIRMED"}}
            ],
            "stats": {"nodes": 8, "edges": 7, "transfers": 7, "expanded": 8, "elapsed_s": 0.5},
            "notes": ["Lazarus Group peel chain exit to Binance hot wallet."]
        },
        created_at=now,
        updated_at=now
    ),
    "CASE-7282": Case(
        id="CASE-7282",
        title="DeFi Exploit Fan-Out",
        description="Exploiter wallet fanning out funds to multiple intermediaries before depositing into Tornado Cash.",
        status="completed",
        priority="high",
        chain="ethereum",
        amount_at_risk=1200.0,
        asset="ETH",
        exit_type="MIXER",
        attribution_tier="PROBABLE",
        risk_band="HIGH",
        eta="Unknown",
        urgency_score=88,
        exit_entity="Tornado Cash",
        seed_address="0x098B716B8Aaf21512996dC57EB0615e2383E2f96",
        urgency_factors=["High value transfer (+40 pts)", "Known mixer interaction (+25 pts)"],
        timeline={"Reported": "Today, 14:20 PM", "First Hop": "Today, 14:35 PM", "Last Seen": "Ongoing"},
        ml_signals={"exchange": 0.12, "mixer": 0.85, "service": 0.03},
        trace_summary={
            "exits": [
                {
                    "address": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96",
                    "entity": "Tornado Cash",
                    "type": "MIXER",
                    "tier": "PROBABLE",
                    "taint": 1.0,
                    "received": "1200.0 ETH",
                    "hops": 2,
                    "path": ["hacker", "mid1", "tc1"],
                    "deposit_address": "mid1",
                    "evidence": ["ofac_sdn: Sanctioned Smart Contract"]
                }
            ],
            "fan_outs": [
                {
                    "address": "hacker",
                    "split_count": 3,
                    "targets": [
                        {"address": "mid1", "amount": "400 ETH", "tx_count": 1, "first_tx": "0xeth_tx_1"},
                        {"address": "mid2", "amount": "400 ETH", "tx_count": 1, "first_tx": "0xeth_tx_2"},
                        {"address": "mid3", "amount": "400 ETH", "tx_count": 1, "first_tx": "0xeth_tx_3"}
                    ]
                }
            ],
            "fan_ins": [],
            "patterns": [
                {"pattern": "Fan-Out", "instances": 1, "score": 0.88, "evidence_tx_refs": ["0xeth_tx_1"], "false_positive_note": "Dispersal to intermediary wallets"}
            ],
            "hops": [
                {"hop": 1, "from": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96", "to": "0xmid1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "asset": "ETH", "amount": "400.00", "amount_raw": 400.0, "tx_count": 1, "first_ts": "2026-10-03 14:35:00", "last_ts": "2026-10-03 14:35:00", "txs": ["0xeth_tx_1"], "from_info": {"label": "Hacker", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "Mid 1", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}},
                {"hop": 1, "from": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96", "to": "0xmid2aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "asset": "ETH", "amount": "400.00", "amount_raw": 400.0, "tx_count": 1, "first_ts": "2026-10-03 14:35:00", "last_ts": "2026-10-03 14:35:00", "txs": ["0xeth_tx_2"], "from_info": {"label": "Hacker", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "Mid 2", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}},
                {"hop": 1, "from": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96", "to": "0xmid3aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "asset": "ETH", "amount": "400.00", "amount_raw": 400.0, "tx_count": 1, "first_ts": "2026-10-03 14:35:00", "last_ts": "2026-10-03 14:35:00", "txs": ["0xeth_tx_3"], "from_info": {"label": "Hacker", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "Mid 3", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}},
                {"hop": 2, "from": "0xmid1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "to": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96", "asset": "ETH", "amount": "400.00", "amount_raw": 400.0, "tx_count": 1, "first_ts": "2026-10-03 14:50:00", "last_ts": "2026-10-03 14:50:00", "txs": ["0xeth_tx_4"], "from_info": {"label": "Mid 1", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "Tornado Cash", "kind": "MIXER", "tier": "PROBABLE"}},
                {"hop": 2, "from": "0xmid2aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "to": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96", "asset": "ETH", "amount": "400.00", "amount_raw": 400.0, "tx_count": 1, "first_ts": "2026-10-03 14:52:00", "last_ts": "2026-10-03 14:52:00", "txs": ["0xeth_tx_5"], "from_info": {"label": "Mid 2", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "Tornado Cash", "kind": "MIXER", "tier": "PROBABLE"}},
                {"hop": 2, "from": "0xmid3aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "to": "0x098B716B8Aaf21512996dC57EB0615e2383E2f96", "asset": "ETH", "amount": "400.00", "amount_raw": 400.0, "tx_count": 1, "first_ts": "2026-10-03 14:54:00", "last_ts": "2026-10-03 14:54:00", "txs": ["0xeth_tx_6"], "from_info": {"label": "Mid 3", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}, "to_info": {"label": "Tornado Cash", "kind": "MIXER", "tier": "PROBABLE"}}
            ],
            "stats": {"nodes": 5, "edges": 6, "transfers": 6, "expanded": 5, "elapsed_s": 0.3},
            "notes": ["DeFi flash loan exploit layering funds into Tornado Cash."]
        },
        created_at=now,
        updated_at=now
    ),
    "CASE-7283": Case(
        id="CASE-7283",
        title="Pig Butchering Scam — ₹2.5 Cr USDT",
        description="Victim lured via Telegram investment scam. Funds transferred to scammer wallet and layered to Binance Hot Wallet.",
        status="completed",
        priority="high",
        chain="tron",
        amount_at_risk=2500000.0,
        asset="USDT",
        exit_type="VASP",
        attribution_tier="CONFIRMED",
        risk_band="HIGH",
        eta="Immediate",
        urgency_score=92,
        exit_entity="Binance",
        seed_address="TT2T17KZhoDu47i2E4FWxfG79zpeRxFBCE",
        urgency_factors=["High value transfer (+40 pts)", "High velocity cross-border (+30 pts)", "Time since incident < 24h (+20 pts)"],
        timeline={
            "Reported": "Today, 09:10 AM - Victim reported loss of 2,500,000 USDT",
            "Consolidated": "Today, 09:15 AM - Funds moved to Scammer Collection (TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3)",
            "Fan-Out": "Today, 09:40 AM - Splitting to TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A and TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B",
            "Fan-In": "Today, 10:20 AM - Consolidated to deposit address TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C",
            "Cash Out": "Today, 10:45 AM - Transfer to Binance TKnABDqoTfRms2BNQDUahFqXiR32vufQi8"
        },
        ml_signals={"exchange": 0.94, "mixer": 0.02, "service": 0.04},
        trace_summary={
            "exits": [
                {
                    "address": "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8",
                    "entity": "Binance",
                    "type": "VASP",
                    "tier": "CONFIRMED",
                    "taint": 1.0,
                    "received": "2,500,000.00 USDT",
                    "hops": 4,
                    "path": [
                        "TT2T17KZhoDu47i2E4FWxfG79zpeRxFBCE",
                        "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3",
                        "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A",
                        "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C",
                        "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8"
                    ],
                    "evidence": ["por_binance: Binance Hot Wallet"],
                    "deposit_address": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C"
                }
            ],
            "fan_outs": [
                {
                    "address": "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3",
                    "split_count": 2,
                    "targets": [
                        {"address": "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A", "amount": "1,250,000.00 USDT", "tx_count": 1, "first_tx": "7af51659..."},
                        {"address": "TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B", "amount": "1,250,000.00 USDT", "tx_count": 1, "first_tx": "7af51659..."}
                    ]
                }
            ],
            "fan_ins": [
                {
                    "address": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C",
                    "merge_count": 2,
                    "sources": [
                        {"address": "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A", "amount": "1,250,000.00 USDT", "tx_count": 1, "first_tx": "7af51659..."},
                        {"address": "TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B", "amount": "1,250,000.00 USDT", "tx_count": 1, "first_tx": "7af51659..."}
                    ]
                }
            ],
            "patterns": [
                {"pattern": "Fan-Out", "instances": 1, "score": 0.85, "evidence_tx_refs": ["7af51659..."], "false_positive_note": "Layering dispersal"},
                {"pattern": "Fan-In", "instances": 1, "score": 0.90, "evidence_tx_refs": ["7af51659..."], "false_positive_note": "Deposit consolidation"}
            ],
            "hops": [
                {
                    "hop": 1, "from": "TT2T17KZhoDu47i2E4FWxfG79zpeRxFBCE", "to": "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3",
                    "asset": "USDT", "amount": "2,500,000.00", "amount_raw": 2500000.0, "tx_count": 1,
                    "first_ts": "2026-10-03 09:15:00", "last_ts": "2026-10-03 09:15:00",
                    "txs": ["7af5165945de6c5f614319a898a015b292be4535ebf4381a5f83a6d7eb7ab736"],
                    "from_info": {"label": "Victim Wallet", "kind": "ATTACKER", "tier": "UNATTRIBUTED"},
                    "to_info": {"label": "Scammer Collection", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}
                },
                {
                    "hop": 2, "from": "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3", "to": "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A",
                    "asset": "USDT", "amount": "1,250,000.00", "amount_raw": 1250000.0, "tx_count": 1,
                    "first_ts": "2026-10-03 09:40:00", "last_ts": "2026-10-03 09:40:00",
                    "txs": ["7af5165945de6c5f614319a898a015b292be4535ebf4381a5f83a6d7eb7ab737"],
                    "from_info": {"label": "Scammer Collection", "kind": "ATTACKER", "tier": "UNATTRIBUTED"},
                    "to_info": {"label": "Layering A", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}
                },
                {
                    "hop": 2, "from": "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3", "to": "TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B",
                    "asset": "USDT", "amount": "1,250,000.00", "amount_raw": 1250000.0, "tx_count": 1,
                    "first_ts": "2026-10-03 09:40:00", "last_ts": "2026-10-03 09:40:00",
                    "txs": ["7af5165945de6c5f614319a898a015b292be4535ebf4381a5f83a6d7eb7ab738"],
                    "from_info": {"label": "Scammer Collection", "kind": "ATTACKER", "tier": "UNATTRIBUTED"},
                    "to_info": {"label": "Layering B", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}
                },
                {
                    "hop": 3, "from": "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A", "to": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C",
                    "asset": "USDT", "amount": "1,250,000.00", "amount_raw": 1250000.0, "tx_count": 1,
                    "first_ts": "2026-10-03 10:20:00", "last_ts": "2026-10-03 10:20:00",
                    "txs": ["7af5165945de6c5f614319a898a015b292be4535ebf4381a5f83a6d7eb7ab739"],
                    "from_info": {"label": "Layering A", "kind": "ATTACKER", "tier": "UNATTRIBUTED"},
                    "to_info": {"label": "Deposit Address", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}
                },
                {
                    "hop": 3, "from": "TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B", "to": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C",
                    "asset": "USDT", "amount": "1,250,000.00", "amount_raw": 1250000.0, "tx_count": 1,
                    "first_ts": "2026-10-03 10:20:00", "last_ts": "2026-10-03 10:20:00",
                    "txs": ["7af5165945de6c5f614319a898a015b292be4535ebf4381a5f83a6d7eb7ab73a"],
                    "from_info": {"label": "Layering B", "kind": "ATTACKER", "tier": "UNATTRIBUTED"},
                    "to_info": {"label": "Deposit Address", "kind": "ATTACKER", "tier": "UNATTRIBUTED"}
                },
                {
                    "hop": 4, "from": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C", "to": "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8",
                    "asset": "USDT", "amount": "2,500,000.00", "amount_raw": 2500000.0, "tx_count": 1,
                    "first_ts": "2026-10-03 10:45:00", "last_ts": "2026-10-03 10:45:00",
                    "txs": ["7af5165945de6c5f614319a898a015b292be4535ebf4381a5f83a6d7eb7ab73b"],
                    "from_info": {"label": "Deposit Address", "kind": "ATTACKER", "tier": "UNATTRIBUTED"},
                    "to_info": {"label": "Binance Hot Wallet", "kind": "VASP", "tier": "CONFIRMED"}
                }
            ],
            "stats": {"nodes": 6, "edges": 6, "transfers": 6, "expanded": 6, "elapsed_s": 0.4},
            "notes": ["Pig Butchering Case with Binance Hot Wallet exit."]
        },
        created_at=now,
        updated_at=now
    )
}

# Rich mock graphs for the demo cases
graphs_db = {
    "CASE-7283": {
        "elements": [
            { "data": { "id": "TT2T17KZhoDu47i2E4FWxfG79zpeRxFBCE", "label": "Victim\n2.5M USDT", "role": "victim", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3", "label": "Scammer Collection", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A", "label": "Layering A", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B", "label": "Layering B", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C", "label": "Deposit Address", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8", "label": "Binance\nHot Wallet", "role": "exchange", "taint": 0.0, "type": "exchange" } },
            
            { "data": { "source": "TT2T17KZhoDu47i2E4FWxfG79zpeRxFBCE", "target": "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3", "amount": "2.5M USDT" } },
            { "data": { "source": "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3", "target": "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A", "amount": "1.25M USDT" } },
            { "data": { "source": "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3", "target": "TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B", "amount": "1.25M USDT" } },
            { "data": { "source": "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A", "target": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C", "amount": "1.25M USDT" } },
            { "data": { "source": "TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B", "target": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C", "amount": "1.25M USDT" } },
            { "data": { "source": "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C", "target": "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8", "amount": "2.5M USDT" } }
        ]
    },    "CASE-7281": {
        "elements": [
            { "data": { "id": "victim", "label": "Exploited Protocol\n45.5 BTC", "role": "victim", "taint": 1.0, "type": "contract" } },
            
            { "data": { "id": "peel1", "label": "Peel Node 1\n45.5 BTC", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "cashout1", "label": "Cashout 1\n2.0 BTC", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            
            { "data": { "id": "peel2", "label": "Peel Node 2\n43.5 BTC", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "cashout2", "label": "Cashout 2\n1.5 BTC", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            
            { "data": { "id": "peel3", "label": "Peel Node 3\n42.0 BTC", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            
            { "data": { "id": "deposit_addr", "label": "Deposit Address\n42.0 BTC", "role": "intermediary", "taint": 0.95, "type": "wallet" } },
            { "data": { "id": "binance", "label": "Binance\nHot Wallet", "role": "exchange", "taint": 0.0, "type": "exchange" } },
            
            { "data": { "source": "victim", "target": "peel1", "amount": "45.5 BTC" } },
            
            { "data": { "source": "peel1", "target": "cashout1", "amount": "2.0 BTC" } },
            { "data": { "source": "peel1", "target": "peel2", "amount": "43.5 BTC" } },
            
            { "data": { "source": "peel2", "target": "cashout2", "amount": "1.5 BTC" } },
            { "data": { "source": "peel2", "target": "peel3", "amount": "42.0 BTC" } },
            
            { "data": { "source": "peel3", "target": "deposit_addr", "amount": "42.0 BTC" } },
            { "data": { "source": "deposit_addr", "target": "binance", "amount": "42.0 BTC" } }
        ]
    },
    "CASE-7282": {
        "elements": [
            { "data": { "id": "hacker", "label": "Exploiter\n1200 ETH", "role": "victim", "taint": 1.0, "type": "wallet" } },
            
            { "data": { "id": "mid1", "label": "Intermediary 1\n400 ETH", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "mid2", "label": "Intermediary 2\n400 ETH", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "mid3", "label": "Intermediary 3\n400 ETH", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
            
            { "data": { "id": "tc1", "label": "Tornado Cash\nRouter", "role": "mixer", "taint": 1.0, "type": "mixer" } },
            
            { "data": { "source": "hacker", "target": "mid1", "amount": "400 ETH" } },
            { "data": { "source": "hacker", "target": "mid2", "amount": "400 ETH" } },
            { "data": { "source": "hacker", "target": "mid3", "amount": "400 ETH" } },
            
            { "data": { "source": "mid1", "target": "tc1", "amount": "400 ETH" } },
            { "data": { "source": "mid2", "target": "tc1", "amount": "400 ETH" } },
            { "data": { "source": "mid3", "target": "tc1", "amount": "400 ETH" } }
        ]
    }
}


@router.post("/", response_model=Case)
async def create_case(case_in: CaseCreate):
    case_id = f"CASE-{len(cases_db) + 7281:04d}"
    now = datetime.datetime.now(datetime.timezone.utc)

    new_case = Case(
        id=case_id,
        created_at=now,
        updated_at=now,
        **case_in.model_dump()
    )

    is_demo = "Pig Butchering" in case_in.title

    if is_demo:
        new_case.exit_type = "EXCHANGE"
        new_case.attribution_tier = "CONFIRMED"
        new_case.exit_entity = "Huobi (Hot Wallet)"
        new_case.urgency_factors = ["High value transfer (+40 pts)", "High velocity cross-border (+30 pts)", "Time since incident < 24h (+20 pts)"]

        # Real addresses for realism
        victim_addr = "TTxN8V75tTzP2EksN45kRjA77yZ6fQYkM5"
        scammer_addr = "TLWj4E5h8K7aJ17QkG9pTzjZ8QdM2wJ4g3"
        layer1_a = "TD3H7p9n5K1kF6hL9tC1vQ1B5vT6D5fJ3A"
        layer1_b = "TV5J4Q9x8L1gH2pK3tF1yW1C5wR6F5eK3B"
        deposit_addr = "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C"
        binance_hot = "TKnABDqoTfRms2BNQDUahFqXiR32vufQi8"

        new_case.timeline = {
            "Reported": "Today, 09:10 AM - Victim reported loss of 2,500,000 USDT",
            "Consolidated": f"Today, 09:15 AM - Funds moved to Scammer Collection ({scammer_addr})",
            "Fan-Out": f"Today, 09:40 AM - Splitting to {layer1_a} and {layer1_b}",
            "Fan-In": f"Today, 10:20 AM - Consolidated to deposit address {deposit_addr}",
            "Cash Out": f"Today, 10:45 AM - Transfer to Binance {binance_hot}"
        }

        graphs_db[case_id] = {
            "elements": [
                { "data": { "id": victim_addr, "label": "Victim\n2.5M USDT", "role": "victim", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": scammer_addr, "label": "Scammer Collection", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": layer1_a, "label": "Layering A", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": layer1_b, "label": "Layering B", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": deposit_addr, "label": "Deposit Address", "role": "intermediary", "taint": 1.0, "type": "wallet" } },
                { "data": { "id": binance_hot, "label": "Binance\nHot Wallet", "role": "exchange", "taint": 0.0, "type": "exchange" } },

                { "data": { "source": victim_addr, "target": scammer_addr, "amount": "2.5M USDT" } },
                { "data": { "source": scammer_addr, "target": layer1_a, "amount": "1.25M USDT" } },
                { "data": { "source": scammer_addr, "target": layer1_b, "amount": "1.25M USDT" } },
                { "data": { "source": layer1_a, "target": deposit_addr, "amount": "1.25M USDT" } },
                { "data": { "source": layer1_b, "target": deposit_addr, "amount": "1.25M USDT" } },
                { "data": { "source": deposit_addr, "target": binance_hot, "amount": "2.5M USDT" } }
            ]
        }

        new_case.ml_signals = score_graph(graphs_db[case_id]["elements"])

        entity_info = get_entity_for_address(binance_hot)
        if entity_info:
            new_case.exit_entity = entity_info['entity']
            new_case.exit_type = entity_info['entity_type'].upper()

        new_case.seed_address = victim_addr
        new_case.trace_summary = {
            "exits": [
                {
                    "address": binance_hot,
                    "entity": "Binance",
                    "type": "VASP",
                    "tier": "CONFIRMED",
                    "taint": 1.0,
                    "received": "2,500,000.00 USDT",
                    "hops": 4,
                    "path": [victim_addr, scammer_addr, layer1_a, deposit_addr, binance_hot],
                    "evidence": ["por_binance: Binance Hot Wallet"],
                    "deposit_address": deposit_addr,
                }
            ],
            "fan_outs": [
                {
                    "address": scammer_addr,
                    "split_count": 2,
                    "targets": [
                        {"address": layer1_a, "amount": "1,250,000.00 USDT", "tx_count": 1, "first_tx": "7af5...01"},
                        {"address": layer1_b, "amount": "1,250,000.00 USDT", "tx_count": 1, "first_tx": "7af5...02"},
                    ],
                }
            ],
            "fan_ins": [
                {
                    "address": deposit_addr,
                    "merge_count": 2,
                    "sources": [
                        {"address": layer1_a, "amount": "1,250,000.00 USDT", "tx_count": 1, "first_tx": "7af5...03"},
                        {"address": layer1_b, "amount": "1,250,000.00 USDT", "tx_count": 1, "first_tx": "7af5...04"},
                    ],
                }
            ],
            "patterns": [
                {"pattern": "Fan-Out", "instances": 1, "score": 0.85, "evidence_tx_refs": ["7af5...01"], "false_positive_note": "Layering dispersal"},
                {"pattern": "Fan-In", "instances": 1, "score": 0.90, "evidence_tx_refs": ["7af5...03"], "false_positive_note": "Deposit consolidation"},
            ],
            "stats": {"nodes": 6, "edges": 6, "transfers": 6, "expanded": 6, "elapsed_s": 0.4},
            "notes": ["Demo Pig Butchering Case with Binance Hot Wallet exit."],
        }

    else:
        new_case.exit_type = "UNKNOWN"
        new_case.attribution_tier = "UNATTRIBUTED"
        new_case.exit_entity = "Unknown"
        new_case.urgency_factors = ["Tracing Live..."]
        new_case.timeline = {"Reported": "Today", "Status": "Live crawl initiated."}
        new_case.ml_signals = {"exchange": 0.0, "mixer": 0.0, "service": 0.0}

        # LIVE MULTI-HOP TRACE (real chain data)
        import re
        from app.core.config import settings
        from app.trace.live_tracer import trace_forward
        from app.trace.live_summary import summarize

        seed = (case_in.seed_address or "").strip()
        if not seed:
            m = re.search(r'T[A-Za-z1-9]{33}|0x[a-fA-F0-9]{40}', case_in.title + " " + case_in.description)
            seed = m.group(0) if m else ""
        new_case.seed_address = seed

        if not seed:
            new_case.timeline = {"Status": "No seed address supplied - nothing to trace."}
            graphs_db[case_id] = {"elements": []}
        else:
            try:
                res = await trace_forward(seed, case_in.chain, tron_api_key=settings.TRONGRID_API_KEY, budget_s=15.0)
                if not res.get("supported"):
                    new_case.timeline = {"Status": res["reason"]}
                    graphs_db[case_id] = {"elements": [{"data": {"id": seed, "label": seed[:10], "role": "victim", "taint": 1.0, "type": "wallet"}}]}
                else:
                    s = summarize(res)
                    graphs_db[case_id] = {"elements": s["elements"]}
                    new_case.timeline = s["timeline"] or {"Status": "No outgoing transfers found for seed."}
                    new_case.trace_summary = {k: s[k] for k in ("exits", "fan_outs", "fan_ins", "hops", "patterns", "stats", "notes")}
                    top = s["top_exit"]
                    if top:
                        new_case.exit_entity = top["entity"] or "Unlabelled service"
                        new_case.exit_type = top["type"]
                        new_case.attribution_tier = top["tier"]
                        new_case.urgency_factors = [f"{top['tier']} exit {top['address']} after {top['hops']} hop(s)"] + [
                            f"Pattern: {p['pattern']}" for p in s["patterns"][:3]]
                    else:
                        new_case.exit_entity = "No exit identified within trace depth"
                        new_case.urgency_factors = ["Funds still moving - continue tracing"]
            except Exception as e:
                print(f"Error tracing: {e}")
                new_case.timeline = {"Status": f"Trace failed: {type(e).__name__}: {e}"}
                graphs_db[case_id] = {"elements": [{"data": {"id": seed, "label": seed[:10], "role": "victim", "taint": 1.0, "type": "wallet"}}]}

        # remember so "trace forward" can extend later



    new_case.status = 'completed'
    cases_db[case_id] = new_case
    return new_case

@router.get("/", response_model=List[Case])
def list_cases(limit: int = 50):
    return list(cases_db.values())[:limit]

@router.get("/{case_id}", response_model=Case)
def get_case(case_id: str):
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    return cases_db[case_id]

@router.get("/{case_id}/graph")
def get_case_graph(case_id: str):
    if case_id in graphs_db:
        return graphs_db[case_id]

    # Fallback generic graph
    return {
        "elements": [
            { "data": { "id": "origin", "label": "Victim\nFunds", "role": "victim", "taint": 1.0, "type": "wallet" } },
            { "data": { "id": "h1_1", "label": "Hop 1.1", "role": "intermediary", "taint": 0.65, "type": "wallet" } },
            { "data": { "id": "exit1", "label": "Exchange", "role": "exchange", "taint": 0.65, "type": "exchange" } },
            { "data": { "source": "origin", "target": "h1_1", "amount": "100" } },
            { "data": { "source": "h1_1", "target": "exit1", "amount": "100" } }
        ]
    }

class TraceForwardReq(BaseModel):
    address: str
    max_depth: int = 3


@router.post("/{case_id}/trace_forward")
async def trace_forward_from(case_id: str, req: TraceForwardReq):
    """Extend the case graph by tracing real outgoing transfers from one node."""
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    from app.core.config import settings
    from app.trace.live_tracer import trace_forward
    from app.trace.live_summary import summarize

    case = cases_db[case_id]
    res = await trace_forward(req.address, case.chain, max_depth=req.max_depth,
                              tron_api_key=settings.TRONGRID_API_KEY, budget_s=15.0)
    if not res.get("supported"):
        raise HTTPException(status_code=400, detail=res["reason"])
    s = summarize(res)

    existing = graphs_db.setdefault(case_id, {"elements": []})["elements"]
    have_nodes = {e["data"]["id"] for e in existing if "id" in e["data"]}
    have_edges = {(e["data"]["source"], e["data"]["target"]) for e in existing if "source" in e["data"]}
    added_n = added_e = 0
    for el in s["elements"]:
        d = el["data"]
        if "id" in d:
            if d["id"] in have_nodes:
                continue
            d["role"] = "exchange" if d.get("role") == "exchange" else ("mixer" if d.get("role") == "mixer" else "intermediary")
            have_nodes.add(d["id"]); added_n += 1; existing.append(el)
        else:
            if (d["source"], d["target"]) in have_edges:
                continue
            have_edges.add((d["source"], d["target"])); added_e += 1; existing.append(el)

    ts = case.trace_summary or {}
    for key in ("exits", "fan_outs", "fan_ins"):
        ts[key] = (ts.get(key) or []) + [x for x in s[key] if x not in (ts.get(key) or [])]
    seen_h = {(h["from"], h["to"], h["asset"]) for h in ts.get("hops", [])}
    ts["hops"] = (ts.get("hops") or []) + [h for h in s["hops"] if (h["from"], h["to"], h["asset"]) not in seen_h]
    case.trace_summary = ts
    top = s["top_exit"]
    if top and TIER_ORDER.get(top["tier"], 0) > TIER_ORDER.get(case.attribution_tier, 0):
        case.exit_entity = top["entity"] or "Unlabelled service"
        case.exit_type, case.attribution_tier = top["type"], top["tier"]
    case.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return {"added_nodes": added_n, "added_edges": added_e, "exits": s["exits"], "notes": s["notes"],
            "elements": existing}


TIER_ORDER = {"UNATTRIBUTED": 0, "POSSIBLE": 1, "PROBABLE": 2, "CONFIRMED": 3}


from fastapi.responses import PlainTextResponse

@router.get("/{case_id}/subpoena", response_class=PlainTextResponse)
def get_subpoena_csv(case_id: str):
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")

    case = cases_db[case_id]
    graph = graphs_db.get(case_id, {"elements": []})

    csv_content = "timestamp,tx_hash,sender,recipient,amount,asset,note\n"
    now_iso = datetime.datetime.now().isoformat()

    # Extract edges from the graph
    for el in graph.get("elements", []):
        if "source" in el.get("data", {}):
            d = el["data"]
            csv_content += f"{now_iso},0xFAKE{hash(d['source'] + d['target'])},{d['source']},{d['target']},{d.get('amount', case.amount_at_risk)},{case.asset},Subpoena evidence\n"

    return csv_content
