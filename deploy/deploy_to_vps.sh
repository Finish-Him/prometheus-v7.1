#!/bin/bash
# =============================================================================
# Prometheus V7 - Quick Deploy Script
# =============================================================================
# This script automates the deployment to Hostinger VPS
# Usage: ./deploy_to_vps.sh
# =============================================================================

set -e

# Configuration
VPS_IP="72.62.9.90"
VPS_USER="root"
APP_DIR="/opt/prometheus/app"
DOMAIN="prometheus.mscconsultoriarj.com.br"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔥 Prometheus V7 - Deploy to VPS${NC}"
echo "============================================================"

# =============================================================================
# Step 1: Upload setup script
# =============================================================================
echo -e "${YELLOW}[1/4] Uploading setup script to VPS...${NC}"

scp deploy/setup_vps.sh ${VPS_USER}@${VPS_IP}:/root/setup_vps.sh

echo -e "${GREEN}✅ Setup script uploaded${NC}"

# =============================================================================
# Step 2: Execute setup on VPS
# =============================================================================
echo -e "${YELLOW}[2/4] Executing setup on VPS...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes...${NC}"

ssh ${VPS_USER}@${VPS_IP} << 'ENDSSH'
chmod +x /root/setup_vps.sh
/root/setup_vps.sh
ENDSSH

echo -e "${GREEN}✅ Setup completed on VPS${NC}"

# =============================================================================
# Step 3: Upload .env file
# =============================================================================
echo -e "${YELLOW}[3/4] Uploading environment variables...${NC}"

if [ -f ".env.production" ]; then
    scp .env.production ${VPS_USER}@${VPS_IP}:${APP_DIR}/.env
    echo -e "${GREEN}✅ Environment variables uploaded${NC}"
else
    echo -e "${RED}⚠️ Warning: .env.production not found${NC}"
    echo -e "${YELLOW}You'll need to manually create .env on the VPS${NC}"
fi

# =============================================================================
# Step 4: Restart service
# =============================================================================
echo -e "${YELLOW}[4/4] Restarting application...${NC}"

ssh ${VPS_USER}@${VPS_IP} << 'ENDSSH'
systemctl restart prometheus
sleep 5
systemctl status prometheus --no-pager
ENDSSH

echo -e "${GREEN}✅ Application restarted${NC}"

# =============================================================================
# Final Summary
# =============================================================================
echo ""
echo "============================================================"
echo -e "${GREEN}🎉 Deploy Complete!${NC}"
echo "============================================================"
echo ""
echo -e "📍 Application URL: ${BLUE}http://${DOMAIN}${NC}"
echo -e "📍 Server IP: ${BLUE}${VPS_IP}${NC}"
echo ""
echo "Next Steps:"
echo "  1. Test: curl http://${DOMAIN}/health"
echo "  2. Setup SSL: ssh ${VPS_USER}@${VPS_IP} 'certbot --nginx -d ${DOMAIN}'"
echo "  3. Monitor logs: ssh ${VPS_USER}@${VPS_IP} 'journalctl -u prometheus -f'"
echo ""
