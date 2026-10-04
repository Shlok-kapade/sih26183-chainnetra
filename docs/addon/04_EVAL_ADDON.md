# 04 — Evaluation (new scripts; results written to a new file `docs/evaluation/ADDON_RESULTS.md`)

All numbers come from scripts; SYNTHETIC results are labeled; no hand-typed metrics.

## A. Scatter–gather (`ml/addon/eval_cohorts.py`, `scripts/addon/synth_scatter.py`)
Scenarios: n in {100, 1k, 10k, 100k} · single vs multi-collector · 2–4 layers · partial convergence (leakage elsewhere) · decoy recipients · entity-level convergence (many deposit addresses of one exchange) · benign look-alikes (airdrop, bulk withdrawal, dust).
Metrics: collector precision/recall · coverage estimate error (sample vs exact) · unaccounted-mass accuracy · API calls vs naive expand-all (counted by the mock provider) · runtime · false-positive rate on look-alikes.
Acceptance: planted collectors recovered in noise-free runs for n >= 1,000 · estimates within the theoretical sampling bound · look-alikes never `CONVERGENCE_CONFIRMED` · API calls scale ≈ n/200 + m + K·pages, not n.

## B. FOT replay (`ml/addon/eval_fot.py`, `scripts/addon/synth_timeline.py`)
1. Cases: cached real public cases (fixtures with full future known) + SYNTHETIC timelines.
2. Replay: complaint time `T0 = seed_time + δ`, δ in {1 h, 6 h, 24 h}; budget `B`; the agent sees only data with `ts <= simulated now` (ClockPort); ground truth read from the full chain.
3. **Secured value** of a plan = value actually at targeted positions at `t_exec` (report with `p=1` as upper bound and with configured priors).
4. Baselines: **B1** trace to completion then notify the final exchange · **B2** BFS then notify first exchange found · **B3** M3-guided then notify first exchange · **B4** FOT.
5. Metrics: secured-value fraction (mean ± bootstrap CI) · time-to-first-action · API calls · regret vs oracle plan (sees the future) · plan stability.
6. Ablations: no uncertainty bounds · no issuer lever · no VOI/act-now · static hazard · no cohort accounting.
7. Sensitivity: vary `p_success` and latency ±50%; report ranking stability (substitute for unknowable real rates).
8. Report negative results honestly.

## C. M8 hazard (`ml/addon/train_m8_hazard.py`)
Temporal split; time-dependent AUC; calibration of predicted hazard; baseline = constant hazard. Model card in `ml/artifacts/m8/`.

## D. M9 linking (COULD)
Recall@k / MRR for other-half retrieval vs N distractors; compare with hand-crafted feature kNN baseline.

## Demo cases (new fixtures under `data/addon_demo/`)
- **D8 (SYNTHETIC)**: 1 wallet scatters to 10,000+ wallets, converges into 2 collectors that forward to an exchange — show cohort super-node, Sankey, verified coverage, unaccounted mass, API-call savings.
- **D9**: timeline replay — funds sit in an intermediate USDT wallet for hours, then move toward an exchange. Show the plan at three moments (issuer blacklist + exchange hold -> plan changes after movement), the countdown, and secured-value vs baselines (generated numbers only; priors labeled illustrative).
