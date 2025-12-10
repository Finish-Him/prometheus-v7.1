# ============================================================
# Prometheus V7 - Deploy from Windows
# Run this script from PowerShell to deploy to VPS
# ============================================================

$VPS_IP = "72.62.9.90"
$VPS_USER = "root"
$VPS_PASSWORD = "Moises@24512987"
$APP_DIR = "/opt/prometheus/app"

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
    Write-Host "ssh root@$VPS_IP" -ForegroundColor Cyan
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
Write-Host "🌐 After deploy, access: http://prometheus.mscconsultoriarj.com.br" -ForegroundColor Green
