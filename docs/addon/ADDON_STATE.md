# Addon State Tracker

## Phase A0 - Audit
- [x] Discover models and adapters
- [x] Discover tests
- [x] Write REPO_MAP.md
- [x] Write TOUCHED_FILES.md

## Phase A1 - Seam + Data
- [x] Create `backend/app/addon/__init__.py`
- [x] Create `backend/app/addon/ports.py`
- [x] Create `backend/app/addon/adapters_existing.py`
- [x] Create `backend/app/addon/adapters_fixture.py`
- [x] Create `backend/config/addon/levers.yaml`
- [x] Create `backend/config/addon/convergence.yaml`
- [x] Create `backend/config/addon/fot.yaml`
- [x] Create DB models in `backend/app/addon/db/models_addon.py`
- [x] Create DB migration for addon tables
- [x] Create API routes in `backend/app/addon/api/routes_addon.py`
- [x] Register routes in `backend/app/api/v1/api.py`
- [x] Create tests in `backend/tests/addon/test_ports.py`
- [x] Run tests and fix failures

## Phase A2 - Scatter-Gather Cohort Tracing
- [x] Create `backend/app/addon/cohorts/__init__.py`
- [x] Create `backend/app/addon/cohorts/detect.py`
- [x] Create `backend/app/addon/cohorts/sample_vote.py`
- [x] Create `backend/app/addon/cohorts/verify.py`
- [x] Create `backend/app/addon/cohorts/score.py`
- [x] Create `backend/app/addon/cohorts/service.py`
- [x] Pass all evaluation checks

## Phase A3 - Mass Maps + Plan
- [x] Create `backend/app/addon/fot/mass_map.py`
- [x] Create `backend/app/addon/fot/levers.py`
- [x] Create `backend/app/addon/fot/planner.py`
- [x] Create `backend/app/addon/fot/voi.py`

## Phase A4 - VOI Tracing + Replay Evaluation
- [x] Create `backend/app/addon/fot/replay.py`
- [x] Create `scripts/addon/synth_timeline.py`
- [x] Create `ml/addon/eval_fot.py`
- [x] Create `backend/tests/addon/test_replay.py`
- [x] Modify `backend/app/addon/adapters_fixture.py`
- [x] Run tests and fix failures
- [x] Run eval_fot.py
