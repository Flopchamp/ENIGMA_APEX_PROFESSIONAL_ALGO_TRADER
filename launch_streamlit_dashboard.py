"""
🚀 UNIVERSAL APEX TRADING DASHBOARD LAUNCHER
Launch the Streamlit-based trading dashboard
Configurable for any trader, any setup

Usage:
    python launch_streamlit_dashboard.py
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'plotly', 
        'pandas',
        'numpy',
        'pillow'
    ]
    
    optional_packages = [
        'pytesseract',
        'opencv-python'
    ]
    
    missing_required = []
    missing_optional = []
    
    print("🔍 Checking dependencies...")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"   ❌ {package} (REQUIRED)")
    
    for package in optional_packages:
        package_name = package.replace('-', '_')  # opencv-python imports as cv2
        if package == 'opencv-python':
            package_name = 'cv2'
        
        try:
            __import__(package_name)
            print(f"   ✅ {package} (OCR functionality)")
        except ImportError:
            missing_optional.append(package)
            print(f"   ⚠️  {package} (OCR functionality - optional)")
    
    return missing_required, missing_optional

def install_dependencies(packages):
    """Install missing dependencies"""
    if not packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(packages)}")
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install'] + packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Installation completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def launch_streamlit():
    """Launch the Streamlit dashboard"""
    dashboard_file = "streamlit_trading_dashboard.py"
    
    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard file not found: {dashboard_file}")
        print("Please ensure you're running this from the correct directory")
        return False
    
    print("🚀 Launching Apex Trading Dashboard...")
    print("📊 The dashboard will open in your web browser")
    print("🌐 URL: http://localhost:8501")
    print("\n⚠️  To stop the dashboard: Press Ctrl+C in this terminal")
    
    try:
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 
            dashboard_file,
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false'
        ]
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return True
    
    return True

def print_banner():
    """Print startup banner"""
    print("\n" + "=" * 70)
    print("🎯 UNIVERSAL APEX TRADING DASHBOARD")
    print("=" * 70)
    print("🌟 Features:")
    print("   📊 Configurable multi-chart visual control")
    print("   🔴🟡🟢 Red/Yellow/Green status indicators")
    print("   💰 Customizable priority indicators")
    print("   👁️  Optional OCR signal reading")
    print("   ⚖️  Apex Trader Funding compliance")
    print("   🚨 Emergency stop protection")
    print("   📈 Real-time performance analytics")
    print("=" * 70)
    print("🔧 Configurable for ANY trader:")
    print("   ✅ Any number of charts (1-12)")
    print("   ✅ Any account size")
    print("   ✅ Any broker platform")
    print("   ✅ Any risk management style")
    print("   ✅ Customizable chart names")
    print("=" * 70)

def main():
    """Main launcher function"""
    print_banner()
    
    # Check dependencies
    missing_required, missing_optional = check_dependencies()
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        
        install = input("\n📦 Install missing packages automatically? (y/n): ").lower().strip()
        
        if install in ['y', 'yes']:
            if not install_dependencies(missing_required):
                print("❌ Failed to install required packages")
                return 1
        else:
            print("❌ Cannot continue without required packages")
            print(f"💡 Manual installation: pip install {' '.join(missing_required)}")
            return 1
    
    if missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("💡 For full OCR functionality, install:")
        print(f"   pip install {' '.join(missing_optional)}")
        
        install_optional = input("\n📦 Install optional packages for OCR? (y/n): ").lower().strip()
        
        if install_optional in ['y', 'yes']:
            install_dependencies(missing_optional)
    
    print("\n" + "=" * 70)
    print("🚀 LAUNCHING DASHBOARD")
    print("=" * 70)
    
    # Launch Streamlit
    success = launch_streamlit()
    
    if success:
        print("\n✅ Dashboard session completed")
        return 0
    else:
        print("\n❌ Dashboard launch failed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
        exit_code = 0
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to close...")
    
    sys.exit(exit_code)
