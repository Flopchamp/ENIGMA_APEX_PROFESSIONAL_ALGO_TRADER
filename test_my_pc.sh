#!/bin/bash

echo ""
echo "==============================================="
echo " ENIGMA APEX PROFESSIONAL - PC SYSTEM TEST"
echo "==============================================="
echo ""

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install Python 3.8+ from https://python.org"
    exit 1
fi

python3 --version

echo ""
echo "Installing/updating required packages..."
pip3 install streamlit pandas numpy plotly requests websockets cryptography psutil

echo ""
echo "Running automated system test..."
python3 enigma_system_test.py

echo ""
echo "Test completed! Check the results above."
echo ""
echo "If tests passed (80%+ success rate), you can now run:"
echo "    streamlit run harrison_original_complete.py"
echo ""
read -p "Press Enter to continue..."
