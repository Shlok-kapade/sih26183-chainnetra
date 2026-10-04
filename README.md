# ChainNetra (चेत्र-नेत्र)

**Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.x-646CFF.svg)](https://vitejs.dev/)
[![Tests](https://img.shields.io/badge/Pytest-140%20Passed-brightgreen.svg)]()
[![SIH 2026](https://img.shields.io/badge/SIH%202026-PS%20SIH26183-orange.svg)]()

**Smart India Hackathon 2026 · Problem Statement SIH26183 · Ministry of Home Affairs (I4C)**  
**Theme:** Blockchain & Cybersecurity · **Category:** Software  

---

## Executive Summary

When a traditional banking fraud victim reports an account number, the target financial institution is readily identifiable from standard routing and IFSC codes. A cryptocurrency wallet address, by contrast, is completely pseudonymous—it does not indicate an issuer, jurisdiction, bank, or real-world identity.

Fraudsters rapidly scatter proceeds across burner wallets, decentralized swap protocols, cross-chain bridges, and peel chains before depositing into exchanges (VASPs) to cash out into fiat currency. Investigating officers face a critical **"freeze window"** before funds exit regulated channels.

```text
Public blockchain data ≠ Actionable investigative intelligence
```

**ChainNetra** provides the investigative intelligence layer: it converts victim-reported crypto addresses into explainable, multi-chain fund-flow graphs, detects money-laundering topologies, attributes exit entities (exchanges, OTC desks, mixers), calculates risk and freeze urgency, and generates cryptographic, SHA-256 hash-verified evidence manifests alongside draft freeze/KYC requests.

---

## System Workflow

```text
Victim-Reported Suspect Wallet (Single / Batch NCRP)
                        ↓
            Address Format & Chain Validation
                        ↓
   Multi-Chain Ingestion (TronGrid / Etherscan / Mempool)
                        ↓
      Guided Tracing Engine (Budget-Aware Best-First)
                        ↓
       Proportional Haircut Taint Tracking & Graph
                        ↓
    Suspicious Pattern Detectors (7 Morphologies)
                        ↓
    Deposit-Address-Reuse & Co-Spend Clustering (DAR)
                        ↓
       ML Role Inference (M1 LightGBM + SHAP Values)
                        ↓
       4-Tier Attribution (CONFIRMED / PROBABLE / ...)
                        ↓
       Urgency & Risk Scoring (0–100 + Confidence)
                        ↓
    Cryptographic Evidence Manifest (SHA-256) & Audit Log
                        ↓
   Investigation Report (PDF/CSV/JSON) & Draft Freeze Order
```

---

## Core Capabilities

| Capability | Technical Implementation |
|---|---|
| **Multi-Chain Tracing** | Native support for **TRON (TRC-20 USDT)**, **Ethereum (ETH / ERC-20)**, and **Bitcoin (UTXO co-spend)**. |
| **Guided Tracing Engine** | Best-first frontier expansion governed by an ML policy (M3) under strict API call budgets and configurable depth limits. |
| **Proportional Haircut Taint** | Quantitative taint conservation model for pooled fungible assets with customizable pruning thresholds. |
| **Clustering Algorithms** | Deposit-Address-Reuse (DAR - Victor 2020) heuristic for exchange deposit identification; Bitcoin common-input co-spend clustering with CoinJoin guards. |
| **Pattern Detection Suite** | 7 pattern detectors: Fan-Out, Fan-In, Rapid Forwarding, Peel Chain, Dormancy Burst, Structuring, and Round-Trip cycles. |
| **ML Role Classification** | M1 LightGBM model calibrated with isotonic regression classifying wallets into 10 role categories with SHAP feature explainability. |
| **Four-Tier Attribution** | Explicit distinction between `CONFIRMED`, `PROBABLE`, `POSSIBLE`, and `UNATTRIBUTED` states. |
| **Triage & Urgency Ranking** | Ranks incoming complaints by recoverable value, probability of reaching a regulated VASP, and velocity toward cash-out. |
| **Chain of Custody & Evidence** | Raw provider responses hashed via SHA-256; immutable append-only audit trail; PDF/CSV/JSON export. |
| **Freeze-Request Drafting** | Auto-generates structured, reviewable Section 91 CrPC / VASP subpoena letters containing transaction references. |
| **Dual Execution Modes** | `LIVE_MODE=true` for live public blockchain querying; `LIVE_MODE=false` for deterministic offline fixture replays. |

---

## Attribution Framework & Cash-Out Taxonomy

Exchange identification relies on **cryptographic label matching combined with deterministic transaction topology**, never unverified guesses.

```text
Suspect Address ──► Layering Hops ──► Deposit Address (DAR) ──► Exchange Hot/Cold Wallet
 (Victim Loss)      (Peel/Forward)      [PROBABLE VASP]             [CONFIRMED VASP]
```

### Attribution Tiers

1. **`CONFIRMED`**: Direct match with verified, timestamped provenance records (e.g., Binance Proof-of-Reserves disclosures, OFAC SDN list, official bridge smart contracts).
2. **`PROBABLE`**: Strong topological evidence—address forwards $\ge 80\%$ of inflow within time window $\tau$ to a confirmed VASP collection wallet from $\ge 5$ distinct senders (Deposit-Address-Reuse heuristic) or high M1 ML probability ($p \ge 0.80$).
3. **`POSSIBLE`**: Moderate heuristic indicators, single weak signals, or M1 probability between $0.50$ and $0.80$.
4. **`UNATTRIBUTED`**: Insufficient or contradictory data. The system explicitly abstains rather than emitting false positives.

### Cash-Out Exit Taxonomy

When funds leave the primary trail, ChainNetra categorizes the exit into one of 8 distinct targets:
- **`VASP`** (Regulated Centralized Exchanges: Binance, WazirX, CoinDCX, Kraken)
- **`P2P_OTC_SUSPECTED`** (High-frequency, multi-counterparty peer-to-peer settlement hubs)
- **`PRIVATE_WALLET`** (Un-hosted self-custodial wallets; dead-end or dormant custody)
- **`MIXER`** (Tornado Cash, privacy protocols)
- **`BRIDGE`** (Cross-chain bridges: Stargate, Across, Wormhole)
- **`DEX_SWAP`** (Uniswap, SunSwap, Curve liquidity pools)
- **`SANCTIONED`** (OFAC / UN sanctioned addresses)
- **`UNKNOWN`** (Unresolved frontier addresses)

---

## Machine Learning Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Machine Learning Pipeline                       │
├────────────────────────────────────────────────────────────────────────┤
│  M1: Wallet Role Classifier                                            │
│  - Architecture: LightGBM Multi-class Classifier + Isotonic Calibrator │
│  - Features: 42 graph-topological, temporal, and volume statistics     │
│  - Explainability: SHAP TreeExplainer waterfall plots in UI            │
├────────────────────────────────────────────────────────────────────────┤
│  M3: Guided Tracing Search Policy                                      │
│  - Goal: Maximize probability of finding VASP exit under API budget    │
│  - Algorithm: Best-first frontier traversal with heuristic scoring     │
├────────────────────────────────────────────────────────────────────────┤
│  M4: Anomaly & Layering Detector                                       │
│  - Algorithm: Isolation Forest trained on normal transaction flows     │
│  - Output: Continuous anomaly score flagging synthetic structuring    │
├────────────────────────────────────────────────────────────────────────┤
│  M7: Freeze Urgency Triage Ranker                                      │
│  - Formula: Urgency = (Amount At Risk × P(Exit VASP) × Freshness) / ETA│
└────────────────────────────────────────────────────────────────────────┘
```

---

## Suspicious Pattern Detectors

ChainNetra implements 7 specialized pattern detectors, each providing **score**, **evidence transaction hashes**, and a mandatory **false-positive disclaimer**:

1. **Fan-Out (Dispersal):** Single wallet splitting funds across $\ge 5$ destinations within a short time window. *(False-Positive note: Payroll, payment processor, or exchange batch withdrawal).*
2. **Fan-In (Consolidation):** Multiple wallets consolidating funds into a central collection point. *(False-Positive note: Merchant settlement or staking pool collection).*
3. **Rapid Forwarding:** Low median dwell time ($< 10$ minutes) across $\ge 3$ consecutive hops. *(False-Positive note: Automated routing sweeps).*
4. **Peel Chain:** Repeated pattern of forwarding a large remainder while peeling off smaller amounts. *(False-Positive note: Bitcoin UTXO change address mechanics).*
5. **Dormancy Burst:** Long inactivity period followed by sudden, high-velocity fund dispersal. *(False-Positive note: Reactivated personal cold-storage wallet).*
6. **Structuring (Smurfing):** Repeated transfers structured just below common regulatory compliance thresholds. *(False-Positive note: Systematic DCA investment plans).*
7. **Round-Trip:** Funds cycled through multiple hops returning to the originator cluster. *(False-Positive note: Self-transfer for wallet re-balancing).*

---

## Technology Stack

### Backend
- **Framework:** Python 3.12, FastAPI, Pydantic v2, Uvicorn
- **Database & ORM:** PostgreSQL 16, SQLAlchemy 2 (Async), Alembic migrations, SQLite (test fixture mode)
- **Graph & Network Analysis:** NetworkX (in-memory graph modeling and traversal)
- **Machine Learning:** LightGBM, scikit-learn, PyTorch, PyTorch Geometric, SHAP, Joblib
- **Reporting & Export:** ReportLab (vector PDF generation), CSV, JSON
- **Security:** Argon2 password hashing, JWT tokens, RBAC (Investigator, Supervisor, Admin)

### Frontend
- **Framework:** React 18, TypeScript, Vite 6
- **Styling:** Tailwind CSS, Lucide Icons
- **Interactive Graphing:** Cytoscape.js with fcose (force-directed compound layout)
- **Data Management:** TanStack React Query, Axios
- **Component Architecture:** Modular tabs (Graph, Timeline, Patterns, Attribution, Evidence, Subpoena)

---

## Repository Structure

```text
chainnetra/
├── .env.example              # Template configuration for live & offline modes
├── .gitignore                # Production ignore rules (blocks keys, caches, venvs)
├── docker-compose.yml        # Multi-container orchestration (API, Frontend, DB)
├── Makefile                  # Developer workflow commands (lint, test, build)
├── backend/
│   ├── app/
│   │   ├── api/              # API Endpoints (auth, cases, complaints, evidence, graph, triage)
│   │   ├── attribution/      # Label store, OFAC ingestion, DAR clustering, tiers
│   │   ├── core/             # Configuration, security, logging
│   │   ├── db/               # SQLAlchemy models and session managers
│   │   ├── graph/            # Graph builder, haircut taint algorithm, export
│   │   ├── ingest/           # Blockchain adapters (TronGrid, EVM/Blockscout, Bitcoin)
│   │   ├── ml/               # Model inference (M1 role classifier, M3 policy, features)
│   │   ├── patterns/         # 7 Suspicious pattern detectors + registry
│   │   ├── reports/          # ReportLab PDF generator, subpoena builder
│   │   └── triage/           # Case triage & freeze-urgency ranker
│   └── tests/                # 140+ unit, integration, and scenario tests
├── frontend/
│   ├── src/
│   │   ├── components/       # Layout, Navbar, Cytoscape graph canvas, tabs
│   │   ├── pages/            # Dashboard, TriageQueue, CaseWorkspace, NewCase
│   │   └── lib/              # API client and TypeScript interfaces
├── data/
│   ├── labels/               # Curated address labels with provenance (OFAC, Binance PoR)
│   └── fixtures/             # Deterministic JSON provider responses for offline replay
├── docs/                     # Specifications, architecture diagrams, SIH briefs
└── scripts/                  # Synthesis, evaluation, and bootstrap utilities
```

---

## Quick Start Guide

### Prerequisites
- Python 3.12+
- Node.js 20+ and npm
- Git

### 1. Clone & Setup Environment

```bash
git clone https://github.com/Shlok-kapade/sih26183-chainnetra.git
cd sih26183-chainnetra

# Copy environment variables
cp .env.example .env
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Run the full test suite (140 tests)
pytest tests -q

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be live at `http://localhost:8000`.  
Interactive OpenAPI documentation: `http://localhost:8000/docs`.

### 3. Frontend Setup

In a new terminal:

```bash
cd frontend
npm install
npm run build    # Verifies TypeScript compilation and bundle generation
npm run dev      # Launches Vite dev server
```

The UI will be accessible at `http://localhost:5173`.

---

## Execution Modes

### 1. Offline Deterministic Mode (`LIVE_MODE=false`)
- Designed for air-gapped demo environments, hackathon judging, and unit testing.
- Uses frozen, realistic blockchain responses stored in `data/fixtures/` and demo cases in `backend/app/api/v1/endpoints/cases.py`.
- **Pre-seeded Cases:**
  - `CASE-7281`: Multi-hop TRON USDT fraud trail leading to a Binance deposit address.
  - `CASE-7282`: Ethereum ERC-20 laundering network featuring rapid forwarding and peel-chains.
  - `CASE-7283`: Cross-entity consolidation flow (Fan-in) into an OTC desk.

### 2. Live Blockchain Mode (`LIVE_MODE=true`)
- Interacts with live blockchain infrastructure through configured API keys in `.env`:
  - `TRONGRID_API_KEY`: TRON mainnet querying.
  - `ETHERSCAN_API_KEY`: Ethereum mainnet querying.
  - Public Blockscout endpoints for EVM chains.
- Employs token-bucket rate limiting and caching to prevent rate-limit exhaustion.

---

## Ethical Boundaries & Legal Disclaimer

- **Asset Tracking Only:** ChainNetra analyzes public on-chain transfer graphs; it **does not identify individual human beings**. Real-world identity attribution requires formal legal processes (such as Section 91 CrPC notices) served to custodial VASPs.
- **Privacy Preservation:** No victim PII (Personally Identifiable Information) or banking passwords are stored. Complaint numbers are stored as alphanumeric reference tokens.
- **Investigative Support:** Risk scores and attribution tiers serve as investigative leads, not definitive proof of guilt. All draft freeze requests must be reviewed and authorized by an investigating officer.

---

## License

This project was built for the **Smart India Hackathon 2026** (Problem Statement SIH26183). All rights reserved.
