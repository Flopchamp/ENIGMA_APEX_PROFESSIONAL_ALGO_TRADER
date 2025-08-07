"""
🥷 NINJATRADER + TRADOVATE LAUNCHER
Quick launcher for the enhanced NinjaTrader + Tradovate dashboard
"""

import subprocess
import sys
import os

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    packages = [
        "streamlit>=1.48.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "plotly>=5.0.0",
        "Pillow>=8.0.0",
        "psutil>=5.9.0"  # For NinjaTrader process detection
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")

def launch_ninjatrader_dashboard():
    """Launch the NinjaTrader + Tradovate dashboard"""
    
    if not check_streamlit():
        print("❌ Streamlit not found. Installing required packages...")
        install_requirements()
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Launch the NinjaTrader dashboard directly
    dashboard_file = os.path.join(current_dir, "system", "ninjatrader_tradovate_dashboard.py")
    
    if os.path.exists(dashboard_file):
        print("🥷 Launching NinjaTrader + Tradovate Dashboard...")
        print("📊 Opening in your default browser...")
        
        # Launch Streamlit with the NinjaTrader dashboard
        cmd = [sys.executable, "-m", "streamlit", "run", dashboard_file, 
               "--server.port", "8502", 
               "--theme.base", "dark",
               "--theme.primaryColor", "#ff6b35"]
        
        subprocess.run(cmd)
    else:
        print("❌ NinjaTrader dashboard file not found!")
        print("🔄 Falling back to main application...")
        
        # Fallback to main app
        main_app = os.path.join(current_dir, "app.py")
        if os.path.exists(main_app):
            cmd = [sys.executable, "-m", "streamlit", "run", main_app]
            subprocess.run(cmd)
        else:
            print("❌ No dashboard files found!")

if __name__ == "__main__":
    print("🥷 NinjaTrader + Tradovate Dashboard Launcher")
    print("=" * 50)
    launch_ninjatrader_dashboard()
