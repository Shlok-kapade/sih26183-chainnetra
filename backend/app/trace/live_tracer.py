"""Live multi-hop forward tracer (Tron via TronGrid, Ethereum via Blockscout).

Starting from a seed address it follows outgoing value hop by hop, attributes
every visited node (public Blockscout tags / local label CSVs / structural
service heuristics), stops at probable cash-out points and returns a graph plus
a structured summary. Everything shown is derived from live chain data; nothing
is fabricated. Confidence is deliberately conservative.
"""
from __future__ import annotations

import asyncio
import csv
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx

LABEL_DIR = os.path.join(os.path.dirname(__file__), "../../../data/labels")

MIXER_WORDS = ("tornado", "mixer", "blender", "sinbad", "railgun", "wasabi", "coinjoin")
EXCHANGE_WORDS = ("binance", "okx", "okex", "huobi", "htx", "kucoin", "bybit", "coinbase", "kraken",
                  "bitfinex", "gate.io", "mexc", "bitget", "crypto.com", "exchange", "hot wallet",
                  "deposit", "poloniex", "bithumb", "upbit", "bitstamp", "gemini", "wazirx", "coindcx")
# bridges and instant swappers: funds leave the chain/trace here, so they are terminal
BRIDGE_WORDS = ("bridge", "wormhole", "multichain", "stargate", "across", "hop protocol", "thorchain",
                "changenow", "sideshift", "fixedfloat", "exch", "chainflip", "synapse", "layerzero",
                "debridge", "orbiter", "relay", "cbridge", "celer", "allbridge", "swapspace", "simpleswap")
DEX_WORDS = ("uniswap", "sushiswap", "1inch", "pancake", "curve", "dex", "router", "swap", "paraswap", "0x:")

# Approximate USD weights, used ONLY to rank/prune which branches to follow (not for reporting).
_STABLE = {"USDT", "USDC", "DAI", "TUSD", "USDD", "FDUSD", "PYUSD", "USDE", "USDS", "BUSD", "USDT-TRC20", "GUSD"}
_WEIGHT = {"ETH": 3000.0, "WETH": 3000.0, "STETH": 3000.0, "WSTETH": 3500.0, "WBTC": 60000.0, "TRX": 0.2}


def approx_usd(asset: str, amount: Decimal) -> float:
    a = (asset or "").upper()
    w = 1.0 if a in _STABLE else _WEIGHT.get(a, 0.0)
    return float(amount) * w


# A node with this many distinct counterparties is almost certainly a service
# (exchange hot wallet / payment processor), not a private person.
SERVICE_DEGREE = 60


def _load_csv_labels() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not os.path.isdir(LABEL_DIR):
        return out
    for fn in os.listdir(LABEL_DIR):
        if not fn.endswith(".csv"):
            continue
        try:
            with open(os.path.join(LABEL_DIR, fn), newline="") as f:
                for row in csv.DictReader(f):
                    addr = (row.get("address") or "").strip()
                    if addr:
                        out[addr.lower() if addr.startswith("0x") else addr] = row
        except Exception:
            continue
    return out


CSV_LABELS = _load_csv_labels()


ATTACKER_WORDS = ("exploit", "hack", "phish", "scam", "stolen", "lazarus", "drainer", "rug pull", "ransom", "theft")


def _kind_from_text(text: str) -> str | None:
    t = text.lower()
    if any(w in t for w in ATTACKER_WORDS):
        return "ATTACKER"
    if any(w in t for w in MIXER_WORDS):
        return "MIXER"
    if any(w in t for w in BRIDGE_WORDS):
        return "BRIDGE"
    if any(w in t for w in EXCHANGE_WORDS):
        return "VASP"
    if any(w in t for w in DEX_WORDS):
        return "DEX_SWAP"
    return None


class Node:
    def __init__(self, addr: str, depth: int):
        self.addr = addr
        self.depth = depth
        self.label: str = ""
        self.kind: str = "UNKNOWN"      # VASP / MIXER / BRIDGE / DEX_SWAP / SERVICE_SUSPECTED / UNKNOWN
        self.tier: str = "UNATTRIBUTED"  # CONFIRMED / PROBABLE / POSSIBLE / UNATTRIBUTED
        self.evidence: list[str] = []
        self.taint: float = 0.0
        self.is_exit: bool = False
        self.distinct_peers: int = 0
        self.first_seen: datetime | None = None
        self.last_seen: datetime | None = None


