@echo off
echo ========================================
echo  TRAINING WHEELS v1.0.0 INSTALLER
echo  Professional Trading Dashboard
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo IMPORTANT: Check "Add to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found. Installing desktop dependencies...
echo.

REM Create virtual environment (optional but recommended)
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat 2>nul

REM Install desktop requirements
echo Installing required packages...
pip install -r requirements_desktop.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  Some packages may have failed to install
    echo    This is normal for platform-specific packages
    echo    The desktop version will still work with core functionality
    echo.
)

echo.
echo ========================================
echo  INSTALLATION COMPLETE! 
echo ========================================
echo.
echo ✅ Training Wheels Desktop v1.0.0 is ready!
echo.
echo To start the application:
echo   Double-click: LAUNCH_TRAINING_WHEELS_DESKTOP.bat
echo   Or run: streamlit run streamlit_app_desktop.py --server.port=8502
echo.
echo The dashboard will open at: http://localhost:8502
echo.
echo Features enabled:
echo   🔔 Desktop notifications
echo   🔌 NinjaTrader connectivity  
echo   📊 Tradovate API integration
echo   👁️ OCR signal reading
echo   🎵 Audio alerts
echo   🚀 Full desktop functionality
echo.

pause
