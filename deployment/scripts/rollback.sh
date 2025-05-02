#!/bin/bash
set -e

DEPLOY_DIR="/opt/meta-ai-platform"

echo "=== Rolling back to previous version ==="

cd $DEPLOY_DIR
git checkout HEAD~1
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up -d

echo "Rollback complete"
