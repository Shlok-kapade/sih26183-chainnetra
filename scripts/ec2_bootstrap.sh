#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap script — run ONCE on a fresh EC2 instance (Amazon Linux 2023)
# to install Docker, Docker Compose v2, git, and clone the repo.
#
# Usage (as ec2-user):
#   curl -sSL https://raw.githubusercontent.com/<org>/chainnetra/main/scripts/ec2_bootstrap.sh | bash
#   OR copy this file to the EC2 and run: bash ec2_bootstrap.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO_URL="${REPO_URL:-}"          # Set to your git remote, or clone manually
APP_DIR="${APP_DIR:-/opt/chainnetra}"

echo "=== ChainNetra EC2 Bootstrap ==="

# ── Detect OS ─────────────────────────────────────────────────────────────────
if command -v dnf >/dev/null 2>&1; then
  PKG="dnf"
elif command -v apt-get >/dev/null 2>&1; then
  PKG="apt"
else
  echo "Unsupported OS"; exit 1
fi

# ── Install Docker ────────────────────────────────────────────────────────────
echo "▶ Installing Docker..."
if [[ "$PKG" == "dnf" ]]; then
  sudo dnf install -y docker git
  sudo systemctl enable --now docker
  sudo usermod -aG docker ec2-user
else
  sudo apt-get update -qq
  sudo apt-get install -y docker.io docker-compose-plugin git curl
  sudo systemctl enable --now docker
  sudo usermod -aG docker ubuntu
fi

# ── Install Docker Compose v2 plugin (if not bundled) ─────────────────────────
if ! docker compose version >/dev/null 2>&1; then
  echo "▶ Installing Docker Compose v2 plugin..."
  ARCH=$(uname -m)
  COMPOSE_VERSION="v2.27.0"
  sudo mkdir -p /usr/local/lib/docker/cli-plugins
  sudo curl -SL \
    "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-${ARCH}" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

echo "  Docker: $(docker --version)"
echo "  Compose: $(docker compose version)"

# ── Clone repo (if REPO_URL provided) ─────────────────────────────────────────
if [[ -n "$REPO_URL" ]]; then
  echo "▶ Cloning repo → $APP_DIR"
  sudo git clone "$REPO_URL" "$APP_DIR"
  sudo chown -R "$(id -u):$(id -g)" "$APP_DIR"
  cd "$APP_DIR"
  echo "▶ Copy and edit your .env:"
  echo "    cp .env.example .env && nano .env"
else
  echo ""
  echo "▶ Next steps:"
  echo "  1. Upload or clone ChainNetra to your preferred directory"
  echo "  2. cp .env.example .env && nano .env"
  echo "  3. bash deploy.sh"
fi

echo ""
echo "NOTE: Log out and back in (or run 'newgrp docker') for docker group to take effect."
echo "=== Bootstrap complete ==="
