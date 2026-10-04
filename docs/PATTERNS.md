# ChainNetra — Suspicious Pattern Detection Suite

This document specifies the 7 heuristic pattern detectors implemented in `backend/app/patterns/`. Each detector identifies distinct topological laundering shapes and produces:
- A standardized **detection score** ($0.0 \le s \le 1.0$)
- Specific **evidence transaction hashes** (`evidence_tx_refs`)
- A legally required **false-positive disclaimer** (`false_positive_note`)

---

## 1. Fan-Out (Dispersal / Layering)
- **Module:** `backend/app/patterns/fan_out.py`
- **Topological Shape:** $1 \longrightarrow N$ (One sender address splits funds across $N \ge 5$ distinct destination addresses within a configurable time window, default 1 hour).
- **Mathematical Criteria:**
  $$\text{Score} = \min\left(1.0, \frac{N_{\text{distinct}}}{10} \times \left(1.0 + \frac{3600}{\max(\Delta t_{\text{span}}, 60)}\right)\right)$$
- **Evidence:** Source address, list of child transaction hashes, time span, total volume dispersed.
- **Documented False-Positive Note:** *"Could indicate legitimate corporate payroll distribution, payment processor batch settlement, or exchange withdrawal batching."*

---

## 2. Fan-In (Consolidation)
- **Module:** `backend/app/patterns/fan_in.py`
- **Topological Shape:** $N \longrightarrow 1$ (Multiple distinct senders $N \ge 5$ consolidate funds into a single recipient address within a short window).
- **Mathematical Criteria:**
  $$\text{Score} = \min\left(1.0, \frac{N_{\text{senders}}}{8}\right)$$
- **Evidence:** Aggregation address, sending counterparty addresses, transaction references.
- **Documented False-Positive Note:** *"Could indicate an exchange deposit collection wallet, merchant payment aggregator, or multi-sig treasury funding."*

---

## 3. Rapid Forwarding (Velocity Layering)
- **Module:** `backend/app/patterns/rapid_forwarding.py`
- **Topological Shape:** $A \longrightarrow B \longrightarrow C \longrightarrow D$ (Funds pass through intermediary wallets with near-zero dwell time).
- **Mathematical Criteria:**
  - Evaluated across $\ge 3$ consecutive hops.
  - Median Dwell Time: $\tilde{\tau}_{\text{dwell}} = \text{median}(t_{\text{out}} - t_{\text{in}}) < 10 \text{ minutes}$.
  - Forwarding ratio: $\frac{\text{Volume}_{\text{out}}}{\text{Volume}_{\text{in}}} \ge 0.85$.
- **Evidence:** Sequence of intermediate hop addresses, timestamps, dwell times in seconds.
- **Documented False-Positive Note:** *"Could indicate automated algorithmic sweeps, bridge relay services, or arbitrage bot operations."*

---

## 4. Peel Chain (Iterative Laundering)
- **Module:** `backend/app/patterns/peel_chain.py`
- **Topological Shape:** Linear chain where each step peels off a small expenditure (or cash-out slice) while forwarding the bulk remainder to a new change wallet.
- **Mathematical Criteria:**
  - Minimum of $\ge 3$ consecutive peeling hops.
  - At each step:
    $$\frac{\text{Remainder}_{\text{forwarded}}}{\text{Total}_{\text{in}}} \ge 0.70 \quad \text{and} \quad \frac{\text{Peeled}_{\text{slice}}}{\text{Total}_{\text{in}}} \le 0.30$$
- **Evidence:** Chain of addresses, peel amounts, remainder transaction hashes.
- **Documented False-Positive Note:** *"Commonly occurs in standard Bitcoin UTXO transactions where unspent change is redirected to fresh addresses."*

---

## 5. Dormancy Burst (Reactivated Wallet)
- **Module:** `backend/app/patterns/dormancy_burst.py`
- **Topological Shape:** Long period of inactivity followed by sudden, high-velocity fund dispersal.
- **Mathematical Criteria:**
  - Inactivity window: $t_{\text{burst}} - t_{\text{last\_active}} \ge 30 \text{ days}$.
  - Rapid dispersal: $\ge 3$ outgoing transfers within 6 hours of reactivation.
- **Evidence:** Reactivation transaction hash, historical last seen date, dormancy duration in days.
- **Documented False-Positive Note:** *"Could represent a legitimate user reactivating cold-storage savings or recovering an old wallet backup."*

---

## 6. Structuring (Smurfing)
- **Module:** `backend/app/patterns/structuring.py`
- **Topological Shape:** Multiple transfers with near-equal amounts or values deliberately calibrated below regulatory reporting thresholds (e.g., just under \$10,000 or \$1,000 USDT).
- **Mathematical Criteria:**
  - Minimum $\ge 3$ transfers within a tolerance $\delta \le 5\%$ of each other, or within $10\%$ below round compliance numbers.
- **Evidence:** Transaction hashes, transfer amounts, coefficient of variation of transaction sizes.
- **Documented False-Positive Note:** *"Could represent periodic subscription payments, payroll disbursements, or systematic Dollar-Cost Averaging (DCA) orders."*

---

## 7. Round-Trip (Cycling)
- **Module:** `backend/app/patterns/round_trip.py`
- **Topological Shape:** Circular fund path where funds traverse multiple intermediaries before returning to the original sender address or its DAR entity cluster.
- **Mathematical Criteria:**
  - Directed cycle detected via Tarjan's strongly connected components algorithm or DFS back-edge detection.
  - Cycle length $\ge 3$ hops.
- **Evidence:** Ordered cycle path $[v_0, v_1, v_2, \dots, v_0]$, net volume returned, fees lost to network gas.
- **Documented False-Positive Note:** *"Could indicate intentional self-transfers for portfolio re-balancing or liquidity management."*
