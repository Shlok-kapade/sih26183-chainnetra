# 08 — Build Plan (follow in order; each phase ends with tests + PROJECT_STATE update)

Priority: **MUST** = core, **SHOULD** = differentiator, **COULD** = stretch. If time runs short, finish all MUST, then M3, then the rest.

## Phase 0 — Scaffold (MUST)
Monorepo per 01, Docker Compose (api, worker, db, web), Makefile targets, `.env.example`, ruff/mypy/pytest/CI, Alembic init, health endpoint, logging.
Accept: `make dev` starts stack; `make test` and `make lint` pass; `/health` OK.

## Phase 1 — Data layer (MUST)
Adapters: TRON (TronGrid), EVM (Etherscan V2 + Blockscout fallback), BTC (mempool.space/Esplora). Cache + evidence store, rate limiter, address validators, `make fixtures` recording tool, fixture replay mode.
Accept: for one address per chain, live and fixture mode produce identical canonical `Transfer` lists; 429 handling tested with mocked responses; hashes stored.

## Phase 2 — Graph + baseline tracing (MUST)
Canonical models, graph builder, haircut/poison/fifo taint, BFS engine with depth/threshold/budget/termination reasons, swap-hop support (EVM/TRON), bridge-unresolved exits.
Accept: property tests (taint conservation ≤ input, no negative values, termination always recorded); golden tests on synthetic graphs.

## Phase 3 — Labels, attribution, clustering (MUST)
Label loader with provenance + CLI (`load-labels`), OFAC + PoR + open label ingest scripts, attribution tiers, DAR clustering (EVM/TRON), BTC co-spend clustering with CoinJoin guard, exit-type resolver (rules-only first).
Accept: CONFIRMED match works; DAR unit tests; provenance shown for every label.

## Phase 4 — Patterns + synthetic generator (MUST)
Seven detectors + `synth_laundering.py` + detector evaluation script.
Accept: detector P/R on synthetic above documented thresholds; benign look-alikes tested.

## Phase 5 — ML core: features + M1 (+M1b) (MUST)
Feature pipeline (point-in-time), dataset builders (`ml/datasets/`), M1 training with calibration, SHAP, model registry, model card, eval script with temporal + leave-one-exchange-out.
Accept: `make train-m1 && make eval` produces RESULTS.md with baselines and CIs; predictions integrated into attribution (PROBABLE/POSSIBLE) with abstention.

## Phase 6 — Guided tracing M3 (SHOULD — headline differentiator)
Build trace-labeled dataset from cached graphs, train M3, integrate best-first search with budgets, benchmark vs BFS/DFS/taint-greedy/random.
Accept: recall-vs-calls plot + recall@B table generated; UI-ready JSON.

## Phase 7 — Risk, triage, reports, evidence (MUST)
Risk engine (YAML weights), triage urgency (M7), evidence manifest, PDF/JSON/CSV reports, freeze-request draft, hash verify utility.
Accept: report contains findings, limitations, evidence refs, manifest hash; verify tool detects tampering.

## Phase 8 — API, jobs, auth, audit (MUST)
All endpoints in 05, Postgres job queue + worker + SSE, RBAC, audit log, bulk intake, complaint-source adapters (CSV/JSON/mock NCRP/SAHYOG).
Accept: API tests incl. authz; bulk 50-row import completes in fixture mode.

## Phase 9 — Frontend (MUST)
Pages per 06. Prioritize: Triage Queue → Case Workspace (Overview, Graph, Attribution, Evidence) → Model Center → the rest.
Accept: Playwright smoke test of the demo flow; a11y checks pass basic axe scan.

## Phase 10 — Advanced ML (COULD)
M2 GNN (PyG, CPU) with ablation; M4 anomaly detector; optional Solana adapter; optional stacked ensemble. Ship only if metrics support it; otherwise document negative results.

## Phase 11 — Demo, docs, SIH pack (MUST)
Demo cases + `preflight.py`, README, architecture doc (2 pages), `docs/sih/` (PPT outline filled with real generated numbers, video script, Q&A), LIMITATIONS.md, ETHICS.md, INTEGRATION.md, deployment guide (free hosts: Render/Railway/Oracle free tier — verify current terms).
Accept: `make demo` runs offline end-to-end; `make eval` regenerates all numbers; fresh-clone quickstart works.

## Working agreement for the agent
- Ask the human only for: API keys, ambiguous product decisions, or when a required free data source is unreachable (then propose alternatives).
- Keep `docs/PROJECT_STATE.md` current; list stubs honestly.
- Never mark a phase done with failing tests or missing acceptance evidence.
