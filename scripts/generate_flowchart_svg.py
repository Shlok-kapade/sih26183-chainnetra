"""
Generate high-resolution forensic architecture flowchart SVG for ChainNetra (SIH26183).
Refined to focus 100% on cyber-forensic intelligence, MHA/I4C investigative workflows,
and Indian legal compliance (BNSS, BSA, CrPC, IEA, PMLA). Zero developer jargon.
"""

import os
import subprocess

def create_flowchart_svg(output_svg_path: str):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 660" width="2400" height="660" style="background-color: transparent; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Card Shadow -->
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="118%" filterUnits="userSpaceOnUse">
      <feGaussianBlur in="SourceAlpha" stdDeviation="6"/>
      <feOffset dx="0" dy="5"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.12"/></feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Gradients for Phase Headers -->
    <linearGradient id="gradPhase1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f2240"/>
      <stop offset="100%" stop-color="#1e3a8a"/>
    </linearGradient>
    <linearGradient id="gradPhase2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
    <linearGradient id="gradPhase3" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0f766e"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="gradPhase4" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
  </defs>

  <!-- ==================== PHASE 1: INGESTION & DATA LEDGER ==================== -->
  <g transform="translate(40, 20)">
    <!-- Container Card -->
    <rect x="0" y="0" width="530" height="600" rx="14" ry="14" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="url(#cardShadow)"/>
    <!-- Top Phase Banner -->
    <rect x="0" y="0" width="530" height="65" rx="14" ry="14" fill="url(#gradPhase1)"/>
    <rect x="0" y="45" width="530" height="20" fill="url(#gradPhase1)"/>
    <circle cx="42" cy="32" r="18" fill="#ffffff" opacity="0.2"/>
    <text x="42" y="38" fill="#ffffff" font-size="18" font-weight="800" text-anchor="middle">01</text>
    <text x="75" y="32" fill="#ffffff" font-size="16" font-weight="700" letter-spacing="0.5">COMPLAINT INTAKE &amp; SCAN</text>
    <text x="75" y="52" fill="#93c5fd" font-size="12" font-weight="500">Victim Wallet Intake &amp; Multi-Chain Data Pull</text>

    <!-- Sub-Box 1.1 -->
    <rect x="25" y="85" width="480" height="135" rx="8" ry="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="25" y="85" width="6" height="135" rx="3" ry="3" fill="#0f2240"/>
    <text x="45" y="112" fill="#0f2240" font-size="15" font-weight="700">Victim Complaint Intake (1930 / NCRP)</text>
    <text x="45" y="135" fill="#475569" font-size="13">• Ingests suspect wallet address &amp; fraudulent transfer timestamp</text>
    <text x="45" y="157" fill="#475569" font-size="13">• Auto-detects target network: TRON (TRC-20 USDT), Ethereum, Bitcoin</text>
    <text x="45" y="179" fill="#475569" font-size="13">• Anchors complaint transaction and calculates initial stolen loss</text>
    <text x="45" y="201" fill="#0284c7" font-size="12" font-weight="600">INPUT: Suspect Address | Initial Loss Amount | Incident Time</text>

    <!-- Internal Connector Down -->
    <path d="M 265 220 L 265 245" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,3"/>

    <!-- Sub-Box 1.2 -->
    <rect x="25" y="245" width="480" height="165" rx="8" ry="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="25" y="245" width="6" height="165" rx="3" ry="3" fill="#1e3a8a"/>
    <text x="45" y="272" fill="#1e3a8a" font-size="15" font-weight="700">Multi-Chain Tracking Connectors</text>
    <text x="45" y="295" fill="#475569" font-size="13">• Fast automated querying across decentralized blockchain RPC nodes</text>
    <text x="45" y="317" fill="#475569" font-size="13">• Decodes internal smart contract transfers (TRC-20 &amp; EVM calls)</text>
    <text x="45" y="339" fill="#475569" font-size="13">• Uncovers hidden token hops missed by standard block explorers</text>
    <text x="45" y="361" fill="#475569" font-size="13">• Sub-second caching ensures lightning-fast investigative lookups</text>
    <text x="45" y="388" fill="#0284c7" font-size="12" font-weight="600">KEY CAPABILITY: Decodes Hidden Internal Contract Calls</text>

    <!-- Internal Connector Down -->
    <path d="M 265 410 L 265 435" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,3"/>

    <!-- Sub-Box 1.3 -->
    <rect x="25" y="435" width="480" height="135" rx="8" ry="8" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1"/>
    <rect x="25" y="435" width="6" height="135" rx="3" ry="3" fill="#2563eb"/>
    <text x="45" y="462" fill="#1e3a8a" font-size="15" font-weight="700">Tamper-Proof Audit Custody Ledger</text>
    <text x="45" y="485" fill="#334155" font-size="13">• Computes cryptographic SHA-256 hash of all retrieved raw data</text>
    <text x="45" y="507" fill="#334155" font-size="13">• Immutable audit record ensures absolute evidence integrity</text>
    <text x="45" y="529" fill="#334155" font-size="13">• Compliant with Section 63 BSA 2023 (Section 65B Evidence Act)</text>
    <text x="45" y="553" fill="#1d4ed8" font-size="12" font-weight="700">LEGAL CERTAINTY: Tamper-Evident Evidence Certificate</text>
  </g>

  <!-- Big Flow Arrow 1 -> 2 -->
  <g transform="translate(585, 300)">
    <circle cx="20" cy="20" r="18" fill="#e0f2fe"/>
    <path d="M 12 20 L 26 20 M 20 14 L 26 20 L 20 26" stroke="#0284c7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  </g>

  <!-- ==================== PHASE 2: CANONICAL DAG & TAINT ENGINE ==================== -->
  <g transform="translate(640, 20)">
    <!-- Container Card -->
    <rect x="0" y="0" width="530" height="600" rx="14" ry="14" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="url(#cardShadow)"/>
    <!-- Top Phase Banner -->
    <rect x="0" y="0" width="530" height="65" rx="14" ry="14" fill="url(#gradPhase2)"/>
    <rect x="0" y="45" width="530" height="20" fill="url(#gradPhase2)"/>
    <circle cx="42" cy="32" r="18" fill="#ffffff" opacity="0.2"/>
    <text x="42" y="38" fill="#ffffff" font-size="18" font-weight="800" text-anchor="middle">02</text>
    <text x="75" y="32" fill="#ffffff" font-size="16" font-weight="700" letter-spacing="0.5">MULTI-HOP FUND TRACING</text>
    <text x="75" y="52" fill="#bfdbfe" font-size="12" font-weight="500">Automated "Follow the Money" Pathfinding</text>

    <!-- Sub-Box 2.1 -->
    <rect x="25" y="85" width="480" height="135" rx="8" ry="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="25" y="85" width="6" height="135" rx="3" ry="3" fill="#1e40af"/>
    <text x="45" y="112" fill="#1e40af" font-size="15" font-weight="700">Unified Blockchain Data Normalization</text>
    <text x="45" y="135" fill="#475569" font-size="13">• Standardizes TRON, Ethereum, and Bitcoin into a single data model</text>
    <text x="45" y="157" fill="#475569" font-size="13">• High-precision Decimal math prevents rounding loss during splits</text>
    <text x="45" y="179" fill="#475569" font-size="13">• Accurately tracks gas fees, token swaps, and liquidity pools</text>
    <text x="45" y="201" fill="#2563eb" font-size="12" font-weight="600">UNIFIED MODEL: Standardized Multi-Chain State</text>

    <!-- Internal Connector Down -->
    <path d="M 265 220 L 265 245" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,3"/>

    <!-- Sub-Box 2.2 -->
    <rect x="25" y="245" width="480" height="165" rx="8" ry="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="25" y="245" width="6" height="165" rx="3" ry="3" fill="#2563eb"/>
    <text x="45" y="272" fill="#1e40af" font-size="15" font-weight="700">Multi-Hop Fund Navigation Engine</text>
    <text x="45" y="295" fill="#475569" font-size="13">• Autonomously traces stolen funds across 10+ hops in &lt;90 seconds</text>
    <text x="45" y="317" fill="#475569" font-size="13">• Loop &amp; wash-trading filter removes circular scammer traps</text>
    <text x="45" y="339" fill="#475569" font-size="13">• Detects cross-chain bridge transfers jumping between blockchains</text>
    <text x="45" y="361" fill="#475569" font-size="13">• Beats the 1–2 hour fraudster P2P cashout window</text>
    <text x="45" y="388" fill="#2563eb" font-size="12" font-weight="600">SPEED ADVANTAGE: &lt;90s Multi-Hop Graph Traversal</text>

    <!-- Internal Connector Down -->
    <path d="M 265 410 L 265 435" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,3"/>

    <!-- Sub-Box 2.3 -->
    <rect x="25" y="435" width="480" height="135" rx="8" ry="8" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1"/>
    <rect x="25" y="435" width="6" height="135" rx="3" ry="3" fill="#3b82f6"/>
    <text x="45" y="462" fill="#1e40af" font-size="15" font-weight="700">Precise Stolen Fund Taint Tracking</text>
    <text x="45" y="485" fill="#334155" font-size="13">• Mathematically tracks exact stolen fund dilution across multi-splits</text>
    <text x="45" y="507" fill="#334155" font-size="13">• Carries true victim dollar fractions through every intermediate hop</text>
    <text x="45" y="529" fill="#334155" font-size="13">• Prevents false dilution when scammers mix illicit funds with clean tokens</text>
    <text x="45" y="553" fill="#1d4ed8" font-size="12" font-weight="700">MATHEMATICAL RIGOR: Exact Stolen Fraction Carried</text>
  </g>

  <!-- Big Flow Arrow 2 -> 3 -->
  <g transform="translate(1185, 300)">
    <circle cx="20" cy="20" r="18" fill="#d1fae5"/>
    <path d="M 12 20 L 26 20 M 20 14 L 26 20 L 20 26" stroke="#059669" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  </g>

  <!-- ==================== PHASE 3: BEHAVIORAL ANALYTICS & DAR ==================== -->
  <g transform="translate(1240, 20)">
    <!-- Container Card -->
    <rect x="0" y="0" width="530" height="600" rx="14" ry="14" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="url(#cardShadow)"/>
    <!-- Top Phase Banner -->
    <rect x="0" y="0" width="530" height="65" rx="14" ry="14" fill="url(#gradPhase3)"/>
    <rect x="0" y="45" width="530" height="20" fill="url(#gradPhase3)"/>
    <circle cx="42" cy="32" r="18" fill="#ffffff" opacity="0.2"/>
    <text x="42" y="38" fill="#ffffff" font-size="18" font-weight="800" text-anchor="middle">03</text>
    <text x="75" y="32" fill="#ffffff" font-size="16" font-weight="700" letter-spacing="0.5">EXCHANGE &amp; MULE IDENTIFICATION</text>
    <text x="75" y="52" fill="#a7f3d0" font-size="12" font-weight="500">Deposit Wallet Clustering &amp; Scam Anomaly Suite</text>

    <!-- Sub-Box 3.1 -->
    <rect x="25" y="85" width="480" height="145" rx="8" ry="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="25" y="85" width="6" height="145" rx="3" ry="3" fill="#0f766e"/>
    <text x="45" y="112" fill="#0f766e" font-size="15" font-weight="700">Exchange Deposit Wallet Clustering</text>
    <text x="45" y="135" fill="#475569" font-size="13">• Identifies unlabelled exchange deposit funnels from wallet behavior</text>
    <text x="45" y="157" fill="#475569" font-size="13">• Detects addresses receiving from multiple victims &amp; sweeping to exchanges</text>
    <text x="45" y="179" fill="#475569" font-size="13">• Uncovers private deposit gateways without needing internal exchange access</text>
    <text x="45" y="201" fill="#475569" font-size="13">• Groups related mule accounts under the same custodial destination exchange</text>
    <text x="45" y="222" fill="#0d9488" font-size="12" font-weight="600">INNOVATION: Uncovers Unlabelled Exchange Deposit Wallets</text>

    <!-- Internal Connector Down -->
    <path d="M 265 230 L 265 255" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,3"/>

    <!-- Sub-Box 3.2 -->
    <rect x="25" y="255" width="480" height="165" rx="8" ry="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="25" y="255" width="6" height="165" rx="3" ry="3" fill="#059669"/>
    <text x="45" y="280" fill="#065f46" font-size="15" font-weight="700">Scam Pattern &amp; Anomaly Detection Suite</text>
    <text x="45" y="302" fill="#475569" font-size="12.5">• Peel Chains: Flags rapid micro-skimming across sequential wallets</text>
    <text x="45" y="322" fill="#475569" font-size="12.5">• Rapid Forwarding: Flags immediate fund pass-through (&lt;15 mins)</text>
    <text x="45" y="342" fill="#475569" font-size="12.5">• Smurfing / Structuring: Detects split amounts below reporting thresholds</text>
    <text x="45" y="362" fill="#475569" font-size="12.5">• Dormancy Burst &amp; Fan-Out: Flags reactivated scammer accounts</text>
    <text x="45" y="382" fill="#475569" font-size="12.5">• Round-Trip Churning: Detects cyclic wash transfers meant to confuse tracers</text>
    <text x="45" y="407" fill="#059669" font-size="12" font-weight="600">BEHAVIORAL SUITE: Flags Smurfing, Peeling &amp; Velocity</text>

    <!-- Internal Connector Down -->
    <path d="M 265 420 L 265 445" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,3"/>

    <!-- Sub-Box 3.3 -->
    <rect x="25" y="445" width="480" height="135" rx="8" ry="8" fill="#ecfdf5" stroke="#a7f3d0" stroke-width="1"/>
    <rect x="25" y="445" width="6" height="135" rx="3" ry="3" fill="#10b981"/>
    <text x="45" y="470" fill="#065f46" font-size="15" font-weight="700">4-Tier Verified Evidence Rating</text>
    <text x="45" y="492" fill="#334155" font-size="13">• CONFIRMED: Verified exchange hot/cold wallet or sanctions list (OFAC)</text>
    <text x="45" y="512" fill="#334155" font-size="13">• PROBABLE: High-confidence sweep pattern directly to verified exchange</text>
    <text x="45" y="532" fill="#334155" font-size="13">• POSSIBLE / UNATTRIBUTED: Clear flag preventing guesswork</text>
    <text x="45" y="555" fill="#047857" font-size="12" font-weight="700">PROTECTION: Protects Police from Wrongful Freezes</text>
  </g>

  <!-- Big Flow Arrow 3 -> 4 -->
  <g transform="translate(1785, 300)">
    <circle cx="20" cy="20" r="18" fill="#fef3c7"/>
    <path d="M 12 20 L 26 20 M 20 14 L 26 20 L 20 26" stroke="#d97706" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  </g>

  <!-- ==================== PHASE 4: LEGAL DOSSIER & ACTIONS ==================== -->
  <g transform="translate(1840, 20)">
    <!-- Container Card -->
    <rect x="0" y="0" width="520" height="600" rx="14" ry="14" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" filter="url(#cardShadow)"/>
    <!-- Top Phase Banner -->
    <rect x="0" y="0" width="520" height="65" rx="14" ry="14" fill="url(#gradPhase4)"/>
    <rect x="0" y="45" width="520" height="20" fill="url(#gradPhase4)"/>
    <circle cx="42" cy="32" r="18" fill="#ffffff" opacity="0.2"/>
    <text x="42" y="38" fill="#ffffff" font-size="18" font-weight="800" text-anchor="middle">04</text>
    <text x="75" y="32" fill="#ffffff" font-size="16" font-weight="700" letter-spacing="0.5">LEGAL FREEZE &amp; COURT DOSSIER</text>
    <text x="75" y="52" fill="#fde68a" font-size="12" font-weight="500">Actionable Law Enforcement Deliverables</text>

    <!-- Sub-Box 4.1 -->
    <rect x="25" y="85" width="470" height="135" rx="8" ry="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="25" y="85" width="6" height="135" rx="3" ry="3" fill="#b45309"/>
    <text x="45" y="112" fill="#92400e" font-size="15" font-weight="700">Target Exchange &amp; Nodal Officer Directory</text>
    <text x="45" y="135" fill="#475569" font-size="13">• Identifies destination exchange (Binance, Bybit, KuCoin, WazirX, etc.)</text>
    <text x="45" y="157" fill="#475569" font-size="13">• Pinpoints specific recipient deposit address and exchange vault</text>
    <text x="45" y="179" fill="#475569" font-size="13">• Checks FIU-IND registration status &amp; designated LEA Nodal Desk</text>
    <text x="45" y="201" fill="#b45309" font-size="12" font-weight="600">ACTIONABLE: Direct Subpoena &amp; Freeze Requisition Target</text>

    <!-- Internal Connector Down -->
    <path d="M 260 220 L 260 245" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,3"/>

    <!-- Sub-Box 4.2 -->
    <rect x="25" y="245" width="470" height="165" rx="8" ry="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="25" y="245" width="6" height="165" rx="3" ry="3" fill="#d97706"/>
    <text x="45" y="272" fill="#92400e" font-size="15" font-weight="700">Instant Statutory Notices (Sec 94/106 BNSS)</text>
    <text x="45" y="295" fill="#475569" font-size="13">• Auto-generates statutory summons notice under Section 94 BNSS (91 CrPC)</text>
    <text x="45" y="317" fill="#475569" font-size="13">• Auto-generates property freeze order under Section 106 BNSS (102 CrPC)</text>
    <text x="45" y="339" fill="#475569" font-size="13">• Pre-populates recipient exchange legal desk and exact transaction hashes</text>
    <text x="45" y="361" fill="#475569" font-size="13">• Incorporates PMLA S.O. 1072(E) compliance &amp; MHA CFCFRMS mandates</text>
    <text x="45" y="388" fill="#d97706" font-size="12" font-weight="600">STATUTORY MANDATE: Instant Notice Ready for IO Signature</text>

    <!-- Internal Connector Down -->
    <path d="M 260 410 L 260 435" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,3"/>

    <!-- Sub-Box 4.3 -->
    <rect x="25" y="435" width="470" height="135" rx="8" ry="8" fill="#fffbeb" stroke="#fde68a" stroke-width="1"/>
    <rect x="25" y="435" width="6" height="135" rx="3" ry="3" fill="#f59e0b"/>
    <text x="45" y="462" fill="#92400e" font-size="15" font-weight="700">Court-Admissible Dossier &amp; Visual Flowchart</text>
    <text x="45" y="485" fill="#334155" font-size="13">• Tamper-evident PDF case file with Section 63 BSA electronic certificate</text>
    <text x="45" y="507" fill="#334155" font-size="13">• Visual money-flow chart showing unbroken trail from victim to exchange</text>
    <text x="45" y="529" fill="#334155" font-size="13">• Ready for direct integration into MHA I4C NCRP / CFCFRMS portal</text>
    <text x="45" y="553" fill="#b45309" font-size="12" font-weight="700">DELIVERABLE: Comprehensive Case Investigation Dossier</text>
  </g>
</svg>'''
    with open(output_svg_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Wrote SVG to {output_svg_path}")

if __name__ == '__main__':
    svg_path = "assets/chainnetra_pipeline_architecture.svg"
    png_path = "assets/chainnetra_pipeline_architecture.png"
    create_flowchart_svg(svg_path)
    cmd = f"resvg --width 2400 {svg_path} {png_path}"
    subprocess.run(cmd, shell=True, check=True)
    print(f"Rendered PNG to {png_path}")
