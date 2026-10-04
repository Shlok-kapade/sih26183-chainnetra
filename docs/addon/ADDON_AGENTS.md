# ADDON_AGENTS.md — rules for adding scatter–gather + FOT to the existing ChainNetra repo

The base project already exists. Your job is to **add** features without breaking or rewriting it.

## Additive-only rules
1. **Audit first.** Before writing code, inspect the repo and write `docs/addon/REPO_MAP.md`: where adapters/providers, cache, canonical Transfer model, graph/trace engine, labels/attribution, ML models (M1/M3 if present), DB models/migrations, API routers, job runner, frontend routes live, plus commands that run tests/lint/dev. Run the existing tests and record the baseline result.
2. **New code goes in new files/folders** under `addon/` namespaces (see 00_ADDON_OVERVIEW). Do not refactor, rename or reformat existing files.
3. **One seam.** All add-on logic depends only on the *ports* in `addon/ports.py`. Only `addon/adapters_existing.py` may import existing project modules.
4. **Minimal registration edits only** (e.g., one `include_router` line, one nav link, one migration chained after the current head). Every edit to an existing file must be listed in `docs/addon/TOUCHED_FILES.md` with the reason. If an existing file needs more than a registration line, stop and ask.
5. **Feature flags**: `ENABLE_COHORTS`, `ENABLE_FOT`, `ENABLE_WATCH` (default true in dev). With flags off, behavior is identical to before.
6. **Own migration**: one new Alembic revision creating only new tables; never alter existing tables.
7. **Tests must stay green.** Run the existing suite before and after each phase.
8. **If an existing capability is missing** (e.g., no M1 model yet), implement the port with a documented fallback returning `None`/heuristic; do not build the missing base feature unless asked.

## Project rules (unchanged)
Free/open-source only · no fabricated data or metrics (all numbers from eval scripts) · SYNTHETIC data labeled everywhere · outputs are investigative leads, never proof or identity · freeze-success and latency priors are ASSUMPTIONS (mark `ILLUSTRATIVE` in config and show a banner in the UI) · no victim PII · do not copy code from other repos · novelty wording only as in `02_FOT_CORE_ADDON.md`.

## Done = code + tests + docs line in `docs/addon/ADDON_STATE.md` + works in fixture/offline mode.
