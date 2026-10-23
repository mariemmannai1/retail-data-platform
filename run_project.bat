
@echo off
cd /d "%~dp0"

echo ========================================
echo RETAIL DATA PLATFORM
echo ========================================

".venv\Scripts\python.exe" "src\run_pipeline.py" --with-forecast

if errorlevel 1 (
    echo.
    echo ERREUR : le pipeline a echoue.
    pause
    exit /b 1
)

echo.
echo Pipeline termine avec succes.
echo Les fichiers Power BI ont ete actualises.
pause
