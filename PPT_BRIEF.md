# ChainNetra — SIH 2026 PPT Brief (for the teammate making the slides)

Everything you need is in this file. You do not need to read the code or the other specs (they are in `docs/spec/` if you want depth).

## 0. Context in 60 seconds
- **Event:** Smart India Hackathon 2026. **Problem Statement:** SIH26183 — *Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics*. **Organisation:** Ministry of Home Affairs (I4C). **Category:** Software. **Theme:** Blockchain & Cybersecurity.
- **Our project:** **ChainNetra** — a free/open-source platform that takes a victim-reported wallet address, traces the money across wallets/chains, finds where it was cashed out (exchange/VASP or another exit route), scores risk, ranks cases by freeze urgency, and produces an evidence-hashed report + draft freeze request.
- **Status honesty (important):** at idea stage the system is **proposed/being built**. Do NOT claim accuracy numbers, user counts or "deployed" anything. Where a slide needs results, write "Target / planned metric" or leave the marked placeholder `[FILL FROM docs/evaluation/RESULTS.md]`. Use "proposed", "designed to", "will".
- **Format:** use the **official SIH PPT template** from the portal (it defines the sections and slide limit). The section order below maps to the usual template headings: Problem Statement, Proposed Solution, Innovation, Technical Approach, Feasibility, Implementation, Impact. If the template's limit is smaller than 10 slides, merge as noted in §3.

