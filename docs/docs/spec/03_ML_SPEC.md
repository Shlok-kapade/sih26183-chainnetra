# 03 — ML Specification

All models live in `backend/app/ml/`, train via `ml/train/*.py`, evaluate via `ml/eval/*.py`, and register in `ml/artifacts/<model>/<version>/` with: `model.*`, `config.yaml`, `metrics.json`, `data_manifest.json` (dataset hashes), `MODEL_CARD.md`. Loader: `registry.load("m1", version="latest")`. Every prediction stores `model_version`.

## Global rules
- **Point-in-time features only**: for a label at time t, compute features from transfers with `ts <= t`.
- **Splits (report all)**: (a) temporal split; (b) entity-disjoint / leave-one-exchange-out (train without exchange X, test on X); (c) random stratified as a sanity baseline only.
- **Calibration**: isotonic (or Platt) on a held-out calibration fold; report ECE and reliability curve. **Abstain** when max prob < threshold -> `UNATTRIBUTED`.
- **Baselines** for each model: rules-only heuristic, logistic regression.
- **Explainability**: SHAP top-k features per prediction stored with the result.
- **Imbalance**: class weights / focal loss; report per-class PR-AUC (not just accuracy).
- Seeds fixed; runs reproducible from `make train-*`.
- `make eval` regenerates `docs/evaluation/RESULTS.md` (tables + plots). No hand-typed numbers.

