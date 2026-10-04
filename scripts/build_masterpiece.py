import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def rgb(r, g, b): return RGBColor(r, g, b)

NAVY   = rgb(15, 23, 42)
ORANGE = rgb(224, 108, 27)
TEAL   = rgb(29, 122, 122)
LGREY  = rgb(241, 245, 249)
MID    = rgb(226, 232, 240)
WHITE  = rgb(255, 255, 255)
BLACK  = rgb(15, 23, 42)

def box(sl, x, y, w, h, fill=None, border=None, border_w=Pt(0.5)):
    shape = sl.shapes.add_shape(1, x, y, w, h)
    shape.line.fill.background()
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if border:
        shape.line.color.rgb = border
        shape.line.width = border_w
    return shape

def txbox(sl, text, x, y, w, h, size=11, bold=False, color=BLACK, align=PP_ALIGN.LEFT, bg=None, border=None):
    shape = sl.shapes.add_textbox(x, y, w, h)
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    if bg:
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
    if border:
        shape.line.color.rgb = border
        shape.line.width = Pt(0.5)
    return shape

def header_bar(sl, label, x, y, w, color=ORANGE):
    b = box(sl, x, y, w, Inches(0.28), fill=color)
    txbox(sl, label, x + Inches(0.05), y + Inches(0.02), w - Inches(0.1), Inches(0.25), size=9.5, bold=True, color=WHITE)
    return b

def flow_step(sl, num, title, body, x, y, w, h):
    box(sl, x, y, w, h, fill=WHITE, border=MID)
    box(sl, x, y, w, Inches(0.28), fill=LGREY)
    txbox(sl, f" {num} | {title}", x, y+Inches(0.03), w, Inches(0.25), size=8.5, bold=True, color=ORANGE)
    txbox(sl, body, x+Inches(0.05), y+Inches(0.35), w-Inches(0.1), h-Inches(0.4), size=8.5, color=BLACK)

def info_card(sl, title, body, x, y, w, h, title_color=NAVY, body_size=9):
    box(sl, x, y, w, h, fill=LGREY, border=MID)
    txbox(sl, title, x+Inches(0.1), y+Inches(0.08), w-Inches(0.2), Inches(0.2), size=9.5, bold=True, color=title_color)
    txbox(sl, body, x+Inches(0.1), y+Inches(0.3), w-Inches(0.2), h-Inches(0.4), size=body_size, color=BLACK)

