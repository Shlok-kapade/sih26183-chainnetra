import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def c(hex_code):
    hex_code = hex_code.lstrip('#')
    return RGBColor(*(int(hex_code[i:i+2], 16) for i in (0, 2, 4)))

# Clean, professional, modern color palette
NAVY_HEADER = c("0F172A")  # Deep Slate Navy
NAVY_ACCENT = c("1E3A8A")  # Royal Navy
BLUE_PILL   = c("2563EB")  # Vivid Blue
BLUE_CARD   = c("EFF6FF")  # Soft Ice Blue
BLUE_BORDER = c("BFDBFE")  # Light Blue Border
TEAL        = c("0D9488")  # Dark Teal
ORANGE_PILL = c("EA580C")  # Vibrant Orange
ORANGE_CARD = c("FFF7ED")  # Soft Amber/Orange
ORANGE_BORD = c("FED7AA")  # Light Orange Border
GREEN_PILL  = c("059669")  # Emerald Green
GREEN_CARD  = c("ECFDF5")  # Soft Emerald
GREEN_BORD  = c("A7F3D0")  # Light Green Border
CARD_BG     = c("F8FAFC")  # Crisp Off-White
CARD_BORDER = c("E2E8F0")  # Clean Grey Border
DARK_TEXT   = c("1E293B")  # Primary Body Text
MUTED_TEXT  = c("64748B")  # Secondary Text
WHITE       = c("FFFFFF")  # Pure White

def add_box(slide, left, top, width, height, fill_color=None, line_color=None, line_width=Pt(0.75)):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    if fill_color:
        s.fill.solid()
        s.fill.fore_color.rgb = fill_color
    else:
        s.fill.background()
    if line_color:
        s.line.color.rgb = line_color
        s.line.width = line_width
    else:
        s.line.fill.background()
    return s

def add_round_box(slide, left, top, width, height, fill_color=None, line_color=None, line_width=Pt(0.75)):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    if fill_color:
        s.fill.solid()
        s.fill.fore_color.rgb = fill_color
    else:
        s.fill.background()
    if line_color:
        s.line.color.rgb = line_color
        s.line.width = line_width
    else:
        s.line.fill.background()
    return s