---
## M1 — Address Role Classifier (core; MUST)
**Task**: multi-class over `{exchange_hot_or_collection, exchange_deposit, mixer, bridge, dex_or_contract, illicit (scam/phishing/sanctioned), personal_or_unknown}`.
**Model**: LightGBM (multiclass) + isotonic calibration. Optional stacked ensemble with M2.
**Features** (per address, computed on chain-specific windows, all point-in-time):
- Degree: n_in_cp (distinct senders), n_out_cp, in/out tx counts, in/out value sums, log-scaled.
- Balance dynamics: turnover = total_out / max(avg_balance, eps), end-of-window balance ratio, near-zero-balance fraction of time.
- Forwarding behavior: fraction of received value forwarded within {10 min, 1 h, 24 h}; median dwell time; amount-match ratio (out ≈ in − fee); single-target forwarding share (top-1 out counterparty share).
- Fan structure: fan-in ratio (n_in_cp / n_out_cp), value-weighted Gini of inflows/outflows, share of inflows from addresses that also send to the same top target (consolidation signature).
- Temporal: activity-by-hour entropy (exchanges are 24/7), inter-arrival mean/CV, burstiness, account age, days-active ratio.
- Value shape: share of round-number amounts, amount entropy, small-deposit share.
- Counterparty labels: share of flow with labeled VASP / mixer / bridge / DEX / sanctioned neighbors (1-hop, using labels available at time t only, excluding the target's own label).
- Contract flags: is_contract, has verified source, token diversity, interacts with router/bridge contracts.
- Chain id and asset mix (train per-chain or include chain as feature; report both).
**Training data**: labeled sets from 02. For deposit addresses use weak_DAR labels flagged separately; report metrics with and without them.
**Outputs**: `{class: prob}`, calibrated; top SHAP features; abstain flag.
**Acceptance**: beats logistic + rules baselines on macro-F1 and PR-AUC on temporal split; ECE < 0.10 after calibration (report actual); leave-one-exchange-out table included; model card documents label bias and payment-processor false positives.

## M1b — BTC illicit transaction scorer (SHOULD)
LightGBM/RandomForest on Elliptic Bitcoin dataset with the standard temporal split (early timesteps train, later test; verify convention from dataset docs). Report illicit-class precision/recall/F1 and PR-AUC. Purpose: credible, reproducible Bitcoin benchmark and a BTC risk feature. Note dataset covers transactions not addresses; if Elliptic++ is accessible, add address-level evaluation.

## M2 — Graph Neural Network role/risk model (COULD; do after M1 + M3)
GraphSAGE and/or GATv2 (PyG, CPU) on sampled 2-hop ego-graphs (neighbor sampling, fanout ≤ 25/10). Node features = M1 features; edge features = log value, tx count, time delta. Semi-supervised on labeled nodes; same splits as M1.
Deliver: ablation table M1 vs M2 vs stacked. Keep it small (hidden 64, ≤3 layers) so it trains on a laptop CPU. If M2 does not beat M1, report that honestly and keep M1 in production.

## M3 — Guided Tracing Policy (core differentiator; MUST if time allows, else SHOULD)
**Why**: free APIs are rate-limited; blind BFS wastes calls on branches that never reach an exchange.
**Task**: for a frontier node v with incoming tainted flow, predict
1. `p_exit` = P(flow reaches a VASP within remaining hop budget k),
2. `eta` = expected hours until cash-out (optional; log-normal or quantile GBM).
**Model**: LightGBM binary classifier (+ quantile regressor for eta). Features: M1 role probabilities of v, path features (hops so far, taint share remaining, dwell so far, fan-out width, value trend, elapsed since seed), local structure (n_out_cp, top-1 forward share), label proximity.
**Training data**: trace-labeled set (02): seeds from illicit lists expanded in cached graphs; per-node label = reached labeled VASP within k hops (yes/no) and time-to-reach. Group split by seed (no seed appears in both train and test).
**Use in engine**: best-first search with priority = `taint_share * p_exit / est_cost(v)` under a per-case API budget B.
**Baselines**: BFS, DFS, taint-weighted greedy (priority = taint_share), random.
**Metric (headline)**: recall of true VASP exits vs number of API calls (curve, plus recall@B for B in {50,100,200,500}); also mean calls-to-first-exit. Report on held-out seeds.
**Caveat to document**: ground truth only includes exits to *labeled* VASPs; unlabeled exchanges are invisible -> metrics are lower bounds.

## M4 — Layering/Structuring anomaly detector (SHOULD)
Unsupervised IsolationForest (and optional small autoencoder) on path-level features (hop count, value decay per hop, split ratio, timing regularity, round-amount share, revisit rate). Complements deterministic detectors in 04; never sole evidence. Tune contamination via synthetic injected patterns (SYNTHETIC-labeled) and sanity-check on real cached traces. Output anomaly score + which features deviate (z-scores).

## M5 — Exit-type resolver (MUST; rules + M1)
Deterministic decision layer over M1 probs + labels + patterns -> `exit_type in {VASP, P2P_OTC_SUSPECTED, PRIVATE_WALLET, MIXER, BRIDGE, DEX_SWAP, SANCTIONED, UNKNOWN}` with tier and evidence. P2P/OTC-suspected is heuristic only (many distinct counterparties, quick pass-through, no VASP label, repeated similar-size transfers) and capped at `POSSIBLE` tier. Document as heuristic in UI.

## M6 — Entity clustering (MUST; deterministic)
- EVM/TRON: Deposit-Address-Reuse (params alpha=amount tolerance, tau=time window; tune on labeled deposit->main pairs), plus funding-source linkage (first-gas funder) as weak edge.
- BTC: multi-input co-spend + conservative change-address rule; **skip CoinJoin-like txs** (many equal outputs) and flag exchange-sized clusters.
- Union-Find with cluster confidence; never merge on a single weak edge; store which heuristic linked each pair.

## M7 — Triage ranking (MUST; formula + M3)
`urgency = value_at_risk_usd * P(exit within k hops) * freshness(t_since_last_move) / max(eta_hours, 1)`; weights in `risk_weights.yaml`. UI shows the components. Evaluate qualitatively on replay of the demo set and with a ranking sanity test (higher-value fast-moving synthetic cases outrank dormant ones).

## Model cards (required per model)
Intended use, training data + provenance, splits, metrics with confidence intervals (bootstrap), calibration plot, failure modes (payment processors, OTC desks, shared deposit addresses, stale labels), fairness/harms note (misattribution risk), version + hash.
