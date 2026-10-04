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

## Technical Documentation & In-Depth Specifications

For comprehensive engineering specifications, mathematical formulations, and evaluation results, refer to the dedicated technical guides:

- 🧠 **[Machine Learning Models Specification](docs/ML_MODELS.md)** — Architectural specs, training procedures, feature dictionaries, calibration, and SHAP explainability for M1 through M8.
- 🔍 **[Suspicious Pattern Detection Suite](docs/PATTERNS.md)** — Topological formulas, dwell-time parameters, evidence hashes, and false-positive notes for all 7 detectors.
- 🏷️ **[Attribution Framework & Clustering Engine](docs/ATTRIBUTION.md)** — Deposit-Address-Reuse (DAR) algorithm, Bitcoin UTXO co-spend clustering, CoinJoin safeguards, and 4-tier taxonomy.
- ⚡ **[Tracing Engine & Haircut Taint Algorithm](docs/docs/spec/04_TRACING_ENGINE.md)** — Proportional value conservation, BFS frontier expansion, and edge budget pruning.
- 📊 **[Evaluation Benchmarks & Model Metrics](docs/evaluation/RESULTS.md)** — Temporal split and leave-one-exchange-out results on Elliptic and Tron datasets.
- 🚀 **[Production Deployment & EC2 Guide](DEPLOYMENT.md)** — Docker Compose, Nginx reverse proxy, and environment provisioning.
- ⚖️ **[Ethical Guidelines](ETHICS.md)** & **[Technical Limitations](LIMITATIONS.md)** — Evidentiary standards, privacy boundaries, and chain coverage constraints.

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

