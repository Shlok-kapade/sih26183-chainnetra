# ChainNetra — Machine Learning Specification & Model Architecture

This document provides a deep-dive technical specification of the machine learning algorithms, statistical estimators, search policies, and calibration layers powering **ChainNetra (SIH 26183)**.

---

## 1. Global ML Principles & Operational Constraints

1. **Strict Point-in-Time Features:**  
   For any wallet evaluation at timestamp $t$, features are calculated exclusively using transactions where $\text{timestamp} \le t$. Future transactions are strictly excluded to avoid look-ahead data leakage.
2. **Leave-One-Exchange-Out (LOEO) Evaluation:**  
   Models are evaluated across two mandatory split types:
   - **Temporal Split:** Training on historical timestamps, testing on future timestamps.
   - **Entity-Disjoint / LOEO Split:** Training after withholding all addresses belonging to exchange $X$, and testing specifically on exchange $X$. This measures generalization to previously unseen exchanges and payment providers.
3. **Probability Calibration & Abstention:**  
   Raw model outputs undergo Isotonic Regression calibration on a held-out validation set. If $\max_c P(y = c \mid \mathbf{x}) < \theta_{\text{abstain}}$ (default $\theta = 0.50$), the model explicitly returns `UNATTRIBUTED` rather than outputting a low-confidence false positive.
4. **SHAP Feature Attributions:**  
   Every inference executes TreeSHAP (`shap.TreeExplainer`) to generate local feature importance explanations, providing investigators with the specific behavioral signals that drove the prediction.

---

## 2. Model Catalog

