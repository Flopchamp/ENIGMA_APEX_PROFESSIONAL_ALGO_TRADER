#!/usr/bin/env python3
"""
🎯 ENIGMA APEX - First Principles Trading Launcher
Launch the simplified trading system focused on:
1. Remaining drawdown per account
2. Enigma signal probability per instrument  
3. Real-time go/no-go decisions

For Michael Canfield - No Hard Coding
"""

import subprocess
import sys
import os
import webbrowser

def main():
    print("🎯 ENIGMA APEX - First Principles Trading System")
    print("=" * 60)
    print("👤 Client: Michael Canfield")
    print("🧠 Philosophy: Drawdown + Enigma Probability = Decision")
    print("🚫 NO HARD CODING - Fully Dynamic")
    print("=" * 60)
    print()
    
    print("🎯 Core Focus:")
    print("  1️⃣  Remaining Drawdown (per Apex account)")
    print("  2️⃣  Enigma Success Probability (per instrument)")
    print("  3️⃣  Real-time Trading Decisions")
    print()
    
    # Launch options
    print("📋 Launch Options:")
    print("  [1] First Principles Interface (Streamlit)")
    print("  [2] Online Configuration (Streamlit Cloud)")
    print("  [3] Exit")
    print()
    
    choice = input("Select option (1-3): ")
    
    if choice == "1":
        launch_local_interface()
    elif choice == "2":
        launch_online_interface()
    elif choice == "3":
        print("👋 Exiting...")
    else:
        print("❌ Invalid choice")

def launch_local_interface():
    """Launch local Streamlit interface"""
    print("🚀 Starting First Principles Trading Interface...")
    
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'first_principles_trader.py')
        
        if os.path.exists(script_path):
            print(f"✅ Found: {script_path}")
            print("🌐 Starting Streamlit server...")
            
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", script_path,
                "--server.headless", "false"
            ])
        else:
            print(f"❌ File not found: {script_path}")
            print("Please ensure first_principles_trader.py exists")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Manual command: streamlit run first_principles_trader.py")

def launch_online_interface():
    """Launch online Streamlit Cloud interface"""
    url = "https://flopchamp-enig-systemapex-compliance-guardian-streamlit-e2zsng.streamlit.app/"
    
    print(f"🌐 Opening: {url}")
    print()
    print("🎯 Features Available Online:")
    print("  ✅ Dynamic Account Configuration")  
    print("  ✅ Enigma Probability Models")
    print("  ✅ Real-time Decision Matrix")
    print("  ✅ Drawdown Monitoring")
    print("  ✅ No Hard Coding")
    print()
    
    try:
        webbrowser.open(url)
        print("✅ Interface opened in browser!")
    except:
        print(f"Please manually open: {url}")

if __name__ == "__main__":
    main()
