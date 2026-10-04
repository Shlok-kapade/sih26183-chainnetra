# 00 — Add-on Overview

## What gets added
- **Cohort layer**: treats a scatter (one wallet -> thousands of wallets) as one aggregated object, finds where it converges, and feeds the main trace.
- **FOT layer** (core): mass map -> lever model -> planner -> VOI tracing + act-now rule -> live frontier watch -> replay evaluation.
- **Hazard model M8** (survival) and optional **M9** campaign linking.
- New API routes, tables, UI tabs, eval scripts, synthetic generators.

## Architecture: ports + adapters
```
existing ChainNetra code  <--  addon/adapters_existing.py  -->  addon/ports.py  <--  addon/{cohorts,fot,...}
```
`addon/ports.py` (Python Protocols / ABCs):
- `TransferPort`: `outgoing(chain, address, asset, since, until, max_pages) -> AsyncIterator[Transfer]`, `incoming(chain, address, asset, since, until, max_pages) -> AsyncIterator[Transfer]` (must go through the existing cache + rate limiter + call-budget counter).
- `LabelPort`: `lookup(chain, address) -> Label | None`; `cluster_of(chain, address) -> ClusterRef | None`; `entity_of(chain, address) -> Entity | None`.
- `RolePort`: `role_probs(chain, address, as_of_ts) -> dict | None` (existing M1; `None` if unavailable).
- `TracePort`: `get_case_graph(case_id)` (nodes, edges, taint, termination reasons), `enqueue_expand(case_id, address, priority, budget)` (reuse the existing trace engine to expand a node), `seed_info(case_id)`.
- `ExitPolicyPort`: `p_exit(case_id, address) -> float | None` (existing M3 if present; else `None`, fallback = 0.5 prior).
- `ClockPort`: `now()`; replay mode injects a simulated clock.
- `BudgetPort`: `calls_used(case_id)`, `calls_left(case_id)`, `charge(n)`.
- `NotifyPort`: `emit(case_id, event_type, payload)` -> existing SSE/job events if present; else a minimal new SSE channel.
`adapters_existing.py` implements each port using the repo's real modules (found in REPO_MAP.md). A parallel `adapters_fixture.py` implements the ports from recorded fixtures/in-memory graphs for tests and replay.

## New folder layout (all new)
```
backend/app/addon/
  ports.py  adapters_existing.py  adapters_fixture.py  config.py
  cohorts/{detect.py,sample_vote.py,verify.py,score.py,service.py}
  fot/{mass_map.py,levers.py,planner.py,voi.py,hazard.py,watch.py,replay.py,service.py}
  api/{routes_cohorts.py,routes_fot.py}
  db/{models_addon.py}   # + one new alembic revision
  tests/
backend/config/addon/{convergence.yaml,levers.yaml,fot.yaml}
ml/addon/{train_m8_hazard.py,train_m9_linking.py,eval_fot.py,eval_cohorts.py}
scripts/addon/{synth_scatter.py,synth_timeline.py}
frontend/src/addon/{ActionPlanTab.tsx,MassMapSankey.tsx,CohortNode.tsx,CohortDrawer.tsx,WatchFeed.tsx,WhatIfPanel.tsx,api.ts}
docs/addon/{REPO_MAP.md,TOUCHED_FILES.md,ADDON_STATE.md}
```

## Feature flags & config
`ENABLE_COHORTS`, `ENABLE_FOT`, `ENABLE_WATCH`. Config in `backend/config/addon/*.yaml`, hashed into reports/plan records (`params_hash`).

## Integration points (the only existing-file touches allowed)
1. Register addon routers (1 line).
2. Chain the new Alembic revision (new file; no edits).
3. Add nav/tab entries in the frontend (1–2 lines) pointing to `frontend/src/addon/*`.
4. Call `cohorts.service.maybe_register_scatter(...)` from the trace loop **only if** the existing engine exposes a hook; otherwise run cohort detection as a post-processing job triggered after trace completion (preferred; zero edits).
5. Call `fot.service.recompute_plan(case_id)` after trace completion via a job (same preference).
