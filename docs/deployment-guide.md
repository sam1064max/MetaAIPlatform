# Deployment Guide

## Architecture

```
GitHub ─► GitHub Actions ─► Build Docker Images ─► Push to GHCR ─► Create Release ─► Deploy VPS
```

No `git pull` occurs on the VPS. All deployments are image-based.

## Prerequisites

- VPS with Docker 24+ and Docker Compose v2+
- Domain `sushantdev.com` managed by Cloudflare
- SSL certificates via Let's Encrypt
- GitHub secrets configured (see below)

## GitHub Secrets

| Secret | Description |
|--------|-------------|
| `DEPLOY_KEY` | SSH private key for VPS access |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions |

## Initial VPS Setup

```bash
# Clone once (only for initial setup)
git clone https://github.com/sam1064max/MetaAIPlatform.git ~/platform/metaai
cd ~/platform/metaai

# Create .env file
cat > .env << 'EOF'
JWT_SECRET=<generate-random>
SECRET_KEY=<generate-random>
GRAFANA_PASSWORD=<generate-random>
EOF

# Create required directories
mkdir -p /etc/letsencrypt

# Obtain SSL certificates
sudo certbot certonly --standalone \
  -d metaai.sushantdev.com \
  -d metaai-api.sushantdev.com \
  -d metaai-observability.sushantdev.com \
  -d staging-metaai.sushantdev.com \
  -d staging-metaai-api.sushantdev.com
```

## Deployment (CI/CD)

### Production
Merge to `main` → auto-builds images → pushes to GHCR → deploys to VPS.

```bash
# Manual trigger
gh workflow run CD --ref main
```

### Staging
Merge to `develop` → auto-builds images → pushes to GHCR → deploys to staging subdomains.

```bash
# Manual trigger
gh workflow run CD --ref develop
```

## Manual Deployment

```bash
# Set environment
export TAG=latest

# Pull images
docker compose pull

# Restart services
docker compose down
docker compose up -d

# Verify
curl -sf http://localhost:8000/health
```

## Release Process

```bash
# Create release
git tag v1.1.0
git push origin v1.1.0

# GitHub Actions auto-generates:
# - Release notes from commits
# - Docker images with version tag
# - GitHub Release with artifacts
```

## Health Checks

| Endpoint | Expected |
|----------|----------|
| `https://metaai-api.sushantdev.com/health` | `{"status": "ok"}` |
| `https://metaai.sushantdev.com/` | Streamlit dashboard |
| `https://metaai-observability.sushantdev.com/` | Grafana login |

## Troubleshooting

### VPS Unreachable
```bash
# Check if VPS is running
ping 80.225.207.230

# Restart Docker
sudo systemctl restart docker

# Check container logs
docker compose logs --tail=50 backend
```

### SSL Certificate Expired
```bash
sudo certbot renew
docker compose restart nginx
```

### Container OOM
```bash
# Check memory usage
docker stats

# Pull images one at a time
docker compose pull nginx
docker compose pull backend
docker compose pull frontend
docker compose pull postgres
docker compose pull redis
docker compose pull qdrant
docker compose pull grafana
```
