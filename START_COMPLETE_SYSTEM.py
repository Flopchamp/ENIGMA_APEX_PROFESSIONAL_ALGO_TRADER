#!/usr/bin/env python3
"""
🚀 ENIGMA-APEX COMPLETE SYSTEM LAUNCHER
Starts all components of the professional trading system
"""

import subprocess
import time
import webbrowser
import os
import sys
from pathlib import Path

def print_header():
    """Display system header"""
    print("=" * 80)
    print("🚀 ENIGMA-APEX PROFESSIONAL TRADING SYSTEM")
    print("   Complete System Launcher")
    print("   Version: 1.0.0 Production")
    print("=" * 80)
    print()

def start_component(name, script_path, background=True):
    """Start a system component"""
    try:
        print(f"🚀 Starting {name}...")
        if background:
            process = subprocess.Popen([
                sys.executable, script_path
            ], cwd=Path(__file__).parent,
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE,
               creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            print(f"   ✅ {name} started in background")
            return process
        else:
            subprocess.run([sys.executable, script_path], cwd=Path(__file__).parent)
            print(f"   ✅ {name} completed")
            return None
    except Exception as e:
        print(f"   ❌ Failed to start {name}: {str(e)}")
        return None

def main():
    """Main launcher function"""
    print_header()
    
    # List of components to start
    components = [
        ("Apex Compliance Guardian", "system/apex_compliance_guardian.py"),
        ("Manual Signal Interface", "system/manual_signal_interface.py"),
        ("Advanced Risk Manager", "system/advanced_risk_manager.py"),
        ("ChatGPT AI Agent", "system/chatgpt_agent_integration.py"),
    ]
    
    processes = []
    
    print("📋 STARTING CORE COMPONENTS:")
    print("-" * 50)
    
    # Start each component
    for name, script_path in components:
        if os.path.exists(script_path):
            process = start_component(name, script_path, background=True)
            if process:
                processes.append((name, process))
            time.sleep(2)  # Wait between starts
        else:
            print(f"   ⚠️  {name} file not found: {script_path}")
    
    print()
    print("🌐 WEB INTERFACES:")
    print("-" * 50)
    print("   📊 Trading Dashboard: http://localhost:5000")
    print("   📈 Signal Input: http://localhost:5000")
    print("   📋 Signal History: http://localhost:5000/dashboard")
    print()
    
    print("🥷 NINJATRADER INTEGRATION:")
    print("-" * 50)
    print("   📁 Indicators: ninjatrader/Indicators/")
    print("   📁 Strategies: ninjatrader/Strategies/")
    print("   📁 AddOns: ninjatrader/AddOns/")
    print("   📖 Setup Guide: ninjatrader/INSTALLATION_GUIDE.md")
    print()
    
    print("📚 DOCUMENTATION:")
    print("-" * 50)
    print("   📖 User Manual: documentation/ENIGMA_APEX_USER_MANUAL.md")
    print("   🔧 Quick Reference: documentation/ENIGMA_APEX_QUICK_REFERENCE.md")
    print("   👥 Seniors Guide: documentation/ENIGMA_APEX_SENIORS_GUIDE.md")
    print("   ❓ FAQ: documentation/ENIGMA_APEX_FAQ.md")
    print()
    
    # Open web interface
    print("🌐 Opening web interface...")
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:5000")
        print("   ✅ Browser opened to trading interface")
    except:
        print("   💡 Please manually open: http://localhost:5000")
    
    print()
    print("🎯 SYSTEM STATUS:")
    print("-" * 50)
    print(f"   🟢 Active Components: {len(processes)}")
    for name, process in processes:
        status = "🟢 RUNNING" if process.poll() is None else "🔴 STOPPED"
        print(f"   {status} {name}")
    
    print()
    print("📋 NEXT STEPS:")
    print("-" * 50)
    print("   1. ✅ System is now running")
    print("   2. 🌐 Use web interface for manual signals")
    print("   3. 🥷 Install NinjaTrader components (see guide)")
    print("   4. 📊 Test with demo account first")
    print("   5. 📖 Review documentation for advanced features")
    
    print()
    print("⚠️  IMPORTANT SAFETY REMINDERS:")
    print("-" * 50)
    print("   • Always test with demo accounts first")
    print("   • The system enforces prop firm compliance")
    print("   • Emergency stops are accessible via web interface")
    print("   • Never risk more than you can afford to lose")
    
    print()
    print("🚀 ENIGMA-APEX SYSTEM IS NOW OPERATIONAL!")
    print("=" * 80)
    
    # Keep running to monitor processes
    try:
        print("\n👁️  Monitoring system... Press Ctrl+C to stop all components")
        while True:
            time.sleep(30)
            running_count = sum(1 for _, proc in processes if proc.poll() is None)
            if running_count < len(processes):
                print(f"⚠️  Warning: {len(processes) - running_count} components stopped")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n🛑 STOPPING ALL COMPONENTS...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"   ✅ Stopped {name}")
            except:
                print(f"   ⚠️  Could not stop {name}")
        print("🏁 System shutdown complete")

if __name__ == "__main__":
    main()
