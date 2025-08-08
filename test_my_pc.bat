@echo off
echo.
echo ===============================================
echo  ENIGMA APEX PROFESSIONAL - PC SYSTEM TEST
echo ===============================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing/updating required packages...
pip install streamlit pandas numpy plotly requests websockets cryptography psutil

echo.
echo Running automated system test...
python enigma_system_test.py

echo.
echo Test completed! Check the results above.
echo.
echo If tests passed (80%+ success rate), you can now run:
echo     streamlit run harrison_original_complete.py
echo.
pause
