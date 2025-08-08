#!/usr/bin/env python3
"""
🎯 HARRISON'S DASHBOARD - SIMPLE LAUNCHER
Quick launch without complex package installation
"""

import subprocess
import sys
import os
from pathlib import Path

def quick_check():
    """Quick check of essential packages"""
    print("🔍 Quick system check...")
    
    essential_packages = {
        'streamlit': 'Streamlit web framework',
        'pandas': 'Data handling',
        'numpy': 'Numerical computing',
        'plotly': 'Interactive charts'
    }
    
    missing_packages = []
    
    for package, description in essential_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (MISSING)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install streamlit pandas numpy plotly")
        return False
    
    print("✅ All essential packages found!")
    return True

def main():
    """Simple main launcher"""
    print("=" * 60)
    print("🎯 HARRISON'S COMPLETE TRADING DASHBOARD")
    print("=" * 60)
    print("🚀 SIMPLE LAUNCHER - No Complex Installation")
    print("")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Quick check
    if not quick_check():
        print("\n❌ Missing essential packages!")
        print("🔧 Please install missing packages and try again:")
        print("   pip install streamlit pandas numpy plotly")
        input("\nPress Enter to continue anyway (may not work properly)...")
    
    # Check if dashboard file exists
    if not os.path.exists("harrison_original_complete.py"):
        print("\n❌ harrison_original_complete.py not found!")
        print("🔧 Please ensure the dashboard file is in the current directory.")
        input("Press Enter to exit...")
        return
    
    print("\n🚀 Launching Harrison's Complete Dashboard...")
    print("📖 Open your browser to: http://localhost:8501")
    print("⏹️ Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Launch dashboard directly
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "harrison_original_complete.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except FileNotFoundError:
        print("\n❌ Streamlit not found!")
        print("💡 Install with: pip install streamlit")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        print("\n🔄 Trying alternative method...")
        try:
            # Try direct Python execution
            subprocess.run([sys.executable, "harrison_original_complete.py"])
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()
