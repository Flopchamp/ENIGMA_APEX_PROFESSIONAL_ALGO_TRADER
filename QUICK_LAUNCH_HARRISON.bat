@echo off
echo ===============================================
echo 🎯 HARRISON'S COMPLETE TRADING DASHBOARD
echo ===============================================
echo 🚀 QUICK LAUNCH - Windows Batch File
echo.

cd /d "%~dp0"

echo 🔍 Checking for Harrison's dashboard...
if not exist "harrison_original_complete.py" (
    echo ❌ harrison_original_complete.py not found!
    echo Please ensure the file is in this directory.
    pause
    exit /b 1
)

echo ✅ Dashboard file found!
echo.

echo 🚀 Launching Harrison's Complete Dashboard...
echo 📖 Dashboard will open at: http://localhost:8501
echo ⏹️ Press Ctrl+C to stop the dashboard
echo.

REM Try to launch with streamlit
python -m streamlit run harrison_original_complete.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false

REM If that fails, try direct python
if errorlevel 1 (
    echo.
    echo ⚠️ Streamlit launch failed, trying direct Python...
    python harrison_original_complete.py
)

echo.
echo 👋 Dashboard stopped.
pause
