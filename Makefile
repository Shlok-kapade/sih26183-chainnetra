.PHONY: dev test lint fixtures train-m1 train-m1b train-m3 bench-m3 eval demo report migrate

VENV = backend/.venv/bin
PYTHON = backend/.venv/bin/python

dev:
	$(VENV)/uvicorn app.main:app --reload --app-dir backend

test:
	$(VENV)/pytest backend/tests/ -v

lint:
	$(VENV)/ruff check backend/app/ backend/tests/ scripts/
	$(VENV)/mypy backend/app/ --ignore-missing-imports --no-strict-optional

train-m1:
	$(PYTHON) backend/ml/train/train_m1.py

train-m1b:
	$(PYTHON) backend/ml/train/train_m1b.py

train-m3:
	$(PYTHON) backend/ml/train/train_m3.py

bench-m3:
	$(PYTHON) backend/ml/eval/benchmark_m3.py

eval:
	$(PYTHON) backend/ml/eval/eval_m1.py

fixtures:
	@echo "Real fixtures already recorded in data/fixtures/ from Phase 1 API calls."

migrate:
	cd backend && .venv/bin/alembic upgrade head

demo:
	@echo "Start the API: make dev"
	@echo "Then: curl http://localhost:8000/health"

report:
	@cat docs/evaluation/RESULTS.md

fetch-real-data:
	$(PYTHON) backend/ml/datasets/fetch_tron_real.py

build-real-datasets:
	$(PYTHON) backend/ml/datasets/build_tron_real.py

train-m1-real:
	$(PYTHON) backend/ml/train/train_m1_real.py

eval-m1-real:
	$(PYTHON) backend/ml/eval/eval_m1_real.py

.PHONY: demo
demo:
	backend/.venv/bin/python scripts/preflight.py
	@echo "Starting Demo Environment..."
	@echo "Backend API running on http://localhost:8000"
	@echo "Frontend running on http://localhost:5173"
	# Start background processes
	cd backend && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
	cd frontend && npm run dev &
	wait