class Edge:
    def __init__(self, src: str, dst: str, asset: str):
        self.src, self.dst, self.asset = src, dst, asset
        self.total = Decimal(0)
        self.count = 0
        self.first: datetime | None = None
        self.last: datetime | None = None
        self.txs: list[str] = []

    def add(self, amount: Decimal, ts: datetime, tx: str):
        self.total += amount
        self.count += 1
        self.first = ts if not self.first or ts < self.first else self.first
        self.last = ts if not self.last or ts > self.last else self.last
        if len(self.txs) < 5:
            self.txs.append(tx)


class RawTransfer:
    __slots__ = ("tx", "frm", "to", "asset", "amount", "ts")

    def __init__(self, tx, frm, to, asset, amount, ts):
        self.tx, self.frm, self.to, self.asset, self.amount, self.ts = tx, frm, to, asset, amount, ts


# --------------------------------------------------------------------- clients
class TronClient:
    chain = "tron"
    base = "https://api.trongrid.io"

    def __init__(self, http: httpx.AsyncClient, api_key: str = ""):
        self.http = http
        self.headers = {"TRON-PRO-API-KEY": api_key} if api_key else {}

    async def _get(self, path: str, params: dict) -> dict:
        for attempt in range(5):
            r = await self.http.get(self.base + path, params=params, headers=self.headers)
            if r.status_code in (401, 403) and self.headers:
                # key not valid for TronGrid (e.g. a Tronscan key) -> fall back to keyless
                self.headers = {}
                continue
            if r.status_code in (429, 503):
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()
        return {}

    async def outgoing(self, addr: str) -> list[RawTransfer]:
        d = await self._get(f"/v1/accounts/{addr}/transactions/trc20",
                            {"limit": 200, "only_from": "true", "order_by": "block_timestamp,desc"})
        out = []
        for tx in d.get("data", []):
            ti = tx.get("token_info", {})
            dec = int(ti.get("decimals", 6) or 6)
            val = Decimal(tx.get("value", 0) or 0) / Decimal(10 ** dec)
            if val > 1_000_000_000_000:
                continue
            out.append(RawTransfer(
                tx.get("transaction_id", ""), tx.get("from", ""), tx.get("to", ""),
                ti.get("symbol", "TRC20"), val,
                datetime.fromtimestamp(int(tx.get("block_timestamp", 0)) / 1000, tz=timezone.utc)))
        return out

    async def inbound_degree(self, addr: str) -> tuple[int, bool]:
        d = await self._get(f"/v1/accounts/{addr}/transactions/trc20",
                            {"limit": 200, "only_to": "true"})
        rows = d.get("data", [])
        return len({t.get("from") for t in rows}), len(rows) >= 200

    async def label(self, addr: str) -> tuple[str, str]:
        headers = self.headers.copy()
        if "TRON-PRO-API-KEY" not in headers or not headers["TRON-PRO-API-KEY"]:
            headers["TRON-PRO-API-KEY"] = "18c5f8a5-f476-4454-b755-760ca190e265"
        for attempt in range(3):
            try:
                r = await self.http.get(
                    f"https://apilist.tronscanapi.com/api/accountv2?address={addr}",
                    headers=headers
                )
                if r.status_code == 200:
                    d = r.json()
                    name = d.get("name") or ""
                    tags = []
                    if d.get("redTag"): tags.append(d.get("redTag"))
                    if d.get("greyTag"): tags.append(d.get("greyTag"))
                    if d.get("blueTag"): tags.append(d.get("blueTag"))
                    text = " | ".join(t for t in [name] + tags if t)
                    return (name or text.split(" | ")[0] if text else ""), text
            except Exception:
                pass
            await asyncio.sleep(1.0)
        return "", ""


