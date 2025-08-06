@echo off
REM 🛡️ APEX COMPLIANCE GUARDIAN - STREAMLIT LAUNCHER
REM Modern Web-Based Interface for Prop Trader Compliance

echo.
echo ==========================================
echo 🛡️ APEX COMPLIANCE GUARDIAN - STREAMLIT
echo ==========================================
echo.
echo Modern Web Interface for Prop Traders
echo Training Wheels for Apex Trader Funding
echo.
echo FOR: Harrison Aloo ^& Michael Canfield
echo Platform: Tradovate (configurable)
echo.
echo ==========================================
echo.

echo 🚀 Starting Streamlit web interface...
echo.
echo 📊 The interface will open automatically in your browser
echo 🌐 URL: http://localhost:8501
echo.
echo ⚠️  To stop the application, press Ctrl+C in this window
echo.

REM Change to the correct directory
cd /d "%~dp0"

REM Start Streamlit
streamlit run system/apex_compliance_guardian_streamlit.py --server.port=8501 --server.headless=false

echo.
echo 🛑 Apex Compliance Guardian stopped.
pause
