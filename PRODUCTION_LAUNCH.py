#!/usr/bin/env python3
"""
🚀 PRODUCTION LAUNCHER
Ready-to-use trading dashboard with Harrison's original interface + enhanced features
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def install_requirements():
    """Install required packages"""
    requirements = [
        "streamlit>=1.48.0",
        "pandas>=1.5.0", 
        "numpy>=1.21.0",
        "plotly>=5.0.0",
        "psutil>=5.9.0",
        "pillow>=8.0.0",
        "opencv-python>=4.5.0",
        "pytesseract>=0.3.8"
    ]
    
    print("🔄 Installing required packages...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                capture_output=True, text=True)
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {package} - continuing...")

def check_system():
    """Check system requirements"""
    print("\n🔍 System Check:")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} - Need 3.8+")
        return False
    
    # Check Streamlit
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not found")
        return False
    
    # Check core files
    required_files = [
        "app.py",
        "streamlit_trading_dashboard.py",
        "system/harrison_enhanced_dashboard.py",
        "system/ninjatrader_tradovate_dashboard.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"⚠️ {file} - missing")
    
    return True

def main():
    """Main launcher"""
    print("=" * 60)
    print("🎯 APEX TRADING DASHBOARD - PRODUCTION LAUNCH")
    print("=" * 60)
    print("📊 Harrison's Original Interface + Enhanced Features")
    print("🥷 NinjaTrader + Tradovate Integration") 
    print("⚡ Universal 6-Chart Control Panel")
    print("=" * 60)
    
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
    
    print("\n🚀 Launching Production Dashboard...")
    print("\n📖 QUICK START GUIDE:")
    print("1. 🎯 Harrison Original - Clean, simple interface with enhanced features")
    print("2. 🥷 NinjaTrader Pro - Advanced NinjaTrader + Tradovate integration")
    print("3. 📊 Universal - Multi-platform dashboard")
    print("4. ⚙️ Settings - Configure your trading setup")
    print("\n💡 TIP: Start with 'Harrison Original' for the best experience!")
    print("=" * 60)
    
    try:
        # Launch Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "light"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
