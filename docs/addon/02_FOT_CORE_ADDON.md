# 02 — Freeze-Optimal Tracing (FOT): the core contribution

## Thesis
Open work and most tools optimise **detection/classification**. The investigator's objective is **value actually frozen**, under time pressure with limited analysts and API calls. FOT reframes tracing as a sequential decision problem:
(1) where is the stolen money now (probabilistically)? (2) which freeze lever can act, how fast, with what chance? (3) which action set maximises expected secured value? (4) is another tracing call worth the delay, or act now?

## F1 — Mass map (`fot/mass_map.py`)
- **Position** = address | cohort | cluster | entity. **Status**: `HELD` · `IN_TRANSIT` · `EXITED_VASP(E)` · `EXITED_OTHER(mixer|bridge|dex|p2p|private)` · `UNRESOLVED`.
- `mass_map(case_id, t)` -> rows `(position, status, value_est, value_lo, value_hi, confidence)`.
- Explored branches: haircut-taint mass read via `TracePort` (cohorts from 01 included). Unexplored/ambiguous mass stays **UNRESOLVED with bounds [0, unresolved]**; point estimate spread using `ExitPolicyPort.p_exit` and destination priors. Do not fake precision; show intervals.
- Snapshots over time (`mass_snapshots`) for time-slider UI and replay.
- Invariant: explored + unresolved = seed amount (minus modeled fees).

## F2 — Lever model (`fot/levers.py`, `config/addon/levers.yaml`)
| Lever | Acts on | Parameters |
|---|---|---|
| `VASP_HOLD(E)` | mass attributed to exchange/VASP E (hot wallet or deposit funnel) | `p_success(E)`, `latency_hours(E)`, `hold_validity_days`, decay with age of deposit |
| `ISSUER_BLACKLIST(token)` | mass at an address in a freezable stablecoin (USDT/USDC) | `p_success`, `latency_hours`, per address+token |
| `LEGAL_ESCALATION` | P2P/OTC/private/other exits | low `p_success`, long latency |
| `WATCH` | HELD mass not yet actionable | schedules monitoring (F5) |
All numeric defaults are **ASSUMPTIONS**, marked `ILLUSTRATIVE` in YAML and in the UI, editable per deployment. The contribution is the framework and its robustness, not real-world freeze rates.

## F3 — Planner (`fot/planner.py`)
- Survival `S(position, t_exec)`: probability mass is still there at execution (M8 hazard; default constant hazard from config).
- Action set value: `EV(A) = Σ over mass units m of value(m) × [1 − Π over a in A covering m of (1 − S_a × p_a)] − cost(A)`.
- Selection: **greedy by marginal gain under cardinality limit K** (analyst capacity). The probabilistic weighted-coverage objective is monotone submodular, so greedy achieves a (1 − 1/e) approximation; **unit-test against brute force** on small random instances.
- Output **Action Plan**: ranked actions with `expected_secured` (+lo/hi from mass bounds), `deadline` (when expected value falls below a fraction of today's), `prerequisites`, link to generated draft documents (VASP freeze request; issuer blacklist request template — both DRAFT, never sent).

## F4 — VOI tracing + act-now (`fot/voi.py`)
- Priority of expanding node v: `unresolved_mass(v) × p_resolve_to_lever(v) × lever_gain(v) / api_cost(v)`. `p_resolve_to_lever` from existing M3 via `ExitPolicyPort` (fallback prior). `lever_gain` = plan EV increase if v resolves to a lever target. Use `TracePort.enqueue_expand` with this priority.
- Anytime: publish a plan after the first actionable finding, keep refining. **Act-now trigger**: when `(−dEV/dt) × expected_delay_of_next_call > VOI(best next call)`, emit the plan now and continue tracing in background.

## F5 — Live frontier watch (`fot/watch.py`, `fot/hazard.py`) — the "real-time" in the PS
- Frontier = HELD positions. Budget-aware polling with adaptive interval (shorter when hazard is high).
- **M8 hazard model** (LightGBM discrete-time survival): P(moves within next Δ). Features: holding time so far, cluster/chain historical dwell, value, hour-of-day, previous-hop dwell, role probs, recent velocity. Train via `ml/addon/train_m8_hazard.py` on cached traces (point-in-time features only; temporal split).
- On movement: update mass map, recompute plan, `NotifyPort.emit(case_id, "plan_changed" | "mass_moved", payload)`.
- Fixture mode replays a recorded timeline for offline demos.

## F6 — Outcome feedback (COULD)
Investigators log `frozen | denied | too_late | no_response`; priors per lever/VASP update by Beta–Bernoulli; Thompson sampling picks which lever to try first when EVs are close. Demo data SYNTHETIC and labeled.

## Secondary — M9 Campaign linking (COULD, `ml/addon/train_m9_linking.py`)
Self-supervised process embeddings to link complaints from one operation. Positives = two disjoint halves of one process (e.g., a scatter cohort split in half), negatives = halves of other processes (contrastive loss). Descriptors: amount distribution, timing rhythm, hop depth, collector reuse, chain-specific fee/energy settings, funding pattern. Eval: retrieve the other half among N distractors (recall@k, MRR). Contrastive subgraph embeddings already exist for classification; our twist is same-process retrieval wired into the planner (union mass across victims).

## Claim wording (use as written)
"To our knowledge, open work on blockchain AML focuses on detection and classification (e.g., AMLworld laundering patterns, GNN and contrastive-subgraph classifiers) and on tracing/clustering heuristics. We did not find a published open framework that (i) models stolen funds as a probabilistic position distribution over time, (ii) separates exchange holds from stablecoin-issuer blacklists as levers with latency and decay, and (iii) jointly chooses tracing calls and freeze actions to maximise expected secured value under analyst-capacity and API-budget constraints." Verify with a Scholar/arXiv search before any stronger claim. Never say "first in the world".

## Acceptance
Mass conservation property tests · planner vs brute force (greedy ≥ (1−1/e)·optimum) · replay eval end-to-end in fixture mode · UI never shows an expected-secured number without its interval and the assumptions banner.
