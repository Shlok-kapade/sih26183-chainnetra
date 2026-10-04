# ChainNetra — spec pack for the AI IDE

Drop this folder's contents into an empty repo root (keep `AGENTS.md`, `GEMINI.md`, `docs/spec/*`). Open the folder in Antigravity (its rules loader reads `AGENTS.md` / `GEMINI.md` from the workspace root — confirm in Settings if it does not pick them up, and paste `AGENTS.md` into a Workspace rule if needed).

## Kickoff prompt (paste into the agent)
> Read AGENTS.md and all files in docs/spec/. Build ChainNetra exactly per docs/spec/08_BUILD_PLAN.md, one phase at a time. After each phase: run tests, update docs/PROJECT_STATE.md, then continue to the next phase without asking unless a decision is genuinely blocked. Start with Phase 0. Use offline fixtures when a live API is unavailable. Never invent evaluation numbers.

## Tips
- Use a strong model for Phases 2, 5, 6 (tracing + ML); a fast model for scaffolding/UI.
- If quota runs out, resume with: "Read AGENTS.md and docs/PROJECT_STATE.md, continue from the next unfinished phase."
- Get free API keys yourself first: Etherscan, TronGrid (optional: Blockscout). Put them in `.env` (see `.env.example` the agent creates).

## Files
| File | Purpose |
|---|---|
| AGENTS.md / GEMINI.md | Agent rules |
| docs/spec/00_BRIEF.md | Problem, scope, novelty, success metrics |
| 01_ARCHITECTURE.md | System design, stack, repo layout |
| 02_DATA_SOURCES.md | Free APIs, labels, datasets, caching |
| 03_ML_SPEC.md | All ML models, features, training, evaluation |
| 04_TRACING_ENGINE.md | Taint tracing, attribution, patterns, risk |
| 05_API_DATA_MODEL.md | DB schema, REST API, alert schema |
| 06_FRONTEND.md | UI pages and graph UX |
| 07_EVAL_DEMO_SIH.md | Benchmarks, synthetic generator, demo, SIH deliverables |
| 08_BUILD_PLAN.md | Phased tasks with acceptance criteria |
