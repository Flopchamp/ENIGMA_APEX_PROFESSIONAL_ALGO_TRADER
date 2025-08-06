@echo off
echo.
echo 🔥 LAUNCHING ENIGMA APEX DEMO SYSTEM
echo ====================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  No configuration found. Setting up demo configuration...
    echo.
    call SETUP_DEMO.bat
    echo.
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    echo    Download from: https://python.org
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required packages...
    pip install streamlit plotly pandas numpy python-dotenv pygame
    echo.
)

echo 🚀 Starting Enigma Apex Demo System...
echo.
echo 🌐 The system will open in your web browser automatically.
echo 📊 Demo Account: $100,000 virtual money
echo 🛡️ Safe Mode: No real trading will occur
echo.

REM Launch the system
cd system
python -m streamlit run apex_compliance_guardian_streamlit.py

pause
