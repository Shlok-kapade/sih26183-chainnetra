# 07 — Evaluation, Demo, SIH Deliverables

## Evaluation suite (`make eval` -> `docs/evaluation/RESULTS.md`)
1. **M1** role classifier: temporal split + leave-one-exchange-out; macro-F1, per-class PR-AUC, confusion matrix, ECE + reliability plot, baselines (rules, logistic), bootstrap CIs, ablation of feature groups.
2. **M1b** Elliptic BTC: precision/recall/F1/PR-AUC on later timesteps.
3. **M3** guided tracer: recall vs API-calls curves for guided / BFS / DFS / taint-greedy / random on held-out seeds; recall@B table; mean calls-to-first-exit.
4. **M2/M4** (if built): ablation vs M1; anomaly detector sanity on synthetic injections.
5. **Pattern detectors**: precision/recall on SYNTHETIC injected patterns (explicitly labeled).
6. **System**: end-to-end latency in fixture mode; cache hit rate; API calls per case; number of labels by source; chains covered.
7. **Limitations section auto-included**: label bias, weak labels, unlabeled exchanges, payment-processor false positives, provider incompleteness.

## Synthetic laundering generator (`scripts/synth_laundering.py`)
Seeded generator producing transaction graphs with: layering via fan-out/fan-in, peel chains, rapid forwarding, dormancy bursts, round trips, structuring, exchange deposit funnels (many deposits sweeping to a hot wallet), P2P-like pass-through, swap hops, bridge hops, plus benign look-alikes (payment processor sweeper, market maker). Emits fixtures in the same shape as provider responses so the full pipeline runs offline. Output tagged `SYNTHETIC`. Used for unit tests, detector evaluation and load tests only.

## Demo cases (`data/demo/cases.yaml`)
- D1: multi-hop USDT-TRC20 trace ending in a CONFIRMED exchange collection wallet (public data).
- D2: deposit-funnel case -> PROBABLE exchange via DAR + M1.
- D3: trail leaving via private wallet / P2P-like pass-through -> exit report says "left regulated perimeter" with recommended route.
- D4: ETH swap hop + bridge (POSSIBLE cross-chain link).
- D5: BTC case with co-spend clustering.
- D6: honest failure: sparse/fresh wallet -> UNATTRIBUTED with reasons.
- D7: SYNTHETIC bulk set of ~50 complaints to show triage ranking.
`scripts/preflight.py` replays each demo case in fixture mode and asserts expected outputs; must pass before any presentation.

## 5-minute demo script
1. Bulk-import 50 complaints -> triage queue ranks by urgency (30s).
2. Open top case -> live progress with API-call counter (30s).
3. Graph + headline result + confidence tiers + "why" panel (90s).
4. Trace-efficiency chart: guided vs BFS, same recall with fewer calls (45s).
5. Exit-type case (private wallet/P2P) showing honest escalation advice (45s).
6. Evidence tab + report PDF + freeze-request draft + hash verification (45s).
7. Model Center: metrics, calibration, limitations (30s).

## SIH deliverables (per official format; SPOC uploads)
- Source code link (GitHub), README with setup, architecture doc (≤2 pages), demo video (≤2 min), technical PPT (use the official template).
- **PPT outline**: 1 Problem & user (investigator, freeze window) · 2 Proposed solution (pipeline diagram) · 3 Innovation (ML + guided tracing + exit taxonomy + batch triage) · 4 Technical approach (stack, data sources, free-tier strategy) · 5 ML results (auto-generated tables/plots) · 6 Feasibility & implementation (phases, offline mode) · 7 Impact (time saved, freeze rate, integration with NCRP/SAHYOG) · 8 Novelty vs existing tools (commercial platforms; open prototypes) · 9 Limitations & ethics · 10 Roadmap.
- **Video script (≤2 min)**: problem (10s) → triage + trace demo (60s) → efficiency + honesty about limits (30s) → impact (20s).

## Jury Q&A prep (write answers into `docs/sih/QA.md`)
Who faces this problem today and what do they do now? · Why not Chainalysis/TRM? (cost, access, India-specific workflow, offline, transparent) · How do you know attributions are right? (benchmarks, tiers, abstention) · False positives (payment processors, OTC)? · Ground truth limits? · Legal admissibility? (integrity hashes only; not certification) · Privacy (no PII) · Scalability (indexing, budgets, batch) · What if funds go through mixers/bridges? · Roadmap to production (own indexers, licensed labels, VASP APIs).