```text
┌────────┬───────────────────────────────────────────┬────────────────────────────────────────┐
│ Model  │ Purpose                                   │ Architecture                           │
├────────┼───────────────────────────────────────────┼────────────────────────────────────────┤
│ M1     │ Wallet Role Classification                │ LightGBM Multi-class + Isotonic Calib. │
│ M1b    │ Bitcoin Illicit Transaction Benchmark     │ LightGBM on Elliptic Temporal Split    │
│ M3     │ Guided Tracing Search Policy              │ Gradient-Boosted Best-First Traversal  │
│ M4     │ Layering & Anomaly Detection              │ Isolation Forest + Z-score Deviations  │
│ M5     │ Exit-Type Decision Layer                  │ Deterministic Multi-Signal Resolver    │
│ M6     │ Entity Clustering                         │ Deposit-Address-Reuse (DAR) + Co-Spend │
│ M7     │ Freeze-Urgency Triage                     │ Multi-Factor Triage Equation           │
└────────┴───────────────────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. M1: Wallet Role Classifier

### Task Formulation
Predict the role $y \in \mathcal{C}$ of a given blockchain address:
$$\mathcal{C} = \{\text{exchange\_hot}, \text{exchange\_deposit}, \text{mixer}, \text{bridge}, \text{dex}, \text{scam/sanctioned}, \text{personal/unknown}\}$$

### Feature Space (42 Engineered Signals)
- **Topological Degree:**
  - $N_{\text{in}}$, $N_{\text{out}}$: In-degree and out-degree (distinct counterparties).
  - $C_{\text{in}}$, $C_{\text{out}}$: Inflow and outflow transaction counts.
  - $\Sigma_{\text{in}}$, $\Sigma_{\text{out}}$: Total volume sent and received (log-scaled).
- **Temporal & Velocity:**
  - Median and interquartile dwell time: $\tau_{\text{dwell}} = t_{\text{send}} - t_{\text{recv}}$.
  - Burstiness coefficient: $B = \frac{\sigma_{\Delta t} - \mu_{\Delta t}}{\sigma_{\Delta t} + \mu_{\Delta t}}$.
  - 24/7 Activity Entropy: Shannon entropy of transaction hour-of-day distribution (VASPs operate continuously).
- **Balance & Forwarding Dynamics:**
  - Velocity / Turnover ratio: $\frac{\Sigma_{\text{out}}}{\max(\bar{B}, \epsilon)}$.
  - Amount preservation: $\text{ratio} = \frac{\text{Amount}_{\text{out}}}{\text{Amount}_{\text{in}} - \text{Gas}}$.
  - Concentration (Gini coefficient) of incoming counterparties.
- **Counterparty & Graph Proximity:**
  - Fraction of 1-hop neighbors with confirmed VASP labels.
  - Fraction of 1-hop neighbors associated with mixers or bridges.

### Explainability
Using TreeSHAP, the UI displays waterfall plots showing the exact contribution of each feature to the top predicted class probability.

---

## 4. M3: Guided Tracing Search Policy

### The Rate-Limit Problem
In live production, free-tier blockchain APIs (TronGrid, Etherscan) enforce rate limits (typically 3–5 requests/second). Blind Breadth-First Search (BFS) explores hundreds of low-probability branches, exhausting API quotas before reaching the cash-out point.

### The Guided Solution
M3 formulates multi-hop tracing as a **heuristic best-first search**. At each step, frontier nodes are prioritized by their estimated utility:

$$\text{Priority}(v) = \frac{\text{TaintShare}(v) \times P(\text{reaches VASP within } k \text{ hops} \mid v)}{\text{EstimatedCost}(v)}$$

- **Target:** Maximize VASP exit recall under a strict per-case API budget $B \in \{50, 100, 200, 500\}$.
- **Outcome:** Benchmarks demonstrate that M3 finds the first VASP cash-out exit in **up to 68% fewer API requests** compared to unguided BFS.

---

## 5. M4: Layering & Anomaly Detector

### Method
An unsupervised **Isolation Forest** trained on background transaction distributions from typical transfer flows.

### Anomaly Scoring
The model computes an anomaly score $s \in [0, 1]$. For flagged anomalies ($s > 0.65$), the system identifies the deviating features using normalized z-scores:
$$z_i = \frac{x_i - \mu_i}{\sigma_i}$$
This flags synthetic peeling, sudden volume surges, and unnatural timing regularity characteristic of algorithmic laundering bots.

---

## 6. M7: Freeze-Urgency Triage Engine

For high-volume cybercrime complaint systems (such as India's NCRP portal), hundreds of victim reports arrive daily. M7 ranks cases so officers can issue freeze requests where funds are most likely to be saved.

$$\text{Urgency} = \frac{\text{AmountAtRisk}_{\text{USD}} \times P(\text{Exit} = \text{VASP}) \times \text{Freshness}}{\max(\text{ETA}_{\text{hours}}, 1.0)}$$

Where:
- $\text{AmountAtRisk}$: Stolen fiat-equivalent balance currently unspent.
- $P(\text{Exit} = \text{VASP})$: Likelihood that the trail terminates at a regulated custodial exchange capable of freezing funds.
- $\text{Freshness} = \exp(-\lambda \Delta t_{\text{last\_move}})$: Exponential decay penalizing stale, long-abandoned trails.
- $\text{ETA}_{\text{hours}}$: Estimated time until funds are swept into an off-chain fiat gateway.

---

## 7. Model Card & Artifact Registry

Trained models are versioned under `ml/artifacts/`:
- `ml/artifacts/m1/v0.1/` (LightGBM Role Classifier + `calibrator.pkl`)
- `ml/artifacts/m1_elliptic_real/` (Elliptic Bitcoin benchmark model)
- `ml/artifacts/m3/v0.1/` (M3 Guided Tracing policy)
- `backend/app/ml/artifacts/m4_anomaly/v1/` (Isolation Forest anomaly model)

Each artifact directory contains:
1. `model.pkl`: Serialized model binary.
2. `config.json`: Hyperparameters, feature subsets, and thresholds.
3. `metrics.json`: Out-of-sample PR-AUC, F1, and calibration error.
4. `MODEL_CARD.md`: Intended use, dataset provenance, and documented false-positive modes.
