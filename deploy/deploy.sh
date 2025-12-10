#!/bin/bash
# ============================================================
# Prometheus V7 - Quick Deploy Script
# Run this to update the application on the VPS
# ============================================================

set -e

APP_DIR="/opt/prometheus/app"
APP_USER="prometheus"

echo "🔥 Prometheus V7 - Quick Deploy"
echo "============================================================"

# Pull latest changes
echo "📥 Pulling latest changes..."
cd $APP_DIR
sudo -u $APP_USER git pull origin main

# Update dependencies if requirements changed
echo "📦 Updating dependencies..."
sudo -u $APP_USER ./venv/bin/pip install -r requirements.txt --quiet

# Restart the service
echo "🔄 Restarting service..."
systemctl restart prometheus

# Wait and check status
sleep 3
systemctl status prometheus --no-pager

echo ""
echo "✅ Deploy complete!"
echo "🌐 Application: http://prometheus.mscconsultoriarj.com.br"