def add_pill(slide, text, left, top, width, height, bg_color=NAVY_ACCENT, text_color=WHITE, font_size=8.5):
    add_round_box(slide, left, top, width, height, fill_color=bg_color)
    tb = slide.shapes.add_textbox(left, top - Inches(0.01), width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.bold = True
    r.font.size = Pt(font_size)
    r.font.color.rgb = text_color
    r.font.name = "Arial"

def add_textbox(slide, left, top, width, height, text="", font_size=9, bold=False, color=DARK_TEXT, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    if text:
        r = p.add_run()
        r.text = text
        r.font.size = Pt(font_size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = "Arial"
    return tb

def add_clean_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=None):
    add_round_box(slide, left, top, width, height, fill_color=bg_color, line_color=border_color)
    if accent_bar_color:
        add_box(slide, left, top, Inches(0.08), height, fill_color=accent_bar_color)

def style_slide_header(slide, title_text):
    # Hide default Title 1 placeholder to avoid template artifacts
    for shape in list(slide.shapes):
        if shape.name == 'Title 1':
            shape.left = Inches(-20)
        elif shape.has_text_frame:
            txt = shape.text.strip()
            if any(k in txt for k in ["Detailed explanation", "Technologies to be used", "Analysis of the feasibility", "Potential impact", "Details / Links", "@SIH Idea"]):
                shape.left = Inches(-20)
            elif shape.name in ['TextBox 8', 'TextBox 9', 'Subtitle 3']:
                shape.left = Inches(-20)
            elif any(w in shape.text for w in ["Your Team Name", "Your\nTeam\nName", "Avengers", "code2trip"]):
                # Style the team oval cleanly
                shape.fill.solid()
                shape.fill.fore_color.rgb = c("1E293B")
                shape.line.fill.background()
                shape.text_frame.text = ""
                p = shape.text_frame.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER
                r = p.add_run()
                r.text = "code2trip"
                r.font.size = Pt(11)
                r.font.bold = True
                r.font.color.rgb = WHITE
                r.font.name = "Arial"
                
    # Place clean, single-line title between oval (left ~1.7) and brain logo (left ~10.7)
    tb = slide.shapes.add_textbox(Inches(1.85), Inches(0.36), Inches(8.5), Inches(0.55))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = title_text
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = NAVY_HEADER
    r.font.name = "Georgia"

def add_footer(slide, slide_num):
    add_box(slide, Inches(0), Inches(6.92), Inches(13.333), Inches(0.58), fill_color=WHITE)
    add_box(slide, Inches(0), Inches(7.15), Inches(13.333), Inches(0.35), fill_color=c("0F172A"))
    add_textbox(slide, Inches(0.5), Inches(7.20), Inches(10.0), Inches(0.25), 
                text=f"SIH 2026  |  PS SIH26183 — ChainNetra  |  Team code2trip", font_size=8.5, bold=True, color=WHITE)
    add_textbox(slide, Inches(12.3), Inches(7.20), Inches(0.5), Inches(0.25), 
                text=str(slide_num), font_size=9, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

def build_slide1(prs):
    s = prs.slides[0]
    for shape in list(s.shapes):
        if shape.name in ['TextBox 9', 'Subtitle 3']:
            shape.left = Inches(-20)
        elif shape.has_text_frame and "Problem Statement ID" in shape.text:
            shape.left = Inches(-20)

    details = [
        ("Problem Statement ID –", "SIH26183"),
        ("Problem Statement Title –", "Real-Time Identification of Fraud-Linked Cryptocurrency\nExchanges from Victim-Reported Suspect Wallet Addresses\nthrough Automated Blockchain Analytics"),
        ("Theme –", "Blockchain & Cybersecurity"),
        ("PS Category –", "Software"),
        ("Organisation –", "Ministry of Home Affairs (I4C)"),
        ("Team ID –", "26183"),
        ("Team Name (Registered on portal) –", "code2trip"),
        ("Institute –", "code2trip Team")
    ]
    
    top = Inches(2.25)
    for label, val in details:
        tb = s.shapes.add_textbox(Inches(0.5), top, Inches(6.4), Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = label + "  "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = NAVY_ACCENT
        r1.font.name = "Arial"
        
        r2 = p.add_run()
        r2.text = val
        r2.font.bold = False
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT
        r2.font.name = "Arial"
        
        if val.count("\n") == 2:
            top += Inches(0.70)
        elif val.count("\n") == 1:
            top += Inches(0.50)
        else:
            top += Inches(0.28)

    card_left = Inches(0.5)
    card_top = Inches(5.48)
    card_w = Inches(6.4)
    card_h = Inches(1.42)
    add_clean_card(s, card_left, card_top, card_w, card_h, bg_color=BLUE_CARD, border_color=BLUE_BORDER, accent_bar_color=NAVY_ACCENT)
    
    tb = s.shapes.add_textbox(card_left + Inches(0.2), card_top + Inches(0.12), card_w - Inches(0.4), card_h - Inches(0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    
    p0 = tf.paragraphs[0]
    p0.space_after = Pt(2)
    r0 = p0.add_run()
    r0.text = "PROPOSED SOLUTION"
    r0.font.size = Pt(8.5)
    r0.font.bold = True
    r0.font.color.rgb = NAVY_ACCENT
    r0.font.name = "Arial"
    
    p1 = tf.add_paragraph()
    p1.space_after = Pt(3)
    r1 = p1.add_run()
    r1.text = "ChainNetra"
    r1.font.size = Pt(20)
    r1.font.bold = True
    r1.font.color.rgb = NAVY_HEADER
    r1.font.name = "Arial"
    
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = "Autonomous Cyber-Forensic Intelligence Engine for Real-Time Exchange Identification, Asset Freezing & Courtroom Evidence Dossier Generation"
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = MUTED_TEXT
    r2.font.name = "Arial"

def build_slide2(prs):
    s = prs.slides[1]
    style_slide_header(s, "ChainNetra: Autonomous Exchange Identification Engine")
            
    sub_top = Inches(1.18)
    add_clean_card(s, Inches(0.5), sub_top, Inches(12.33), Inches(0.36), bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=NAVY_ACCENT)
    tb = s.shapes.add_textbox(Inches(0.7), sub_top + Inches(0.07), Inches(12.0), Inches(0.24))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Real-time blockchain forensics that traces stolen crypto across wallets, identifies the destination exchange, and auto-generates a court-ready freeze order — faster than any manual investigation."
    r.font.size = Pt(9)
    r.font.bold = False
    r.font.color.rgb = NAVY_ACCENT
    r.font.name = "Arial"

    add_pill(s, "PROPOSED SOLUTION: 4-STAGE CORE FORENSIC PIPELINE",
             Inches(0.5), Inches(1.68), Inches(4.5), Inches(0.28), bg_color=NAVY_ACCENT, font_size=8)
             
    pipeline_stages = [
        ("01", "SUSPECT WALLET INTAKE",
         "• Scans TRON, Ethereum & Bitcoin from a single suspect address\n• Decodes hidden smart-contract token transfers (zero missed txns)\n• SHA-256 timestamps every API response for tamper-proof custody"),
        ("02", "MULTI-HOP FUND TRACING",
         "• Autonomously follows funds through 10+ burner wallets across multiple hops\n• Mathematically tracks exact stolen fraction across all splits\n• Detects & removes wash-trade loops injected to mislead tracers"),
        ("03", "EXCHANGE IDENTIFICATION",
         "• Clusters deposit wallets to unmask the receiving exchange\n• 7 pattern detectors flag peel chains, smurfing & rapid forwarding\n• 4-tier confidence scoring: CONFIRMED / PROBABLE / POSSIBLE / UNATTRIBUTED"),
        ("04", "LEGAL FREEZE & DOSSIER",
         "• Maps exchange to its FIU-IND-designated Nodal LEO contact\n• 1-click Section 94/106 BNSS freeze notice pre-filled with evidence\n• Court-ready PDF with SHA-256 certified blockchain proof of funds"),
    ]
    
    stage_w = Inches(2.82)
    stage_h = Inches(1.72)
    stage_y = Inches(2.04)
    
    for i, (num, title, body) in enumerate(pipeline_stages):
        x = Inches(0.5) + i * Inches(3.17)
        add_clean_card(s, x, stage_y, stage_w, stage_h, bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=NAVY_ACCENT)
        
        add_round_box(s, x + Inches(0.12), stage_y + Inches(0.1), Inches(0.35), Inches(0.22), fill_color=NAVY_ACCENT)
        add_textbox(s, x + Inches(0.12), stage_y + Inches(0.12), Inches(0.35), Inches(0.22), text=num, font_size=8, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        
        add_textbox(s, x + Inches(0.52), stage_y + Inches(0.12), stage_w - Inches(0.6), Inches(0.22), text=title, font_size=8, bold=True, color=NAVY_ACCENT)
        add_textbox(s, x + Inches(0.15), stage_y + Inches(0.40), stage_w - Inches(0.25), stage_h - Inches(0.45), text=body, font_size=7.5, color=DARK_TEXT)

        # Directional Flow Arrow between cards
        if i < 3:
            arrow_x = x + stage_w + Inches(0.06)
            arrow_y = stage_y + Inches(0.72)
            arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_x, arrow_y, Inches(0.23), Inches(0.20))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = c("94A3B8")
            arrow.line.fill.background()

    bot_y = Inches(3.95)
    
    col1_x = Inches(0.5)
    col1_w = Inches(6.0)
    add_pill(s, "HOW IT ADDRESSES CRITICAL POLICING BOTTLENECKS", col1_x, bot_y, Inches(4.5), Inches(0.28), bg_color=ORANGE_PILL, font_size=8)
    
    add_clean_card(s, col1_x, bot_y + Inches(0.35), col1_w, Inches(2.50), bg_color=ORANGE_CARD, border_color=ORANGE_BORD, accent_bar_color=ORANGE_PILL)
    
    prob_tb = s.shapes.add_textbox(col1_x + Inches(0.2), bot_y + Inches(0.42), col1_w - Inches(0.35), Inches(2.35))
    tf_p = prob_tb.text_frame
    tf_p.word_wrap = True
    
    sol_items = [
        ("The 'Golden Hour' Recovery Gap:", "Fraudsters liquidate crypto via P2P within 1–2 hours. Manual tracing takes 6–12 hours. ChainNetra automates multi-hop graph traversal, enabling proactive freezing before fiat conversion."),
        ("Overcoming Peeling & Smurfing Layering:", "Syndicates split funds into micro-transfers across dozens of burner hops. ChainNetra's mathematical engine automatically tracks the exact fractional stolen value through every branch."),
        ("Internal Smart Contract Visibility:", "Scammers exploit DEX swaps and TRC-20 internal contract calls where public explorers display false zero balances. ChainNetra decodes execution traces natively with zero transaction drop."),
        ("Eliminating Wrongful Freezes:", "Strict 4-tier evidentiary confidence scoring ensures innocent merchants or payment gateways are never wrongfully frozen, protecting law enforcement from legal liability.")
    ]
    for h, b in sol_items:
        p = tf_p.add_paragraph() if tf_p.paragraphs[0].text else tf_p.paragraphs[0]
        r1 = p.add_run()
        r1.text = h + " "
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = ORANGE_PILL
        r2 = p.add_run()
        r2.text = b + "\n"
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = DARK_TEXT

    col2_x = Inches(6.83)
    col2_w = Inches(6.0)
    add_pill(s, "INNOVATION AND DOMAIN UNIQUENESS", col2_x, bot_y, Inches(4.5), Inches(0.28), bg_color=GREEN_PILL, font_size=8)
    
    add_clean_card(s, col2_x, bot_y + Inches(0.35), col2_w, Inches(2.50), bg_color=GREEN_CARD, border_color=GREEN_BORD, accent_bar_color=GREEN_PILL)
    
    inn_tb = s.shapes.add_textbox(col2_x + Inches(0.2), bot_y + Inches(0.42), col2_w - Inches(0.35), Inches(2.35))
    tf_i = inn_tb.text_frame
    tf_i.word_wrap = True
    
    innovations = [
        ("Deposit Wallet Reverse Attribution:", "Detects high-frequency exchange deposit wallets without requiring internal exchange access, revealing the destination exchange directly from public blockchain patterns."),
        ("Zero-Cost Architecture for Police Units:", "Built 100% on open blockchain infrastructure and public intelligence, eliminating multi-lakh commercial software licenses for grassroots cyber cells."),
        ("Automated Indian Legal Compliance:", "Bridges technical blockchain evidence directly into Indian criminal procedure—auto-generating Section 94/106 BNSS freeze requisitions with pre-filled transaction hashes."),
        ("Syndicate & Mule Network Correlation:", "Cross-references separate victim complaints across states to discover shared deposit wallets, unmasking organized interstate cybercrime syndicates."),
        ("Browser Addon for Field Investigators:", "A Chromium extension lets officers check any wallet address on TronScan/Etherscan live — instantly overlaying ChainNetra's taint score without switching tools."),
        ("Court-Admissible Cryptographic Custody:", "Every external API response is SHA-256 hashed and stored with provenance, satisfying Section 63 BSA (Sec 65B IEA) electronic-evidence admissibility requirements."),
    ]
    for h, b in innovations:
        p = tf_i.add_paragraph() if tf_i.paragraphs[0].text else tf_i.paragraphs[0]
        r1 = p.add_run()
        r1.text = h + " "
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = GREEN_PILL
        r2 = p.add_run()
        r2.text = b + "\n"
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = DARK_TEXT

    add_footer(s, 2)

def build_slide3(prs):
    s = prs.slides[2]
    style_slide_header(s, "Technical Approach")

    add_pill(s, "METHODOLOGY & FORENSIC PIPELINE: AUTOMATED INVESTIGATION LIFECYCLE",
             Inches(0.5), Inches(1.15), Inches(6.6), Inches(0.26), bg_color=NAVY_ACCENT, font_size=8)

    # Embed High-Resolution Forensic Flowchart Diagram (Clear top & bottom margins)
    flowchart_path = "assets/chainnetra_pipeline_architecture.png"
    if os.path.exists(flowchart_path):
        s.shapes.add_picture(flowchart_path, Inches(0.5), Inches(1.44), width=Inches(12.33), height=Inches(3.16))

    # Bottom Section: 3 distinct columns (Capabilities, Tech Stack, Prototype Deliverables)
    bot_y = Inches(4.74)
    card_h = Inches(2.28)
    gap = Inches(0.18)

    # Column 1: Core Forensic Capabilities
    col1_x = Inches(0.5)
    col1_w = Inches(3.70)
    add_pill(s, "KEY FORENSIC CAPABILITIES", col1_x, bot_y, Inches(3.3), Inches(0.26), bg_color=NAVY_ACCENT, font_size=7.5)
    add_clean_card(s, col1_x, bot_y + Inches(0.28), col1_w, card_h - Inches(0.28), bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=NAVY_ACCENT)
    
    tech_tb = s.shapes.add_textbox(col1_x + Inches(0.14), bot_y + Inches(0.32), col1_w - Inches(0.24), card_h - Inches(0.36))
    tf_t = tech_tb.text_frame
    tf_t.word_wrap = True
    
    tech_capabilities = [
        ("Multi-Chain Tracking:", "Traces TRON (USDT), Ethereum & Bitcoin in one unified graph."),
        ("Contract Call Decoder:", "Decodes internal smart contract traces to uncover hidden transfers & swaps."),
        ("Mathematical Taint Engine:", "Carries exact proportional stolen dollar value through every multi-hop split."),
        ("Scam Wash Filtering:", "Automatically removes circular churn transactions engineered to mislead tracers."),
        ("Interactive Visual Canvas:", "Node-link inspection workspace for officers to analyze hops & freeze targets.")
    ]
    for cat, val in tech_capabilities:
        p = tf_t.add_paragraph() if tf_t.paragraphs[0].text else tf_t.paragraphs[0]
        p.space_after = Pt(2.0)
        r1 = p.add_run()
        r1.text = cat + " "
        r1.font.bold = True
        r1.font.size = Pt(7.2)
        r1.font.color.rgb = NAVY_ACCENT
        r2 = p.add_run()
        r2.text = val
        r2.font.size = Pt(6.8)
        r2.font.color.rgb = DARK_TEXT

    # Column 2: Tech Stack — 2-col table layout
    col2_x = col1_x + col1_w + gap  # 4.38
    col2_w = Inches(4.45)
    add_pill(s, "TECHNOLOGIES USED", col2_x, bot_y, Inches(3.3), Inches(0.26), bg_color=NAVY_ACCENT, font_size=7.5)
    add_clean_card(s, col2_x, bot_y + Inches(0.28), col2_w, card_h - Inches(0.28), bg_color=c("F1F5F9"), border_color=c("CBD5E1"), accent_bar_color=NAVY_ACCENT)

    TECH_ROWS = [
        ("Frontend",        "React 19 · TypeScript 6 · Vite 8 · Tailwind 4 · Cytoscape.js · Axios"),
        ("Backend",         "Python 3.12 · FastAPI · SQLAlchemy 2 (async) · asyncpg · Pydantic v2"),
        ("Database",        "PostgreSQL 16 (Docker) · asyncpg driver · Alembic"),
        ("Chain APIs",      "TronGrid (TRC-20 USDT) · Etherscan v2 (ERC-20) · Mempool.space (BTC)"),
        ("Analytics & AI",  "NetworkX (graph) · LightGBM · SHAP (explainability) · Hypothesis"),
        ("Reports & Tool",  "ReportLab (PDF dossier) · pytest · Browser Extension (Manifest v3)"),
    ]
    tbl_x = col2_x + Inches(0.12)
    tbl_y = bot_y + Inches(0.32)
    tbl_w = col2_w - Inches(0.20)
    tbl_h = card_h - Inches(0.42)
    n_rows = len(TECH_ROWS)
    row_h = tbl_h / n_rows
    col1_tw = Inches(1.10)
    col2_tw = tbl_w - col1_tw

    for i, (cat, val) in enumerate(TECH_ROWS):
        ry = tbl_y + i * row_h
        if i > 0:
            sep = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                     tbl_x, ry - Inches(0.005), tbl_w, Inches(0.005))
            sep.fill.solid(); sep.fill.fore_color.rgb = c("CBD5E1")
            sep.line.fill.background()

        tb_cat = s.shapes.add_textbox(tbl_x, ry + Inches(0.02), col1_tw - Inches(0.05), row_h - Inches(0.02))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = False
        p_cat = tf_cat.paragraphs[0]
        p_cat.alignment = PP_ALIGN.LEFT
        r_cat = p_cat.add_run()
        r_cat.text = cat
        r_cat.font.bold = True
        r_cat.font.size = Pt(7.5)
        r_cat.font.color.rgb = NAVY_ACCENT

        tb_val = s.shapes.add_textbox(tbl_x + col1_tw, ry + Inches(0.02), col2_tw - Inches(0.05), row_h - Inches(0.02))
        tf_val = tb_val.text_frame
        tf_val.word_wrap = True
        p_val = tf_val.paragraphs[0]
        p_val.alignment = PP_ALIGN.LEFT
        r_val = p_val.add_run()
        r_val.text = val
        r_val.font.size = Pt(7.0)
        r_val.font.color.rgb = DARK_TEXT

    # Column 3: Dedicated Prototype & Deliverables Table
    col3_x = col2_x + col2_w + gap  # 9.01
    col3_w = Inches(3.82)
    add_pill(s, "PROTOTYPE & DELIVERABLES", col3_x, bot_y, Inches(3.3), Inches(0.26), bg_color=GREEN_PILL, font_size=7.5)
    add_clean_card(s, col3_x, bot_y + Inches(0.28), col3_w, card_h - Inches(0.28), bg_color=GREEN_CARD, border_color=GREEN_BORD, accent_bar_color=GREEN_PILL)

    PROTOTYPE_LINKS = [
        (
            "🌐 Live Interactive Prototype",
            "https://chainnetra.shelfio.in/",
            "chainnetra.shelfio.in",
            "Hosted deployment · Interactive graph tracer & case builder",
            c("059669")
        ),
        (
            "▶ Video Demonstration",
            "https://youtu.be/LiQ5pdvHW3k",
            "youtu.be/LiQ5pdvHW3k",
            "End-to-end investigation & Section 94/106 BNSS notice demo",
            c("DC2626")
        ),
        (
            "⌥ Source Code Repository",
            "https://github.com/Shlok-kapade/sih26183-chainnetra.git",
            "github.com/Shlok-kapade/sih26183-chainnetra",
            "FastAPI backend, React 19 UI, ML models & test suites",
            NAVY_ACCENT
        )
    ]

    item_h = (card_h - Inches(0.42)) / 3
    for i, (title, full_url, display_url, desc, color_acc) in enumerate(PROTOTYPE_LINKS):
        iy = bot_y + Inches(0.32) + i * item_h
        
        # Sub-card container box
        box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, col3_x + Inches(0.10), iy + Inches(0.02), col3_w - Inches(0.20), item_h - Inches(0.04))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = c("A7F3D0")
        box.line.width = Pt(0.75)
        
        tb_link = s.shapes.add_textbox(col3_x + Inches(0.14), iy + Inches(0.02), col3_w - Inches(0.28), item_h - Inches(0.04))
        tf_k = tb_link.text_frame
        tf_k.word_wrap = True
        tf_k.margin_left = tf_k.margin_right = tf_k.margin_top = tf_k.margin_bottom = Inches(0.02)
        
        # Line 1: Header / Title
        p1 = tf_k.paragraphs[0]
        p1.space_after = Pt(1)
        r_hdr = p1.add_run()
        r_hdr.text = title
        r_hdr.font.bold = True
        r_hdr.font.size = Pt(7.3)
        r_hdr.font.color.rgb = color_acc
        
        # Line 2: Clickable Hyperlink
        p2 = tf_k.add_paragraph()
        p2.space_after = Pt(1)
        r_lnk = p2.add_run()
        r_lnk.text = "🔗 " + display_url + " ↗"
        r_lnk.font.bold = True
        r_lnk.font.underline = True
        r_lnk.font.size = Pt(7.0)
        r_lnk.font.color.rgb = c("1D4ED8")  # Royal blue clickable link
        r_lnk.hyperlink.address = full_url
        
        # Line 3: Description
        p3 = tf_k.add_paragraph()
        r_dsc = p3.add_run()
        r_dsc.text = desc
        r_dsc.font.size = Pt(6.2)
        r_dsc.font.color.rgb = MUTED_TEXT

    add_footer(s, 3)

def build_slide4(prs):
    s = prs.slides[3]
    style_slide_header(s, "Feasibility & Viability")

    add_pill(s, "OPERATIONAL, LEGAL & TECHNICAL FEASIBILITY OF CHAINNETRA", Inches(0.5), Inches(1.18), Inches(5.2), Inches(0.28), bg_color=GREEN_PILL, font_size=8)
    
    feas_pillars = [
        ("TECHNICAL FEASIBILITY", "Lightweight & Scalable", "Runs on standard government cyber lab servers or state police data centers without requiring expensive specialized GPU/graph supercomputers."),
        ("ECONOMIC FEASIBILITY", "Zero Licensing Barrier", "Leverages decentralized public RPCs, open-source intelligence (OSINT), and crowd-sourced verified label databases, requiring ₹0 software licensing fees."),
        ("OPERATIONAL FEASIBILITY", "Built for Grassroots IOs", "Designed for investigating officers with zero blockchain engineering background—enter victim address, obtain actionable target VASP and pre-drafted freeze order."),
        ("LEGAL FEASIBILITY", "Courtroom Admissible", "Every on-chain metric is mathematically deterministic, eliminating AI hallucinations and satisfying the strict electronic evidence requirements of Indian courts.")
    ]
    
    card_w = Inches(2.95)
    card_h = Inches(1.25)
    for i, (title, sub, desc) in enumerate(feas_pillars):
        x = Inches(0.5) + i * Inches(3.12)
        add_clean_card(s, x, Inches(1.54), card_w, card_h, bg_color=GREEN_CARD, border_color=GREEN_BORD, accent_bar_color=GREEN_PILL)
        
        tb = add_textbox(s, x + Inches(0.15), Inches(1.61), card_w - Inches(0.25), card_h - Inches(0.15))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = title + "\n"
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = GREEN_PILL
        
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = sub + "\n"
        r2.font.bold = True
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = NAVY_HEADER
        
        p3 = tf.add_paragraph()
        r3 = p3.add_run()
        r3.text = desc
        r3.font.size = Pt(7)
        r3.font.color.rgb = DARK_TEXT

    mid_y = Inches(2.94)
    add_pill(s, "REAL-WORLD CYBER-FORENSIC CHALLENGES", Inches(0.5), mid_y, Inches(3.8), Inches(0.28), bg_color=ORANGE_PILL, font_size=8)
    add_pill(s, "CHAINNETRA FORENSIC MITIGATION STRATEGIES", Inches(6.7), mid_y, Inches(4.5), Inches(0.28), bg_color=NAVY_ACCENT, font_size=8)
    
    risks_matrix = [
        ("High-Velocity Peeling & Smurfing Layering: Fraudsters split illicit funds into dozens of sub-threshold transfers across 10+ hops to exhaust manual police tracing.",
         "Autonomous Recursive Taint Engine: Traverses complex branching DAGs, carrying exact proportional stolen dollar value through every split regardless of depth or fan-out."),
        ("Internal Smart Contract & DEX Obfuscation: Over 90% of laundered USDT moves through contract calls and liquidity swaps that regular explorers fail to display.",
         "Native Smart Contract Trace Parsing: Decodes TRC-20 and EVM internal call trees directly, capturing hidden fund movements and bridge transfers."),
        ("Stale & Misattributed Public Address Labels: Inaccurate open-source labels risk pointing investigators toward the wrong entity or causing illegal freezes.",
         "On-Chain Provenance & Verification: Every label is verified on-chain against historical volume and Proof-of-Reserves (PoR); unverified labels capped at PROBABLE/POSSIBLE."),
        ("Commercial Payment Gateways Mimicking Scams: Legitimate e-commerce payment processors aggregate funds similarly to scam consolidation funnels.",
         "Mandatory False-Positive Filtering: Behavioral suite actively checks for business hours, regular payroll sweeps, and merchant return loops before flagging."),
        ("Foreign Non-Compliant Exchanges (Offshore VASPs): Scammers deliberately funnel funds into non-FIU-IND compliant offshore exchanges that ignore Indian LEA notices.",
         "FIU-IND Status Intelligence & Global LEA Routing: Flags VASP compliance status (FIU-IND registered vs. offshore), routing notices to international LEA portals (Interpol/NCB).")
    ]
    
    ry = mid_y + Inches(0.35)
    for risk, strat in risks_matrix:
        add_clean_card(s, Inches(0.5), ry, Inches(6.0), Inches(0.66), bg_color=ORANGE_CARD, border_color=ORANGE_BORD, accent_bar_color=ORANGE_PILL)
        add_textbox(s, Inches(0.65), ry + Inches(0.05), Inches(5.75), Inches(0.56), text=risk, font_size=7.5, color=DARK_TEXT)
        
        add_clean_card(s, Inches(6.7), ry, Inches(6.13), Inches(0.66), bg_color=BLUE_CARD, border_color=BLUE_BORDER, accent_bar_color=NAVY_ACCENT)
        add_textbox(s, Inches(6.85), ry + Inches(0.05), Inches(5.88), Inches(0.56), text=strat, font_size=7.5, color=DARK_TEXT)
        
        ry += Inches(0.70)

    add_footer(s, 4)

def build_slide5(prs):
    s = prs.slides[4]
    style_slide_header(s, "Impact & Benefits")

    add_pill(s, "SCALE OF CYBER FRAUD IN INDIA & OPERATIONAL VALUE DELIVERY", Inches(0.5), Inches(1.18), Inches(5.5), Inches(0.28), bg_color=NAVY_ACCENT, font_size=8)
    
    stats = [
        ("₹22,845+ Crore", "Annual Cyber Fraud Losses in India", "Official MHA data reported across Indian citizens on NCRP in 2024, highlighting the critical urgency for automated tracing tools."),
        ("22.68+ Lakh Cases", "Registered Cybercrime Incidents", "Complaints registered on the National Cybercrime Reporting Portal (+42% YoY surge), overwhelming district investigation units."),
        ("Automated vs Manual", "Investigation Velocity", "Automated multi-hop graph traversal replaces days of manual blockchain explorer work — investigators get exchange identification instantly instead of 6–12 hours of manual analysis.")
    ]
    
    stat_x = Inches(0.5)
    for big_num, title, desc in stats:
        add_clean_card(s, stat_x, Inches(1.52), Inches(3.95), Inches(1.05), bg_color=BLUE_CARD, border_color=BLUE_BORDER, accent_bar_color=NAVY_ACCENT)
        tb = add_textbox(s, stat_x + Inches(0.18), Inches(1.60), Inches(3.7), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = big_num + "\n"
        r1.font.bold = True
        r1.font.size = Pt(14)
        r1.font.color.rgb = NAVY_ACCENT
        
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = title + ": "
        r2.font.bold = True
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = NAVY_HEADER
        r3 = p2.add_run()
        r3.text = desc
        r3.font.size = Pt(7)
        r3.font.color.rgb = DARK_TEXT
        
        stat_x += Inches(4.18)

    mid_y = Inches(2.70)
    add_pill(s, "TARGET USER AUDIENCE & OPERATIONAL VALUE DELIVERY", Inches(0.5), mid_y, Inches(4.5), Inches(0.28), bg_color=NAVY_ACCENT, font_size=8)
    
    personas = [
        ("DISTRICT IOs", "Cyber Cell Sub-Inspectors", "Empowers grassroots investigating officers with zero crypto training to trace suspect wallets and obtain ready-to-sign Section 94/106 BNSS (Sec 91/102 CrPC) notices within minutes."),
        ("STATE CYBER CELLS", "I4C & State Central Analysts", "Discovers hidden syndicate clusters where the same exchange deposit funnel collects stolen funds from dozens of complaints across multiple states, unmasking organized crime networks."),
        ("POLICE LEADERSHIP", "Supervisory Chiefs & Courts", "Delivers court-admissible Section 63 BSA (Sec 65B IEA) certified PDF case files with complete cryptographic SHA-256 hash trails for swift judicial conviction and asset recovery.")
    ]
    
    px = Inches(0.5)
    for role, user, desc in personas:
        add_clean_card(s, px, mid_y + Inches(0.35), Inches(3.95), Inches(1.15), bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=NAVY_ACCENT)
        tb = add_textbox(s, px + Inches(0.18), mid_y + Inches(0.42), Inches(3.7), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = role + " — " + user + "\n"
        r1.font.bold = True
        r1.font.size = Pt(8)
        r1.font.color.rgb = NAVY_ACCENT
        
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = desc
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = DARK_TEXT
        
        px += Inches(4.18)

    bot_y = Inches(4.34)
    add_pill(s, "OPERATIONAL WORKFLOW COMPARISON", Inches(0.5), bot_y, Inches(3.5), Inches(0.28), bg_color=GREEN_PILL, font_size=8)
    
    comp_y = bot_y + Inches(0.35)
    add_clean_card(s, Inches(0.5), comp_y, Inches(5.95), Inches(0.95), bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=MUTED_TEXT)
    tb_c1 = add_textbox(s, Inches(0.68), comp_y + Inches(0.1), Inches(5.65), Inches(0.8))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    p1 = tf_c1.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "CURRENT MANUAL INVESTIGATION BOTTLENECK\n"
    r1.font.bold = True
    r1.font.size = Pt(8)
    r1.font.color.rgb = MUTED_TEXT
    p2 = tf_c1.add_paragraph()
    r2 = p2.add_run()
    r2.text = "Investigating officers manually toggle public block explorers across 20 browser tabs. Tracing 3 hops takes 6–12 hours, frequently stalls at internal contract calls or mixers, and yields unstandardized notes inadmissible in court."
    r2.font.size = Pt(7.5)
    r2.font.color.rgb = DARK_TEXT

    add_clean_card(s, Inches(6.7), comp_y, Inches(6.13), Inches(0.95), bg_color=GREEN_CARD, border_color=GREEN_BORD, accent_bar_color=GREEN_PILL)
    tb_c2 = add_textbox(s, Inches(6.88), comp_y + Inches(0.1), Inches(5.85), Inches(0.8))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True
    p1 = tf_c2.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "WITH CHAINNETRA AUTOMATION\n"
    r1.font.bold = True
    r1.font.size = Pt(8)
    r1.font.color.rgb = GREEN_PILL
    p2 = tf_c2.add_paragraph()
    r2 = p2.add_run()
    r2.text = "Autonomous multi-hop tracing, DAR clustering, and VASP identification run fully automated. Instantly generates Section 94/106 BNSS (Sec 91/102 CrPC) legal freeze notices with SHA-256 evidence logs."
    r2.font.size = Pt(7.5)
    r2.font.color.rgb = DARK_TEXT

    bound_y = Inches(5.74)
    add_clean_card(s, Inches(0.5), bound_y, Inches(12.33), Inches(0.92), bg_color=ORANGE_CARD, border_color=ORANGE_BORD, accent_bar_color=ORANGE_PILL)
    tb_b = add_textbox(s, Inches(0.68), bound_y + Inches(0.08), Inches(12.0), Inches(0.78))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    
    p0 = tf_b.paragraphs[0]
    r0 = p0.add_run()
    r0.text = "ETHICAL, LEGAL & TECHNICAL BOUNDARIES OF CHAINNETRA\n"
    r0.font.bold = True
    r0.font.size = Pt(8)
    r0.font.color.rgb = ORANGE_PILL
    
    p1 = tf_b.add_paragraph()
    r1 = p1.add_run()
    r1.text = "• Custodial Institution Identification, Not Private Doxxing: Public blockchain data identifies regulated custodial entities (VASPs); private citizen KYC remains protected until lawful subpoena execution.\n• Objective Taint Evidence vs. Criminal Guilt: The system outputs mathematical contamination scores and behavioral anomaly metrics; formal guilt determination remains the sole prerogative of the court.\n• Open Integration Standard: Designed with modular REST APIs ready for direct native integration into I4C NCRP and CFCFRMS portals."
    r1.font.size = Pt(7)
    r1.font.color.rgb = DARK_TEXT

    add_footer(s, 5)

def build_slide6(prs):
    s = prs.slides[5]
    style_slide_header(s, "Research & References")

    add_pill(s, "INDIAN STATUTORY FRAMEWORK, FORENSIC RESEARCH & COMPLIANCE ASSURANCE", Inches(0.5), Inches(1.18), Inches(6.5), Inches(0.28), bg_color=NAVY_ACCENT, font_size=8)
    
    col_w = Inches(3.95)
    col_h = Inches(4.82)
    col_y = Inches(1.54)
    
    # Column 1: Indian Legal & Statutory Mandates
    add_clean_card(s, Inches(0.5), col_y, col_w, col_h, bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=NAVY_ACCENT)
    tb1 = add_textbox(s, Inches(0.68), col_y + Inches(0.12), col_w - Inches(0.3), col_h - Inches(0.25))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p0 = tf1.paragraphs[0]
    r0 = p0.add_run()
    r0.text = "INDIAN STATUTORY & PROCEDURAL MANDATES\n\n"
    r0.font.bold = True
    r0.font.size = Pt(8.5)
    r0.font.color.rgb = NAVY_ACCENT
    
    c1_items = [
        ("MHA / I4C NCRP-CFCFRMS SOP (Jan 2026):", "Establishes standard protocol directing LEAs to conduct forensic VDA tracing to identify custodial exchange nodes for non-onboarded VASPs."),
        ("Section 94 BNSS 2023 (Sec 91 CrPC):", "Statutory summons authority empowering investigating officers to requisition KYC records, login IP histories, and linked accounts from exchanges."),
        ("Section 106 BNSS 2023 (Sec 102 CrPC):", "Police power to issue immediate property seizure and balance freezing directives on fraud-linked VASP custodial accounts."),
        ("Section 63 BSA 2023 (Sec 65B IEA):", "Mandates cryptographic SHA-256 hash certification and immutable chain-of-custody for electronic evidence admissibility in Indian courts."),
        ("PMLA Gazette S.O. 1072(E) & FIU-IND:", "Mandates anti-money laundering registration and reporting compliance for all Virtual Digital Asset Service Providers operating in India.")
    ]
    for h, b in c1_items:
        p = tf1.add_paragraph()
        r1 = p.add_run()
        r1.text = h + " "
        r1.font.bold = True
        r1.font.size = Pt(7.5)
        r1.font.color.rgb = NAVY_HEADER
        r2 = p.add_run()
        r2.text = b + "\n\n"
        r2.font.size = Pt(7)
        r2.font.color.rgb = DARK_TEXT

    # Column 2: Academic Forensics & Threat Patterns
    add_clean_card(s, Inches(4.7), col_y, col_w, col_h, bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=ORANGE_PILL)
    tb2 = add_textbox(s, Inches(4.88), col_y + Inches(0.12), col_w - Inches(0.3), col_h - Inches(0.25))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    
    p0 = tf2.paragraphs[0]
    r0 = p0.add_run()
    r0.text = "ACADEMIC FORENSICS & THREAT INTELLIGENCE\n\n"
    r0.font.bold = True
    r0.font.size = Pt(8.5)
    r0.font.color.rgb = ORANGE_PILL
    
    c2_items = [
        ("UNODC Southeast Asia Crime Report (2024):", "Identifies TRON-based USDT as the predominant currency for regional scam syndicates, confirming the necessity of specialized TRC-20 tracking."),
        ("TRM Labs Illicit Crypto Report (2025):", "Documents that 58%+ of global illicit stablecoin volume moves via TRON due to sub-dollar fees, validating ChainNetra's deep TRC-20 trace parsing."),
        ("Enforcement Directorate (ED) Precedents:", "Case studies (₹285 Cr scam, ₹391 Cr syndicate) prove illicit proceeds systematically off-ramp via P2P networks into Indian bank accounts."),
        ("Victor (2020) Deposit Address Clustering:", "Peer-reviewed heuristic establishing deposit-address-reuse patterns and sweeping thresholds for custodial exchange attribution."),
        ("Meiklejohn et al. Taint Tracking Models:", "Scientific validation proving Proportional Haircut Taint propagation is superior to FIFO in split, merge, and mixing laundering scenarios.")
    ]
    for h, b in c2_items:
        p = tf2.add_paragraph()
        r1 = p.add_run()
        r1.text = h + " "
        r1.font.bold = True
        r1.font.size = Pt(7.5)
        r1.font.color.rgb = NAVY_HEADER
        r2 = p.add_run()
        r2.text = b + "\n\n"
        r2.font.size = Pt(7)
        r2.font.color.rgb = DARK_TEXT

    # Column 3: System Integrity & Production Verification
    add_clean_card(s, Inches(8.9), col_y, col_w, col_h, bg_color=CARD_BG, border_color=CARD_BORDER, accent_bar_color=GREEN_PILL)
    tb3 = add_textbox(s, Inches(9.08), col_y + Inches(0.12), col_w - Inches(0.3), col_h - Inches(0.25))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    
    p0 = tf3.paragraphs[0]
    r0 = p0.add_run()
    r0.text = "SYSTEM INTEGRITY & PRODUCTION VERIFICATION\n\n"
    r0.font.bold = True
    r0.font.size = Pt(8.5)
    r0.font.color.rgb = GREEN_PILL
    
    c3_items = [
        ("Forensic Anomaly Suite Validation:", "Tested against realistic synthetic laundering patterns: peel chains, rapid forwarding, smurfing, dormancy bursts, and wash churning."),
        ("OFAC SDN Sanctioned Entity Ingestion:", "Incorporates 400+ verified cryptocurrency addresses from global sanctions lists, automatically flagged as Tier-1 CONFIRMED sanctions risks."),
        ("Proof-of-Reserves (PoR) Verification:", "Exchange-published reserve addresses (Binance, OKX, CoinDCX, WazirX) ingested and verified on-chain to maintain zero-cost attribution precision."),
        ("Cryptographic Chain-of-Custody:", "Every raw JSON response from external RPCs is stored alongside its SHA-256 hash in PostgreSQL to ensure unbroken chain-of-custody in court."),
        ("Designed for National Scale (NCRP / CFCFRMS):", "Modular API architecture ready for direct integration into I4C's national cybercrime reporting infrastructure and state cyber cells.")
    ]
    for h, b in c3_items:
        p = tf3.add_paragraph()
        r1 = p.add_run()
        r1.text = h + " "
        r1.font.bold = True
        r1.font.size = Pt(7.5)
        r1.font.color.rgb = NAVY_HEADER
        r2 = p.add_run()
        r2.text = b + "\n\n"
        r2.font.size = Pt(7)
        r2.font.color.rgb = DARK_TEXT

    add_textbox(s, Inches(0.5), Inches(6.52), Inches(12.33), Inches(0.28), 
                text="Compliance Assurance: All blockchain queries adhere strictly to public API rate terms. No proprietary databases scraped. Every label records source, license, and capture timestamp.",
                font_size=7.5, color=MUTED_TEXT, align=PP_ALIGN.CENTER)

    add_footer(s, 6)

def main():
    template_path = "docs/SIH_2026_PPT_Template.pptx"
    output_path = "docs/ChainNetra_SIH26183_code2trip.pptx"
    
    prs = Presentation(template_path)
    
    if len(prs.slides) > 6:
        try:
            prs.slides._sldIdLst.remove(list(prs.slides._sldIdLst)[6])
        except Exception:
            pass
            
    print("Building Slide 1...")
    build_slide1(prs)
    print("Building Slide 2...")
    build_slide2(prs)
    print("Building Slide 3...")
    build_slide3(prs)
    print("Building Slide 4...")
    build_slide4(prs)
    print("Building Slide 5...")
    build_slide5(prs)
    print("Building Slide 6...")
    build_slide6(prs)
    
    prs.save(output_path)
    print(f"Saved master presentation to {output_path}")

if __name__ == "__main__":
    main()
