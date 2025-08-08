@echo off
REM 🎯 APEX TRADING DASHBOARD - PRODUCTION READY
REM Windows batch file for Harrison's original interface + enhanced features

echo.
echo ================================================
echo 🎯 APEX TRADING DASHBOARD - PRODUCTION READY
echo ================================================
echo � Harrison's Original Interface + Enhanced Features
echo 🥷 NinjaTrader + Tradovate Integration
echo ⚡ Universal 6-Chart Control Panel
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    echo Download from: https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Install dependencies quickly
echo 📦 Installing/updating dependencies...
pip install streamlit pandas numpy plotly psutil --quiet
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo ✅ Dependencies ready
echo.

REM Launch production system
echo 🚀 Launching Production Dashboard...
echo.
echo Available Dashboards:
echo   • 🎯 Harrison Original - Clean interface with enhanced features
echo   • 🥷 NinjaTrader Pro - Advanced NinjaTrader + Tradovate integration  
echo   • 📊 Universal - Multi-platform dashboard
echo   • ⚙️ Settings - Configure your trading setup
echo.
echo 💡 TIP: Start with 'Harrison Original' for the best experience!
echo.
echo Opening in your web browser...
echo Press Ctrl+C to stop the application
echo.

python launch_production.py

echo.
echo 👋 Application stopped
pause
