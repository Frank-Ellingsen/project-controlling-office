# ==============================================================================
# ELKEM CONTROLLER HUB — AUTOMATED LOCAL ENVIRONMENT BOOTSTRAPPER (PowerShell)
# ==============================================================================
# Script: run_all.ps1
# Description: Automated setup and launcher for Elkem Technology Controller Hub.
# Targets: Docker Containers, Local DuckDB, Streamlit UI, FastAPI OpenAPI Docs.
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   ELKEM CONTROLLER HUB — LOCAL ENVIRONMENT LAUNCHER                 " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verify working directory
$ProjectRoot = Get-Location
Write-Host "[1/6] Checking project directory: $ProjectRoot" -ForegroundColor Yellow

# 2. Environment File Check
Write-Host "[2/6] Verifying environment configuration (.env)..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "  -> Created .env from env.example" -ForegroundColor Green
    } else {
        Write-Host "  -> WARNING: Neither .env nor env.example found." -ForegroundColor Red
    }
} else {
    Write-Host "  -> .env file present." -ForegroundColor Green
}

# 3. Initialize DuckDB & Local Analytics Store
Write-Host "[3/6] Running Dev Bootstrap (DuckDB & Local Store)..." -ForegroundColor Yellow
try {
    python bootstrap_dev.py
    Write-Host "  -> DuckDB store initialized." -ForegroundColor Green
} catch {
    Write-Host "  -> WARNING: Failed to run bootstrap_dev.py. Please verify python environment." -ForegroundColor Red
}

# 4. Check Docker Engine Status
Write-Host "[4/6] Checking Docker Engine..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    Write-Host "  -> Docker Engine is running." -ForegroundColor Green
    
    # 5. Start Docker Compose Stack
    Write-Host "[5/6] Building and starting Docker containers (Backend, Frontend, Qdrant)..." -ForegroundColor Yellow
    docker compose up --build -d
    Write-Host "  -> Docker containers started in detached mode." -ForegroundColor Green
} catch {
    Write-Host "  -> NOTICE: Docker Desktop is not active or docker command failed." -ForegroundColor Red
    Write-Host "  -> Falling back to direct local execution mode..." -ForegroundColor Yellow
}

# 6. Open Web Dashboards
Write-Host "[6/6] Launching User Interface and API Explorer..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open Streamlit Dashboard
Write-Host "  -> Opening Streamlit Dashboard: http://localhost:8501" -ForegroundColor Cyan
Start-Process "http://localhost:8501"

# Open OpenAPI / Swagger Docs
Write-Host "  -> Opening OpenAPI Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Start-Process "http://localhost:8000/docs"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host " ✅ ELKEM CONTROLLER HUB IS UP AND RUNNING!                            " -ForegroundColor Green
Write-Host "   - Streamlit UX : http://localhost:8501                              " -ForegroundColor White
Write-Host "   - FastAPI Docs : http://localhost:8000/docs                          " -ForegroundColor White
Write-Host "   - Qdrant Vector: http://localhost:6333                              " -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
