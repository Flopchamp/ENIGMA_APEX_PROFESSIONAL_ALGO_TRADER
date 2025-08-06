#!/usr/bin/env python3
"""
🔍 ENIGMA-APEX SYSTEM STATUS CHECKER
Real-time system health monitoring
"""

import requests
import subprocess
import sqlite3
import os
import sys
from datetime import datetime
import psutil

def check_web_interface():
    """Check if web interface is running"""
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        return False, "HTTP Error"
    except Exception as e:
        return False, str(e)

def check_database():
    """Check database connectivity"""
    try:
        conn = sqlite3.connect('trading_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM signals")
        count = cursor.fetchone()[0]
        conn.close()
        return True, f"{count} signals stored"
    except Exception as e:
        return False, str(e)

def check_processes():
    """Check running Python processes"""
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'enigma' in cmdline.lower() or 'apex' in cmdline.lower():
                    python_processes.append({
                        'pid': proc.info['pid'],
                        'command': cmdline
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return python_processes

def check_files():
    """Check critical files exist"""
    critical_files = [
        'system/apex_compliance_guardian.py',
        'system/manual_signal_interface.py',
        'system/advanced_risk_manager.py',
        'system/chatgpt_agent_integration.py',
        'system/ocr_enigma_reader.py',
        'templates/signal_input.html',
        'templates/dashboard.html',
        'ninjatrader/Indicators/EnigmaApexPowerScore.cs',
        'ninjatrader/Strategies/EnigmaApexAutoTrader.cs',
        'ninjatrader/AddOns/EnigmaApexRiskManager.cs'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return critical_files, missing_files

def main():
    """Main status check function"""
    print("🔍 ENIGMA-APEX SYSTEM STATUS CHECK")
    print("=" * 60)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check web interface
    print("🌐 WEB INTERFACE STATUS:")
    print("-" * 30)
    web_status, web_data = check_web_interface()
    if web_status:
        print("   ✅ Web interface: RUNNING")
        print(f"   📊 Signals sent: {web_data.get('signals_sent', 0)}")
        print(f"   🔌 WebSocket: {web_data.get('websocket_server', 'unknown')}")
    else:
        print("   ❌ Web interface: NOT RUNNING")
        print(f"   💬 Error: {web_data}")
    print()
    
    # Check database
    print("💾 DATABASE STATUS:")
    print("-" * 30)
    db_status, db_info = check_database()
    if db_status:
        print("   ✅ Database: OPERATIONAL")
        print(f"   📈 {db_info}")
    else:
        print("   ❌ Database: ERROR")
        print(f"   💬 Error: {db_info}")
    print()
    
    # Check running processes
    print("🏃 RUNNING PROCESSES:")
    print("-" * 30)
    processes = check_processes()
    if processes:
        print(f"   ✅ Found {len(processes)} Enigma-Apex processes:")
        for proc in processes:
            command_short = proc['command'][:60] + "..." if len(proc['command']) > 60 else proc['command']
            print(f"   📊 PID {proc['pid']}: {command_short}")
    else:
        print("   ⚠️  No Enigma-Apex processes found")
    print()
    
    # Check files
    print("📁 FILE INTEGRITY:")
    print("-" * 30)
    all_files, missing = check_files()
    if not missing:
        print(f"   ✅ All {len(all_files)} critical files present")
    else:
        print(f"   ⚠️  {len(missing)} files missing:")
        for file in missing:
            print(f"   ❌ {file}")
    print()
    
    # Overall status
    print("🎯 OVERALL SYSTEM STATUS:")
    print("-" * 30)
    
    issues = []
    if not web_status:
        issues.append("Web interface not running")
    if not db_status:
        issues.append("Database error")
    if not processes:
        issues.append("No background processes")
    if missing:
        issues.append(f"{len(missing)} missing files")
    
    if not issues:
        print("   🟢 SYSTEM STATUS: FULLY OPERATIONAL")
        print("   ✅ All components working correctly")
        print("   🚀 Ready for trading operations")
    elif len(issues) <= 2:
        print("   🟡 SYSTEM STATUS: PARTIALLY OPERATIONAL")
        print("   ⚠️  Minor issues detected:")
        for issue in issues:
            print(f"   • {issue}")
        print("   🔧 System mostly functional")
    else:
        print("   🔴 SYSTEM STATUS: CRITICAL ISSUES")
        print("   ❌ Multiple problems detected:")
        for issue in issues:
            print(f"   • {issue}")
        print("   🛠️  Immediate attention required")
    
    print()
    print("🚀 QUICK ACTIONS:")
    print("-" * 30)
    if not web_status:
        print("   💡 Start web interface: python system/manual_signal_interface.py")
    if not processes:
        print("   💡 Start all components: python START_COMPLETE_SYSTEM.py")
    if missing:
        print("   💡 Re-run installer: INSTALL.bat")
    
    print()
    print("📖 HELPFUL LINKS:")
    print("-" * 30)
    print("   🌐 Trading Interface: http://localhost:5000")
    print("   📊 Dashboard: http://localhost:5000/dashboard")
    print("   📚 Documentation: documentation/ENIGMA_APEX_USER_MANUAL.md")
    print("   ❓ FAQ: documentation/ENIGMA_APEX_FAQ.md")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