| Capability | Technical Implementation | Detailed Reference |
|---|---|---|
| **Multi-Chain Tracing** | Native support for **TRON (TRC-20 USDT)**, **Ethereum (ETH / ERC-20)**, and **Bitcoin (UTXO co-spend)**. | [docs/spec/02_DATA_SOURCES.md](docs/docs/spec/02_DATA_SOURCES.md) |
| **Guided Tracing Engine** | Best-first frontier expansion governed by an ML policy (M3) under strict API call budgets and depth limits. | [docs/spec/04_TRACING_ENGINE.md](docs/docs/spec/04_TRACING_ENGINE.md) |
| **Proportional Haircut Taint** | Quantitative taint conservation model for pooled fungible assets with customizable pruning thresholds. | [docs/spec/04_TRACING_ENGINE.md](docs/docs/spec/04_TRACING_ENGINE.md) |
| **Clustering Algorithms** | Deposit-Address-Reuse (DAR - Victor 2020) heuristic for exchange deposit identification; Bitcoin common-input co-spend clustering with CoinJoin guards. | [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md) |
| **Pattern Detection Suite** | 7 pattern detectors: Fan-Out, Fan-In, Rapid Forwarding, Peel Chain, Dormancy Burst, Structuring, and Round-Trip cycles. | [docs/PATTERNS.md](docs/PATTERNS.md) |
| **ML Role Classification** | M1 LightGBM model calibrated with isotonic regression classifying wallets into 10 role categories with SHAP feature explainability. | [docs/ML_MODELS.md](docs/ML_MODELS.md) |
| **Four-Tier Attribution** | Explicit distinction between `CONFIRMED`, `PROBABLE`, `POSSIBLE`, and `UNATTRIBUTED` states. | [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md) |
| **Triage & Urgency Ranking** | Ranks incoming complaints by recoverable value, probability of reaching a regulated VASP, and velocity toward cash-out. | [docs/ML_MODELS.md#6-m7-freeze-urgency-triage-engine](docs/ML_MODELS.md) |
| **Chain of Custody & Evidence** | Raw provider responses hashed via SHA-256; immutable append-only audit trail; PDF/CSV/JSON export. | [docs/spec/05_API_DATA_MODEL.md](docs/docs/spec/05_API_DATA_MODEL.md) |
| **Freeze-Request Drafting** | Auto-generates structured, reviewable Section 91 CrPC / VASP subpoena letters containing transaction references. | [backend/app/reports/subpoena.py](backend/app/reports/subpoena.py) |
| **Dual Execution Modes** | `LIVE_MODE=true` for live public blockchain querying; `LIVE_MODE=false` for deterministic offline fixture replays. | [Section Below](#execution-modes) |

---

## Machine Learning Architecture & Model Catalog

ChainNetra incorporates specialized AI/ML models designed specifically for graph-topological forensics under strict computational and API constraints. Full details are documented in **[docs/ML_MODELS.md](docs/ML_MODELS.md)**.

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ChainNetra ML Ecosystem                                   │
├────────┬──────────────────────────────────────────────────────────┬─────────────────────────┤
│ Model  │ Purpose & Target                                         │ Underlying Architecture │
├────────┼──────────────────────────────────────────────────────────┼─────────────────────────┤
│ **M1** │ Wallet Role Classifier (Exchange hot/deposit, mixer, etc)│ LightGBM + Isotonic +   │
│        │ Evaluates 42 topological, temporal, and volume signals.  │ TreeSHAP Explainability │
├────────┼──────────────────────────────────────────────────────────┼─────────────────────────┤
│ **M1b**│ Bitcoin Transaction Illicit Scorer                       │ Benchmark LightGBM on   │
│        │ Evaluated on the standardized Elliptic temporal dataset. │ Elliptic Bitcoin graph  │
├────────┼──────────────────────────────────────────────────────────┼─────────────────────────┤
│ **M2** │ Ego-Graph Semi-Supervised Role Scorer                    │ GraphSAGE / GATv2       │
│        │ 2-hop neighborhood message-passing graph neural network. │ PyTorch Geometric (CPU) │
├────────┼──────────────────────────────────────────────────────────┼─────────────────────────┤
│ **M3** │ Guided Tracing Search Policy                             │ Gradient-Boosted Policy │
│        │ Best-first frontier expansion minimizing API calls.      │ Heuristic Traversal     │
├────────┼──────────────────────────────────────────────────────────┼─────────────────────────┤
│ **M4** │ Layering & Structuring Anomaly Detection                 │ Isolation Forest +      │
│        │ Detects synthetic smurfing and algorithmic sweeps.       │ Z-Score Outlier Indices │
├────────┼──────────────────────────────────────────────────────────┼─────────────────────────┤
│ **M5** │ Multi-Signal Exit-Type Resolver                          │ Hierarchical Rules +    │
│        │ Resolves cash-out points into 8 distinct taxonomy types. │ Calibrated M1 Softmax   │
├────────┼──────────────────────────────────────────────────────────┼─────────────────────────┤
│ **M6** │ Entity Clustering Engine                                 │ Deposit-Address-Reuse & │
│        │ Identifies exchange deposit hubs and UTXO co-spends.     │ Union-Find Data Struct  │
├────────┼──────────────────────────────────────────────────────────┼─────────────────────────┤
│ **M7** │ Freeze-Urgency Triage Ranker                             │ Multi-Factor Decision   │
│        │ Prioritizes bulk complaints by recoverable value & ETA.  │ Optimization Equation   │
└────────┴──────────────────────────────────────────────────────────┴─────────────────────────┘
```

### Detailed Highlights of Key Models:

#### 1. M1 — Wallet Role Classifier
- **Objective:** Classifies an arbitrary address into `{exchange_hot, exchange_deposit, mixer, bridge, dex, scam/sanctioned, personal/unknown}`.
- **Features:** 42 engineered signals covering in/out degree, counterparty Gini coefficient, median dwell time, 24/7 diurnal entropy, balance turnover, and 1-hop labeled counterparty proportions.
- **Calibration & Explainability:** Raw probabilities are calibrated using isotonic regression. Every inference provides top-5 SHAP feature contributions so investigating officers understand the exact rationale behind a prediction.

#### 2. M3 — Guided Tracing Policy
- **Objective:** Solves the API rate-limit bottleneck by replacing blind BFS with best-first search.
- **Priority Function:**
  $$\text{Priority}(v) = \frac{\text{TaintShare}(v) \times P(\text{reaches VASP within } k \text{ hops} \mid v)}{\text{EstimatedCost}(v)}$$
- **Result:** Locates exchange cash-out exits with **up to 68% fewer API requests**, allowing real-time investigation on free-tier provider limits.

#### 3. M7 — Freeze-Urgency Triage Engine
- **Equation:**
  $$\text{Urgency} = \frac{\text{AmountAtRisk}_{\text{USD}} \times P(\text{Exit} = \text{VASP}) \times \text{Freshness}}{\max(\text{ETA}_{\text{hours}}, 1.0)}$$
- **Function:** Prioritizes incoming complaints on portals like NCRP/SAHYOG, directing LEA attention to cases where funds are still recoverable before they are swept into off-chain fiat accounts.

---

## Attribution Framework & Cash-Out Taxonomy

Exchange identification relies on **cryptographic label matching combined with deterministic transaction topology**, never unverified guesses. Full specifications are in **[docs/ATTRIBUTION.md](docs/ATTRIBUTION.md)**.

```text
Suspect Address ──► Layering Hops ──► Deposit Address (DAR) ──► Exchange Hot/Cold Wallet
 (Victim Loss)      (Peel/Forward)      [PROBABLE VASP]             [CONFIRMED VASP]
```

### The 4 Attribution Tiers
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

## Suspicious Pattern Detectors

ChainNetra implements 7 specialized pattern detectors in `backend/app/patterns/`. Each detector provides a **score**, **evidence transaction hashes**, and a mandatory **false-positive disclaimer**. Detailed specifications are in **[docs/PATTERNS.md](docs/PATTERNS.md)**:

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
├── .gitignore                # Production ignore rules (blocks keys, caches, raw datasets)
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
│   ├── ML_MODELS.md          # In-depth specification of ML models M1 to M8
│   ├── PATTERNS.md           # Deep dive into the 7 suspicious pattern detectors
│   ├── ATTRIBUTION.md        # DAR clustering and attribution tier documentation
│   └── evaluation/           # Evaluation logs and benchmark metrics
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
