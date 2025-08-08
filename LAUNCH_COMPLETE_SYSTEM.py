#!/usr/bin/env python3
"""
MICHAEL'S COMPLETE SYSTEM LAUNCHER
==================================
Launch all components: Kelly Engine, OCR, Control Panel, Everything!

Run this to start your complete trading system with:
- Red/Green/Yellow control panel
- OCR screen reading of your 6-chart setup  
- Kelly Criterion position sizing
- ChatGPT AI analysis
- NinjaTrader integration (port 36973)
- Apex compliance monitoring

ONE CLICK = EVERYTHING RUNNING
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def main():
    print("🚀 STARTING MICHAEL'S COMPLETE TRADING SYSTEM")
    print("=" * 60)
    print("🎯 ALL COMPONENTS: Kelly Engine + OCR + Control Panel + AI")
    print("📊 Your 6-Chart Setup: ES, NQ, YM, RTY, GC, CL")
    print("🔴🟢🟡 Red/Green/Yellow Decision Boxes")
    print("=" * 60)
    
    # Change to system directory
    system_path = Path(__file__).parent / "system"
    
    try:
        print("🏃‍♂️ Launching complete system...")
        
        # Run the complete system
        subprocess.run([
            sys.executable, 
            "ENIGMA_APEX_COMPLETE_SYSTEM.py"
        ], cwd=system_path)
        
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("📁 Make sure you're running from the correct directory")

if __name__ == "__main__":
    main()