class EthClient:
    chain = "ethereum"
    base = "https://eth.blockscout.com/api/v2"

    def __init__(self, http: httpx.AsyncClient):
        self.http = http
        self._tags: dict[str, tuple[str, str]] = {}

    async def _get(self, path: str, params: dict | None = None) -> dict:
        for attempt in range(4):
            r = await self.http.get(self.base + path, params=params)
            if r.status_code in (429, 503):
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            if r.status_code == 404:
                return {}
            r.raise_for_status()
            return r.json()
        return {}

    def _note(self, party: dict) -> None:
        h = (party.get("hash") or "").lower()
        if not h:
            return
        tags = (party.get("metadata") or {}).get("tags") or []
        names = [t.get("name") or "" for t in tags]
        entity = next((((t.get("meta") or {}).get("main_entity")) for t in tags
                       if (t.get("meta") or {}).get("main_entity")), "")
        text = " | ".join(n for n in names + [party.get("name") or "", party.get("ens_domain_name") or ""] if n)
        if party.get("is_scam"):
            text += " | scam"
        self._tags[h] = (entity or (names[0] if names else party.get("name") or ""), text)

    async def outgoing(self, addr: str) -> list[RawTransfer]:
        out: list[RawTransfer] = []
        tt = await self._get(f"/addresses/{addr}/token-transfers", {"type": "ERC-20", "filter": "from"})
        for it in tt.get("items", []):
            self._note(it.get("from") or {})
            self._note(it.get("to") or {})
            tok = it.get("token") or {}
            dec = int(tok.get("decimals") or 18)
            val = Decimal((it.get("total") or {}).get("value") or 0) / Decimal(10 ** dec)
            out.append(RawTransfer(it.get("transaction_hash", ""), (it["from"]["hash"]).lower(),
                                   (it["to"]["hash"]).lower(), tok.get("symbol") or "ERC20", val,
                                   datetime.fromisoformat(it["timestamp"].replace("Z", "+00:00"))))
        tx = await self._get(f"/addresses/{addr}/transactions", {"filter": "from"})
        for it in tx.get("items", []):
            v = Decimal(it.get("value") or 0) / Decimal(10 ** 18)
            if v <= 0 or not it.get("to"):
                continue
            self._note(it.get("from") or {})
            self._note(it.get("to") or {})
            out.append(RawTransfer(it.get("hash", ""), it["from"]["hash"].lower(), it["to"]["hash"].lower(),
                                   "ETH", v, datetime.fromisoformat(it["timestamp"].replace("Z", "+00:00"))))
        return out

    async def inbound_degree(self, addr: str) -> tuple[int, bool]:
        d = await self._get(f"/addresses/{addr}/token-transfers", {"type": "ERC-20", "filter": "to"})
        items = d.get("items", [])
        return len({(i.get("from") or {}).get("hash") for i in items}), bool(d.get("next_page_params"))

    async def label(self, addr: str) -> tuple[str, str]:
        a = addr.lower()
        if a not in self._tags:
            info = await self._get(f"/addresses/{addr}")
            if info:
                self._note({**info, "hash": addr})
        return self._tags.get(a, ("", ""))


