#!/usr/bin/env python3
"""
🎯 HARRISON'S COMPLETE TRADING DASHBOARD LAUNCHER
All features integrated - Production Ready!

FEATURES INCLUDED:
✅ Harrison's Original Clean Interface
✅ NinjaTrader + Tradovate Integration  
✅ Real Connection Testing (Demo/Test/Live)
✅ Multi-account Futures Trading
✅ OCR Signal Reading
✅ Emergency Stop Protection
✅ Professional Margin Monitoring
✅ 6-Chart Control Grid
✅ All Enhanced Capabilities
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def install_requirements():
    """Install all required packages for full functionality"""
    # Core requirements (essential)
    core_requirements = [
        "streamlit>=1.48.0",
        "pandas>=1.5.0", 
        "numpy>=1.21.0",
        "plotly>=5.0.0"
    ]
    
    # Enhanced requirements (optional)
    enhanced_requirements = [
        "psutil>=5.9.0",        # For NinjaTrader process detection
        "pillow>=8.0.0",        # For OCR image processing
        "opencv-python>=4.5.0",  # For advanced OCR
        "pytesseract>=0.3.8",   # For OCR text recognition
        "requests>=2.25.0"      # For API connections
    ]
    
    print("🔄 Installing required packages for full functionality...")
    
    # Install core packages first
    print("📦 Installing core packages...")
    for package in core_requirements:
        try:
            print(f"   Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ {package}")
            else:
                print(f"⚠️ {package} - install issues (continuing)")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, Exception) as e:
            print(f"⚠️ {package} - failed ({type(e).__name__})")
    
    # Install enhanced packages (optional)
    print("🎯 Installing enhanced packages...")
    for package in enhanced_requirements:
        try:
            print(f"   Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ {package}")
            else:
                print(f"⚠️ {package} - optional feature, continuing without")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, Exception) as e:
            print(f"⚠️ {package} - optional feature, skipping ({type(e).__name__})")

def check_system():
    """Check system requirements and capabilities"""
    print("\n🔍 System Capability Check:")
    
    # Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} - Need 3.8+")
        return False
    
    # Core packages
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not found")
        return False
    
    try:
        import psutil
        print(f"✅ psutil {psutil.__version__} - NinjaTrader detection enabled")
    except ImportError:
        print("⚠️ psutil not found - NinjaTrader detection disabled")
    
    try:
        import cv2
        print(f"✅ OpenCV - OCR capabilities enabled")
    except ImportError:
        print("⚠️ OpenCV not found - OCR capabilities limited")
    
    try:
        import pytesseract
        print(f"✅ Tesseract - OCR text recognition enabled")
    except ImportError:
        print("⚠️ Tesseract not found - OCR text recognition disabled")
    
    # Core files
    required_files = [
        "harrison_original_complete.py",
        "app.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - missing!")
            return False
    
    return True

def main():
    """Main launcher for Harrison's complete dashboard"""
    print("=" * 80)
    print("🎯 HARRISON'S COMPLETE TRADING DASHBOARD")
    print("=" * 80)
    print("🚀 ALL FEATURES INTEGRATED - PRODUCTION READY!")
    print("")
    print("📊 INCLUDED FEATURES:")
    print("  ✅ Harrison's Original Clean Interface")
    print("  ✅ NinjaTrader + Tradovate Integration")
    print("  ✅ Real Connection Testing (Demo/Test/Live)")
    print("  ✅ Multi-account Futures Trading Management")
    print("  ✅ OCR Signal Reading Capabilities")
    print("  ✅ Emergency Stop Protection")
    print("  ✅ Professional Margin Monitoring")
    print("  ✅ 6-Chart Control Grid")
    print("  ✅ Real-time Data Updates")
    print("  ✅ Risk Management & Compliance")
    print("")
    print("=" * 80)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Install packages
    install_requirements()
    
    # System check
    if not check_system():
        print("\n❌ System check failed!")
        print("Please fix the issues above and try again.")
        input("Press Enter to exit...")
        return
    
    print("\n🚀 Launching Harrison's Complete Trading Dashboard...")
    print("\n📋 QUICK START GUIDE:")
    print("1. 🎯 Start in DEMO mode for safe exploration")
    print("2. 🔷 Test connections in TEST mode") 
    print("3. 🔴 Only use LIVE mode when ready for real trading")
    print("4. 📊 Monitor the OVERALL MARGIN (most important indicator)")
    print("5. 🚨 Use EMERGENCY STOP if needed")
    print("\n💡 TIP: Harrison's interface is clean and simple - perfect for focus!")
    print("=" * 80)
    
    try:
        # Launch Harrison's complete dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "harrison_original_complete.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "light"
        ])
    except KeyboardInterrupt:
        print("\n👋 Harrison's Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        print("Trying alternative launch method...")
        try:
            # Fallback: launch main app
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", "8502",
                "--server.address", "localhost"
            ])
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()
