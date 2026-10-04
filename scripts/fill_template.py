import sys
from pptx import Presentation

def replace_text(shape, new_text):
    if shape.has_text_frame:
        shape.text = new_text

def fill_template(template_path, output_path):
    prs = Presentation(template_path)
    
    # --- Slide 1 (Cover) ---
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.name == 'Subtitle 3':
            shape.text = ""
        elif shape.name == 'TextBox 9':
            shape.text = (
                "Problem Statement ID: SIH26183\n"
                "Problem Statement Title: Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics\n"
                "Theme: Blockchain & Cybersecurity\n"
                "PS Category: Software\n"
                "Organisation: Ministry of Home Affairs\n"
                "Team ID: 26183\n"
                "Team Name: code2trip\n"
                "Institute: [Your Institute Name]"
            )

    # --- Slide 2 (Proposed Solution) ---
    s2 = prs.slides[1]
    for shape in s2.shapes:
        if shape.name == 'Title 1':
            shape.text = "ChainNetra — Which Exchange Received the Money?"
        elif shape.name == 'TextBox 8':
            shape.text = (
                "PROPOSED SOLUTION: RETRIEVE → NORMALISE → TRACE → GRAPH+PATTERNS → ATTRIBUTE → REPORT\n\n"
                "HOW IT ADDRESSES THE PROBLEM:\n"
                "• An address names nobody. ChainNetra names the institution behind the deposit address.\n"
                "• Two or three hops by hand takes hours. ChainNetra automatically expands branches and finishes in ~90 seconds.\n"
                "• 'Probably Binance' is a guess. ChainNetra returns CONFIRMED/PROBABLE/UNATTRIBUTED with hard evidence.\n\n"
                "INNOVATION AND UNIQUENESS:\n"
                "1. Three tiers that cannot be mixed up: The DB rejects any claim that isn't CONFIRMED, PROBABLE or UNATTRIBUTED.\n"
                "2. Confidence is only as strong as its weakest link (0.90 deposit × 0.80 exchange = 0.72).\n"
                "3. Seven named reasons a trace stops.\n"
                "4. Every detector lists its own false alarms to prevent false positives."
            )
        elif shape.has_text_frame and "Your Team Name" in shape.text:
            shape.text = "code2trip"
            
    # --- Slide 3 (Technical Approach) ---
    s3 = prs.slides[2]
    for shape in s3.shapes:
        if shape.name == 'Title 1':
            shape.text = "TECHNICAL APPROACH"
        elif shape.name == 'TextBox 8':
            shape.text = (
                "METHODOLOGY AND PROCESS FOR IMPLEMENTATION:\n"
                "1. INPUT: Suspect wallet address + chain + asset + reported amount.\n"
                "2. RETRIEVE & NORMALISE: Pull from TronGrid/Etherscan, retry, hash every raw reply, map to single Transfer model.\n"
                "3. ANALYSE: Taint engine, stop conditions, 6 pattern detectors, deposit-address score.\n"
                "4. OUTPUT: Exchange named with tier + evidence. PDF freeze request generated with every hop hash.\n\n"
                "TECHNOLOGIES USED:\n"
                "• Frontend: React, TypeScript, Vite, Tailwind, Cytoscape.js\n"
                "• Backend: Python 3.12, FastAPI, SQLAlchemy, Pydantic\n"
                "• Data: PostgreSQL 16\n"
                "• Chain Data: TronGrid, TronScan, Blockscout, Etherscan\n"
                "• Reports & AI: ReportLab, NetworkX, LightGBM, Docker"
            )
        elif shape.has_text_frame and "Your Team Name" in shape.text:
            shape.text = "code2trip"

    # --- Slide 4 (Feasibility) ---
    s4 = prs.slides[3]
    for shape in s4.shapes:
        if shape.name == 'TextBox 8':
            shape.text = (
                "FEASIBILITY AND VIABILITY:\n"
                "• IT ALREADY RUNS: A suspect address goes in; a named exchange, risk score, and PDF come out.\n"
                "• NO PAID DATA NEEDED: Uses free public APIs and openly licensed datasets.\n"
                "• ORDINARY DEPLOYMENT: One server (Python, PostgreSQL, Docker). No cluster, no GPU needed.\n"
                "• THE SAME ANSWER EVERY TIME: Exact fractions, deterministic tracing.\n\n"
                "CHALLENGES & STRATEGIES:\n"
                "• API Limits: Cached traces stay fast; work to an address budget.\n"
                "• Dirty Public Labels: We check every label on-chain ourselves.\n"
                "• Internal Transfers: We fetch and treat internal transfers like any other to avoid missing funds.\n"
                "• False Alarms: Behaviour alone never gives CONFIRMED tier."
            )
        elif shape.has_text_frame and "Your Team Name" in shape.text:
            shape.text = "code2trip"

    # --- Slide 5 (Impact) ---
    s5 = prs.slides[4]
    for shape in s5.shapes:
        if shape.name == 'TextBox 8':
            shape.text = (
                "POTENTIAL IMPACT:\n"
                "• 22,68,346 cybercrime incidents reported in 2024; ₹22,845 cr lost.\n"
                "• Primary User (District Cyber Cell): Types in victim address and gets an evidenced exchange to serve.\n"
                "• Secondary User (I4C Analyst): Links multiple unconnected cases sharing the same deposit address.\n\n"
                "BENEFITS (WITH CHAINNETRA vs TODAY):\n"
                "• Reaches the exchange in time (90 seconds instead of hours/days).\n"
                "• Finds victims who never complained (backward tracing).\n"
                "• No per-seat licence cost (runs on public data).\n"
                "• Every answer can be checked with stored raw reply hashes.\n\n"
                "LIMITS: Does not name a person; does not decide fraud happened; not plugged into NCRP directly."
            )
        elif shape.has_text_frame and "Your Team Name" in shape.text:
            shape.text = "code2trip"

    # --- Slide 6 (Research) ---
    s6 = prs.slides[5]
    for shape in s6.shapes:
        if shape.name == 'TextBox 8':
            shape.text = (
                "GOVERNMENT MANDATE & LAW:\n"
                "• MHA / I4C SOP (Jan 2026): Officers may conduct VDA forensic analysis.\n"
                "• Lok Sabha Unstarred Q.432 (Dec 2025): ₹7,130 cr saved via CFCFRMS.\n\n"
                "WHY TRON AND USDT:\n"
                "• UNODC (Jan 2024): USDT on TRON is a preferred choice for regional cyberfraud.\n"
                "• TRM Labs (Feb 2025): 58% of illicit crypto volume in 2024 was on TRON.\n\n"
                "DATA SOURCES:\n"
                "• TronGrid, Blockscout, Etherscan.\n"
                "• OFAC SDN sanctioned addresses.\n"
                "• Note: We never scrape explorer label databases (terms forbid it). Every label we ship records its source and capture date."
            )
        elif shape.has_text_frame and "Your Team Name" in shape.text:
            shape.text = "code2trip"

    # Set team name on footer or other text boxes where it might be present as "@SIH Idea submission- Template"
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                if "@SIH Idea submission" in shape.text:
                    shape.text = "SIH 2026 | PS SIH26183 — ChainNetra"

    # Delete slide 7 (Instructions) if it exists
    if len(prs.slides) > 6:
        xml_slides = prs.slides._sldIdLst
        slides = list(xml_slides)
        xml_slides.remove(slides[6])

    prs.save(output_path)
    print(f"Template filled and saved to {output_path}")

if __name__ == "__main__":
    fill_template(sys.argv[1], sys.argv[2])
