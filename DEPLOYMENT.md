# Deployment Guide

ChainNetra uses a standard Docker Compose stack which can be deployed to any VPS or cloud provider.

## Local Quickstart
```bash
git clone https://github.com/your-org/chainnetra.git
cd chainnetra
cp .env.example .env
# Edit .env and add your API keys (TRONGRID_API_KEY, ETHERSCAN_API_KEY)
make dev
```
The UI will be available at `http://localhost:5173`.
The API will be available at `http://localhost:8000`.

## Production Deployment (Free Hosts / Hobby Tier)
If you wish to deploy ChainNetra for a demo using free cloud hosting:

### 1. Render.com
- **Backend:** Create a new "Web Service", connect your repo, set the root directory to `backend`, build command `pip install -r requirements.txt`, start command `uvicorn app.main:app --host 0.0.0.0 --port 10000`.
- **Frontend:** Create a new "Static Site", root directory `frontend`, build command `npm run build`, publish directory `dist`. Update the `VITE_API_URL` environment variable to point to your backend Render URL.

### 2. Oracle Cloud Free Tier
Oracle offers an Always Free ARM instance (up to 4 OCPUs, 24GB RAM).
- Spin up an Ubuntu 22.04 ARM instance.
- Install Docker and Docker Compose.
- Clone the repository and run:
  ```bash
  docker-compose -f docker-compose.prod.yml up -d
  ```
- Make sure to open ports `80` and `443` in the Oracle Cloud Security Lists.
