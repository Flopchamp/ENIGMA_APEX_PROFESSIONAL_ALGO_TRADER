@echo off
echo.
echo 🚀 ENIGMA APEX INSTANT DEMO SETUP
echo ================================
echo.

REM Check if .env already exists
if exist ".env" (
    echo ⚠️  Configuration file .env already exists.
    echo.
    choice /C YN /M "Do you want to overwrite it with demo configuration"
    if errorlevel 2 (
        echo ❌ Setup cancelled. Your existing .env file is unchanged.
        pause
        exit /b
    )
    echo.
)

REM Copy demo configuration
echo 📋 Copying demo configuration...
copy ".env.template" ".env" >nul

if errorlevel 1 (
    echo ❌ Failed to copy configuration file.
    echo Make sure .env.template exists in this folder.
    pause
    exit /b 1
)

echo ✅ Demo configuration created successfully!
echo.
echo 🎯 WHAT'S CONFIGURED:
echo    • $100,000 virtual demo account
echo    • All trading platforms in demo/paper mode
echo    • Safe development environment
echo    • No real money or live trading
echo.
echo 🔥 READY TO LAUNCH!
echo    • Run: streamlit run system\apex_compliance_guardian_streamlit.py
echo    • Or double-click: LAUNCH_DEMO.bat
echo.
echo 📚 LEARNING MODE:
echo    • All features are unlocked
echo    • Practice with virtual money
echo    • Test all AlgoBar strategies
echo    • Learn risk management rules
echo.

pause
