#!/bin/bash
set -e

DEPLOY_DIR="/opt/meta-ai-platform"
REPO_URL="git@github.com:sushantdev/MetaAIPlatform.git"

echo "=== MetaAI Platform Deployment ==="
echo "Timestamp: $(date)"

# Create deploy directory if needed
sudo mkdir -p $DEPLOY_DIR
sudo chown -R $USER:$USER $DEPLOY_DIR

# Clone/pull latest code
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd $DEPLOY_DIR
    git pull origin main
else
    git clone $REPO_URL $DEPLOY_DIR
    cd $DEPLOY_DIR
fi

# Copy environment file
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    cp $DEPLOY_DIR/.env.example $DEPLOY_DIR/.env
    echo "Please configure .env file and re-run deploy"
    exit 1
fi

# Build and restart containers
docker compose -f $DEPLOY_DIR/docker-compose.yml down
docker compose -f $DEPLOY_DIR/docker-compose.yml build --no-cache
docker compose -f $DEPLOY_DIR/docker-compose.yml up -d

# Wait for services
echo "Waiting for services..."
sleep 10

# Health check
curl -f http://localhost:8000/health || {
    echo "Health check failed!"
    exit 1
}

# Cleanup old images
docker image prune -f

echo "=== Deployment Complete ==="
echo "Frontend: https://sushantdev.com/MetaAIPlatform"
echo "API: https://sushantdev.com/MetaAIPlatform/api"
