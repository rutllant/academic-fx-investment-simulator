@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title Agent FX TDR

set "PYTHON=%~dp0runtime\python.exe"

if not exist "%PYTHON%" (
    echo.
    echo ERROR: No s'ha trobat el runtime Python inclos amb l'aplicacio.
    echo.
    echo Si has descarregat el codi font des de GitHub, utilitza una Release de Windows
    echo o executa manualment l'aplicacio amb el teu propi entorn Python.
    echo.
    pause
    exit /b 1
)

"%PYTHON%" -c "import streamlit, pandas, numpy, plotly" >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: El paquet de l'aplicacio sembla incomplet o malmes.
    echo Torna a descarregar la Release oficial FX des de GitHub.
    echo.
    pause
    exit /b 1
)

echo Iniciant Agent FX TDR...
"%PYTHON%" -m streamlit run "app\app.py" --server.headless false --browser.gatherUsageStats false --server.address localhost --server.port 8501
exit /b %errorlevel%
