#!/usr/bin/env python3
"""
MICHAEL'S SYSTEM INSTALLER
=========================
Install all required packages for your complete trading system
"""

import subprocess
import sys

def install_package(package_name):
    """Install a Python package"""
    print(f"📦 Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"   ✅ {package_name} installed successfully")
        return True
    except Exception as e:
        print(f"   ❌ Failed to install {package_name}: {e}")
        return False

def main():
    print("🚀 MICHAEL'S SYSTEM INSTALLER")
    print("=" * 50)
    print("Installing all required packages for your trading system")
    print("Kelly Engine + OCR + AI + Control Panel + Everything")
    print("=" * 50)
    
    # Required packages
    packages = [
        "streamlit",
        "opencv-python", 
        "numpy",
        "pandas",
        "mss",
        "websocket-client",
        "pillow",
        "requests",
        "python-dotenv"
    ]
    
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 INSTALLATION SUMMARY:")
    print("-" * 30)
    print(f"✅ Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count == len(packages):
        print("\n🎯 ALL PACKAGES INSTALLED SUCCESSFULLY!")
        print("✅ Your system is ready to launch")
        print("🚀 Run: python WORKING_LAUNCHER.py")
    else:
        print("\n⚠️ Some packages failed to install")
        print("💡 Try running as administrator or check your Python installation")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
