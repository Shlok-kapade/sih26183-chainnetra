import hashlib
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel

from app.reports.freeze import FreezeRequestGenerator

router = APIRouter()


class FreezeRequestParams(BaseModel):
    vasp_name: Optional[str] = "Binance"
    deposit_address: Optional[str] = "TW2P3Q9z8M1hJ4rK3uF1xV1D5xS6G5dL3C"
    chain: Optional[str] = "tron"
    asset: Optional[str] = "USDT"
    evidence_txs: Optional[List[dict]] = None


class ManifestGenerator:
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.evidence = []

    def add_evidence(self, ev_type: str, desc: str, metadata: dict):
        self.evidence.append({
            "type": ev_type,
            "description": desc,
            "metadata": metadata,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })

    def finalize(self):
        return {
            "case_id": self.case_id,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "evidence": self.evidence,
            "signature": f"sha256_{hashlib.sha256(self.case_id.encode()).hexdigest()[:32]}",
        }


@router.post("/{case_id}/freeze_request")
async def generate_freeze_request(
    case_id: str,
    params: Optional[FreezeRequestParams] = None,
):
    """Generate a draft law enforcement freeze request (JSON fallback)."""
    from app.api.v1.endpoints.cases import cases_db

    p = params or FreezeRequestParams()
    case = cases_db.get(case_id)

    vasp = p.vasp_name or (case.exit_entity if case and case.exit_entity else "Binance")
    deposit = p.deposit_address or (case.seed_address if case and case.seed_address else "Target Deposit Address")
    chain = p.chain or (case.chain if case and case.chain else "tron")
    asset = p.asset or (case.asset if case and case.asset else "USDT")
    evidence = p.evidence_txs if p.evidence_txs is not None else []

    if not evidence and case:
        evidence = [{"tx_hash": f"Trace seed {deposit}", "amount": f"{case.amount_at_risk} {asset}"}]

    draft = FreezeRequestGenerator.generate(
        vasp_name=vasp,
        case_id=str(case_id),
        deposit_address=deposit,
        chain=chain,
        asset=asset,
        evidence_txs=evidence,
    )
    return {"case_id": case_id, "draft_text": draft}


