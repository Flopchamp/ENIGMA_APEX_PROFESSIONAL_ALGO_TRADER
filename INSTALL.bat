@echo off
echo ====================================================
echo    ENIGMA-APEX TRADING SYSTEM INSTALLER
echo    Professional Prop Trading Automation
echo ====================================================
echo.

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python found - OK

echo [2/6] Installing required Python packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages. Check your internet connection.
    pause
    exit /b 1
)
echo Packages installed - OK

echo [3/6] Creating system directories...
if not exist "logs" mkdir logs
if not exist "config" mkdir config
if not exist "data" mkdir data
echo Directories created - OK

echo [4/6] Setting up configuration files...
echo # Enigma-Apex Configuration > config\settings.ini
echo [TRADING] >> config\settings.ini
echo max_risk_per_trade=0.02 >> config\settings.ini
echo daily_loss_limit=0.05 >> config\settings.ini
echo enable_ai_recommendations=true >> config\settings.ini
echo [PLATFORMS] >> config\settings.ini
echo ninjatrader_enabled=true >> config\settings.ini
echo tradovate_enabled=false >> config\settings.ini
echo Configuration created - OK

echo [5/6] Creating desktop shortcuts...
echo @echo off > "Start_Enigma_Apex.bat"
echo cd /d "%~dp0" >> "Start_Enigma_Apex.bat"
echo python system\ENIGMA_APEX_COMPLETE_SYSTEM.py >> "Start_Enigma_Apex.bat"
echo pause >> "Start_Enigma_Apex.bat"
echo Shortcuts created - OK

echo [6/6] Installation complete!
echo.
echo ====================================================
echo    INSTALLATION SUCCESSFUL!
echo ====================================================
echo.
echo Next Steps:
echo 1. Read documentation\ENIGMA_APEX_USER_MANUAL.md
echo 2. Run "Start_Enigma_Apex.bat" to launch system
echo 3. Configure NinjaTrader connection (see manual)
echo.
echo Support: See documentation\ENIGMA_APEX_FAQ.md
echo.
pause
