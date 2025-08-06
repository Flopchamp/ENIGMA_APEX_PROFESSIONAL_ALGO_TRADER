@echo off
echo ====================================================
echo    ENIGMA-APEX NINJATRADER 8 SETUP
echo    Professional Trading Integration
echo ====================================================
echo.

echo [1/4] Copying NinjaTrader files...

set "NT_PATH=%USERPROFILE%\Documents\NinjaTrader 8\bin\Custom"

echo Creating NinjaTrader directories...
if not exist "%NT_PATH%\Indicators" mkdir "%NT_PATH%\Indicators"
if not exist "%NT_PATH%\Strategies" mkdir "%NT_PATH%\Strategies"
if not exist "%NT_PATH%\AddOns" mkdir "%NT_PATH%\AddOns"

echo Copying Enigma-Apex files...
copy "ninjatrader\Indicators\EnigmaApexPowerScore.cs" "%NT_PATH%\Indicators\" >nul
copy "ninjatrader\Strategies\EnigmaApexAutoTrader.cs" "%NT_PATH%\Strategies\" >nul
copy "ninjatrader\AddOns\EnigmaApexRiskManager.cs" "%NT_PATH%\AddOns\" >nul

echo [2/4] Files copied successfully!

echo [3/4] Next steps for NinjaTrader:
echo 1. Open NinjaTrader 8
echo 2. Press F11 to open NinjaScript Editor
echo 3. Press F5 to compile all scripts
echo 4. Add indicators to your charts
echo 5. Enable automated trading strategies

echo [4/4] Setup complete!
echo.
echo ====================================================
echo    NINJATRADER INTEGRATION READY!
echo ====================================================
echo.
echo Files copied to: %NT_PATH%
echo.
echo Read ninjatrader\INSTALLATION_GUIDE.md for detailed setup
echo.
pause
