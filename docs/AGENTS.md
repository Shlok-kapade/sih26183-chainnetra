# AGENTS.md — ChainNetra (SIH 2026, PS SIH26183)

You are building **ChainNetra**: a free/open-source blockchain forensic platform that takes a victim-reported suspect wallet and identifies the exchange/VASP (or other cash-out route) that received the funds, with ML-assisted attribution, evidence and investigator reports.

## Read first (in order)
1. `docs/spec/00_BRIEF.md` 2. `01_ARCHITECTURE.md` 3. `08_BUILD_PLAN.md` (follow its phase order), then the other specs when a phase needs them.
Keep `docs/PROJECT_STATE.md` updated after every phase: what is done, what is stubbed, known issues, exact commands to run.

## Hard rules
- **Free only.** No paid APIs, no paid datasets, no credit-card services. Free-tier keys go in `.env` (never committed). Every provider needs an offline fixture fallback.
- **No fabricated data or numbers.** Every metric shown in UI/docs must be produced by a committed script (`make eval`) and written to `docs/evaluation/RESULTS.md` automatically. Synthetic data must be labeled `SYNTHETIC` everywhere it appears and never used for headline accuracy claims.
- **Honest language.** Outputs are *investigative leads*, not proof of guilt, ownership or identity. Never claim to de-anonymize a person. Always show confidence tier + evidence + limitations.
- **No copying** code from other public SIH/forensics repos (many have no licence). Use papers/docs for ideas only; write original code.
- **Verify external APIs before relying on them**: make one tiny live call, record the response as a fixture in `data/fixtures/`, and code against the recorded shape. Endpoints in the specs are starting points, not guarantees.
- **Respect rate limits**: token-bucket per provider, exponential backoff on 429/403/503, cache every response (hash + timestamp), resumable pagination.
- **Leakage discipline in ML**: features use only data with timestamp <= label time; report temporal and entity-disjoint splits. See `03_ML_SPEC.md`.
- **No victim PII / KYC** stored. Complaint reference numbers only.

## Engineering standards
- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, Pydantic v2, type hints everywhere, `ruff` + `mypy --strict` on `app/`.
- Frontend: React 18 + TypeScript + Vite + Tailwind + Cytoscape.js + Recharts. Accessible (keyboard, contrast), dark mode.
- ML: scikit-learn, LightGBM, PyTorch + PyTorch Geometric (CPU), SHAP. Deterministic seeds. Artifacts versioned under `ml/artifacts/`.
- Tests: `pytest` (+ `hypothesis` for graph invariants). Each phase ships with tests; do not move on with failing tests.
- Small, reviewable commits: `feat(scope): ...`, `fix(scope): ...`.
- Prefer boring, few moving parts: Postgres + a table-backed job queue (no Redis/Kafka needed).

## Commands (create these Makefile targets in Phase 0)
`make dev` · `make test` · `make lint` · `make fixtures` · `make train-m1` · `make train-m3` · `make eval` · `make demo` (offline demo with fixtures) · `make report`

## Definition of done (per feature)
Code + tests + docs line in PROJECT_STATE + works in offline fixture mode + errors surfaced in UI (no silent failures).
