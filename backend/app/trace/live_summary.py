"""Turn a live_tracer result into case fields + Cytoscape elements with full detail."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from app.ingest.normalize import Transfer

TIER_RANK = {"CONFIRMED": 3, "PROBABLE": 2, "POSSIBLE": 1, "UNATTRIBUTED": 0}


def _short(a: str) -> str:
    return f"{a[:6]}…{a[-4:]}" if len(a) > 12 else a


def _fmt(x) -> str:
    return f"{float(x):,.2f}"


def _path(edges, seed: str, target: str) -> list[str]:
    adj = defaultdict(list)
    for (s, d, _), _e in edges.items():
        adj[s].append(d)
    prev = {seed: None}
    q = deque([seed])
    while q:
        u = q.popleft()
        if u == target:
            break
        for v in adj[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    if target not in prev:
        return []
    p, cur = [], target
    while cur is not None:
        p.append(cur)
        cur = prev[cur]
    return p[::-1]


def summarize(res: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, seed = res["nodes"], res["edges"], res["seed"]
    asset_of = {}
    for (_s, _d, a) in edges:
        asset_of.setdefault(a, 0)

    out_map, in_map = defaultdict(list), defaultdict(list)
    for (s, d, a), e in edges.items():
        out_map[s].append((d, a, e))
        in_map[d].append((s, a, e))

    # ---- fan-out / fan-in with exact addresses
    fan_outs, fan_ins = [], []
    for a, outs in out_map.items():
        if len(outs) >= 3:
            fan_outs.append({
                "address": a,
                "split_count": len(outs),
                "targets": [{"address": d, "amount": f"{_fmt(e.total)} {asset}", "tx_count": e.count,
                             "first_tx": e.txs[0] if e.txs else ""} for d, asset, e in
                            sorted(outs, key=lambda x: x[2].total, reverse=True)[:15]],
            })
    for a, ins in in_map.items():
        if len(ins) >= 3:
            fan_ins.append({
                "address": a,
                "merge_count": len(ins),
                "sources": [{"address": s, "amount": f"{_fmt(e.total)} {asset}", "tx_count": e.count,
                             "first_tx": e.txs[0] if e.txs else ""} for s, asset, e in
                            sorted(ins, key=lambda x: x[2].total, reverse=True)[:15]],
            })

    # ---- other pattern detectors from the real engine
    patterns: list[dict] = []
    try:
        from app.patterns.registry import PatternRegistry
        tr = [Transfer(chain=res["chain"], tx_hash=t.tx, ts=t.ts.replace(tzinfo=None), from_addr=t.frm,
                       to_addr=t.to, asset=t.asset, amount=t.amount, kind="token", block=0)
              for t in res["transfers"]]
        raw = PatternRegistry().detect_all(tr)
        grouped: dict[str, list[dict]] = defaultdict(list)
        for p in raw:
            grouped[p["pattern"]].append(p)
        for name, items in grouped.items():
            items.sort(key=lambda p: p.get("score", 0), reverse=True)
            best = items[0]
            patterns.append({
                "pattern": name, "instances": len(items), "score": best.get("score", 0),
                "evidence_tx_refs": best.get("evidence_tx_refs", [])[:5],
                "false_positive_note": best.get("false_positive_note", ""),
            })
    except Exception as e:  # never let pattern engine kill the case
        res["notes"].append(f"pattern engine error: {type(e).__name__}")

    # ---- exits with explicit paths
    exits = []
    for a, n in nodes.items():
        if not n.is_exit or a == seed:
            continue
        received = sum(e.total for _s, _asset, e in in_map.get(a, []))
        asset = next((asset for _s, asset, _e in in_map.get(a, [])), "")
        path = _path(edges, seed, a)
        exits.append({
            "address": a, "entity": n.label, "type": n.kind, "tier": n.tier, "taint": round(n.taint, 3),
            "received": f"{_fmt(received)} {asset}", "hops": max(len(path) - 1, 0), "path": path,
            "evidence": n.evidence,
            "deposit_address": path[-2] if len(path) >= 2 else "",
        })
    exits.sort(key=lambda x: (TIER_RANK[x["tier"]], x["taint"]), reverse=True)

    # ---- graph elements
    elements = []
    for a, n in nodes.items():
        role = "victim" if a == seed else ("exchange" if n.kind == "VASP" else "mixer" if n.kind == "MIXER"
                                           else "exchange" if n.kind == "SERVICE_SUSPECTED" else "intermediary")
        elements.append({"data": {
            "id": a, "label": (n.label.split(":")[0][:22] + "\n" if n.label else "") + _short(a),
            "role": role, "taint": round(n.taint, 3) or 0.1, "type": "exchange" if role == "exchange" else
            "mixer" if role == "mixer" else "wallet", "tier": n.tier, "kind": n.kind,
            "evidence": n.evidence, "full_address": a,
            "depth": n.depth, "distinct_peers": n.distinct_peers}})
    for (s, d, asset), e in edges.items():
        elements.append({"data": {
            "source": s, "target": d, "amount": f"{_fmt(e.total)} {asset}", "count": e.count,
            "first_ts": e.first.isoformat() if e.first else "", "last_ts": e.last.isoformat() if e.last else "",
            "txs": e.txs}})

    # ---- timeline (real timestamps)
    events = sorted(((e.first, s, d, asset, e) for (s, d, asset), e in edges.items() if e.first), key=lambda x: x[0])
    timeline = {}
    for i, (ts, s, d, asset, e) in enumerate(events[:12], 1):
        timeline[f"{ts:%Y-%m-%d %H:%M} UTC · hop {i}"] = f"{_short(s)} → {_short(d)}: {_fmt(e.total)} {asset} ({e.count} tx)"

    # ---- complete hop-by-hop ledger (every transfer edge, full detail)
    def _node_info(a: str) -> dict:
        n = nodes.get(a)
        return {"label": (n.label if n else "") or "", "kind": (n.kind if n else "UNKNOWN"),
                "tier": (n.tier if n else "UNATTRIBUTED")}

    dist = {seed: 0}
    _q = deque([seed])
    _adj = defaultdict(list)
    for (s_, d_, _a), _e in edges.items():
        _adj[s_].append(d_)
    while _q:
        u = _q.popleft()
        for v in _adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                _q.append(v)

    hops = []
    for (s, d, asset), e in edges.items():
        hops.append({
            "hop": dist.get(d, 0),
            "from": s, "to": d, "asset": asset,
            "amount": _fmt(e.total), "amount_raw": float(e.total), "tx_count": e.count,
            "first_ts": e.first.strftime("%Y-%m-%d %H:%M:%S") if e.first else "",
            "last_ts": e.last.strftime("%Y-%m-%d %H:%M:%S") if e.last else "",
            "txs": list(e.txs)[:10],
            "from_info": _node_info(s), "to_info": _node_info(d),
        })
    hops.sort(key=lambda h: (h["hop"], h["first_ts"], h["from"]))

    top = exits[0] if exits else None
    return {
        "elements": elements, "exits": exits, "fan_outs": fan_outs, "fan_ins": fan_ins, "hops": hops,
        "patterns": patterns, "timeline": timeline,
        "top_exit": top,
        "stats": {"nodes": len(nodes), "edges": len(edges), "transfers": len(res["transfers"]),
                  "expanded": res["expanded"], "elapsed_s": res["elapsed_s"]},
        "notes": res["notes"],
    }
