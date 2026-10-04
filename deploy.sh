#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# ChainNetra — EC2 Deploy Script
# Usage: ./deploy.sh [--pull]   (--pull does a git pull before building)
#
# Assumptions:
#   - Amazon Linux 2023 / Ubuntu 22.04+ on EC2
#   - Docker + Docker Compose v2 installed
#   - .env file exists (copied from .env.example and filled in)
#   - Port 80 open in the EC2 security group
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

COMPOSE="docker compose"   # Docker Compose v2 (plugin)
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PULL=false

for arg in "$@"; do
  [[ "$arg" == "--pull" ]] && PULL=true
done

cd "$APP_DIR"

# ── 0. Sanity checks ─────────────────────────────────────────────────────────
echo "▶ Checking prerequisites..."
command -v docker  >/dev/null 2>&1 || { echo "✗ Docker not found. Install it first."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "✗ Docker Compose v2 not found."; exit 1; }

if [[ ! -f .env ]]; then
  echo "✗ .env file not found. Copy .env.example and fill in your secrets:"
  echo "    cp .env.example .env && nano .env"
  exit 1
fi

# ── 1. Pull latest code (optional) ───────────────────────────────────────────
if [[ "$PULL" == "true" ]]; then
  echo "▶ Pulling latest from git..."
  git pull --ff-only
fi

# ── 2. Build images ───────────────────────────────────────────────────────────
echo "▶ Building Docker images (this takes a few minutes on first run)..."
$COMPOSE build --parallel

# ── 3. Stop existing containers gracefully ────────────────────────────────────
echo "▶ Stopping existing containers..."
$COMPOSE down --remove-orphans --timeout 30 || true

# ── 4. Start services ─────────────────────────────────────────────────────────
echo "▶ Starting services..."
$COMPOSE up -d

# ── 5. Wait for backend healthcheck ───────────────────────────────────────────
echo "▶ Waiting for backend to become healthy..."
MAX=30
COUNT=0
until docker inspect --format='{{.State.Health.Status}}' chainnetra-backend 2>/dev/null | grep -q "healthy"; do
  COUNT=$((COUNT+1))
  if [[ $COUNT -ge $MAX ]]; then
    echo "✗ Backend did not become healthy after ${MAX} attempts."
    echo "  Check logs: docker compose logs backend"
    exit 1
  fi
  echo "  ... attempt $COUNT/$MAX"
  sleep 5
done

echo ""
echo "✓ ChainNetra is live!"
echo ""

# Detect public IP
PUBLIC_IP=$(curl -sf http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "<your-ec2-ip>")
echo "  Frontend:  http://${PUBLIC_IP}"
echo "  API docs:  http://${PUBLIC_IP}/api/v1/docs"
echo "  Health:    http://${PUBLIC_IP}/api/v1/health"
echo ""
echo "  Logs:      docker compose logs -f"
echo "  Restart:   docker compose restart"
echo "  Stop:      docker compose down"
