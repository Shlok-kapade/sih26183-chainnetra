# ChainNetra — PROJECT_STATE

> Last updated: 2026-09-30T14:00+05:30

## Current Status: Phases 0–6 ✅ COMPLETE — 88 tests passing, lint clean

---

## Phase 0 — Scaffold ✅ DONE
- Monorepo layout, pyproject.toml, Docker Compose (db/api/worker/web), Makefile
- All 17 SQLAlchemy 2 async models, Alembic migration
- FastAPI app, `/health` + `/version` endpoints, RFC7807 errors, structured logging
- `.env.example`, config YAML files, ruff + mypy config
- **Tests:** 1 | **Lint:** clean

## Phase 1 — Data Layer ✅ DONE
- TRON (TronGrid), EVM (Etherscan V2 + Blockscout fallback), BTC (mempool.space) adapters
- Canonical Transfer model (Pydantic), address validators (TRON/EVM/BTC), SHA-256 cache, token-bucket rate limiter, fixture mode
- **API verification:** TronGrid ✅ keyless, Blockscout ✅ keyless, mempool.space ✅ keyless, Etherscan V2 ⚠️ needs free key
- **Fixtures recorded:** data/fixtures/ (tron, blockscout, mempool, etherscan error-response)
- **Tests:** +9 | **Lint:** clean

## Phase 2 — Graph + Baseline Tracing ✅ DONE
- NetworkX DiGraph builder, taint engine (haircut/poison/FIFO), BFS trace engine
- 12 TerminationReason enum values, swap + bridge detection
- Hypothesis property tests for taint conservation invariants
- **Tests:** +7 | **Lint:** clean

## Phase 3 — Labels, Attribution, Clustering ✅ DONE
- AddressLabel model with full provenance on every record
- LabelStore CSV loader, lookup, stats()
- Attribution tiers: CONFIRMED/PROBABLE/POSSIBLE/UNATTRIBUTED with evidence list
- Exit-type resolver (rules-only)
- DAR clustering (>=5 senders, >=80% forward), BTC co-spend (Union-Find, CoinJoin guard)
- Label files: data/labels/ (ofac_sample, por_sample, contracts_bridges, contracts_dex)
- **Tests:** +16 (labels×3, attribution×5, clustering×8) | **Lint:** clean

## Phase 4 — Patterns + Synthetic Generator ✅ DONE
- 7 pattern detectors: fan_out, fan_in, rapid_forwarding, peel_chain, dormancy_burst, structuring, round_trip
- PatternRegistry running all 7 with FP notes
- Synthetic generator (scripts/synth_laundering.py): 6 malicious + 2 benign look-alikes + 1 market-maker
- Eval script: scripts/eval_patterns.py
- **Tests:** +11 (detector×7, benign FP×2, registry×1, extra×1) | **Lint:** clean

---

## Phase 5 — ML Core ✅ DONE

**Files:**
- `backend/app/ml/features.py` — 37-feature point-in-time extractor
- `backend/app/ml/registry.py` — ModelRegistry save/load/list_versions
- `backend/app/ml/datasets.py` — `build_synthetic_dataset`, `build_dataset_from_labels_and_synthetics`
- `backend/app/ml/utils.py` — ECE (last-bin fix), per-class PR-AUC (binary OvR)
- `backend/app/ml/predictor.py` — M1Predictor with calibrated predict_proba + SHAP + abstain
- `backend/ml/train/train_m1.py` — LightGBM + isotonic cal + temporal split + LOEO + baselines + SHAP → `ml/artifacts/m1/v0.1`
- `backend/ml/train/train_m1b.py` — M1b (blocked on Elliptic dataset)
- `backend/ml/eval/eval_m1.py` — writes `docs/evaluation/RESULTS.md`
- `backend/tests/test_ml.py` — 23 tests

**Metrics (synthetic data only — see RESULTS.md caveat):**
- LightGBM macro-F1: **1.000** (synthetic) | LogReg: 1.000 | Rules: 0.036
- ECE (before cal): 0.000 | ECE (after isotonic cal): 0.000
- LOEO recall: 0.000 for all withheld classes (by design — unseen class)
- Top SHAP features: `log_n_out_cp`, `n_out_cp`, `n_in_cp`, `log_n_in_cp`, `n_out_tx`

**Tests:** +23 → 67 total | **Lint:** clean

**Blocked:** M1b requires Elliptic dataset:
```
data/raw/elliptic/elliptic_txs_features.csv
data/raw/elliptic/elliptic_txs_classes.csv
data/raw/elliptic/elliptic_txs_edgelist.csv
```
Source: https://www.kaggle.com/datasets/ellipticco/elliptic-data-set (CC BY 4.0)
Then run: `make train-m1b && make eval`

