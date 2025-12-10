#!/bin/bash
# ============================================================
# Prometheus V7 - VPS Setup Script
# Hostinger VPS - AlmaLinux 9 with cPanel
# Server: 72.62.9.90 (srv1180544.hstgr.cloud)
# Domain: prometheus.mscconsultoriarj.com.br
# ============================================================

set -e  # Exit on error

echo "🔥 Prometheus V7 - VPS Setup"
echo "============================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="prometheus"
APP_USER="prometheus"
APP_DIR="/opt/prometheus"
DOMAIN="prometheus.mscconsultoriarj.com.br"
PYTHON_VERSION="3.11"

# ============================================================
# Step 1: System Update and Dependencies
# ============================================================
echo -e "${YELLOW}[1/8] Updating system and installing dependencies...${NC}"

# Update system
dnf update -y

# Install EPEL and development tools
dnf install -y epel-release
dnf groupinstall -y "Development Tools"

# Install Python 3.11 and dependencies
dnf install -y python3.11 python3.11-pip python3.11-devel
dnf install -y nginx git curl wget nano htop

# Install Node.js (for some Streamlit features)
dnf module install -y nodejs:18

echo -e "${GREEN}✅ System dependencies installed${NC}"

# ============================================================
# Step 2: Create Application User
# ============================================================
echo -e "${YELLOW}[2/8] Creating application user...${NC}"

# Create user if doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -m -d $APP_DIR -s /bin/bash $APP_USER
    echo -e "${GREEN}✅ User $APP_USER created${NC}"
else
    echo -e "${YELLOW}⚠️ User $APP_USER already exists${NC}"
fi

# ============================================================
# Step 3: Setup Application Directory
# ============================================================
echo -e "${YELLOW}[3/8] Setting up application directory...${NC}"

mkdir -p $APP_DIR
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/backups

chown -R $APP_USER:$APP_USER $APP_DIR

echo -e "${GREEN}✅ Application directory created at $APP_DIR${NC}"

# ============================================================
# Step 4: Clone/Update Repository
# ============================================================
echo -e "${YELLOW}[4/8] Cloning repository...${NC}"

cd $APP_DIR

if [ -d "$APP_DIR/app" ]; then
    echo "Updating existing repository..."
    cd $APP_DIR/app
    sudo -u $APP_USER git pull origin main
else
    echo "Cloning repository..."
    sudo -u $APP_USER git clone https://github.com/Finish-Him/prometheus-v7.1.git app
    cd $APP_DIR/app
fi

echo -e "${GREEN}✅ Repository ready${NC}"

# ============================================================
# Step 5: Setup Python Virtual Environment
# ============================================================
echo -e "${YELLOW}[5/8] Setting up Python virtual environment...${NC}"

cd $APP_DIR/app

# Create venv
sudo -u $APP_USER python3.11 -m venv venv

# Upgrade pip and install requirements
sudo -u $APP_USER ./venv/bin/pip install --upgrade pip
sudo -u $APP_USER ./venv/bin/pip install -r requirements.txt

echo -e "${GREEN}✅ Python environment ready${NC}"

# ============================================================
# Step 6: Configure Nginx
# ============================================================
echo -e "${YELLOW}[6/8] Configuring Nginx...${NC}"

# Create Nginx config
cat > /etc/nginx/conf.d/prometheus.conf << 'NGINX_CONF'
# Prometheus V7 - Nginx Configuration
# Domain: prometheus.mscconsultoriarj.com.br

upstream prometheus_backend {
    server 127.0.0.1:8501;
    keepalive 32;
}

server {
    listen 80;
    server_name prometheus.mscconsultoriarj.com.br;

    # Redirect HTTP to HTTPS (uncomment after SSL setup)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://prometheus_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }

    # Streamlit specific
    location /_stcore/stream {
        proxy_pass http://prometheus_backend/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }

    # Static files
    location /static {
        alias /opt/prometheus/app/static;
        expires 30d;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}

# HTTPS configuration (uncomment after SSL setup with certbot)
# server {
#     listen 443 ssl http2;
#     server_name prometheus.mscconsultoriarj.com.br;
#
#     ssl_certificate /etc/letsencrypt/live/prometheus.mscconsultoriarj.com.br/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/prometheus.mscconsultoriarj.com.br/privkey.pem;
#
#     # ... same location blocks as above ...
# }
NGINX_CONF

# Test and reload nginx
nginx -t
systemctl enable nginx
systemctl restart nginx

echo -e "${GREEN}✅ Nginx configured${NC}"

# ============================================================
# Step 7: Configure Systemd Service
# ============================================================
echo -e "${YELLOW}[7/8] Configuring systemd service...${NC}"

cat > /etc/systemd/system/prometheus.service << 'SERVICE_CONF'
[Unit]
Description=Prometheus V7 - Dota 2 Analytics Platform
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=prometheus
Group=prometheus
WorkingDirectory=/opt/prometheus/app
Environment="PATH=/opt/prometheus/app/venv/bin:/usr/local/bin:/usr/bin"
Environment="STREAMLIT_SERVER_PORT=8501"
Environment="STREAMLIT_SERVER_ADDRESS=127.0.0.1"
Environment="STREAMLIT_SERVER_HEADLESS=true"
Environment="STREAMLIT_BROWSER_GATHER_USAGE_STATS=false"

ExecStart=/opt/prometheus/app/venv/bin/streamlit run app.py \
    --server.port=8501 \
    --server.address=127.0.0.1 \
    --server.headless=true \
    --browser.gatherUsageStats=false

Restart=always
RestartSec=10
StandardOutput=append:/opt/prometheus/logs/prometheus.log
StandardError=append:/opt/prometheus/logs/prometheus-error.log

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/prometheus

[Install]
WantedBy=multi-user.target
SERVICE_CONF

# Reload and start service
systemctl daemon-reload
systemctl enable prometheus
systemctl start prometheus

echo -e "${GREEN}✅ Systemd service configured and started${NC}"

# ============================================================
# Step 8: Configure Firewall
# ============================================================
echo -e "${YELLOW}[8/8] Configuring firewall...${NC}"

# Open HTTP and HTTPS ports
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

echo -e "${GREEN}✅ Firewall configured${NC}"

# ============================================================
# Final Summary
# ============================================================
echo ""
echo "============================================================"
echo -e "${GREEN}🎉 Prometheus V7 Setup Complete!${NC}"
echo "============================================================"
echo ""
echo "📍 Application URL: http://$DOMAIN"
echo "📍 Server IP: 72.62.9.90"
echo "📁 App Directory: $APP_DIR/app"
echo "📜 Logs: $APP_DIR/logs/"
echo ""
echo "Commands:"
echo "  - Status:  systemctl status prometheus"
echo "  - Logs:    journalctl -u prometheus -f"
echo "  - Restart: systemctl restart prometheus"
echo ""
echo "Next Steps:"
echo "  1. Setup SSL with: certbot --nginx -d $DOMAIN"
echo "  2. Configure .env file with API keys"
echo "  3. Test the application at http://$DOMAIN"
echo ""
