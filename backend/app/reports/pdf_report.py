"""Evidence-focused PDF report: every hop, fan-out/fan-in, exit path - full addresses, amounts, tx hashes, timestamps."""
from __future__ import annotations

import datetime
import hashlib
import io
import json
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

NAVY = colors.HexColor("#0f172a")
BLUE = colors.HexColor("#1d4ed8")
GREY = colors.HexColor("#e2e8f0")
LIGHT = colors.HexColor("#f8fafc")
RED = colors.HexColor("#b91c1c")

PAGE = landscape(A4)
USABLE = PAGE[0] - 24 * mm  # 12mm margins


def _styles():
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=ss["Title"], textColor=NAVY, fontSize=18, alignment=0, spaceAfter=2),
        "sub": ParagraphStyle("s", parent=ss["Normal"], textColor=colors.grey, fontSize=8, spaceAfter=6),
        "h1": ParagraphStyle("h1", parent=ss["Heading1"], textColor=BLUE, fontSize=12, spaceBefore=10, spaceAfter=4),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], textColor=NAVY, fontSize=9.5, spaceBefore=6, spaceAfter=3),
        "body": ParagraphStyle("b", parent=ss["BodyText"], fontSize=8.5, leading=11),
        "cell": ParagraphStyle("c", parent=ss["BodyText"], fontSize=7.5, leading=9.2),
        "head": ParagraphStyle("hd", parent=ss["BodyText"], fontSize=7.5, leading=9, textColor=NAVY, fontName="Helvetica-Bold"),
        "mono": ParagraphStyle("m", parent=ss["Code"], fontSize=6.6, leading=8.2),
        "note": ParagraphStyle("n", parent=ss["BodyText"], fontSize=7.5, leading=9.5, textColor=RED),
    }