---

## Phase 6 — M3 Guided Tracing Policy ✅ DONE

**Files:**
- `backend/app/ml/m3_dataset.py` — trace-labeled dataset builder; BFS over synthetic graphs labels each frontier node as 1 if labeled VASP reachable within remaining budget, 0 otherwise. Group split by seed_id.
- `backend/app/trace/engine.py` — **extended** `TraceEngine` with:
  - `TraceResult` dataclass (graph_nodes, graph_edges, termination_reasons, api_calls_used, found_exits, policy, budget)
  - 5 policies: `bfs` (FIFO), `dfs` (LIFO), `taint_greedy`, `random`, `guided` (M3 priority = taint × p_exit / depth+1)
  - `vasp_classifier` callback for recall tracking
  - VASP check moved before fetch so leaf VASPs (no outgoing transfers) are correctly found
- `backend/ml/train/train_m3.py` — M3 training: LightGBM binary + isotonic cal + SHAP + model card → `ml/artifacts/m3/v0.1/`
- `backend/ml/eval/benchmark_m3.py` — 5-policy benchmark: recall@B for B ∈ {20,50,100,200,500}, calls-to-first-exit
- `backend/ml/eval/eval_m1.py` — updated to include M3 recall@B table and ground-truth bias caveat
- `backend/tests/test_m3.py` — 21 tests
- `Makefile` — added `train-m3`, `bench-m3` targets

**M3 Metrics (synthetic test set — 103 nodes, 12 held-out seeds):**
- PR-AUC: **1.000** | ROC-AUC: 1.000 | F1 @ 0.5: 1.000 | ECE: 0.000
- Top SHAP features: `taint_share` (5.71), `dwell_so_far_hours` (2.69), `value_trend_log` (0.39)

**Recall@B (20 held-out synthetic traces):**

| Policy | @20 | @50 | @100 | @200 | @500 | Mean calls-to-1st |
|--------|-----|-----|------|------|------|-------------------|
| bfs | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 7.0 |
| dfs | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 7.0 |
| taint_greedy | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 7.0 |
| random | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 7.0 |
| **M3-guided** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **7.0** |

> All policies reach recall=1.0 on synthetic graphs because the graphs are tiny (≤12 nodes) and shallow — budget=20 is sufficient for any policy. Policy differentiation requires heterogeneous, sparse, real-world graphs where budget is binding.

**⚠️ Ground-Truth Bias Caveat:** Recall is measured only against labeled VASPs in `data/labels/*.csv`. Published figures are **lower bounds** on true coverage. Synthetic distribution = training distribution → overfit metrics guaranteed.

**Tests:** +21 → **88 total** | **Lint:** clean

---

## Test Summary (88 passing, ~17s)
```
test_health.py:          1
test_validators.py:      6
test_ratelimit.py:       2
test_fixtures.py:        2
test_graph_builder.py:   1
test_taint.py:           3
test_trace_engine.py:    2
test_swaps.py:           1
test_labels.py:          3
test_attribution.py:     5
test_clustering.py:      8
test_patterns.py:       11
test_ml.py:             23
test_m3.py:             21
                        ---
Total:                  89 (88 pass + 0 fail)
```

## Commands
```bash
make test           # 88 tests
make lint           # ruff clean
make train-m1       # retrain M1
make train-m3       # retrain M3 (run after train-m1)
make bench-m3       # run standalone benchmark
make eval           # regenerate docs/evaluation/RESULTS.md (includes M3 recall@B)
make report         # cat RESULTS.md
```

## API Keys Needed
- ETHERSCAN_API_KEY — free tier from etherscan.io (Blockscout works without)
- TRONGRID_API_KEY — optional

## Stubs / Known Gaps
- **M1b:** blocked on Elliptic dataset (Kaggle)
- **M3 policy differentiation:** all policies identical on tiny synthetic graphs; policy advantage only visible on deep, sparse, real-world graphs with binding budgets
- **M1 probs in M3 features:** M1 not loaded at M3 dataset build time (circular dep); uniform probs passed instead
- **mypy strict:** not enforced (too many upstream stubs missing)
- **Real-data M1 metrics:** synthetic only; add labels to `data/labels/*.csv` then `make train-m1 && make eval`
- Etherscan fixture: error-response only (Blockscout is real fallback)

## Next Phases
- **Phase 7 (MUST):** REST API endpoints + async Celery worker (trace, taint, pattern detect, M1 predict)
- **Phase 8 (MUST):** Frontend scaffold (React 18 + Vite + graph viz)
- Phase 9: Reporting + freeze-request draft
- Phase 10: Docker prod + CI/CD
- Phase 11: SIH demo polish
