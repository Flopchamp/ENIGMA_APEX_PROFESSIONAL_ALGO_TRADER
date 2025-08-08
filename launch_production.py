#!/usr/bin/env python3
"""
🚀 PRODUCTION LAUNCHER - Universal 6-Chart Trading System
Ready for production deployment with all features enabled
Includes Harrison's enhanced dashboard and NinjaTrader integration
"""

import os
import sys
import subprocess
import pkg_resources
from pathlib import Path

# Required packages for production
REQUIRED_PACKAGES = [
    'streamlit>=1.48.0',
    'pandas>=2.0.0',
    'numpy>=1.24.0',
    'plotly>=5.17.0',
    'Pillow>=10.0.0',
    'opencv-python>=4.8.0.76',
    'pytesseract>=0.3.10',
    'psutil>=5.9.0',
    'requests>=2.31.0',
    'python-dotenv>=1.0.0',
    'watchdog>=3.0.0',
]

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_required_packages():
    """Install all required packages"""
    print("🔧 Checking and installing required packages...")
    
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            pkg_name = package.split('>=')[0].split('==')[0]
            if pkg_name == 'opencv-python':
                import cv2
            elif pkg_name == 'python-dotenv':
                import dotenv
            else:
                __import__(pkg_name)
            print(f"✅ {pkg_name} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {pkg_name} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
        print("✅ All packages installed successfully!")
    else:
        print("✅ All required packages are already installed!")
    
    return True

def setup_environment():
    """Setup production environment"""
    print("🌟 Setting up production environment...")
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    system_dir = current_dir / 'system'
    
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    if str(system_dir) not in sys.path:
        sys.path.insert(0, str(system_dir))
    
    # Set environment variables for production
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'false'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    print("✅ Environment configured for production")
    return True

def verify_system_files():
    """Verify all system files exist"""
    print("📁 Verifying system files...")
    
    required_files = [
        'app.py',
        'system/streamlit_6_chart_dashboard.py',
        'system/harrison_enhanced_dashboard.py',
        'system/ninjatrader_tradovate_dashboard.py',
        'system/streamlit_system_integration.py',
    ]
    
    missing_files = []
    current_dir = Path(__file__).parent.absolute()
    
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - MISSING")
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} system files are missing!")
        print("Please ensure all files are properly copied to the system folder.")
        return False
    
    print("✅ All system files verified!")
    return True

def create_production_config():
    """Create production configuration file"""
    config_path = Path(__file__).parent / '.streamlit' / 'config.toml'
    config_path.parent.mkdir(exist_ok=True)
    
    config_content = """
[server]
headless = false
port = 8501
enableCORS = true
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f4e79"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#262730"

[logger]
level = "info"
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print("✅ Production configuration created")

def launch_production_app():
    """Launch the production app"""
    print("\n🚀 Launching Universal 6-Chart Trading System - PRODUCTION MODE")
    print("=" * 60)
    print("📊 Available Dashboards:")
    print("  • Universal 6-Chart Dashboard (Default)")
    print("  • Harrison's Enhanced Dashboard")
    print("  • NinjaTrader + Tradovate Dashboard")
    print("  • System Integration Panel")
    print("  • Analytics & Settings")
    print("=" * 60)
    
    app_path = Path(__file__).parent / 'app.py'
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', str(app_path),
            '--server.headless', 'false',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")

def main():
    """Main production launcher"""
    print("🚀 UNIVERSAL 6-CHART TRADING SYSTEM - PRODUCTION LAUNCHER")
    print("=" * 60)
    
    # Pre-flight checks
    if not check_python_version():
        return False
    
    if not install_required_packages():
        return False
    
    if not setup_environment():
        return False
    
    if not verify_system_files():
        return False
    
    # Create production config
    create_production_config()
    
    # Launch the app
    launch_production_app()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
    except Exception as e:
        print(f"\n❌ Production launcher error: {e}")
        input("Press Enter to exit...")
