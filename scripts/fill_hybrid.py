import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Palette (extracted from template) ─────────────────────────────────────────
NAVY   = RGBColor(0x0F, 0x17, 0x2A)
ORANGE = RGBColor(0xE0, 0x6C, 0x1B)
TEAL   = RGBColor(0x1D, 0x7A, 0x7A)
LBLUE  = RGBColor(0x1E, 0x3A, 0x5F)
LGREY  = RGBColor(0xF1, 0xF5, 0xF9)
MID    = RGBColor(0xE2, 0xE8, 0xF0)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
BLACK  = RGBColor(0x0F, 0x17, 0x2A)
GREEN  = RGBColor(0x16, 0xA3, 0x4A)

def rgb(r, g, b): return RGBColor(r, g, b)

def box(sl, x, y, w, h, fill=None, border=None, border_w=Pt(0.5)):
    shape = sl.shapes.add_shape(1, x, y, w, h)
    shape.line.fill.background()
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if border:
        shape.line.color.rgb = border
        shape.line.width = border_w
    else:
        shape.line.fill.background()
    return shape

def txbox(sl, text, x, y, w, h, size=11, bold=False, color=BLACK, align=PP_ALIGN.LEFT, bg=None, border=None, wrap=True, italic=False, border_w=Pt(0.5)):
    shape = sl.shapes.add_textbox(x, y, w, h)
    tf = shape.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    if bg:
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
    else:
        shape.fill.background()
    if border:
        shape.line.color.rgb = border
        shape.line.width = border_w
    else:
        shape.line.fill.background()
    return shape

def header_bar(sl, label, x=Inches(0.3), y=Inches(1.55), w=Inches(3.8), color=ORANGE):
    b = box(sl, x, y, w, Inches(0.22), fill=color)
    txbox(sl, label, x + Inches(0.07), y + Inches(0.01), w - Inches(0.1), Inches(0.2), size=7.5, bold=True, color=WHITE, bg=None)
    return b

