# Elkem Technology Controller Hub - PowerShell Launcher
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "  Elkem Technology Controller Hub - Starting Services" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[1/2] Starter Streamlit Workstation på http://localhost:8501 ..." -ForegroundColor Yellow
Start-Process python -ArgumentList "-m streamlit run app.py --server.port 8501" -WindowStyle Minimized
Start-Sleep -Seconds 3
Write-Host "[2/2] Åpner Streamlit Dashbord i nettleseren..." -ForegroundColor Green
Start-Process "http://localhost:8501"
Write-Host ""
Write-Host "Elkem Controller Hub kjører nå på http://localhost:8501!" -ForegroundColor Green

