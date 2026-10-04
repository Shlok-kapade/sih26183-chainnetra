"""Evaluation: trace recent Tether-frozen Tron addresses and list the cash-out candidates found.

Ground truth here = Tether froze the address (issuer judged it illicit). Flagged exits must then
be verified by hand on Tronscan. Usage (from backend/): .venv/bin/python ../scripts/eval_tether_frozen.py [N]
"""
import asyncio
import hashlib
import json
import sys

import httpx

from app.trace.live_summary import summarize
from app.trace.live_tracer import trace_forward

USDT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
ALPHA = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def hex_to_tron(h: str) -> str:
    raw = bytes.fromhex("41" + h.lower().replace("0x", ""))
    chk = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[:4]
    n = int.from_bytes(raw + chk, "big")
    s = ""
    while n:
        n, r = divmod(n, 58)
        s = ALPHA[r] + s
    return s


async def frozen(n: int) -> list[tuple[str, int]]:
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"https://api.trongrid.io/v1/contracts/{USDT}/events",
                        params={"event_name": "AddedBlackList", "limit": n, "order_by": "block_timestamp,desc"})
        return [(hex_to_tron(e["result"]["_user"]), e["block_timestamp"]) for e in r.json().get("data", [])]


async def main(n: int):
    rows = []
    for addr, ts in await frozen(n):
        try:
            res = await trace_forward(addr, "tron", max_depth=4, max_nodes=40, budget_s=45)
            s = summarize(res)
        except Exception as e:
            print(addr, "ERROR", type(e).__name__, e, flush=True)
            continue
        st = s["stats"]
        print(f"\n{addr}  edges={st['edges']} nodes={st['nodes']} transfers={st['transfers']}", flush=True)
        for e in s["exits"][:5]:
            print(f"   {e['tier']:9} {e['type']:17} hops={e['hops']} {e['received']:>22}  {e['address']}  [{e['entity']}]", flush=True)
        if not s["exits"]:
            print("   (no cash-out candidate within depth)", flush=True)
        rows.append({"seed": addr, "stats": st, "exits": s["exits"][:5]})
    json.dump(rows, open("/tmp/tether_eval.json", "w"), indent=1, default=str)


asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 10))