def pill(sl, label, x=Inches(0.3), y=Inches(0.12), w=Inches(1.0), color=NAVY):
    b = box(sl, x, y, w, Inches(0.28), fill=color)
    txbox(sl, label, x + Inches(0.07), y + Inches(0.03), w - Inches(0.1), Inches(0.22), size=7.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

def slide_title(sl, title, subtitle=None):
    txbox(sl, title, Inches(1.55), Inches(0.06), Inches(10.0), Inches(0.72), size=30, bold=True, color=NAVY, align=PP_ALIGN.LEFT)
    if subtitle:
        txbox(sl, subtitle, Inches(1.55), Inches(0.78), Inches(10.5), Inches(0.3), size=11, bold=False, color=NAVY, align=PP_ALIGN.LEFT)

def sih_badge(sl):
    txbox(sl, "SMART INDIA\nHACKATHON\n2026", Inches(11.9), Inches(0.05), Inches(1.35), Inches(0.68), size=7.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

def footer(sl, page_num):
    box(sl, 0, Inches(7.5) - Inches(0.32), Inches(13.33), Inches(0.32), fill=LGREY)
    txbox(sl, f"SIH 2026  |  PS SIH26183  —  ChainNetra", Inches(0.2), Inches(7.5) - Inches(0.29), Inches(10), Inches(0.26), size=7.5, color=RGBColor(0x64, 0x74, 0x8B), align=PP_ALIGN.LEFT)
    txbox(sl, str(page_num), Inches(12.8), Inches(7.5) - Inches(0.29), Inches(0.4), Inches(0.26), size=9, bold=True, color=NAVY, align=PP_ALIGN.RIGHT)

def card(sl, title, body, x, y, w, h, title_color=ORANGE, bg=LGREY, border=MID):
    box(sl, x, y, w, h, fill=bg, border=border, border_w=Pt(0.4))
    txbox(sl, title, x + Inches(0.08), y + Inches(0.06), w - Inches(0.16), Inches(0.2), size=7.5, bold=True, color=title_color)
    txbox(sl, body, x + Inches(0.08), y + Inches(0.25), w - Inches(0.16), h - Inches(0.32), size=8, color=BLACK, wrap=True)

def numbered_card(sl, num, title, body, x, y, w, h, num_color=ORANGE, bg=LGREY):
    box(sl, x, y, w, h, fill=bg, border=MID, border_w=Pt(0.4))
    box(sl, x + Inches(0.08), y + Inches(0.08), Inches(0.25), Inches(0.25), fill=num_color)
    txbox(sl, num, x + Inches(0.08), y + Inches(0.08), Inches(0.25), Inches(0.25), size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txbox(sl, title, x + Inches(0.38), y + Inches(0.08), w - Inches(0.48), Inches(0.22), size=8, bold=True, color=NAVY)
    txbox(sl, body, x + Inches(0.08), y + Inches(0.33), w - Inches(0.16), h - Inches(0.42), size=7.5, color=BLACK, wrap=True)

def pipeline_step(sl, num, title, body, x, y, w=Inches(1.95), h=Inches(1.55)):
    box(sl, x, y, w, h, fill=WHITE, border=MID, border_w=Pt(0.5))
    box(sl, x, y, w, Inches(0.28), fill=LGREY)
    txbox(sl, f"  {num}  {title}", x + Inches(0.05), y + Inches(0.04), w - Inches(0.1), Inches(0.22), size=8, bold=True, color=ORANGE)
    txbox(sl, body, x + Inches(0.08), y + Inches(0.32), w - Inches(0.16), h - Inches(0.42), size=7.5, color=BLACK, wrap=True)

def tech_row(sl, label, value, x, y, w):
    box(sl, x, y, w * 0.35, Inches(0.24), fill=LGREY, border=MID, border_w=Pt(0.3))
    box(sl, x + w * 0.35, y, w * 0.65, Inches(0.24), fill=WHITE, border=MID, border_w=Pt(0.3))
    txbox(sl, label, x + Inches(0.05), y + Inches(0.03), w * 0.35 - Inches(0.1), Inches(0.2), size=8, bold=True, color=NAVY)
    txbox(sl, value, x + w * 0.35 + Inches(0.05), y + Inches(0.03), w * 0.65 - Inches(0.1), Inches(0.2), size=8, color=BLACK)

def flow_row(sl, items, x, y, w_total, h=Inches(0.22)):
    n = len(items)
    item_w = (w_total - Inches(0.15) * (n - 1)) / n
    for i, itm in enumerate(items):
        ix = x + i * (item_w + Inches(0.15))
        box(sl, ix, y, item_w, h, fill=LGREY, border=MID, border_w=Pt(0.3))
        txbox(sl, itm, ix + Inches(0.04), y + Inches(0.02), item_w - Inches(0.08), h - Inches(0.04), size=7, color=BLACK)
        if i < n - 1:
            txbox(sl, "▶", ix + item_w + Inches(0.03), y + Inches(0.03), Inches(0.1), Inches(0.18), size=7, color=ORANGE, align=PP_ALIGN.CENTER)

def clear_slide(sl):
    # Hide all existing shapes so we have a clean canvas from the template
    for shape in sl.shapes:
        try:
            # We can't always delete shapes easily in python-pptx, but we can clear text
            if shape.has_text_frame:
                shape.text = ""
            # Move shape off-screen to hide it
            shape.left = Inches(-20)
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════════════════

prs = Presentation("docs/SIH_2026_PPT_Template.pptx")
# Set slide dimensions to widescreen
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

# Delete Slide 7 if it exists
if len(prs.slides) > 6:
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    xml_slides.remove(slides[6])

# SLIDE 1 — Cover
s = prs.slides[0]
clear_slide(s)
txbox(s, "SMART INDIA HACKATHON 2026", Inches(0.3), Inches(0.05), Inches(10.5), Inches(0.85), size=36, bold=True, color=NAVY)
box(s, Inches(0.3), Inches(0.9), Inches(12.5), Inches(0.015), fill=MID)
sih_badge(s)

details = [
    ("Problem Statement ID", "SIH26183"),
    ("Problem Statement Title", "Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from\nVictim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics"),
    ("Theme", "Blockchain & Cybersecurity"),
    ("PS Category", "Software"),
    ("Organisation", "Ministry of Home Affairs"),
    ("Team ID", "26183"),
    ("Team Name", "code2trip"),
    ("Institute", "[Your Institute Name]"),
]
dy = Inches(1.05)
for label, val in details:
    txbox(s, label + "  –", Inches(0.35), dy, Inches(2.6), Inches(0.26), size=9.5, bold=True, color=ORANGE)
    txbox(s, val, Inches(2.9), dy, Inches(5.5), Inches(0.3), size=9.5, bold=False, color=BLACK, wrap=True)
    dy += Inches(0.32)

box(s, Inches(0.3), Inches(5.85), Inches(5.5), Inches(1.3), fill=WHITE, border=LGREY, border_w=Pt(1.5))
box(s, Inches(0.3), Inches(5.85), Inches(0.015), Inches(1.3), fill=ORANGE)
txbox(s, "OUR SOLUTION", Inches(0.42), Inches(5.9), Inches(5), Inches(0.22), size=7.5, bold=True, color=ORANGE)
txbox(s, "ChainNetra", Inches(0.42), Inches(6.12), Inches(5), Inches(0.45), size=22, bold=True, color=NAVY)
txbox(s, "A suspect wallet address goes in. The exchange that must receive\nthe freeze request comes out — with every hop and hash attached.", Inches(0.42), Inches(6.55), Inches(5), Inches(0.55), size=8.5, color=RGBColor(0x64, 0x74, 0x8B), wrap=True)

box(s, Inches(7.2), Inches(1.2), Inches(5.5), Inches(5.0), fill=LGREY)
txbox(s, "🔗  Victim Address\n          ↓\n   Blockchain Trace\n          ↓\n🏦  Exchange Identified\n          ↓\n📄  Freeze Request PDF", Inches(8.0), Inches(1.8), Inches(4.2), Inches(4.0), size=14, bold=False, color=NAVY, align=PP_ALIGN.CENTER)
footer(s, 1)

# SLIDE 2 — Proposed Solution
s = prs.slides[1]
clear_slide(s)
pill(s, "code2trip", w=Inches(1.1))
slide_title(s, "ChainNetra — Which Exchange Received the Money?", subtitle="A suspect wallet address goes in; the exchange that must receive the freeze request comes out, with the evidence attached.")
sih_badge(s)
header_bar(s, "PROPOSED SOLUTION · RETRIEVE → NORMALISE → TRACE → GRAPH+PATTERNS → ATTRIBUTE → REPORT", x=Inches(0.3), y=Inches(1.48), w=Inches(12.7), color=ORANGE)

steps = [
    ("01", "RETRIEVE",  "Pull transactions from TronGrid/Etherscan. Every raw reply SHA-256 hashed and time-stamped as evidence."),
    ("02", "NORMALISE", "TRON and Ethereum collapsed into one Transfer model — including internal transfers most tracers miss."),
    ("03", "TRACE",     "Follow money hop-by-hop. Each address gets only the victim's exact share — never more."),
    ("04", "GRAPH+PATTERNS", "Six detectors: splitting, pooling, fast layering, peel chain, fan-out, fan-in."),
    ("05", "ATTRIBUTE", "Name the exchange behind a deposit address — tier (CONFIRMED/PROBABLE) + full evidence chain."),
    ("06", "SCORE+REPORT", "19 risk signals ranked one-by-one. PDF case file with every transaction hash."),
]
step_w = Inches(2.08)
for i, (num, title, body) in enumerate(steps):
    pipeline_step(s, num, title, body, Inches(0.3) + i * (step_w + Inches(0.07)), Inches(1.72), w=step_w, h=Inches(1.5))

header_bar(s, "HOW IT ADDRESSES THE PROBLEM", x=Inches(0.3), y=Inches(3.35), w=Inches(4.4), color=TEAL)
problems = [
    ("An address names nobody.", "A bank account tells you the bank. A wallet address tells you nothing.\nChainNetra names the institution behind the deposit address."),
    ("Two or three hops, by hand.", "Money splits faster than a person can follow. ChainNetra expands every branch automatically."),
    ('"Probably Binance."', "A guess, with nothing behind it. ChainNetra returns CONFIRMED / PROBABLE / UNATTRIBUTED — never rounded up."),
    ("6–12 hours, usually 'unknown'.", "Long after the money has moved on. ChainNetra returns an evidenced answer from cached data in ~90 seconds."),
]
py = Inches(3.6)
ph = Inches(0.64)
for title, body in problems:
    box(s, Inches(0.3), py, Inches(4.4), ph, fill=WHITE, border=MID, border_w=Pt(0.4))
    txbox(s, title, Inches(0.4), py + Inches(0.04), Inches(4.1), Inches(0.2), size=8, bold=True, color=NAVY)
    txbox(s, body, Inches(0.4), py + Inches(0.22), Inches(4.1), ph - Inches(0.26), size=7.5, color=BLACK, wrap=True)
    py += ph + Inches(0.06)

header_bar(s, "INNOVATION AND UNIQUENESS OF THE SOLUTION", x=Inches(4.9), y=Inches(3.35), w=Inches(8.1), color=TEAL)
innovations = [
    ("01", "THREE TIERS THAT CANNOT BE MIXED UP", "The database itself rejects any claim that is not CONFIRMED, PROBABLE or UNATTRIBUTED."),
    ("02", "CONFIDENCE IS ONLY AS STRONG AS ITS WEAKEST LINK", "0.90 deposit × 0.80 exchange = 0.72. Never higher than that, never above 0.95."),
    ("03", "SEVEN NAMED REASONS A TRACE STOPS", '"We could not look further" is never reported as "the money stopped here".'),
    ("04", "EVERY DETECTOR LISTS ITS OWN FALSE ALARMS", "A detector that cannot name an innocent explanation is not allowed to run."),
]
iw = Inches(3.9)
for idx, (num, title, body) in enumerate(innovations):
    ix = Inches(4.9) + (idx % 2) * (iw + Inches(0.15))
    iy_off = Inches(3.6) + (idx // 2) * Inches(0.75)
    numbered_card(s, num, title, body, ix, iy_off, iw, Inches(0.72), num_color=ORANGE, bg=LGREY)

tier_y = Inches(7.5) - Inches(0.65)
for label, col in [("■ CONFIRMED", GREEN), ("■ PROBABLE", ORANGE), ("■ UNATTRIBUTED", RGBColor(0x94, 0xA3, 0xB8))]:
    txbox(s, label, Inches(0.3) if label.startswith("■ C") else (Inches(2.8) if label.startswith("■ P") else Inches(5.0)), tier_y, Inches(2.3), Inches(0.2), size=8, bold=False, color=col)
footer(s, 2)

# SLIDE 3 — Technical Approach
s = prs.slides[2]
clear_slide(s)
pill(s, "code2trip", w=Inches(1.1))
slide_title(s, "TECHNICAL APPROACH")
sih_badge(s)
header_bar(s, "METHODOLOGY AND PROCESS FOR IMPLEMENTATION", x=Inches(0.3), y=Inches(1.02), w=Inches(6.8), color=ORANGE)

flow_steps = [
    ("INPUT", "Suspect wallet address + chain + asset + reported amount — the victim's report is the anchor."),
    ("RETRIEVE &\nNORMALISE", "Rate-limited, retried, provider-switched. Every raw reply SHA-256 hashed. TRON/ETH → one Transfer model."),
    ("ANALYSE", "Taint engine (haircut, proportional). Five stop conditions. Six pattern detectors. DAR deposit-address score."),
    ("OUTPUT", "Exchange named with tier + evidence. 19 risk signals ranked. PDF freeze request with every hop hash."),
]
fy = Inches(1.28)
for i, (title, body) in enumerate(flow_steps):
    bx = Inches(0.3)
    by = fy + i * Inches(1.22)
    box(s, bx, by, Inches(6.8), Inches(1.15), fill=WHITE, border=MID, border_w=Pt(0.4))
    box(s, bx, by, Inches(1.5), Inches(1.15), fill=LGREY)
    txbox(s, title, bx + Inches(0.08), by + Inches(0.35), Inches(1.35), Inches(0.45), size=9, bold=True, color=NAVY)
    txbox(s, body, bx + Inches(1.62), by + Inches(0.1), Inches(5.0), Inches(0.95), size=8.5, color=BLACK, wrap=True)
    if i < len(flow_steps) - 1:
        txbox(s, "↓", bx + Inches(0.6), by + Inches(1.16), Inches(0.3), Inches(0.2), size=12, color=ORANGE, align=PP_ALIGN.CENTER)

header_bar(s, "TECHNOLOGIES USED", x=Inches(7.3), y=Inches(1.02), w=Inches(5.7), color=TEAL)
tech = [
    ("Frontend",     "React · TypeScript · Vite · Tailwind · Cytoscape.js"),
    ("Backend",      "Python 3.12 · FastAPI · SQLAlchemy · Pydantic"),
    ("Data",         "PostgreSQL 16"),
    ("Chain data",   "TronGrid · TronScan · Blockscout · Etherscan"),
    ("Analytics & AI", "NetworkX · LightGBM · SHAP (planned)"),
    ("Reports",      "ReportLab · pytest · Docker · Nginx"),
]
ty = Inches(1.28)
for label, val in tech:
    tech_row(s, label, val, Inches(7.3), ty, Inches(5.7))
    ty += Inches(0.27)

box(s, Inches(7.3), ty + Inches(0.1), Inches(5.7), Inches(3.0), fill=LGREY, border=MID, border_w=Pt(0.4))
txbox(s, "BUILT AND VERIFIED TODAY", Inches(7.42), ty + Inches(0.18), Inches(5.4), Inches(0.22), size=8.5, bold=True, color=NAVY)
built_items = [
    "Full pipeline runs: retrieval → tracing → graph → patterns → attribution → risk → PDF",
    "REST API with 28+ endpoints; React workspace with 7 tabs and live graph",
    "Hop-by-hop transfer table with full addresses, timestamps, clickable tx hashes",
    "VASP Freeze Request PDF with legal basis, evidence table, SHA-256 integrity hash",
    "OFAC-sanctioned address detection: CONFIRMED tier, exits highlighted red",
    "3 demo cases (BTC peel chain, ETH fan-out → Tornado Cash, TRON pig-butchering)",
    "Deployed via Docker Compose — EC2-ready with nginx reverse proxy",
    "Not claimed: ML classifier not yet trained; sign-in is single-factor",
]
bi_y = ty + Inches(0.44)
for item in built_items:
    txbox(s, "• " + item, Inches(7.42), bi_y, Inches(5.4), Inches(0.25), size=7.5, color=BLACK, wrap=False)
    bi_y += Inches(0.26)

ev_items = ["RAW RESPONSE\nstored, SHA-256", "TRANSFER\none canonical row", "TRACE EDGE\nwith its share", "ATTRIBUTION\ntier + evidence", "PDF APPENDIX\nhash + fetch time"]
flow_row(s, ev_items, Inches(0.3), Inches(7.5) - Inches(0.65), Inches(6.8))
footer(s, 3)

# SLIDE 4 — Feasibility & Viability
s = prs.slides[3]
clear_slide(s)
pill(s, "code2trip", w=Inches(1.1))
slide_title(s, "FEASIBILITY AND VIABILITY")
sih_badge(s)
header_bar(s, "ANALYSIS OF THE FEASIBILITY OF THE IDEA", x=Inches(0.3), y=Inches(1.02), w=Inches(12.7), color=ORANGE)
feasibility = [
    ("IT ALREADY RUNS", "A suspect address goes in; a named exchange, an itemised risk score and a PDF come out. All tests pass with no internet."),
    ("NO PAID DATA NEEDED", "Free public APIs and openly licensed datasets. No commercial forensics licence — which is why a district cyber cell could afford it."),
    ("ORDINARY DEPLOYMENT", "One server: Python, PostgreSQL, Docker + Nginx. No cluster, no GPU, no graph database. EC2 t3.medium is sufficient."),
    ("THE SAME ANSWER EVERY TIME", "Exact fractions, never floats. The same input gives the same answer — every claim traces back to a stored, hashed API reply."),
]
fw = Inches(3.05)
for i, (title, body) in enumerate(feasibility):
    fx = Inches(0.3) + i * (fw + Inches(0.1))
    card(s, title, body, fx, Inches(1.28), fw, Inches(1.3), title_color=ORANGE, bg=WHITE)

header_bar(s, "POTENTIAL CHALLENGES AND RISKS", x=Inches(0.3), y=Inches(2.75), w=Inches(6.0), color=TEAL)
header_bar(s, "STRATEGIES FOR OVERCOMING THESE CHALLENGES", x=Inches(6.6), y=Inches(2.75), w=Inches(6.4), color=TEAL)
challenges = [
    ("TRON's free API is slow.", "Half a req/sec per method; a cold 200-address trace takes ~400 seconds — not 120.", "We work to an address budget, not to hope. ~60 new addresses inside 120 seconds; anything short of complete comes back PARTIAL. Cached traces stay fast."),
    ("Public TRON labels are few and dirty.", "Of 151 published exchange addresses we checked, 9 were not even valid TRON addresses.", "We check every label on-chain ourselves. 94 of 151 survived. Each records its source, licence and the date we captured it."),
    ("A simple tracer cannot see internal transfers.", "On one sanctioned address, 173,600 ETH arrived where the ordinary transaction list showed nothing.", "We fetch and treat internal transfers like any other. Without that step a tracer misses 95.2% of the money."),
    ("A behaviour test raises false alarms.", "Payment processors, OTC desks and company sweep accounts all look like deposit addresses.", "Behaviour alone never gives CONFIRMED. A detector that cannot name an innocent explanation is not allowed to run."),
    ("A live demo depends on someone else's API.", "One rate-limit reply during a timed presentation ends the demo.", "Offline by default. Real chain data, captured and frozen, replayed from disk behind a visible 'cached snapshot' banner."),
]
cy = Inches(3.0)
ch = Inches(0.7)
for prob_title, prob_body, strat in challenges:
    box(s, Inches(0.3), cy, Inches(6.0), ch, fill=WHITE, border=MID, border_w=Pt(0.3))
    txbox(s, prob_title, Inches(0.4), cy + Inches(0.04), Inches(5.7), Inches(0.2), size=8, bold=True, color=NAVY)
    txbox(s, prob_body, Inches(0.4), cy + Inches(0.22), Inches(5.7), ch - Inches(0.26), size=7.5, color=BLACK, wrap=True)
    box(s, Inches(6.6), cy, Inches(6.4), ch, fill=LGREY, border=MID, border_w=Pt(0.3))
    txbox(s, strat, Inches(6.7), cy + Inches(0.08), Inches(6.1), ch - Inches(0.1), size=7.5, color=BLACK, wrap=True)
    cy += ch + Inches(0.05)

txbox(s, "Every figure above is our own measurement, taken on-chain and written up in the repository — not an estimate.", Inches(0.3), Inches(7.5) - Inches(0.65), Inches(12.7), Inches(0.2), size=7.5, italic=True, color=RGBColor(0x64, 0x74, 0x8B))
footer(s, 4)

# SLIDE 5 — Impact & Benefits
s = prs.slides[4]
clear_slide(s)
pill(s, "code2trip", w=Inches(1.1))
slide_title(s, "IMPACT AND BENEFITS")
sih_badge(s)
header_bar(s, "POTENTIAL IMPACT ON THE TARGET AUDIENCE", x=Inches(0.3), y=Inches(1.02), w=Inches(12.7), color=ORANGE)
stats = [
    ("22,68,346", "cybercrime incidents on NCRP in 2024, up 42% on 2023"),
    ("₹22,845.73 cr", "reported lost to cybercrime in 2024"),
    ("₹7,130 cr", "saved through CFCFRMS across 23.02 lakh complaints\n(MHA Lok Sabha Unstarred Q.432, 2 Dec 2025)"),
]
sw = Inches(4.1)
for i, (num, label) in enumerate(stats):
    sx = Inches(0.3) + i * (sw + Inches(0.15))
    txbox(s, num, sx, Inches(1.28), sw, Inches(0.4), size=20, bold=True, color=NAVY)
    txbox(s, label, sx, Inches(1.68), sw, Inches(0.35), size=8, color=BLACK, wrap=True)

users = [
    ("PRIMARY USER", "DISTRICT / STATE CYBER CELL INVESTIGATOR", "Not a blockchain expert. Types in the address the victim reported and gets back a named institution, the hops in between, and the hashes to attach to the request."),
    ("SECONDARY", "I4C / CENTRAL ANALYST", "Sees the same deposit address turn up in complaints from different states — which turns twenty unconnected case files into one operation."),
    ("SECONDARY", "SUPERVISORY OFFICER", "Sorts a queue by where the money still seems to be, and can read why any finding was made without having to ask an engineer."),
]
uw = Inches(4.1)
uy = Inches(2.15)
for i, (badge, title, body) in enumerate(users):
    ux = Inches(0.3) + i * (uw + Inches(0.15))
    box(s, ux, uy, uw, Inches(1.55), fill=WHITE, border=MID, border_w=Pt(0.4))
    txbox(s, badge, ux + Inches(0.08), uy + Inches(0.06), uw - Inches(0.18), Inches(0.18), size=7, bold=True, color=ORANGE)
    txbox(s, title, ux + Inches(0.08), uy + Inches(0.22), uw - Inches(0.18), Inches(0.22), size=8.5, bold=True, color=NAVY)
    txbox(s, body, ux + Inches(0.08), uy + Inches(0.44), uw - Inches(0.18), Inches(1.0), size=8, color=BLACK, wrap=True)

header_bar(s, "BENEFITS OF THE SOLUTION (SOCIAL, ECONOMIC, ENVIRONMENTAL)", x=Inches(0.3), y=Inches(3.85), w=Inches(12.7), color=TEAL)
box(s, Inches(0.3), Inches(4.1), Inches(5.8), Inches(0.82), fill=WHITE, border=MID, border_w=Pt(0.4))
txbox(s, "HOW IT IS DONE TODAY", Inches(0.4), Inches(4.14), Inches(5.5), Inches(0.2), size=8, bold=True, color=NAVY)
txbox(s, "A block explorer is opened and clicked through two or three hops by hand. Six to twelve hours per address, and it usually ends in 'unknown'.", Inches(0.4), Inches(4.33), Inches(5.5), Inches(0.55), size=8, color=BLACK, wrap=True)
txbox(s, "▶", Inches(6.2), Inches(4.35), Inches(0.3), Inches(0.3), size=14, color=ORANGE, align=PP_ALIGN.CENTER)
box(s, Inches(6.6), Inches(4.1), Inches(6.4), Inches(0.82), fill=LGREY, border=MID, border_w=Pt(0.4))
txbox(s, "WITH CHAINNETRA", Inches(6.7), Inches(4.14), Inches(6.0), Inches(0.2), size=8, bold=True, color=TEAL)
txbox(s, "The automated stages finish in about ninety seconds on cached or warm data. The investigator checks an evidenced answer instead of producing one.", Inches(6.7), Inches(4.33), Inches(6.0), Inches(0.55), size=8, color=BLACK, wrap=True)

benefit_cards = [
    ("REACHES THE EXCHANGE IN TIME", "A freeze request needs someone to send it to. Naming that exchange early is the difference between getting the money back and not."),
    ("FINDS VICTIMS WHO NEVER COMPLAINED", "Tracing backwards from a scam wallet lists the other addresses that paid into it — people who never filed a complaint."),
    ("NO PER-SEAT LICENCE COST", "Commercial forensics platforms cost more than most state cyber cells can pay. This runs on free public data, on one server."),
    ("AN ANSWER THAT CAN BE CHECKED", "Every number opens into its signals, its transactions, and the stored raw reply with its hash and the time it was fetched."),
]
bw = Inches(3.05)
by = Inches(5.05)
for i, (title, body) in enumerate(benefit_cards):
    bx = Inches(0.3) + i * (bw + Inches(0.1))
    card(s, title, body, bx, by, bw, Inches(1.0), title_color=TEAL, bg=LGREY)

txbox(s, "WHERE THIS SYSTEM STOPS  ·  It does not name a person.  ·  It does not decide that fraud happened.  ·  It is not plugged into NCRP or CFCFRMS.", Inches(0.3), Inches(7.5) - Inches(0.65), Inches(12.7), Inches(0.22), size=7.5, italic=True, color=RGBColor(0x64, 0x74, 0x8B), wrap=True)
footer(s, 5)

# SLIDE 6 — Research & References
s = prs.slides[5]
clear_slide(s)
pill(s, "code2trip", w=Inches(1.1))
slide_title(s, "RESEARCH AND REFERENCES")
sih_badge(s)
header_bar(s, "DETAILS / LINKS OF THE REFERENCE AND RESEARCH WORK", x=Inches(0.3), y=Inches(1.02), w=Inches(12.7), color=ORANGE)

col_w = Inches(4.1)
cols = [
    ("GOVERNMENT MANDATE, SCALE & LAW", [
        ("MHA / I4C — SOP for NCRP-CFCFRMS, 2 Jan 2026", "Where funds reach an exchange not onboarded to CFCFRMS, the officer 'may conduct a VDA forensic analysis'.\nmha.gov.in/MHA1/Par2017/pdfs/par2026-pdfs/RS04022026/553.pdf"),
        ("MHA — Lok Sabha Unstarred Q.432, 2 Dec 2025", "22,68,346 NCRP incidents in 2024 (+42.08%); ₹22,845.73 crore reported; ₹7,130 crore saved via CFCFRMS.\nmha.gov.in/.../LS02122025/432.pdf"),
        ("Standing Committee on Home Affairs — 254th Report", "Recommends training in 'digital forensics, blockchain analysis and virtual asset tracing'.\nsansad.in › Committee_File › ReportFile › 254_2025_8_12.pdf"),
        ("PIB / FIU-IND, 1 Oct 2025", "50 VDA service providers registered; non-compliance notices issued to 25 offshore exchanges.\npib.gov.in/PressReleasePage.aspx?PRID=2173758"),
    ]),
    ("WHY TRON AND USDT", [
        ("UNODC — Casinos, Money Laundering, Underground Banking", "'USDT on TRON has become a preferred choice for regional cyberfraud … ease, anonymity, low fees.'\nunodc.org/roseap › Casino_Underground_Banking_Report_2024.pdf"),
        ("TRM Labs — 2025 Crypto Crime Report, 10 Feb 2025", "58% of illicit crypto volume in 2024 was on TRON, ahead of ETH (24%) and BTC (12%).\ntrmlabs.com/reports-and-whitepapers/2025-crypto-crime-report"),
        ("Enforcement Directorate — press release, 20 Nov 2025", "Proceeds of ₹285-crore cyber-fraud network turned into USDT over exchange P2P; ₹8.46 crore attached.\nenforcementdirectorate.gov.in › PAO-Cyber-Fraud-Case"),
        ("Enforcement Directorate — press release, 26 Sep 2025", "₹391 crore attached across 185 accounts. Investment scam, 5-6% monthly returns, USDT.\nenforcementdirectorate.gov.in › Navab-Hassan-QFX"),
    ]),
    ("DATA SOURCES & OUR OWN MEASUREMENTS", [
        ("TronGrid · Blockscout · Etherscan", "Transaction data for TRON and Ethereum under their API terms. We never scrape explorer label databases.\ndevelopers.tron.network/reference/rate-limits · docs.blockscout.com"),
        ("OFAC SDN sanctioned digital-currency addresses", "405 addresses ingested (281 TRON, 124 Ethereum), extracted with the MIT-licensed 0xB10C tool.\ngithub.com/0xB10C/ofac-sanctioned-digital-currency-addresses"),
        ("Dune spellbook — TRON exchange addresses", "A lead list only. Its BSL 1.1 licence does not cover our use, so we re-establish every address ourselves.\ngithub.com/duneanalytics/spellbook"),
        ("Our measurements, 2026-09-05", "TronGrid: 0.5 req/sec per method. 9 of 151 published TRON labels not valid addresses; 94 survived.\ndocs/research/OQ-01-provider-rate-limits.md"),
    ]),
]

for ci, (title, refs) in enumerate(cols):
    cx = Inches(0.3) + ci * (col_w + Inches(0.15))
    txbox(s, title, cx, Inches(1.28), col_w, Inches(0.22), size=8, bold=True, color=NAVY)
    box(s, cx, Inches(1.5), col_w, Inches(0.015), fill=ORANGE)
    ry = Inches(1.55)
    for ref_title, ref_body in refs:
        rh = Inches(0.9)
        box(s, cx, ry, col_w, rh, fill=WHITE, border=MID, border_w=Pt(0.3))
        txbox(s, ref_title, cx + Inches(0.06), ry + Inches(0.04), col_w - Inches(0.12), Inches(0.2), size=7.5, bold=True, color=NAVY)
        txbox(s, ref_body, cx + Inches(0.06), ry + Inches(0.23), col_w - Inches(0.12), rh - Inches(0.28), size=7, color=BLACK, wrap=True)
        ry += rh + Inches(0.05)

box(s, Inches(0.3), Inches(7.5) - Inches(0.65), Inches(12.7), Inches(0.22), fill=LGREY, border=None)
txbox(s, "HOW WE USE THESE SOURCES  ·  We never scrape explorer label databases — their terms forbid it. Every label we ship records its source, its licence and the date we captured it.", Inches(0.4), Inches(7.5) - Inches(0.63), Inches(12.5), Inches(0.2), size=7.5, italic=True, color=RGBColor(0x1E, 0x3A, 0x5F), wrap=True)
footer(s, 6)

prs.save("docs/ChainNetra_SIH26183_code2trip.pptx")
print("Successfully generated high-fidelity PPT matching the PDF but built onto the SIH Template metadata.")
