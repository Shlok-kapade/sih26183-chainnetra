# 05 — Build Plan & Antigravity Prompts (add-on)

Priority: **MUST** = A0–A3 · **SHOULD** = A4–A5 · **COULD** = A6. If time is short: A0, A1, A2, A3 (core planner + eval) first.

## Phases
- **A0 Audit (MUST)** — map the repo, run baseline tests, create `docs/addon/{REPO_MAP,TOUCHED_FILES,ADDON_STATE}.md`. Accept: REPO_MAP lists real file paths for every port in 00.
- **A1 Seam + data (MUST)** — `ports.py`, `adapters_existing.py`, `adapters_fixture.py`, config YAMLs, new Alembic revision, models. Accept: ports unit-tested with fixture adapters; migration applies and rolls back; existing tests unchanged.
- **A2 Cohorts (MUST)** — 01 spec end to end + `synth_scatter.py` + `eval_cohorts.py`. Accept: 04-A acceptance.
- **A3 FOT core (MUST)** — mass map, levers, planner, plan API, Action Plan tab (basic), property tests, brute-force comparison. Accept: 02 acceptance for conservation and optimality.
- **A4 VOI + replay eval (SHOULD)** — VOI priority, act-now rule, replay harness, baselines, ablations, sensitivity, `ADDON_RESULTS.md`.
- **A5 Watch + M8 (SHOULD)** — hazard model, watcher job, SSE events, fixture timeline replay, WatchFeed UI.
- **A6 Extras (COULD)** — M9 linking, F6 feedback, plan PDF report polish.

## Prompts (paste in order; one per session/phase)

### Prompt A0 — audit
```
Read docs/addon/ADDON_AGENTS.md and docs/addon/00_ADDON_OVERVIEW.md. Do NOT write feature code yet. Audit this repository: find where the data adapters/cache/rate-limiter, canonical Transfer model, trace engine, labels/clustering/attribution, ML models (M1, M3 if present), DB models + migrations, API routers + auth, job runner + SSE events, and frontend routes/components live. Run the existing test suite and lint and record results. Write docs/addon/REPO_MAP.md (real paths, key function names, how to run things), docs/addon/TOUCHED_FILES.md (empty template) and docs/addon/ADDON_STATE.md. List which ports from 00_ADDON_OVERVIEW are already satisfiable and which need fallbacks. Stop after that and summarize.
```

### Prompt A1 — seam and data
```
Read docs/addon/ADDON_AGENTS.md, 00_ADDON_OVERVIEW.md, 03_INTEGRATION_DATA_API_UI.md and docs/addon/REPO_MAP.md. Implement Phase A1: addon/ports.py, adapters_existing.py (the only module importing existing code), adapters_fixture.py, config YAMLs (levers.yaml entries marked ILLUSTRATIVE), the new Alembic revision for the addon_* tables, SQLAlchemy models in addon/db/. Additive only; list any existing-file edit in TOUCHED_FILES.md. Run existing tests + new tests; update ADDON_STATE.md.
```

### Prompt A2 — cohorts
```
Read docs/addon/01_SCATTER_GATHER_ADDON.md, 04_EVAL_ADDON.md (section A) and REPO_MAP.md. Implement Phase A2 under addon/cohorts/ plus scripts/addon/synth_scatter.py and ml/addon/eval_cohorts.py. Use a mock TransferPort that counts API calls. Cohort members must never become graph nodes. Add tests for benign look-alikes. Generate ADDON_RESULTS.md section A from the eval script only. Run all tests; update ADDON_STATE.md.
```

### Prompt A3 — FOT core
```
Read docs/addon/02_FOT_CORE_ADDON.md (F1–F3), 03_INTEGRATION_DATA_API_UI.md and REPO_MAP.md. Implement Phase A3: fot/mass_map.py, levers.py, planner.py, plan service + routes, and the Action Plan tab (basic) in frontend/src/addon/. Include property tests for mass conservation and a brute-force comparison test for the greedy planner on small random instances. Priors must be marked ILLUSTRATIVE in config and shown in the UI banner; never display an expected-secured value without its interval. Additive only. Run all tests; update ADDON_STATE.md.
```

### Prompt A4 — VOI + replay eval
```
Read 02_FOT_CORE_ADDON.md (F4) and 04_EVAL_ADDON.md (section B). Implement fot/voi.py (priority + act-now rule) using TracePort.enqueue_expand, fot/replay.py with ClockPort-based simulated time, scripts/addon/synth_timeline.py, and ml/addon/eval_fot.py with baselines B1–B4, ablations and ±50% sensitivity. Write results only via the script into docs/evaluation/ADDON_RESULTS.md with bootstrap CIs and a limitations section. Report negative results honestly.
```

### Prompt A5 — watch + hazard
```
Read 02_FOT_CORE_ADDON.md (F5) and 04_EVAL_ADDON.md (section C). Implement fot/hazard.py (+ ml/addon/train_m8_hazard.py with point-in-time features, temporal split, calibration, model card), fot/watch.py as a job using the existing job runner, SSE events plan_changed/mass_moved, WatchFeed UI, and a fixture timeline replay mode. Keep everything behind ENABLE_WATCH.
```

### Prompt A6 — extras (optional)
```
Read 02_FOT_CORE_ADDON.md (F6, M9) and 04_EVAL_ADDON.md (section D). Implement the Beta–Bernoulli outcome feedback with Thompson sampling (synthetic demo data labeled) and the split-half contrastive M9 linking model with recall@k/MRR eval. Skip anything that destabilizes the build.
```

### Resume prompt
```
Read docs/addon/ADDON_AGENTS.md and docs/addon/ADDON_STATE.md. Run the full test suite. Continue from the first unfinished addon phase. Do not touch unrelated existing code.
```

### Final verification prompt
```
Run the full test suite, lint, ml/addon/eval_cohorts.py and ml/addon/eval_fot.py in fixture mode. Confirm: with ENABLE_COHORTS=false ENABLE_FOT=false ENABLE_WATCH=false the app behaves exactly as before; every existing-file edit is listed in TOUCHED_FILES.md; no metric in UI/docs is hand-typed; priors are labeled ILLUSTRATIVE everywhere. List anything stubbed.
```
