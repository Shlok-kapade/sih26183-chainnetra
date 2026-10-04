# 01 — Scatter–Gather (Split & Converge) Cohort Tracing

Scenario: seed -> W0 -> N wallets (up to ~100,000, tiny amounts) -> optional layers -> convergence at a few collectors or at one exchange (via many deposit addresses) -> cash-out.
Note: scatter–gather is a standard laundering pattern in the literature (e.g., IBM AMLworld). It is a **capability** here, not our invention.

## Why plain tracing misses it
1. Per-wallet taint is tiny, so per-wallet `min_taint` thresholds drop every branch.
2. "Top-N fan-out" keeps only the largest branches; all are small.
3. API budget: querying 100k wallets exhausts free quotas. Enumerating W0's outgoing list is cheap (about n/200 pages on TronGrid ≈ 500 calls for 100k).

## Principles
Track **cohorts** not wallets · apply thresholds to the cohort's **aggregate** · find convergence by **sample -> vote -> verify** · verify against the **full** member set via set membership on the collector's inbound transfers · aggregate by **cluster/entity** too · always show *verified* vs *estimated*.

## Definitions
- **Scatter event**: `u` sends the tracked asset to >= `K_scatter` (default 50) distinct recipients within `T_scatter` (24 h), amounts far below the seed amount.
- **Cohort**: `{origin, n, S_total, amount median/CV/histogram, t_start, t_end, layer, truncated, kind}`; members live in a table, never as graph nodes.
- **Collector**: address / cluster / entity receiving a large share of the cohort's onward value.

## Algorithm (`addon/cohorts/`)
1. **detect.py** — page `u`'s outgoing transfers (via `TransferPort`), compute scatter stats on the fly; stop at `N_max` (200,000) and set `truncated`.
2. **service.py** — register cohort + members; add ONE super-node to the case view (stored in addon tables; do not mutate existing graph tables).
3. **sample_vote.py** — stratified sample `m = min(n, 300)` (strata: amount quantile × arrival-time bucket). For each sampled member fetch outgoing transfers after receipt. Build vote table: destination -> votes, value. Map destinations to clusters/entities (`LabelPort`) and aggregate votes by cluster/entity. If most sampled members forward to fresh cohort-like wallets, create the next-layer cohort (`L_max` = 4) and recurse with re-sampling.
4. **verify.py** — for top `K` (10) candidate collectors fetch inbound restricted to `[t_start, t_end + slack]` and asset; filter senders by membership in the full cohort. Compute exactly: `coverage_value`, `coverage_breadth`, `time_compactness`, `conservation_error`. Sample-based estimate is `votes/m` (worst-case ±5.7 percentage points at 95% for m=300).
5. **score.py** — convergence score (weights in `config/addon/convergence.yaml`): coverage_value 0.40 · breadth 0.20 · time_compactness 0.15 · conservation 0.15 · collector novelty 0.10. Tiers: `CONVERGENCE_CONFIRMED` (verified, score >= 0.8) · `CONVERGENCE_PROBABLE` (0.5–0.8 or sample-only) · `NONE`.
6. **Hand-off to the existing trace**: for each collector call `TracePort.enqueue_expand(case_id, collector, priority, budget)` with taint = `coverage_value × cohort share`, so the existing engine continues toward the exit. Record **unaccounted mass** = 1 − Σ coverage.
7. **Bidirectional rescue**: if forward sampling fails, take labeled exchange hot wallets / deposit-funnel addresses (`RolePort`/`LabelPort`), fetch their inbound in the window, and test overlap with the member set.

## Benign look-alikes (document + test)
Airdrops/payroll (fan-out, no convergence) · exchange bulk withdrawals · sybil airdrop farming (fan-out then fan-in) · dust attacks / address poisoning (tiny amounts, no onward movement -> `DUST_DISPERSAL`) · exchange sweeps (expected fan-in). Each result carries `false_positive_note`.

## API-call estimate (design, to be measured)
≈ `n/200` (enumerate) + `m` (+pages) (sample) + `K × pages` (verify), versus ≥ `n` for naive expansion. Report measured counts from the mock provider.

## Outputs consumed by FOT
Cohort super-positions with `value`, bounds, collector candidates with coverage, unaccounted mass, verified/estimated flag.
