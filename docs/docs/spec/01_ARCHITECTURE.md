# 01 — Architecture

## Stack (all free / open source)
| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, Pydantic v2, httpx (async), tenacity |
| DB | PostgreSQL 16 (SQLite in-memory for unit tests) |
| Jobs | Postgres-backed job table (`SELECT ... FOR UPDATE SKIP LOCKED`) + worker process. No Redis. |
| Graph | NetworkX in-memory per case; persisted as nodes/edges tables |
| ML | scikit-learn, LightGBM, PyTorch + PyG (CPU), SHAP, joblib |
| Frontend | React 18, TypeScript, Vite, Tailwind, TanStack Query, Cytoscape.js (+ fcose layout), Recharts |
| Reports | ReportLab (PDF), JSON, CSV |
| Infra | Docker Compose (api, worker, db, web/nginx). GitHub Actions CI (lint, test). |
| Live updates | Server-Sent Events for job progress |

## Repo layout
```
chainnetra/
  AGENTS.md  GEMINI.md  README.md  Makefile  docker-compose.yml  .env.example
  backend/
    app/
      api/            # routers: auth, cases, complaints, graph, labels, models, reports, triage
      core/           # config, security, logging, errors
      db/             # models, session, migrations (alembic)
      ingest/         # adapters: tron.py, evm.py (etherscan v2 + blockscout), btc.py, (solana.py stretch)
                      # cache.py, ratelimit.py, normalize.py
      graph/          # builder, taint, clustering (DAR, co-spend), export
      trace/          # engine (BFS + guided), termination, budgets, swap/bridge handling
      attribution/    # labels loader, tiers, confidence, exit-type taxonomy
      patterns/       # fan_in, fan_out, peel_chain, rapid_forwarding, dormancy_burst, structuring, round_trip
      ml/             # features.py, roles.py (M1), gnn.py (M2), policy.py (M3), anomaly.py (M4), registry.py, explain.py
      risk/           # scoring engine + weights yaml
      triage/         # urgency ranking, bulk intake
      evidence/       # raw response store, hashing, manifest, audit
      reports/        # pdf/json/csv, freeze-request draft
      jobs/           # queue, worker, pipeline orchestration
      cli.py          # load-labels, create-admin, fixtures, train, eval
    tests/
  ml/
    datasets/         # download/build scripts (no raw data committed if large)
    train/            # train_m1.py, train_m2.py, train_m3.py, train_m4.py
    eval/             # eval_*.py -> docs/evaluation/RESULTS.md
    artifacts/        # versioned models + metrics.json + model cards
  frontend/
  data/
    labels/           # CSVs with provenance (see 02)
    fixtures/         # recorded provider responses
    demo/             # demo cases config
  scripts/            # synth_laundering.py, fetch_datasets.sh, preflight.py
  docs/               # spec/, evaluation/, PROJECT_STATE.md, sih/
```

## Pipeline (one case)
`intake -> validate -> ingest(seed) -> guided trace loop -> normalize -> graph -> cluster -> label join -> M1 role scores -> patterns -> exit-type -> attribution tiers -> risk -> triage score -> evidence manifest -> report`

The trace loop is iterative: ingest a frontier node's transfers -> update taint -> score frontier with M3 -> expand best nodes until a termination condition or API budget is hit (see 04).

## Canonical models (Pydantic)
- `Transfer{chain, tx_hash, log_index, ts, from_addr, to_addr, asset, amount(Decimal), kind: native|token|internal, block, raw_ref}`
- `Address{chain, address, first_seen, last_seen, is_contract, labels[], role_probs{}, cluster_id}`
- `Edge{src, dst, asset, total_amount, tx_count, first_ts, last_ts, taint_share, tx_refs[]}`
- `Attribution{address, tier, entity, entity_type, confidence, evidence[], source}`
- `ExitReport{exit_type, entity?, tier, confidence, path[], amount_at_risk, eta_hours?}`

## Config
`config/*.yaml`: `trace.yaml` (depth, thresholds, budgets), `risk_weights.yaml`, `labels_sources.yaml`, `providers.yaml`. All versioned and hashed into every report manifest.

## Modes
- `LIVE_MODE=true`: real providers (budgeted, cached).
- `LIVE_MODE=false`: fixtures only (deterministic; used for demo, CI, judging).
Both run the identical downstream pipeline. UI badge shows the mode and marks cached/fixture data.

## Security
JWT auth (Argon2 password hashing), roles (investigator/supervisor/admin), case-scoped access, append-only audit log, input validation on all addresses, secrets via env, CORS locked to web origin.
