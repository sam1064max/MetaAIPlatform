#!/bin/bash
# One-time VPS setup script
set -e

echo "=== MetaAI Platform VPS Setup ==="

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install -y docker-compose-plugin

# Create deploy directory
sudo mkdir -p /opt/meta-ai-platform
sudo chown -R $USER:$USER /opt/meta-ai-platform

# Install Nginx
sudo apt-get install -y nginx
sudo cp deployment/nginx/nginx.conf /etc/nginx/sites-available/metaai
sudo ln -sf /etc/nginx/sites-available/metaai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Configure firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

echo "VPS setup complete. Clone repository to /opt/meta-ai-platform and run deploy.sh"
