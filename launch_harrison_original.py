#!/usr/bin/env python3
"""
🎯 HARRISON'S ORIGINAL DASHBOARD LAUNCHER
Direct launcher for Harrison's clean, original dashboard interface
Based on: https://flopchamp-enig-systemapex-compliance-guardian-streamlit-e2zsng.streamlit.app/
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def install_requirements():
    """Install required packages for Harrison's dashboard"""
    requirements = [
        "streamlit>=1.48.0",
        "pandas>=1.5.0", 
        "numpy>=1.21.0",
        "plotly>=5.0.0"
    ]
    
    print("🔄 Installing packages for Harrison's dashboard...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                capture_output=True, text=True)
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {package} - continuing...")

def main():
    """Launch Harrison's original dashboard directly"""
    print("=" * 60)
    print("🎯 HARRISON'S ORIGINAL TRADING DASHBOARD")
    print("=" * 60)
    print("📊 Clean • Simple • Effective")
    print("🎯 6-Chart Visual Control Panel")
    print("📈 Overall Margin Monitoring (Most Important)")
    print("🟢🟡🔴 Visual Status Indicators")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Install packages
    install_requirements()
    
    # Check if Harrison's dashboard exists
    harrison_file = "harrison_original_dashboard.py"
    if not os.path.exists(harrison_file):
        print(f"\n❌ {harrison_file} not found!")
        print("Please ensure the file is in the current directory.")
        input("Press Enter to exit...")
        return
    
    print(f"\n✅ {harrison_file} found")
    print("\n🚀 Launching Harrison's Original Dashboard...")
    print("\n📖 FEATURES:")
    print("• 🎯 Overall Margin Indicator (Most Important)")
    print("• 📊 6-Chart Status Grid (2x3 Layout)")
    print("• 🟢🟡🔴 Visual Status Colors")
    print("• 🎮 Simple Control Buttons")
    print("• ⚙️ Clean Configuration Sidebar")
    print("\n💡 TIP: Focus on the Overall Margin - it's the most important!")
    print("=" * 60)
    
    try:
        # Launch Harrison's dashboard directly
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", harrison_file,
            "--server.port", "8502",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--theme.base", "light"
        ])
    except KeyboardInterrupt:
        print("\n👋 Harrison's dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching Harrison's dashboard: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
