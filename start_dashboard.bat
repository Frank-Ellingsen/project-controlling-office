@echo off
title Elkem Technology Controller Hub Launcher
echo ==============================================================
echo   Elkem Technology Controller Hub - Starting Services
echo ==============================================================
echo.
echo [1/2] Starter Streamlit Workstation paa http://localhost:8501 ...
start "Elkem Streamlit Workstation" python -m streamlit run app.py --server.port 8501
timeout /t 3 >nul
echo [2/2] Aapner Streamlit Dashbord i nettleseren...
start http://localhost:8501
echo.
echo ==============================================================
echo   Elkem Controller Hub kjoerer naa paa http://localhost:8501!
echo ==============================================================