# ---------------------------------------------------------------- attribution
async def attribute(node: Node, client, check_degree: bool) -> None:
    key = node.addr.lower() if node.addr.startswith("0x") else node.addr
    row = CSV_LABELS.get(key)
    if row:
        node.label = row.get("entity", "")
        node.kind = _kind_from_text(f"{row.get('entity','')} {row.get('entity_type','')}") or (
            "SANCTIONED" if "sanction" in row.get("entity_type", "") else "UNKNOWN")
        node.tier = "CONFIRMED"
        node.evidence.append(f"Exact match in label file ({row.get('source','')}, retrieved {row.get('retrieved_at','?')})")
        node.is_exit = node.kind != "ATTACKER"
        return

    entity, text = await client.label(node.addr)
    if text:
        kind = _kind_from_text(text)
        if kind:
            node.label, node.kind, node.tier = entity or text.split("|")[0].strip(), kind, "CONFIRMED"
            node.evidence.append(f"Public explorer tag: {text}")
            if kind == "ATTACKER":
                node.evidence.append("Known attacker/scam-tagged wallet: not a cash-out; tracing continues through it.")
            node.is_exit = kind != "ATTACKER"
            return

    if check_degree:
        peers, saturated = await client.inbound_degree(node.addr)
        node.distinct_peers = peers
        if peers >= SERVICE_DEGREE or (saturated and peers >= SERVICE_DEGREE // 2):
            node.kind, node.tier = "SERVICE_SUSPECTED", "POSSIBLE"
            node.label = "Suspected service / exchange deposit-or-hot wallet"
            node.evidence.append(f"Receives from {peers}{'+' if saturated else ''} distinct senders (>= {SERVICE_DEGREE}); "
                                 "structurally behaves like an aggregation wallet. No public tag, so NOT confirmed.")
            node.is_exit = True


# ---------------------------------------------------------------------- trace
async def trace_forward(seed: str, chain: str, *, max_depth: int = 6, max_nodes: int = 120,
                        branch: int = 6, min_usd: float = 100.0,
                        budget_s: float = 100.0, tron_api_key: str = "") -> dict[str, Any]:
    """Best-first forward trace.

    Each level expands the `branch*2` highest-value unexplored addresses. Branches are ranked by
    approximate USD value moved (ranking only). Stops at confirmed/suspected exits, bridges, mixers
    and DEX routers (value leaves the traceable path there).
    """
    chain = chain.lower()
    t0 = time.time()
    async with httpx.AsyncClient(timeout=20.0) as http:
        if chain in ("tron", "trc20"):
            client: Any = TronClient(http, tron_api_key)
        elif chain in ("ethereum", "eth", "erc20"):
            client = EthClient(http)
            seed = seed.lower()
        else:
            return {"supported": False, "reason": f"Live tracing for '{chain}' is not implemented yet."}

        nodes: dict[str, Node] = {seed: Node(seed, 0)}
        nodes[seed].taint = 1.0
        usd_in: dict[str, float] = defaultdict(float)
        edges: dict[tuple[str, str, str], Edge] = {}
        all_transfers: list[RawTransfer] = []
        expanded_set: set[str] = set()
        frontier = [seed]
        notes: list[str] = []

        for depth in range(max_depth):
            cand: list[str] = []
            for addr in frontier:
                if time.time() - t0 > budget_s:
                    notes.append("Time budget reached; trace is partial - use 'Trace Forward from Here' to continue.")
                    break
                node = nodes[addr]
                try:
                    out = await client.outgoing(addr)
                except Exception as e:  # network / rate limit
                    notes.append(f"Could not fetch {addr[:10]}…: {type(e).__name__}")
                    continue
                expanded_set.add(addr)
                out = [t for t in out if t.to and t.to != addr and approx_usd(t.asset, t.amount) >= min_usd]
                all_transfers.extend(out)
                if out:
                    node.first_seen = min(t.ts for t in out)
                    node.last_seen = max(t.ts for t in out)
                per_dst: dict[str, float] = defaultdict(float)
                for t in out:
                    e = edges.setdefault((t.frm, t.to, t.asset), Edge(t.frm, t.to, t.asset))
                    e.add(t.amount, t.ts, t.tx)
                    per_dst[t.to] += approx_usd(t.asset, t.amount)
                total_out = sum(per_dst.values()) or 1.0
                for dst, usd in sorted(per_dst.items(), key=lambda kv: kv[1], reverse=True)[:branch * 3]:
                    n = nodes.get(dst)
                    if n is None:
                        if len(nodes) >= max_nodes:
                            continue
                        n = nodes[dst] = Node(dst, depth + 1)
                    n.taint = min(1.0, max(n.taint, node.taint * (usd / total_out)))
                    usd_in[dst] += usd
                    if dst not in expanded_set and dst not in cand:
                        cand.append(dst)
            # Label everything newly reached (tags arrive free with the transfer payloads on ETH).
            keep = []
            for addr in cand:
                if time.time() - t0 > budget_s:
                    break
                n = nodes[addr]
                if not n.evidence and not n.is_exit:
                    try:
                        await attribute(n, client, check_degree=depth + 1 < max_depth)
                    except Exception as e:
                        notes.append(f"Attribution failed for {addr[:10]}…: {type(e).__name__}")
                if not n.is_exit:
                    keep.append(addr)
            frontier = sorted(keep, key=lambda a: usd_in[a], reverse=True)[:branch * 2]
            if not frontier:
                break


        for a, n in nodes.items():
            if n.kind == "UNKNOWN" and a != seed and not n.evidence and time.time() - t0 < budget_s:
                try:
                    await attribute(n, client, check_degree=False)
                except Exception:
                    pass

    return {
        "supported": True, "seed": seed, "chain": chain, "nodes": nodes, "edges": edges,
        "transfers": all_transfers, "expanded": len(expanded_set), "notes": notes,
        "elapsed_s": round(time.time() - t0, 1),
    }
