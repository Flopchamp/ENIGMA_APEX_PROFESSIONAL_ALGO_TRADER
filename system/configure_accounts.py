#!/usr/bin/env python3
"""
🎯 ENIGMA APEX - Professional Trading System Configuration
Streamlit-based configuration for multi-chart Algobox integration
Production-ready for Michael Canfield's 6-chart setup
"""

import streamlit as st
import json
import os
from datetime import datetime
import socket
import asyncio
import websockets
from pathlib import Path

"""
🎯 ENIGMA APEX - Michael's Control Panel Launcher
Direct access to Red/Green/Yellow decision boxes
"""

import subprocess
import sys
import os

def main():
    """Launch Michael's control panel directly"""
    print("🎯 ENIGMA APEX - Michael's Trading Control Panel")
    print("=" * 60)
    print("� Red/Green/Yellow Decision Boxes")
    print("🔘 Toggle Control Panel On/Off")  
    print("📈 6-Chart Layout (ES, NQ, YM, RTY, GC, CL)")
    print("🔌 NinjaTrader Port: 36973 (Your Current Setup)")
    print("=" * 60)
    print()
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'michael_control_panel.py')
        
        if os.path.exists(script_path):
            print("🚀 Starting Michael's control panel...")
            print("📊 Features:")
            print("  - Toggle control panel with sidebar button")
            print("  - Red boxes: NO TRADE with percentage") 
            print("  - Green boxes: TRADE ON with percentage")
            print("  - Yellow boxes: MARGINAL with percentage")
            print("  - Based on: Drawdown remaining + Enigma probability")
            print()
            
            # Launch directly
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", script_path,
                "--server.headless", "false"
            ])
        else:
            print("❌ Control panel file not found")
            print("Please ensure michael_control_panel.py exists")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Try manually: streamlit run michael_control_panel.py")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
