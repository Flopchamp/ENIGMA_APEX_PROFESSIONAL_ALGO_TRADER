"""
🚀 UNIVERSAL TRADING DASHBOARD LAUNCHER
Simple launcher for the complete Streamlit-based trading system
Works for any trader - fully configurable and universal
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def check_streamlit_installed():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit():
    """Install Streamlit if not available"""
    print("📦 Installing Streamlit...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("✅ Streamlit installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Streamlit")
        return False

def check_dependencies():
    """Check and install required dependencies"""
    dependencies = [
        "streamlit",
        "pandas", 
        "numpy",
        "plotly",
        "pillow",
        "opencv-python"
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            missing_deps.append(dep)
            print(f"❌ {dep} - Missing")
    
    if missing_deps:
        print(f"\n📦 Installing missing dependencies: {', '.join(missing_deps)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_deps)
            print("✅ All dependencies installed!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def launch_streamlit_app():
    """Launch the Streamlit application"""
    app_path = Path(__file__).parent / "universal_trading_app.py"
    
    if not app_path.exists():
        print(f"❌ Application file not found: {app_path}")
        return False
    
    try:
        print("🚀 Launching Universal Trading Dashboard...")
        print("📊 Starting Streamlit server...")
        
        # Launch Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ]
        
        print(f"🔧 Command: {' '.join(cmd)}")
        
        # Start the process
        process = subprocess.Popen(cmd)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        print("🌐 Opening dashboard in browser...")
        webbrowser.open("http://localhost:8501")
        
        print("\n" + "="*60)
        print("🎯 UNIVERSAL TRADING DASHBOARD LAUNCHED!")
        print("="*60)
        print("📊 Dashboard URL: http://localhost:8501")
        print("🔧 To stop: Press Ctrl+C in this terminal")
        print("🌐 Browser should open automatically")
        print("⚙️ If browser doesn't open, visit the URL above")
        print("="*60)
        
        # Wait for process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down dashboard...")
            process.terminate()
            process.wait()
            print("✅ Dashboard stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        return False

def print_banner():
    """Print startup banner"""
    print("\n" + "="*70)
    print("🎯 UNIVERSAL MULTI-CHART TRADING DASHBOARD")
    print("="*70)
    print("📊 Features:")
    print("   🔴🟢🟡 Visual Chart Status (Red/Green/Yellow)")
    print("   👁️  OCR Integration (AlgoBox, TradingView, etc.)")
    print("   ⚖️  Apex Trader Funding Compliance")
    print("   📈 Real-time Performance Analytics")
    print("   💰 Overall Margin Indicator")
    print("   🚨 Emergency Stop Protection")
    print("   ⚙️  Fully Configurable for Any Trader")
    print("="*70)
    print("🌟 UNIVERSAL SYSTEM:")
    print("   ✅ Works for ANY trader (not hardcoded)")
    print("   ✅ Configurable account names & settings")
    print("   ✅ Multiple prop firm support")
    print("   ✅ Web-based interface (Streamlit)")
    print("   ✅ Cross-platform compatibility")
    print("="*70)

def main():
    """Main launcher function"""
    print_banner()
    
    print("\n🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        input("Press Enter to exit...")
        return
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install required dependencies")
        input("Press Enter to exit...")
        return
    
    print("✅ All dependencies available")
    
    # Launch application
    print("\n🚀 Launching application...")
    
    if launch_streamlit_app():
        print("✅ Application launched successfully")
    else:
        print("❌ Failed to launch application")
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to close...")

if __name__ == "__main__":
    main()