def build_presentation(template_path, output_path):
    prs = Presentation(template_path)
    
    for i, slide in enumerate(prs.slides):
        if 1 <= i <= 5:
            for shape in slide.shapes:
                if shape.has_text_frame and shape.name == 'TextBox 8':
                    shape.left = Inches(-20)
                if shape.has_text_frame and "Your\nTeam\nName" in shape.text:
                    shape.text = "code2trip"
                elif shape.has_text_frame and "Your Team Name" in shape.text:
                    shape.text = "code2trip"
                
    # --- SLIDE 1: COVER ---
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.name == 'Subtitle 3': shape.text = ""
        elif shape.name == 'TextBox 9': shape.left = Inches(-20)
    
    txbox(s1, "ChainNetra", Inches(0.5), Inches(2.0), Inches(6), Inches(0.6), size=40, bold=True, color=NAVY)
    txbox(s1, "Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics", 
          Inches(0.5), Inches(2.8), Inches(6.5), Inches(1.5), size=16, bold=False, color=TEAL)
    
    details = [
        ("Problem Statement ID:", "SIH26183"),
        ("Theme:", "Blockchain & Cybersecurity"),
        ("PS Category:", "Software"),
        ("Organisation:", "Ministry of Home Affairs"),
        ("Team ID:", "26183"),
        ("Team Name:", "code2trip"),
        ("Institute:", "[Your Institute Name]"),
    ]
    dy = Inches(4.5)
    for label, val in details:
        txbox(s1, label, Inches(0.5), dy, Inches(1.8), Inches(0.25), size=11, bold=True, color=ORANGE)
        txbox(s1, val, Inches(2.5), dy, Inches(3.5), Inches(0.25), size=11, bold=True, color=NAVY)
        dy += Inches(0.3)

    # --- SLIDE 2: PROPOSED SOLUTION ---
    s2 = prs.slides[1]
    for shape in s2.shapes:
        if shape.name == 'Title 1': shape.text = "ChainNetra: Proposed Solution"
    
    header_bar(s2, "Detailed explanation of the proposed solution (Pipeline)", Inches(0.5), Inches(1.5), Inches(12.33), color=ORANGE)
    steps = [
        ("01", "INGESTION & NORMALIZATION", "Asynchronous ingestion of UTXO/Account RPCs. Normalizes heterogeneous block data into strict Pydantic schemas."),
        ("02", "GRAPH TAINT ENGINE", "Constructs a Directed Acyclic Graph (DAG) for multi-hop tracing. Applies FIFO and proportional taint math to compute contamination."),
        ("03", "HEURISTICS & ML", "Deposit-Address-Reuse (DAR) clustering. 7 anomaly detectors (Peel Chains, Fan-out, Fan-in) assess obfuscation with probability scoring."),
        ("04", "ATTRIBUTION & COMPLIANCE", "Cross-references addresses with OFAC SDN lists and Exchange Proof-of-Reserves (PoR). Auto-drafts court-ready freeze requests.")
    ]
    sw = Inches(2.95)
    for i, (num, t, b) in enumerate(steps):
        flow_step(s2, num, t, b, Inches(0.5) + i*(sw+Inches(0.15)), Inches(1.85), sw, Inches(1.5))

    header_bar(s2, "How it addresses the problem", Inches(0.5), Inches(3.5), Inches(6.0), color=TEAL)
    info_card(s2, "Eliminating the Tracing Blindspot", "District cyber cells can see addresses but cannot serve a legal notice to a hexadecimal string. ChainNetra identifies the centralized fiat off-ramp (the Exchange) and provides the exact evidentiary transaction hash required by law enforcement to freeze funds before they enter offshore mixers.", Inches(0.5), Inches(3.85), Inches(6.0), Inches(1.3))

    header_bar(s2, "Innovation and uniqueness of the solution", Inches(6.8), Inches(3.5), Inches(6.0), color=TEAL)
    info_card(s2, "Advanced Heuristics & Verifiability", "1. Combines recursive DAG tracing with behavioral heuristics (clustering deposits without KYC).\n2. Implements a strict 3-Tier Confidence System (Confirmed/Probable) to eliminate false positives.\n3. Preserves cryptographic chain-of-custody for court admissibility.", Inches(6.8), Inches(3.85), Inches(6.0), Inches(1.3))

    # --- SLIDE 3: TECHNICAL APPROACH ---
    s3 = prs.slides[2]
    header_bar(s3, "Methodology and process for implementation (Flow Chart)", Inches(0.5), Inches(1.5), Inches(7.0), color=ORANGE)
    
    # Sophisticated Flowchart
    flow = [
        ("INPUT LAYER", "Victim Address & Tx Hash → API Gateway"),
        ("RPC ABSTRACTION", "TronGrid / Etherscan → Normalization Engine"),
        ("GRAPH COMPUTATION", "NetworkX DAG Construction & Taint Decay Math"),
        ("BEHAVIORAL ANALYSIS", "Peel Chain / Fan-out Detection & DAR Clustering"),
        ("ATTRIBUTION LAYER", "KYC/PoR DB Matching (PostgreSQL)"),
        ("OUTPUT LAYER", "Auto-Generated Legal Freeze Request PDF (Sec 94/102 CRPC)")
    ]
    fy = Inches(1.85)
    for i, (title, step) in enumerate(flow):
        box(s3, Inches(0.5), fy, Inches(6.5), Inches(0.55), fill=LGREY, border=MID)
        txbox(s3, f"[{i+1}] {title}", Inches(0.6), fy+Inches(0.05), Inches(6.3), Inches(0.2), size=9, bold=True, color=ORANGE)
        txbox(s3, step, Inches(0.6), fy+Inches(0.25), Inches(6.3), Inches(0.2), size=10, bold=True, color=NAVY)
        if i < len(flow)-1:
            txbox(s3, "↓", Inches(3.5), fy+Inches(0.55), Inches(0.5), Inches(0.2), size=16, bold=True, color=TEAL)
        fy += Inches(0.75)
        
    header_bar(s3, "Technologies to be used", Inches(7.8), Inches(1.5), Inches(5.0), color=TEAL)
    techs = [
        ("Compute & API", "Python 3.12, FastAPI, Celery (Async)"), 
        ("Graph & ML", "NetworkX (DAG), Pandas, LightGBM"), 
        ("Data Persistence", "PostgreSQL 16, Redis (Caching)"), 
        ("Frontend Layer", "React 18, TypeScript, TailwindCSS"), 
        ("DevOps & Sec", "Docker, AWS EC2, Nginx, SSL")
    ]
    ty = Inches(1.85)
    for k, v in techs:
        box(s3, Inches(7.8), ty, Inches(1.5), Inches(0.7), fill=NAVY)
        txbox(s3, k, Inches(7.8), ty+Inches(0.15), Inches(1.5), Inches(0.5), size=9.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        box(s3, Inches(9.3), ty, Inches(3.5), Inches(0.7), fill=LGREY, border=MID)
        txbox(s3, v, Inches(9.4), ty+Inches(0.15), Inches(3.3), Inches(0.5), size=10, bold=False, color=BLACK)
        ty += Inches(0.85)

    # --- SLIDE 4: FEASIBILITY ---
    s4 = prs.slides[3]
    header_bar(s4, "Analysis of the feasibility of the idea", Inches(0.5), Inches(1.5), Inches(12.33), color=ORANGE)
    info_card(s4, "Zero-Cost Infrastructure & High Scalability", "The architecture relies exclusively on public RPC endpoints and Open-Source Intelligence (OSINT), avoiding expensive proprietary forensic software licenses (e.g., Chainalysis). The entire system operates smoothly on a standard AWS t3.medium instance, making it financially accessible for deployment across all district cyber cells.", Inches(0.5), Inches(1.85), Inches(12.33), Inches(0.9), body_size=10.5)

    header_bar(s4, "Potential challenges and risks", Inches(0.5), Inches(2.9), Inches(6.0), color=TEAL)
    info_card(s4, "Technical & Operational Risks", "1. RPC API Rate Limits and timeouts during high-depth graph traversal.\n2. Fund obfuscation via Non-Compliant Mixers (e.g., Tornado Cash) breaking the deterministic trace.\n3. Dynamic rotation of Exchange Cold/Hot wallets complicating attribution.", Inches(0.5), Inches(3.25), Inches(6.0), Inches(1.3), body_size=10)

    header_bar(s4, "Strategies for overcoming these challenges", Inches(6.8), Inches(2.9), Inches(6.0), color=TEAL)
    info_card(s4, "Mitigation & Caching", "1. Implemented aggressive Redis caching for block heights to slash API calls.\n2. Behavioral detectors explicitly flag Mixer interactions to halt the trace and report verified dead-ends cleanly.\n3. Continuous ingestion of updated Proof-of-Reserve (PoR) cryptographic data.", Inches(6.8), Inches(3.25), Inches(6.0), Inches(1.3), body_size=10)

    # --- SLIDE 5: IMPACT ---
    s5 = prs.slides[4]
    header_bar(s5, "Potential impact on the target audience", Inches(0.5), Inches(1.5), Inches(12.33), color=ORANGE)
    info_card(s5, "Empowering I4C and State Police Cyber Cells", "In 2024, 22.68 lakh cybercrimes were reported. District Investigators currently spend 6-12 hours manually clicking through block explorers. ChainNetra reduces this to 90 seconds, equipping non-technical officers with immediate, legally sound action items.", Inches(0.5), Inches(1.85), Inches(12.33), Inches(1.0), body_size=10.5)

    header_bar(s5, "Benefits of the solution (social, economic, environmental, etc.)", Inches(0.5), Inches(3.0), Inches(12.33), color=TEAL)
    by = Inches(3.35)
    b_items = [
        ("Economic Benefit: Accelerated Capital Recovery", "Naming the Exchange early is the sole difference between recovering funds and losing them entirely to offshore entities. Directly impacts the ₹22,845 crore lost annually."),
        ("Social Benefit: Identifying Silent Victims", "Backward DAG tracing from scam wallets autonomously identifies related victim wallets who never filed formal police complaints."),
        ("Operational Benefit: Evidentiary Admissibility", "Maintains chain-of-custody by embedding SHA-256 hashes of original API responses into the PDF, ensuring compliance under Section 65B of the Indian Evidence Act.")
    ]
    for title, desc in b_items:
        box(s5, Inches(0.5), by, Inches(12.33), Inches(0.8), fill=LGREY, border=MID)
        txbox(s5, title, Inches(0.6), by+Inches(0.1), Inches(4.5), Inches(0.4), size=10.5, bold=True, color=NAVY)
        txbox(s5, desc, Inches(4.8), by+Inches(0.1), Inches(7.5), Inches(0.6), size=10, color=BLACK)
        by += Inches(0.9)

    # --- SLIDE 6: RESEARCH ---
    s6 = prs.slides[5]
    header_bar(s6, "Details / Links of the reference and research work", Inches(0.5), Inches(1.5), Inches(12.33), color=ORANGE)
    
    col_w = Inches(4.0)
    cols = [
        ("MHA / I4C Legal Mandates", "SOP for NCRP: Officers are mandated to conduct VDA forensic analysis for non-onboarded exchanges.\nReferences: Rajya Sabha USQ 553, Section 94/102 CRPC protocols."),
        ("Taint Math & Clustering", "Heuristics modeled on Victor (2020) 'Deposit Address Reuse (DAR)' clustering techniques, and FOFO (First-In-First-Out) taint tracking literature (Meiklejohn et al.)."),
        ("UNODC Crypto Intelligence", "UNODC 2025 Crypto Crime Report highlighting TRON's 58% share in illicit volume, dictating our multi-chain normalization strategy prioritizing TRX over ETH.")
    ]
    for i, (title, desc) in enumerate(cols):
        cx = Inches(0.5) + i*(col_w + Inches(0.16))
        info_card(s6, title, desc, cx, Inches(1.85), col_w, Inches(1.8), title_color=NAVY, body_size=10)

    if len(prs.slides) > 6:
        try:
            prs.slides._sldIdLst.remove(list(prs.slides._sldIdLst)[6])
        except Exception:
            pass

    prs.save(output_path)

if __name__ == "__main__":
    build_presentation(sys.argv[1], sys.argv[2])
