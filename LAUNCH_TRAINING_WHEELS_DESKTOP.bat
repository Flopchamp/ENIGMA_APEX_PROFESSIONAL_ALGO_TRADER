@echo off
echo ========================================
echo  TRAINING WHEELS DESKTOP LAUNCHER
echo  Professional Trading Dashboard
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing desktop dependencies...
echo.

REM Install desktop requirements
pip install -r requirements_desktop.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Some packages may have failed to install
    echo This is normal for platform-specific packages
    echo.
)

echo.
echo ========================================
echo  LAUNCHING TRAINING WHEELS DESKTOP
echo ========================================
echo.
echo Starting desktop version with full functionality...
echo - Desktop notifications enabled
echo - NinjaTrader connection enabled  
echo - Tradovate API enabled
echo - Full OCR capabilities
echo - Audio alerts enabled
echo.

REM Launch the desktop version
streamlit run streamlit_app_desktop.py --server.port=8502 --server.headless=false

pause
