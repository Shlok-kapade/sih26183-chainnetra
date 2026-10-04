#!/bin/bash
# ChainNetra startup script - starts both backend and frontend
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "=== ChainNetra SIH 2026 ==="
echo "Starting services..."

# Kill any existing processes
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# Run DB migrations
echo "[1/3] Running database migrations..."
cd "$BACKEND_DIR"
.venv/bin/alembic upgrade head || true

# Start backend
echo "[2/3] Starting backend on :8000..."
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/chainnetra_backend.log 2>&1 &
BACKEND_PID=$!
disown $BACKEND_PID 2>/dev/null || true
echo "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to start..."
READY=0
for i in $(seq 1 25); do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done

if [ $READY -eq 0 ]; then
  echo "ERROR: Backend failed to start. Check /tmp/chainnetra_backend.log"
  exit 1
fi
echo "Backend ready."

# Start frontend
echo "[3/3] Starting frontend on :5173..."
cd "$FRONTEND_DIR"
nohup npm run dev > /tmp/chainnetra_frontend.log 2>&1 &
FRONTEND_PID=$!
disown $FRONTEND_PID 2>/dev/null || true
echo "Frontend PID: $FRONTEND_PID"

sleep 2
echo ""
echo "=== ChainNetra is running ==="
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend:   /tmp/chainnetra_backend.log"
echo "  Frontend:  /tmp/chainnetra_frontend.log"
echo ""
echo "To stop: pkill -f 'uvicorn app.main' && pkill -f vite"
