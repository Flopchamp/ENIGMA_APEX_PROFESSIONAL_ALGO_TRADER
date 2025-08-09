#!/bin/bash

# Training Wheels Desktop Launcher - Linux/macOS Version
echo "========================================"
echo "  TRAINING WHEELS DESKTOP LAUNCHER"
echo "  Professional Trading Dashboard"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from your package manager"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3 from your package manager"
    echo "Ubuntu/Debian: sudo apt install python3-pip"
    exit 1
fi

echo "Python found. Installing desktop dependencies..."
echo

# Install desktop requirements
pip3 install -r requirements_desktop.txt

if [ $? -ne 0 ]; then
    echo
    echo "WARNING: Some packages may have failed to install"
    echo "This is normal for platform-specific packages"
    echo
fi

echo
echo "========================================"
echo "  LAUNCHING TRAINING WHEELS DESKTOP"
echo "========================================"
echo
echo "Starting desktop version with full functionality..."
echo "- Desktop notifications enabled"
echo "- NinjaTrader connection enabled (if available)"
echo "- Tradovate API enabled"
echo "- Full OCR capabilities"
echo "- Audio alerts enabled"
echo

# Launch the desktop version
streamlit run streamlit_app_desktop.py --server.port=8502 --server.headless=false

echo "Press any key to exit..."
read -n 1