## 1. Design guidance
- 16:9, dark navy/near-black background (#0B1220), accent teal (#14B8A6), warning amber (#F59E0B), text off-white (#E5E7EB). Font: Inter or Poppins. Max 6 lines per slide, ≤ 12 words per line; use diagrams over paragraphs.
- Diagrams: draw in draw.io/Excalidraw/Figma; export SVG/PNG. Consistent icons (Lucide/Phosphor).
- Screenshots: real UI will exist later. For now make **clean mock screens** (Figma/blocks) labelled "Prototype UI (design)" — replace with real screenshots when the build is ready.
- Every claim with a number needs a source line in small text at the slide bottom (sources in §6).
- No stock photos of hackers/blockchain coins. No jargon without a 3-word explanation.

## 2. Glossary (put simple versions in speaker notes)
- **Wallet address:** account identifier on a blockchain; public, pseudonymous.
- **VASP / exchange:** company that holds customer accounts (with KYC). Only they can freeze funds and identify account holders.
- **Burner / intermediary wallet:** throwaway wallets fraudsters use to hide the trail (layering).
- **Hop:** one transfer from wallet to wallet. **Taint:** share of a wallet's funds that came from the stolen money.
- **Deposit address:** per-customer address an exchange gives users; funds are swept to the exchange's main wallet.
- **USDT on TRON (TRC-20):** most common stablecoin route in scams (see sources).
- **Freeze window:** the short time before funds are cashed out.

## 3. Slide-by-slide (copy-ready text + visuals + speaker notes)

### Slide 1 — Title
- **Title:** ChainNetra
- **Tagline:** From a victim's wallet address to the cash-out point — faster freezing of stolen crypto
- **Sub-line:** SIH 2026 · PS SIH26183 · Ministry of Home Affairs (I4C) · Blockchain & Cybersecurity
- Team name / members / college: `[FILL]`
- **Visual:** simple graph illustration (nodes flowing to a highlighted "exchange" node).

### Slide 2 — Problem Statement
**On-slide:**
- Cyber-fraud victims report wallet addresses — usually burner or intermediary wallets
- Funds are layered through many wallets, swaps, bridges and mixers
- Investigators must find *which exchange/VASP received the money* to freeze it
- Manual multi-chain tracing needs specialist skill and time; delay lets funds vanish
- Result: delayed freezing, weak evidence, low recovery
**Visual:** left-to-right strip: Victim → Scam wallet → Layering wallets → Exchange (question mark) with a clock icon labelled "freeze window".
**India context strip (small cards, with sources):**
- ED case (Jul 2026): ₹303 crore syndicate; USDT, SOL and ETH frozen; part of the trail ended in private wallets
- Tamil Nadu case (Aug 2026): ~₹400 crore scheme; money funnelled into USDT
- Reports describe scam proceeds converted to USDT on the TRON network
**Notes:** Bank frauds are easy to route — the account number identifies the bank. A crypto address does not identify any institution, so investigators must reconstruct the path.

### Slide 3 — Proposed Solution
**On-slide (pipeline diagram):** `Complaint intake → Multi-chain trace → ML classification → Exit attribution → Risk + urgency → Evidence report + freeze-request draft`
Five bullets under it:
- Ingests wallets from complaint feeds (single or bulk; NCRP/SAHYOG-ready adapters)
- Traces funds across hops and chains (TRON, Ethereum, Bitcoin; swaps and bridges handled)
- Identifies the cash-out: exchange/VASP, P2P/OTC-suspected, private wallet, mixer, bridge, DEX
- Ranks cases by *freeze urgency* so investigators act on the most recoverable first
- Generates hash-verified evidence and a draft KYC/freeze request for investigator review
**Notes:** Output is an investigative lead with confidence and evidence, never an accusation.

### Slide 4 — Innovation (what is new)
Six tiles:
1. **ML attribution with measured accuracy** — calibrated address-role classifier; says "unattributed" when unsure
2. **Learned guided tracing** — an AI policy picks which branches to follow, reaching exits with fewer API calls (built for free-tier limits)
3. **Cash-out taxonomy** — when money leaves regulated exchanges (P2P/OTC/private wallet), we say so and suggest the right legal route
4. **Batch triage** — ranks hundreds of complaints by expected recoverable value × time-to-cash-out
5. **Explainable + auditable** — SHAP "why" panel, SHA-256 hashed evidence, reproducibility manifest
6. **Fully free and offline-capable** — no paid intelligence APIs; deterministic offline mode for reliable demos
**Bottom line:** *Existing open prototypes mostly do graph tracing + rule-based tagging; ChainNetra adds benchmarked ML, budget-aware tracing and an India-realistic exit model.*

### Slide 5 — Technical Approach
**Architecture diagram (draw):** Data sources (TronGrid, Etherscan/Blockscout, mempool.space, open labels/OFAC/exchange proof-of-reserves) → Ingestion (cache, rate-limit, evidence store) → Graph & taint engine → ML layer (M1 role classifier, M3 tracing policy, anomaly detector) → Attribution & risk → API (FastAPI) → Web UI (React, Cytoscape graph) → Reports.
**Tech stack strip:** Python · FastAPI · PostgreSQL · LightGBM · PyTorch Geometric · SHAP · React · Cytoscape.js · Docker
**Key technique bullets:** haircut (proportional) taint · deposit-address-reuse clustering · swap/bridge hop handling · Bitcoin co-spend clustering with CoinJoin guard
**Notes:** All data comes from free public sources; every raw response is stored with a SHA-256 hash.

### Slide 6 — AI/ML Models
Table (Model | Purpose | Method):
| M1 | Classify a wallet: exchange hot/deposit, mixer, bridge, DEX, scam, personal | LightGBM + calibration + SHAP |
| M3 | Choose which trace branch to expand under an API budget | Gradient-boosted policy, best-first search |
| M4 | Flag layering/structuring anomalies | Isolation Forest (+ rule detectors) |
| M2 (stretch) | Graph-based role/risk | GraphSAGE/GAT on ego-graphs |
| M7 | Freeze-urgency ranking | value × P(exit) × freshness ÷ ETA |
**Evaluation (planned):** temporal split, leave-one-exchange-out, per-class PR-AUC, calibration (ECE), guided-vs-BFS "exits found per API call"; Bitcoin benchmark on the Elliptic dataset.
**Results box:** `[FILL FROM docs/evaluation/RESULTS.md — leave as "planned" until real numbers exist]`
**Notes:** Labels are incomplete and biased toward large exchanges; we report this openly.

### Slide 7 — Trust, Evidence & Ethics
- Attribution tiers: **CONFIRMED** (sourced label match) · **PROBABLE** (deposit-funnel + model) · **POSSIBLE** (weak/heuristic) · **UNATTRIBUTED**
- Separate *risk score* and *confidence*; unevaluated signals lower confidence, never count as "safe"
- Evidence: hashed raw responses, audit log, reproducibility manifest
- We trace funds, we do **not** identify people; KYC needs the VASP and legal process
- No victim PII stored; freeze request is a **draft** for the investigator
**Visual:** four coloured tier badges + a small "evidence chain" icon row.

### Slide 8 — Feasibility
- 100% free/open-source stack; free-tier APIs with caching, rate-limiting and per-case call budgets
- Offline fixture mode → reliable demo without internet
- Data availability: public chains, OFAC list, exchange proof-of-reserves lists, open labeled datasets
- **Risk → Mitigation table:** API limits → cache + guided tracing · Label gaps → ML + tiers + abstention · Mixers/privacy coins → explicit "exit: mixer" with limits stated · False positives (payment processors, OTC) → confidence tiers + false-positive notes
**Notes:** Production path: own indexers, licensed labels, direct VASP integrations.

### Slide 9 — Implementation Plan
Timeline graphic:
1. **Phase 1 – Core:** ingestion, tracing, labels, attribution, reports
2. **Phase 2 – ML:** M1 classifier, calibration, explanations, benchmarks
3. **Phase 3 – Efficiency:** guided tracing (M3), triage queue
4. **Phase 4 – Product:** UI, auth/RBAC, audit log, bulk intake
5. **Phase 5 – Advanced:** GNN, anomaly detection, Solana; NCRP/SAHYOG integration after approvals
Note under it: prototype to be completed for the December grand finale if shortlisted.

### Slide 10 — Impact
- **Investigators:** hours of manual tracing → guided, explainable leads; better use of the freeze window
- **Victims:** higher chance of recovery through earlier freezing
- **Agencies (I4C/LEAs):** standardised reports; triage across high complaint volumes; integration-ready
- **Society:** raises the cost of using crypto for laundering
- **KPIs (planned):** time-to-attribution · exits found per API call · attribution precision by tier · % cases with actionable exit
**Scalability:** batch intake, budgeted tracing, pluggable chain adapters.

### Backup slides (keep if the template allows / for Q&A)
- **B1 Limitations & ethics:** incomplete labels; mixers/privacy tools; shared deposit addresses; OTC desks; provider gaps; not court certification.
- **B2 Comparison:** commercial platforms (paid, closed) vs open prototypes (rule-based tracing) vs ChainNetra (free, ML-benchmarked, budget-aware, India-realistic exits). Do not name-drop unverifiable claims about competitors.
- **B3 UI mock screens:** Triage queue · Case graph · "Why" panel · Trace-efficiency chart.

**If slide limit is tight:** merge 7 into 5; 9 into 8; 1 stays; keep 2,3,4,6,10.

## 4. Visuals to prepare (checklist)
1. Problem strip (victim → layering → exchange ? + clock)
2. Pipeline diagram (Slide 3)
3. Architecture diagram (Slide 5)
4. Model table graphic (Slide 6)
5. Tier badges (Slide 7)
6. Risk/mitigation table (Slide 8)
7. Roadmap timeline (Slide 9)
8. 4 mock UI screens: (a) triage table ranked by urgency; (b) graph with coloured nodes and a highlighted exchange node + side "Why" drawer; (c) evidence tab with hash list; (d) line chart "exits found vs API calls: guided above BFS" (label as *illustrative mock* until real data exists).

## 5. Do / Don't
**Do:** use "proposed/planned"; show confidence + limitations; keep text short; put sources on slides with numbers.
**Don't:** invent accuracy %, "X hours saved", user/adoption numbers, or claim integration with NCRP/SAHYOG/exchanges; say "identifies criminals"; copy text or diagrams from other teams' repos/PPTs; mention paid tools as if we use them.

## 6. Sources for numbers on Slide 2 (verify before final)
- ED ₹303 crore syndicate, frozen USDT/SOL/ETH, trail ending in private wallets: https://www.theweek.in/news/india/2026/07/13/ed-uncovers-indian-rs-303-crore-transnational-cyber-fraud-syndicate-10-arrested-crypto-trail-traced-to-dubai.html and https://www.cryptotimes.io/2026/07/14/indias-ed-busts-inr-303-crore-cyber-fraud-ring-crypto-trail-leads-to-dubai/
- Tamil Nadu ~₹400 crore scheme funnelled into USDT; CBI advisory: https://bitcoinworld.co.in/why-indias-cbi-just-told-crypto-users-to-rethink-every-p2p-trade/
- Scam proceeds converted to USDT on TRON: https://cambodianess.com/article/indian-cyber-scam-syndicates-build-corporate-style-operations-in-myanmar-compounds-targeting-india-and-the-us
- Scammers swapping into ETH/DAI then USDT before cash-out: TRM Labs 2026 Crypto Crime Report — https://www.trmlabs.com/reports-and-whitepapers/2026-crypto-crime-report
- Problem statement text: https://zaidsayyed.in/tools/sih-problem-statements/sih26183 (mirror of the official listing; confirm on sih.gov.in)
- Deposit-address heuristic: Victor, "Address Clustering Heuristics for Ethereum", FC 2020.

## 7. Likely jury questions (rehearse; short answers)
1. *Who faces this problem today?* Cyber-crime investigators handling wallet-based complaints; they trace manually and must identify the receiving VASP fast.
2. *Why not Chainalysis/TRM?* Paid, closed, not built around the Indian complaint workflow; we are free, transparent, offline-capable and benchmarked.
3. *How do you know it's right?* Confidence tiers, sourced labels, calibrated ML with abstention, benchmarks on open datasets.
4. *What if funds go via P2P/mixers/bridges?* We classify the exit type and say when the trail leaves regulated exchanges.
5. *Is it legally usable?* Integrity hashes and audit trail support investigation; not a legal certification; freeze requests are drafts.
6. *Scalability?* Batch intake, budgeted tracing, pluggable chain adapters, indexers later.
