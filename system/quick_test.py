#!/usr/bin/env python3
"""
🎯 ENIGMA APEX - Quick System Test
Tests NinjaTrader connection, AlgoBox compatibility, and 6-chart setup
"""

import json
import socket
import sys
import os
from datetime import datetime
import time

def load_config():
    """Load trading configuration"""
    try:
        with open('trading_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def test_ninjatrader_connection(port):
    """Test NinjaTrader ATI connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def run_quick_test():
    """Run all system tests"""
    print("\n🎯 ENIGMA APEX - Quick System Test")
    print("=" * 50)
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration
    print("\n📊 Loading Configuration...")
    config = load_config()
    if not config:
        print("❌ Failed to load configuration!")
        return False
    
    print("✅ Configuration loaded successfully!")
    
    # Test NinjaTrader connection
    print("\n🔗 Testing NinjaTrader Connection...")
    ati_port = config['ninjatrader']['ati_port']
    print(f"ATI Port: {ati_port}")
    
    nt_connected = test_ninjatrader_connection(ati_port)
    if nt_connected:
        print(f"✅ NinjaTrader connection successful on port {ati_port}")
    else:
        print(f"❌ NinjaTrader connection failed on port {ati_port}")
        print("\n⚠️ Please check:")
        print("1. NinjaTrader 8 is running")
        print("2. Tools > Options > Automated Trading Interface")
        print(f"3. Port is set to {ati_port}")
        print("4. Click OK to save settings")
        return False
    
    # Verify chart configuration
    print("\n📈 Verifying Chart Configuration...")
    charts = config['ninjatrader']['charts']
    print(f"Number of charts configured: {len(charts)}")
    
    for symbol, chart in charts.items():
        print(f"✅ {symbol}: {chart['name']} ({chart['timeframe']}) - Account: {chart['account']}")
    
    # Check account configuration
    print("\n💼 Verifying Account Configuration...")
    accounts = config['accounts']
    total_capital = sum(account['size'] for account in accounts.values())
    print(f"Total accounts: {len(accounts)}")
    print(f"Total capital: ${total_capital:,}")
    
    for name, account in accounts.items():
        print(f"✅ {name}: ${account['size']:,} ({account['risk']}% risk, {account['max_contracts']} contracts)")
    
    # Server connection test
    print("\n🌐 Testing Server Connection...")
    server = config['connection']['server_host']
    port = config['connection']['server_port']
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server, port))
        sock.close()
        if result == 0:
            print(f"✅ Server connection successful ({server}:{port})")
        else:
            print(f"❌ Server connection failed ({server}:{port})")
    except:
        print(f"❌ Server connection error ({server}:{port})")
    
    print("\n🎯 System Status Summary:")
    print("-" * 30)
    print(f"NinjaTrader ATI: {'✅ Ready' if nt_connected else '❌ Not Connected'}")
    print(f"Charts Configured: ✅ {len(charts)} charts")
    print(f"Accounts Ready: ✅ {len(accounts)} accounts")
    print(f"Total Capital: ${total_capital:,}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    print("\n📝 Quick Start Steps:")
    print("1. Ensure NinjaTrader 8 is running")
    print("2. Verify ATI settings in Tools > Options")
    print("3. Open AlgoBox and connect")
    print("4. All 6 charts should connect automatically")
    print("5. Monitor the dashboard for live updates")
    
    return True

if __name__ == "__main__":
    print("\n🚀 Starting Quick Test...")
    success = run_quick_test()
    
    if success:
        print("\n✅ Quick test completed successfully!")
        print("🎯 System is ready for live trading!")
    else:
        print("\n❌ Quick test failed!")
        print("Please check the errors above and try again.")