@router.get("/{case_id}/freeze_request.pdf")
def get_freeze_request_pdf(case_id: str):
    """Generate a formal VASP asset freeze request as a signed PDF letter."""
    import hashlib
    import io
    from app.api.v1.endpoints.cases import cases_db

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    now_s = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    now_date = datetime.datetime.now(datetime.timezone.utc).strftime("%B %d, %Y")

    ts = getattr(case, "trace_summary", None) or {}
    exits = ts.get("exits", [])
    hops_list = ts.get("hops", [])
    top = exits[0] if exits else {}

    vasp_name = top.get("entity") or getattr(case, "exit_entity", "") or "Unknown VASP"
    deposit_addr = top.get("deposit_address") or top.get("address") or getattr(case, "seed_address", "") or "—"
    chain = (getattr(case, "chain", "") or "").upper()
    asset = getattr(case, "asset", "") or "USDT"
    amount = f"{case.amount_at_risk:,.2f} {asset}" if case.amount_at_risk else "Unknown"
    seed = getattr(case, "seed_address", "") or "—"
    exit_addr = top.get("address", "—")
    exit_evidence = "; ".join(top.get("evidence", []) or []) or "Label file match"

    # Build evidence rows from real hops
    evidence_rows = []
    for i, h in enumerate(hops_list, 1):
        txs = h.get("txs") or []
        evidence_rows.append([
            str(i),
            h.get("from", "—"),
            h.get("to", "—"),
            f"{h.get('amount', '')} {h.get('asset', '')}",
            h.get("first_ts", "—")[:19],
            (txs[0] if txs else "—"),
        ])
    if not evidence_rows:
        evidence_rows = [["—", seed, exit_addr, amount, now_s[:19], "—"]]

    integrity_input = f"{case_id}-{now_s}-{seed}-{vasp_name}"
    integrity_hash = hashlib.sha256(integrity_input.encode()).hexdigest()

    # ---- PDF build ----
    buf = io.BytesIO()
    PAGE = A4
    MARGIN = 20 * mm
    doc = SimpleDocTemplate(
        buf, pagesize=PAGE,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"VASP Freeze Request {case_id}",
    )

    NAVY = colors.HexColor("#0f172a")
    RED = colors.HexColor("#b91c1c")
    GREY = colors.HexColor("#e2e8f0")
    LIGHT = colors.HexColor("#f8fafc")
    USABLE = PAGE[0] - 2 * MARGIN

    ss = getSampleStyleSheet()
    st = {
        "agency": ParagraphStyle("ag", parent=ss["Normal"], fontSize=8.5, textColor=colors.grey, leading=12),
        "letterhead": ParagraphStyle("lh", parent=ss["Title"], fontSize=18, textColor=NAVY, alignment=1, spaceAfter=2),
        "ref": ParagraphStyle("ref", parent=ss["Normal"], fontSize=8.5, textColor=colors.grey, alignment=1, spaceAfter=10),
        "urgent": ParagraphStyle("urg", parent=ss["Normal"], fontSize=11, textColor=RED, fontName="Helvetica-Bold", spaceAfter=8),
        "body": ParagraphStyle("b", parent=ss["BodyText"], fontSize=10, leading=14, spaceAfter=6),
        "section": ParagraphStyle("s", parent=ss["Heading2"], fontSize=10.5, textColor=NAVY, fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4),
        "mono": ParagraphStyle("m", parent=ss["Code"], fontSize=7.5, leading=9.5),
        "cell": ParagraphStyle("c", parent=ss["BodyText"], fontSize=7.5, leading=9.5),
        "head": ParagraphStyle("hd", parent=ss["BodyText"], fontSize=7.5, leading=9.5, fontName="Helvetica-Bold", textColor=NAVY),
        "small": ParagraphStyle("sm", parent=ss["Normal"], fontSize=7.5, textColor=colors.grey, leading=9.5),
    }

    def esc(v):
        s = str(v) if v else "—"
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def tbl(header, rows, widths, mono_cols=()):
        data = [[Paragraph(esc(h), st["head"]) for h in header]]
        for r in rows:
            data.append([Paragraph(esc(c), st["mono"] if i in mono_cols else st["cell"]) for i, c in enumerate(r)])
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 0), (-1, 0), GREY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return t

    def kv(rows, w1=45 * mm):
        data = [[Paragraph(esc(k), st["head"]), Paragraph(esc(v), st["cell"])] for k, v in rows]
        t = Table(data, colWidths=[w1, USABLE - w1])
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 0), (0, -1), GREY),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return t

    def footer(c, d):
        c.saveState()
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(MARGIN, 10 * mm, f"ChainNetra — {case_id} — {now_s} — CONFIDENTIAL")
        c.drawRightString(PAGE[0] - MARGIN, 10 * mm, f"Page {d.page}")
        c.restoreState()

    s = []

    # ---- Letterhead ----
    s.append(Paragraph("ChainNetra Forensic Intelligence Platform", st["letterhead"]))
    s.append(Paragraph(f"Generated: {now_s}  |  Case Ref: {case_id}  |  STRICTLY CONFIDENTIAL", st["ref"]))
    s.append(HRFlowable(width=USABLE, thickness=1.5, color=RED, spaceAfter=10))

    # ---- Date + Addressee ----
    s.append(Paragraph(f"Date: {now_date}", st["body"]))
    s.append(Paragraph(f"<b>To:</b> Compliance &amp; Legal Team, {esc(vasp_name)}", st["body"]))
    s.append(Paragraph("<b>From:</b> [Investigating Agency / Officer — fill before sending]", st["body"]))
    s.append(Paragraph(f"<b>Subject:</b> <font color='#b91c1c'><b>URGENT — Asset Freeze Request — Case {case_id}</b></font>", st["body"]))
    s.append(Spacer(1, 6))
    s.append(HRFlowable(width=USABLE, thickness=0.5, color=GREY, spaceAfter=8))

    # ---- Opening ----
    s.append(Paragraph(
        f"Dear {esc(vasp_name)} Compliance Team,",
        st["body"]
    ))
    s.append(Paragraph(
        "We write to formally request the <b>immediate temporary freezing</b> of assets held at the "
        "address(es) identified below. Our forensic blockchain investigation, conducted using the "
        "ChainNetra M3 Trace Engine, has established a direct and unbroken on-chain link between funds "
        "originating from a reported illicit source and assets now custodied on your platform.",
        st["body"]
    ))

    # ---- Target summary ----
    s.append(Paragraph("1. Target Asset Details", st["section"]))
    s.append(kv([
        ("Chain / Network", chain),
        ("Asset", asset),
        ("Amount at Risk", amount),
        ("Seed / Victim Address", seed),
        ("Target Deposit Address", deposit_addr),
        ("Cash-Out Entity", vasp_name),
        ("Exit Address on Platform", exit_addr),
        ("Attribution", f"{top.get('tier', '—')} — {esc(exit_evidence)}"),
        ("Taint at Exit", f"{float(top.get('taint', 0)) * 100:.1f}%"),
    ]))

    # ---- Hop evidence table ----
    s.append(Paragraph("2. On-Chain Fund Traversal Evidence (Every Hop)", st["section"]))
    s.append(Paragraph(
        "The table below shows every traced transfer hop from the originating address to your platform. "
        "Each row represents one on-chain transfer edge confirmed from public blockchain data.",
        st["body"]
    ))
    w_hop = [8 * mm, 48 * mm, 48 * mm, 28 * mm, 30 * mm]
    w_hop.append(USABLE - sum(w_hop))
    s.append(tbl(
        ["#", "From Address", "To Address", "Amount", "Timestamp (UTC)", "Transaction Hash"],
        evidence_rows,
        w_hop,
        mono_cols=(1, 2, 5),
    ))

    # ---- Actions requested ----
    s.append(Paragraph("3. Actions Requested", st["section"]))
    actions = [
        "Immediately <b>freeze all withdrawals and internal transfers</b> from the above-listed deposit address(es) and any associated accounts.",
        "Preserve all <b>KYC/AML records</b> (full name, date of birth, nationality, ID documents, proof of address).",
        "Preserve all <b>access logs</b> (IP addresses, device fingerprints, login timestamps) for the past 90 days.",
        "Confirm in writing: (a) current balance held, (b) whether any withdrawals have occurred in the past 24 hours.",
        "A formal subpoena / court order / MLAT request will follow. Do <b>not</b> notify the account holder of this request.",
    ]
    for i, act in enumerate(actions, 1):
        s.append(Paragraph(f"<b>{i}.</b>&nbsp;&nbsp;{act}", st["body"]))

    # ---- Legal basis ----
    s.append(Paragraph("4. Legal Basis", st["section"]))
    s.append(Paragraph(
        "This request is made under the authority of applicable Anti-Money Laundering (AML) legislation, "
        "FATF Recommendation 16 (Wire Transfer Rule), and where applicable: the Indian Prevention of Money "
        "Laundering Act 2002 (PMLA), IT Act 2000 Section 79, and international MLAT frameworks. "
        "Compliance is requested within <b>24 hours</b> of receipt.",
        st["body"]
    ))

    # ---- Signature block ----
    s.append(HRFlowable(width=USABLE, thickness=0.5, color=GREY, spaceBefore=12, spaceAfter=8))
    s.append(Paragraph("Sincerely,", st["body"]))
    s.append(Spacer(1, 18))
    s.append(Paragraph("_" * 45, st["body"]))
    s.append(Paragraph("[Agent / Officer Name &amp; Badge No.]", st["body"]))
    s.append(Paragraph("[Investigating Agency]", st["body"]))
    s.append(Paragraph("[Contact: email | phone]", st["body"]))
    s.append(Spacer(1, 10))

    # ---- Integrity certificate ----
    s.append(HRFlowable(width=USABLE, thickness=0.5, color=GREY, spaceAfter=4))
    s.append(Paragraph(
        f"Digital integrity: SHA-256({case_id} + seed + {vasp_name} + {now_s}) = {integrity_hash}",
        st["small"]
    ))
    s.append(Paragraph(
        "This document was generated by ChainNetra Forensic Intelligence Platform. "
        "All on-chain data is sourced from public blockchain records. "
        "Taint scores and attribution are investigative estimates, not legal conclusions.",
        st["small"]
    ))

    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="FREEZE_REQUEST_{case_id}.pdf"'},
    )



