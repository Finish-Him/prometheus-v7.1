# ============================================================
# Prometheus V7 - Deploy from Windows
# Run this script from PowerShell to deploy to VPS
# ============================================================
# Required environment variables:
#   $env:VPS_IP       - VPS IP address
#   $env:VPS_USER     - VPS username (default: root)
#   $env:VPS_PASSWORD - VPS password
#   $env:VPS_DOMAIN   - Domain name (optional)
# ============================================================

$VPS_IP = $env:VPS_IP
$VPS_USER = if ($env:VPS_USER) { $env:VPS_USER } else { "root" }
$VPS_PASSWORD = $env:VPS_PASSWORD
$APP_DIR = "/opt/prometheus/app"

if (-not $VPS_IP -or -not $VPS_PASSWORD) {
    Write-Host "❌ Missing required environment variables: VPS_IP, VPS_PASSWORD" -ForegroundColor Red
    Write-Host "Set them before running:" -ForegroundColor Yellow
    Write-Host '  $env:VPS_IP="x.x.x.x"' -ForegroundColor Cyan
    Write-Host '  $env:VPS_PASSWORD="your-password"' -ForegroundColor Cyan
    exit 1
}

Write-Host "🔥 Prometheus V7 - Deploy to VPS" -ForegroundColor Cyan
Write-Host "============================================================"

# Check if plink is available (PuTTY)
$usePlink = Get-Command plink -ErrorAction SilentlyContinue

if ($usePlink) {
    Write-Host "Using PuTTY plink..." -ForegroundColor Yellow

    # Deploy commands
    $commands = @"  
cd $APP_DIR
 git pull origin main
 source venv/bin/activate
 pip install -r requirements.txt --quiet
 systemctl restart prometheus
 systemctl status prometheus --no-pager
"@ 

    echo $commands | plink -ssh $VPS_USER@$VPS_IP -pw $VPS_PASSWORD
} else {
    Write-Host "Using native SSH..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run these commands manually:" -ForegroundColor Green
    Write-Host "============================================================"
    Write-Host ""
    Write-Host "ssh $VPS_USER@$VPS_IP" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "# Then run:" -ForegroundColor Yellow
    Write-Host "cd /opt/prometheus/app"
    Write-Host "git pull origin main"
    Write-Host "source venv/bin/activate"
    Write-Host "pip install -r requirements.txt"
    Write-Host "systemctl restart prometheus"
    Write-Host "systemctl status prometheus"
}

Write-Host ""
Write-Host "============================================================"
$DOMAIN = if ($env:VPS_DOMAIN) { $env:VPS_DOMAIN } else { "your-domain.com" }
Write-Host "🌐 After deploy, access: http://$DOMAIN" -ForegroundColor Green
