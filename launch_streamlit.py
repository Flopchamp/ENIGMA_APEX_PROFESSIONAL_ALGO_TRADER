"""
🚀 UNIVERSAL 6-CHART TRADING SYSTEM LAUNCHER
Simple launcher for the Streamlit-based trading application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_streamlit_installed():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0", 
        "numpy>=1.21.0",
        "plotly>=5.0.0",
        "opencv-python>=4.5.0",
        "Pillow>=8.0.0",
        "pytesseract>=0.3.0"
    ]
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All packages installed successfully!")
    return True

def launch_streamlit_app():
    """Launch the Streamlit application"""
    app_path = Path(__file__).parent / "app.py"
    
    if not app_path.exists():
        print(f"❌ App file not found: {app_path}")
        return False
    
    print("🚀 Launching Universal 6-Chart Trading System...")
    print("📊 Opening in your default web browser...")
    print("🛑 Press Ctrl+C in this terminal to stop the application")
    print()
    
    try:
        # Launch Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.headless", "false"]
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🎯 UNIVERSAL 6-CHART TRADING SYSTEM")
    print("   Streamlit-based control panel for any trader")
    print("=" * 60)
    
    # Check if Streamlit is installed
    if not check_streamlit_installed():
        print("⚠️  Streamlit not found. Installing required packages...")
        if not install_requirements():
            print("❌ Failed to install requirements. Please install manually:")
            print("   pip install streamlit pandas numpy plotly opencv-python Pillow pytesseract")
            return 1
    else:
        print("✅ Streamlit found - ready to launch!")
    
    # Launch the application
    success = launch_streamlit_app()
    
    if success:
        print("\n✅ Application completed successfully")
        return 0
    else:
        print("\n❌ Application completed with errors")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to close...")
    
    sys.exit(exit_code)