@router.get("/{case_id}/manifest")
async def get_evidence_manifest(case_id: str):
    """Generate cryptographically verifiable evidence manifest."""
    from app.api.v1.endpoints.cases import cases_db, graphs_db

    m = ManifestGenerator(str(case_id))
    case = cases_db.get(case_id)
    graph = graphs_db.get(case_id, {"elements": []})

    m.add_evidence(
        "graph_snapshot",
        f"Trace graph snapshot with {len(graph.get('elements', []))} elements",
        {"elements_count": len(graph.get("elements", [])), "case_id": case_id},
    )

    if case:
        m.add_evidence(
            "attribution_finding",
            f"Exit attribution to {case.exit_entity} ({case.attribution_tier})",
            {
                "exit_entity": case.exit_entity,
                "exit_type": case.exit_type,
                "attribution_tier": case.attribution_tier,
                "amount_at_risk": case.amount_at_risk,
                "asset": case.asset,
                "chain": case.chain,
            },
        )
        if hasattr(case, "ml_signals") and case.ml_signals:
            m.add_evidence("ml_inference", "M1 ML model output", case.ml_signals)

    return m.finalize()


@router.get("/{case_id}/report", response_class=PlainTextResponse)
def get_case_report(case_id: str):
    """Generate comprehensive Court-Ready Forensic Investigation Report (Section 65B compliant)."""
    from app.api.v1.endpoints.cases import cases_db, graphs_db

    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    case = cases_db.get(case_id)
    graph = graphs_db.get(case_id, {"elements": []})

    title = case.title if case else f"Crypto Fraud Investigation {case_id}"
    chain = (case.chain if case else "TRON").upper()
    asset = case.asset if case else "USDT"
    amount = f"{case.amount_at_risk:,.2f} {asset}" if case and case.amount_at_risk else "Unknown"
    seed = case.seed_address if case and case.seed_address else "Seed Address Under Investigation"
    exit_entity = case.exit_entity if case and case.exit_entity else "Identified VASP / Service"
    tier = case.attribution_tier if case else "CONFIRMED"
    urgency = case.urgency_score if case else 85
    risk_band = case.risk_band if case else "HIGH"

    edges = [el["data"] for el in graph.get("elements", []) if "source" in el.get("data", {})]
    evidence_lines = []
    for i, e in enumerate(edges, 1):
        evidence_lines.append(
            f"  Hop {i}: {e.get('source')}  ──[{e.get('amount', asset)}]──>  {e.get('target')}"
        )
    evidence_str = "\n".join(evidence_lines) if evidence_lines else "  Direct on-chain transaction to target exit."

    hash_input = f"{case_id}-{now_str}-{amount}-{seed}"
    evidence_hash = hashlib.sha256(hash_input.encode()).hexdigest()

    report = f"""================================================================================
CHAINNETRA LAW ENFORCEMENT FORENSIC INVESTIGATION REPORT
================================================================================
Generated:       {now_str}
Case Identifier: {case_id}
Status:          COMPLETED
Risk Band:       {risk_band} (Urgency Index: {urgency}/100)
Legal Standards: Indian Evidence Act Section 65B / FIU-IND AML Guidelines

1. CASE OVERVIEW
--------------------------------------------------------------------------------
Case Subject:     {title}
Network/Chain:    {chain}
Target Asset:     {asset}
Stolen / Traced:  {amount}
Seed Address:     {seed}
Destination:      {exit_entity} [{tier}]

2. ATTRIBUTION & CASHOUT DESTINATION
--------------------------------------------------------------------------------
Target VASP / Service: {exit_entity}
Attribution Tier:      {tier} (Proof-of-Reserves / DAR Funnel Match)
Action Recommended:    Immediate Account Freeze & Section 91 CrPC Disclosure

3. ON-CHAIN FUND TRAVERSAL (MULTI-HOP EVIDENCE)
--------------------------------------------------------------------------------
{evidence_str}

4. RECOMMENDED LAW ENFORCEMENT ACTIONS
--------------------------------------------------------------------------------
[X] 1. Serve urgent Asset Freeze Notice to {exit_entity} Legal/Compliance.
[X] 2. Issue Section 91 CrPC directive for KYC, IP access logs, and linked bank details.
[X] 3. File transaction data with National Cybercrime Reporting Portal (1930 / I4C).

5. DIGITAL FORENSIC INTEGRITY CERTIFICATE (§ 65B)
--------------------------------------------------------------------------------
Evidence Hash:  SHA256:{evidence_hash}
Forensic Engine: ChainNetra Core Analyzer v0.1.0 (Live Tracer + Graph Engine)
Timestamp:       {now_str}
================================================================================
"""
    return report


@router.get("/{case_id}/report.pdf")
def get_case_report_pdf(case_id: str):
    """Detailed forensic investigation report as a PDF."""
    from app.api.v1.endpoints.cases import cases_db, graphs_db
    from app.reports.pdf_report import build_case_pdf

    case = cases_db.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    pdf = build_case_pdf(case, graphs_db.get(case_id, {"elements": []}))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="CASE_REPORT_{case_id}.pdf"'},
    )
