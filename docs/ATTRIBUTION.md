# ChainNetra — Attribution Framework & Clustering Engine

This document details the entity attribution algorithms, clustering heuristics, and evidence standards implemented in `backend/app/attribution/` and `backend/app/graph/clustering.py`.

---

## 1. The Core Challenge of Exchange Identification

Centralized Virtual Asset Service Providers (VASPs)—such as Binance, Kraken, CoinDCX, and WazirX—assign unique, disposable **deposit addresses** to each customer account.

When a victim sends stolen funds to a fraudster's deposit address:
1. The deposit address is not publicly named as the exchange.
2. The exchange later automatically sweeps funds from the deposit address into its large, publicly known **main collection or hot wallet**.
3. Therefore, direct label lookup on the initial deposit address will yield **no results**.

ChainNetra solves this through **Deposit-Address-Reuse (DAR)** clustering and multi-hop forwarding analysis.

```text
Victim Transfer ──► Suspect Deposit Address ──► Automated Sweep ──► Known Exchange Hot Wallet
                          │                                                 │
                          ▼                                                 ▼
                  [PROBABLE VASP]                                   [CONFIRMED VASP]
```

---

## 2. Four-Tier Attribution Taxonomy

To prevent premature accusations or false positives from entering legal proceedings, ChainNetra strictly enforces a 4-tier confidence hierarchy:

| Tier | Required Evidence | Typical Entities | Legal Utility |
|---|---|---|---|
| **`CONFIRMED`** | Exact address match in verified first-party datasets with cryptographic or regulatory provenance (OFAC SDN list, Proof-of-Reserves, official smart contract registries). | Binance Hot Wallet, Tornado Cash contract, Stargate Router | Court-admissible factual identification; direct subpoena target. |
| **`PROBABLE`** | Strong topological evidence: Address forwards $\ge 80\%$ of inflow to a `CONFIRMED` VASP main wallet from $\ge 5$ distinct senders within time window $\tau$, OR M1 role model predicts VASP with calibrated probability $p \ge 0.80$. | Customer deposit addresses at centralized exchanges | Primary investigative lead; grounds for Section 91 CrPC notice to VASP. |
| **`POSSIBLE`** | Moderate heuristic indicators: 1-hop counterparty to an exchange, M1 role probability $0.50 \le p < 0.80$, or uncalibrated pass-through pattern. | Suspected OTC brokers, P2P merchants, unclassified payment processors | Secondary lead; requires additional manual intelligence corroboration. |
| **`UNATTRIBUTED`** | Insufficient on-chain activity, dormant balance, or model confidence below abstention threshold ($p < 0.50$). | Fresh burner wallets, unhosted personal storage, dead ends | Abstention; explicit warning that no reliable entity attribution exists. |

---

## 3. Deposit-Address-Reuse (DAR) Algorithm

Implemented in `backend/app/attribution/clustering.py`, following the peer-reviewed methodology established by Victor (2020):

### Rules & Thresholds:
An address $A$ is clustered as an **Exchange Deposit Address** linked to VASP entity $E$ if:
1. **Counterparty Diversity:** $A$ receives incoming transactions from $N \ge 5$ distinct external EOAs (Externally Owned Accounts).
2. **Sweep Forwarding:** $A$ forwards $\ge 80\%$ of its total received value to a `CONFIRMED` main collection wallet of entity $E$.
3. **Temporal Tightness:** The sweep occurs within time window $\tau \le 24 \text{ hours}$ of receipt.

If all three conditions are satisfied, address $A$ is attributed as `PROBABLE VASP (entity = E)` with confidence calculated from counterparty count and forwarding ratio.

---

## 4. Bitcoin UTXO Co-Spend Clustering

For Bitcoin traces, ChainNetra uses a **Union-Find (Disjoint-Set)** data structure to cluster addresses belonging to the same entity:

### The Multi-Input Heuristic:
When a Bitcoin transaction spends UTXOs originating from multiple distinct input addresses $I_1, I_2, \dots, I_k$, all $I_i$ are inferred to be controlled by the same wallet entity.

### The CoinJoin Guard (Crucial Safeguard):
To prevent catastrophic false-positive clustering:
- If a transaction possesses $\ge 3$ inputs and $\ge 3$ equal-value outputs (signature of Wasabi Wallet, Whirlpool, or JoinMarket), **the transaction is flagged as a CoinJoin and skipped from co-spend clustering**.
- Without this guard, thousands of unrelated privacy users would be erroneously merged into a single mega-cluster.

---

## 5. Curated Label Provenance

All labels used for `CONFIRMED` attributions are stored in `data/labels/` with explicit provenance metadata:

```csv
address,chain,entity,entity_type,source,source_url,retrieved_at,license,label_confidence
TNVaKWQzau4pirzvwSH17CPvMk4p7yPAn6,tron,Lazarus Group,sanctioned,ofac_sdn,https://sanctionssearch.ofac.treas.gov,2026-01-01,public_domain,strong
0x098B716B8Aaf21512996dC57EB0615e2383E2f96,ethereum,Tornado Cash,sanctioned,ofac_sdn,https://sanctionssearch.ofac.treas.gov,2026-01-01,public_domain,strong
TKnABDqoTfRms2BNQDUahFqXiR32vufQi8,tron,Binance,exchange_hot,por_binance,https://www.binance.com/en/proof-of-reserves,2026-01-01,public,strong
```

Every label record contains:
- `source`: Institutional provenance (e.g., `ofac_sdn`, `por_binance`, `ethtx_verified`)
- `source_url`: Verifiable URL
- `retrieved_at`: Ingestion timestamp
- `license`: Data redistribution rights
