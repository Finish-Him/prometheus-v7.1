# Prometheus Launcher
# Execute: .\run.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🔥 PROMETHEUS V7 - Betting Platform  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot

# Verificar ambiente virtual
if (-not (Test-Path "$projectRoot\.venv\Scripts\python.exe")) {
    Write-Host "❌ Ambiente virtual não encontrado. Criando..." -ForegroundColor Yellow
    python -m venv "$projectRoot\.venv"
    & "$projectRoot\.venv\Scripts\pip.exe" install streamlit pandas requests python-dotenv pydantic loguru tqdm
}

Write-Host "✅ Ambiente virtual OK" -ForegroundColor Green

# Verificar Streamlit
$hasStreamlit = & "$projectRoot\.venv\Scripts\pip.exe" show streamlit 2>$null
if (-not $hasStreamlit) {
    Write-Host "📦 Instalando Streamlit..." -ForegroundColor Yellow
    & "$projectRoot\.venv\Scripts\pip.exe" install streamlit
}

Write-Host ""
Write-Host "🚀 Iniciando servidor..." -ForegroundColor Green
Write-Host "   URL: http://localhost:8501" -ForegroundColor White
Write-Host "   Para parar: Ctrl+C" -ForegroundColor Gray
Write-Host ""

# Rodar da raiz do projeto
Set-Location "$projectRoot"

# Abrir navegador
Start-Process "http://localhost:8501"

# Rodar Streamlit
& "$projectRoot\.venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501
