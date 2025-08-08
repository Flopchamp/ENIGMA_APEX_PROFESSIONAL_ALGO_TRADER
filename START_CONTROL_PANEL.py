#!/usr/bin/env python3
"""
MICHAEL'S DIRECT CONTROL PANEL LAUNCHER
=======================================
Just the Red/Green/Yellow boxes - Simple and Direct
First Principles Only: Drawdown + Enigma Probability
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🎯 MICHAEL'S RED/GREEN/YELLOW CONTROL PANEL")
    print("=" * 50)
    print("🔴 RED = NO Trade")
    print("🟢 GREEN = Trade ON") 
    print("🟡 YELLOW = Marginal Call")
    print("📊 Charts: ES, NQ, YM, RTY, GC, CL")
    print("=" * 50)
    
    try:
        print("🚀 Starting control panel...")
        
        # Use the virtual environment python
        python_exe = "C:/Users/alooh/OneDrive/Pictures/ENIGMA_APEX_PROFESSIONAL_CLIENT_PACKAGE/.venv/Scripts/python.exe"
        
        # Launch streamlit
        subprocess.run([
            python_exe, "-m", "streamlit", "run", "michael_control_panel.py",
            "--server.port=8501",
            "--server.headless=false",
            "--server.address=localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Control panel stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Alternative launch methods:")
        print("   1. Double-click michael_control_panel.py")
        print("   2. Run: streamlit run michael_control_panel.py")

if __name__ == "__main__":
    main()