def _esc(v: Any) -> str:
    s = "-" if v is None or v == "" else str(v)
    s = s.replace("₹", "Rs.").replace("—", "-").replace("–", "-").replace("→", "->").replace("…", "...")
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _tbl(header, rows, widths, st, mono=()):
    data = [[Paragraph(_esc(h), st["head"]) for h in header]]
    for r in rows:
        data.append([Paragraph(_esc(c), st["mono"] if i in mono else st["cell"]) for i, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (-1, 0), GREY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def _kv(rows, st, w1=48 * mm):
    t = Table([[Paragraph(_esc(k), st["head"]), Paragraph(_esc(v), st["cell"])] for k, v in rows],
              colWidths=[w1, USABLE - w1])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), GREY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _who(addr: str, info: dict | None) -> str:
    """Full address plus label/tier when known."""
    if info and (info.get("label") or info.get("tier") not in (None, "UNATTRIBUTED")):
        tag = f"{info.get('label') or info.get('kind')} [{info.get('tier')}]"
        return f"{addr}\n{tag}"
    return addr


def build_case_pdf(case: Any, graph: dict, generated_by: str = "ChainNetra") -> bytes:
    st = _styles()
    now_s = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    chain = (getattr(case, "chain", "") or "").lower()
    asset = getattr(case, "asset", "") or ""
    ts = getattr(case, "trace_summary", None) or {}
    exits = ts.get("exits", [])
    fan_outs, fan_ins = ts.get("fan_outs", []), ts.get("fan_ins", [])
    patterns = ts.get("patterns", [])
    stats = ts.get("stats", {})
    elements = (graph or {}).get("elements", [])
    nodes = [e["data"] for e in elements if "source" not in e.get("data", {})]
    edges = [e["data"] for e in elements if "source" in e.get("data", {})]
    hops = ts.get("hops")
    if not hops:  # fallback for cases without a stored ledger (demo data)
        hops = [{"hop": "", "from": e["source"], "to": e["target"], "asset": asset, "amount": e.get("amount", ""),
                 "tx_count": e.get("count", ""), "first_ts": (e.get("first_ts") or "")[:19].replace("T", " "),
                 "last_ts": (e.get("last_ts") or "")[:19].replace("T", " "), "txs": e.get("txs") or [],
                 "from_info": None, "to_info": None} for e in edges]
    info_by_addr = {(n.get("full_address") or n.get("id")): {"label": (n.get("label") or "").split("\n")[0],
                    "kind": n.get("kind"), "tier": n.get("tier")} for n in nodes}

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=PAGE, leftMargin=12 * mm, rightMargin=12 * mm, topMargin=12 * mm,
                            bottomMargin=14 * mm, title=f"ChainNetra Trace Report {case.id}", author=generated_by)

    def footer(c, d):
        c.saveState()
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(12 * mm, 7 * mm, f"ChainNetra - {case.id} - {now_s}")
        c.drawRightString(PAGE[0] - 12 * mm, 7 * mm, f"Page {d.page}")
        c.restoreState()

    s: list = [Paragraph("Fund Trace Report", st["title"]),
               Paragraph(_esc(f"{case.id}  |  {case.title}  |  generated {now_s}"), st["sub"])]

    # ---- summary
    top = exits[0] if exits else {}
    s.append(_kv([
        ("Chain / asset", f"{chain.upper()} / {asset}"),
        ("Seed address", getattr(case, "seed_address", "") or "not supplied"),
        ("Amount at risk (as entered)", f"{case.amount_at_risk:,.2f} {asset}" if case.amount_at_risk else "not entered"),
        ("Destination found", f"{case.exit_entity} - {case.exit_type} - {case.attribution_tier}"),
        ("Trace size", f"{len(hops)} transfer edges, {len(nodes)} addresses, {stats.get('transfers', len(hops))} raw transfers"
                       + (f", {top.get('hops')} hop(s) to destination" if top else "")),
    ], st))

    # ---- exits
    s.append(Paragraph("1. Destination / cash-out", st["h1"]))
    if not exits:
        s.append(Paragraph("No labelled destination found within the trace depth. Funds may still be moving.", st["body"]))
    for i, ex in enumerate(exits, 1):
        s.append(Paragraph(_esc(f"Destination {i}: {ex.get('entity') or 'Unlabelled'} ({ex.get('type')}, {ex.get('tier')})"), st["h2"]))
        s.append(_kv([
            ("Address", ex.get("address")),
            ("Received (total)", ex.get("received")),
            ("Taint at destination", f"{float(ex.get('taint', 0)) * 100:.1f}%"),
            ("Last-hop (deposit) address", ex.get("deposit_address") or "-"),
            ("Why it is attributed", "; ".join(ex.get("evidence", []) or []) or "-"),
        ], st))
        if ex.get("path"):
            s.append(Spacer(1, 3))
            s.append(_tbl(["Step", "Address on the path from seed", "Label"],
                          [[n, a, (info_by_addr.get(a) or {}).get("label", "")] for n, a in enumerate(ex["path"])],
                          [14 * mm, 150 * mm, USABLE - 164 * mm], st, mono=(1,)))

    # ---- hop ledger
    s.append(Paragraph("2. Hop-by-hop transfers (every edge traced)", st["h1"]))
    rows = []
    for n, h in enumerate(hops, 1):
        when = h["first_ts"] if h["first_ts"] == h["last_ts"] or not h["last_ts"] else f"{h['first_ts']}\n-> {h['last_ts']}"
        rows.append([n, h.get("hop", ""), _who(h["from"], h.get("from_info") or info_by_addr.get(h["from"])),
                     _who(h["to"], h.get("to_info") or info_by_addr.get(h["to"])),
                     f"{h['amount']} {h.get('asset', '')}", h.get("tx_count", ""), when,
                     "\n".join(h.get("txs") or []) or "no hash recorded"])
    w = [8 * mm, 9 * mm, 57 * mm, 57 * mm, 24 * mm, 8 * mm, 24 * mm]
    w.append(USABLE - sum(w))
    s.append(_tbl(["#", "Hop", "From", "To", "Amount", "Tx", "Time (UTC)", "Transaction hash(es)"], rows, w, st, mono=(2, 3, 7)))
    if any(not h.get("txs") for h in hops):
        s.append(Spacer(1, 3))
        s.append(Paragraph("Rows marked 'no hash recorded' come from seeded demo data, not from the blockchain.", st["note"]))

    # ---- fan-out / fan-in
    s.append(Paragraph("3. Fan-out points (one address splitting to many)", st["h1"]))
    if not fan_outs:
        s.append(Paragraph("None: no address in the trace sent to 3 or more recipients.", st["body"]))
    for fo in fan_outs:
        s.append(Paragraph(_esc(f"{fo['address']}  ->  {fo['split_count']} recipients"), st["h2"]))
        s.append(_tbl(["Recipient", "Amount", "Tx count", "First tx hash"],
                      [[t["address"], t["amount"], t["tx_count"], t.get("first_tx", "")] for t in fo["targets"]],
                      [90 * mm, 40 * mm, 18 * mm, USABLE - 148 * mm], st, mono=(0, 3)))
    s.append(Paragraph("4. Fan-in points (many addresses merging into one)", st["h1"]))
    if not fan_ins:
        s.append(Paragraph("None: no address in the trace received from 3 or more senders.", st["body"]))
    for fi in fan_ins:
        s.append(Paragraph(_esc(f"{fi['merge_count']} senders  ->  {fi['address']}"), st["h2"]))
        s.append(_tbl(["Sender", "Amount", "Tx count", "First tx hash"],
                      [[t["address"], t["amount"], t["tx_count"], t.get("first_tx", "")] for t in fi["sources"]],
                      [90 * mm, 40 * mm, 18 * mm, USABLE - 148 * mm], st, mono=(0, 3)))

    # ---- patterns
    s.append(Paragraph("5. Laundering patterns detected", st["h1"]))
    if patterns:
        s.append(_tbl(["Pattern", "Instances", "Score", "Evidence tx", "Possible innocent explanation"],
                      [[p.get("pattern"), p.get("instances"), p.get("score"), "\n".join(p.get("evidence_tx_refs", [])[:5]),
                        p.get("false_positive_note")] for p in patterns],
                      [32 * mm, 18 * mm, 14 * mm, 110 * mm, USABLE - 174 * mm], st, mono=(3,)))
    else:
        s.append(Paragraph("No pattern detectors fired on this trace.", st["body"]))

    # ---- labelled addresses only
    labelled = [(a, i) for a, i in info_by_addr.items() if i.get("tier") not in (None, "UNATTRIBUTED") or i.get("label")]
    s.append(Paragraph("6. Labelled addresses in the trace", st["h1"]))
    if labelled:
        evid = {(n.get("full_address") or n.get("id")): n.get("evidence") for n in nodes}
        s.append(_tbl(["Address", "Entity", "Type", "Tier", "Source / evidence"],
                      [[a, i.get("label"), i.get("kind"), i.get("tier"),
                        "; ".join(evid.get(a) or []) if isinstance(evid.get(a), list) else (evid.get(a) or "")]
                       for a, i in labelled],
                      [80 * mm, 45 * mm, 24 * mm, 24 * mm, USABLE - 173 * mm], st, mono=(0,)))
    else:
        s.append(Paragraph("No address in this trace matched a label source.", st["body"]))

    # ---- integrity
    digest = hashlib.sha256(json.dumps({"case": case.model_dump(mode="json") if hasattr(case, "model_dump") else str(case),
                                        "graph": graph}, sort_keys=True, default=str).encode()).hexdigest()
    s.append(Spacer(1, 8))
    s.append(Paragraph(_esc(f"Data integrity: SHA-256 of case + graph = {digest}. Verify any hash on a block explorer. "
                            "Taint and ML scores are investigative estimates, not proof."), st["cell"]))
    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
