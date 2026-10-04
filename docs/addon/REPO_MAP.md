# Repository Map

- **Canonical Transfer model path**: `backend/app/db/models.py` (class `Transfer`)
- **Data adapters**: `backend/app/ingest/` (e.g., `tron.py`, `btc.py`, `evm.py`)
- **Graph/trace engine**: `backend/app/trace/engine.py`, `backend/app/graph/`
- **Labels/clustering/attribution**: `backend/app/attribution/` (e.g., `labels.py`, `clustering.py`, `exit_resolver.py`, `tiers.py`, `label_models.py`)
- **ML models**: `backend/app/ml/` (e.g., `predictor.py`, `registry.py`)
- **DB models + migrations**: `backend/app/db/models.py`, `backend/alembic/` (Alembic exists)
- **API routers**: `backend/app/api/v1/api.py`, `backend/app/api/v1/endpoints/`
- **Job runner**: `backend/app/jobs/worker.py`
- **Frontend routes/components**: `frontend/` (not specified in detail, but directory exists)

## Tests / Lint / Dev
- Tests: run `cd backend && PYTHONPATH=. .venv/bin/pytest tests/ -v`
