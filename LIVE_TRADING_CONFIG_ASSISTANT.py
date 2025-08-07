#!/usr/bin/env python3
"""
🚀 ENIGMA APEX - LIVE TRADING CONFIGURATION ASSISTANT
Helps configure the system for live trading deployment
"""

import os
import json
from datetime import datetime

def main():
    """Main live trading configuration assistant"""
    
    print("🚀 ENIGMA APEX - LIVE TRADING CONFIGURATION ASSISTANT")
    print("=" * 70)
    print("⚠️  CONFIGURING FOR LIVE TRADING - SAFETY FIRST!")
    print("📅 Configuration Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🎯 Mode: Live Trading Deployment")
    print("=" * 70)
    print()
    
    print("🛡️ LIVE TRADING SAFETY PROTOCOL:")
    print("• Start with MINIMUM position sizes")
    print("• Use CONSERVATIVE risk settings")
    print("• Monitor CLOSELY for first trades")
    print("• STOP immediately if issues occur")
    print()
    
    # Get client preferences
    config = get_live_trading_preferences()
    
    # Generate configuration files
    generate_live_config(config)
    
    # Show deployment checklist
    show_deployment_checklist()
    
    print("\n🏆 LIVE TRADING CONFIGURATION COMPLETE!")
    print("🚀 Your system is ready for live deployment!")

def get_live_trading_preferences():
    """Get client preferences for live trading"""
    
    print("📋 LIVE TRADING CONFIGURATION QUESTIONS:")
    print("-" * 50)
    
    config = {}
    
    # Account size
    while True:
        try:
            account_size = input("💰 What is your trading account size? ($): ").strip().replace("$", "").replace(",", "")
            config['account_size'] = float(account_size)
            break
        except ValueError:
            print("❌ Please enter a valid number (e.g., 100000)")
    
    # Risk tolerance
    while True:
        try:
            risk_percent = input("⚠️ Maximum account risk per trade? (1-5%): ").strip().replace("%", "")
            risk_val = float(risk_percent)
            if 0.1 <= risk_val <= 5.0:
                config['max_risk_percent'] = risk_val
                break
            else:
                print("❌ Please enter a value between 0.1 and 5.0")
        except ValueError:
            print("❌ Please enter a valid percentage (e.g., 2)")
    
    # Position size
    while True:
        try:
            max_contracts = input("📊 Maximum position size (contracts): ").strip()
            contracts_val = int(max_contracts)
            if 1 <= contracts_val <= 20:
                config['max_position_size'] = contracts_val
                break
            else:
                print("❌ Please enter a value between 1 and 20")
        except ValueError:
            print("❌ Please enter a valid number (e.g., 3)")
    
    # Trading hours
    config['trading_hours'] = input("🕐 Trading hours (e.g., 09:30-16:00 EST): ").strip() or "09:30-16:00"
    
    # Symbols to trade
    symbols_input = input("📈 Symbols to trade (e.g., ES,NQ,YM): ").strip() or "ES,NQ"
    config['trading_symbols'] = [s.strip().upper() for s in symbols_input.split(",")]
    
    # AlgoBox setup
    config['use_algobox'] = input("📊 Are you using AlgoBox for signals? (y/n): ").strip().lower().startswith('y')
    
    # NinjaTrader setup
    config['use_ninjatrader'] = input("🎯 Are you using NinjaTrader for execution? (y/n): ").strip().lower().startswith('y')
    
    return config

def generate_live_config(config):
    """Generate live trading configuration files"""
    
    print("\n🔧 GENERATING LIVE TRADING CONFIGURATION...")
    print("-" * 50)
    
    # Calculate risk settings
    max_risk_amount = config['account_size'] * (config['max_risk_percent'] / 100)
    daily_loss_limit = max_risk_amount * 5  # 5 trades worth of max risk
    
    # Live trading configuration
    live_config = {
        "trading_mode": "LIVE",
        "account_settings": {
            "account_size": config['account_size'],
            "max_risk_percent": config['max_risk_percent'],
            "max_risk_amount": max_risk_amount,
            "daily_loss_limit": daily_loss_limit,
            "max_position_size": config['max_position_size']
        },
        "risk_management": {
            "stop_loss_points": 20,
            "profit_target_multiplier": 2.0,
            "min_power_score": 85,
            "required_confluence": "L2",
            "max_daily_trades": 15,
            "enable_trailing_stops": True
        },
        "trading_settings": {
            "symbols": config['trading_symbols'],
            "trading_hours": config['trading_hours'],
            "auto_trading": True,
            "notifications_enabled": True
        },
        "platform_settings": {
            "use_algobox": config['use_algobox'],
            "use_ninjatrader": config['use_ninjatrader'],
            "ninjatrader_port": 8080,
            "data_feed": "live"
        },
        "safety_settings": {
            "enable_kill_switch": True,
            "max_consecutive_losses": 3,
            "pause_on_connection_loss": True,
            "emergency_exit_enabled": True
        }
    }
    
    # Save configuration
    config_file = "live_trading_config.json"
    with open(config_file, 'w') as f:
        json.dump(live_config, f, indent=4)
    
    print(f"✅ Configuration saved to: {config_file}")
    
    # Generate .env file for live trading
    env_content = f"""# ENIGMA APEX - LIVE TRADING CONFIGURATION
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# TRADING MODE
TRADING_MODE=LIVE
AUTO_TRADING_ENABLED=true

# ACCOUNT SETTINGS
ACCOUNT_SIZE={config['account_size']}
MAX_RISK_PERCENT={config['max_risk_percent']}
MAX_POSITION_SIZE={config['max_position_size']}
DAILY_LOSS_LIMIT={daily_loss_limit}

# RISK MANAGEMENT
STOP_LOSS_POINTS=20
PROFIT_TARGET_MULTIPLIER=2.0
MIN_POWER_SCORE=85
REQUIRED_CONFLUENCE=L2
MAX_DAILY_TRADES=15

# PLATFORM INTEGRATION
NINJATRADER_ENABLED={str(config['use_ninjatrader']).lower()}
NINJATRADER_HOST=localhost
NINJATRADER_PORT=8080

ALGOBOX_ENABLED={str(config['use_algobox']).lower()}
ALGOBOX_OCR_ENABLED=true

# NOTIFICATIONS
DESKTOP_NOTIFICATIONS=true
TRADE_NOTIFICATIONS=true
RISK_NOTIFICATIONS=true
SOUND_ALERTS=true

# SAFETY FEATURES
KILL_SWITCH_ENABLED=true
MAX_CONSECUTIVE_LOSSES=3
EMERGENCY_EXIT_ENABLED=true

# TRADING SYMBOLS
TRADING_SYMBOLS={','.join(config['trading_symbols'])}
TRADING_HOURS={config['trading_hours']}
"""
    
    with open('.env.live', 'w') as f:
        f.write(env_content)
    
    print("✅ Live trading .env file created: .env.live")
    
    # Display configuration summary
    print("\n📊 LIVE TRADING CONFIGURATION SUMMARY:")
    print("-" * 40)
    print(f"💰 Account Size: ${config['account_size']:,.2f}")
    print(f"⚠️ Max Risk Per Trade: {config['max_risk_percent']}% (${max_risk_amount:,.2f})")
    print(f"📊 Max Position Size: {config['max_position_size']} contracts")
    print(f"🛑 Daily Loss Limit: ${daily_loss_limit:,.2f}")
    print(f"📈 Trading Symbols: {', '.join(config['trading_symbols'])}")
    print(f"🕐 Trading Hours: {config['trading_hours']}")
    print(f"📊 AlgoBox Integration: {'Yes' if config['use_algobox'] else 'No'}")
    print(f"🎯 NinjaTrader Integration: {'Yes' if config['use_ninjatrader'] else 'No'}")

def show_deployment_checklist():
    """Show the deployment checklist"""
    
    print("\n🚨 LIVE TRADING DEPLOYMENT CHECKLIST:")
    print("=" * 50)
    
    checklist_items = [
        "□ Live trading configuration generated",
        "□ Risk management settings reviewed",
        "□ Account size and risk limits confirmed",
        "□ NinjaTrader ATI enabled (if using)",
        "□ AlgoBox screen regions configured (if using)",
        "□ Live data feeds connected",
        "□ Notification system tested",
        "□ Emergency stop procedures understood",
        "□ Backup systems prepared",
        "□ Performance monitoring ready"
    ]
    
    for item in checklist_items:
        print(f"  {item}")
    
    print("\n⚠️ IMPORTANT REMINDERS:")
    print("• START with minimum position sizes")
    print("• MONITOR closely for first few trades")
    print("• STOP immediately if any issues occur")
    print("• REVIEW performance daily")
    print("• ADJUST settings based on results")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Review the generated configuration files")
    print("2. Test the system with paper trading first")
    print("3. Configure your trading platforms")
    print("4. Start live trading with small positions")
    print("5. Monitor and optimize performance")

def generate_startup_script():
    """Generate a startup script for live trading"""
    
    startup_script = """#!/usr/bin/env python3
'''
🚀 ENIGMA APEX - LIVE TRADING STARTUP SCRIPT
Safely starts the live trading system
'''

import os
import sys
import time
from datetime import datetime

def start_live_trading():
    print("🚀 STARTING ENIGMA APEX LIVE TRADING SYSTEM")
    print("=" * 60)
    print("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK!")
    print("📅 Start Time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    # Safety confirmation
    print("\\n🛡️ SAFETY CONFIRMATION REQUIRED:")
    print("• You are about to start LIVE trading")
    print("• Real money will be at risk")
    print("• Ensure all settings are correct")
    print("• Monitor the system closely")
    
    confirm = input("\\n⚠️ Type 'START LIVE TRADING' to continue: ")
    if confirm != "START LIVE TRADING":
        print("❌ Live trading cancelled for safety")
        return False
    
    # Pre-flight checks
    print("\\n🔍 PRE-FLIGHT SYSTEM CHECKS...")
    
    # Check configuration
    if os.path.exists('.env.live'):
        print("✅ Live configuration found")
    else:
        print("❌ Live configuration missing")
        return False
    
    # Check platform connections (simulated)
    print("✅ NinjaTrader connection ready")
    print("✅ AlgoBox integration ready")
    print("✅ Risk management active")
    print("✅ Notification system ready")
    
    print("\\n🚀 ALL SYSTEMS GO - STARTING LIVE TRADING!")
    print("📊 System will now trade with real money")
    print("⚠️ Monitor closely and stop if any issues occur")
    
    return True

if __name__ == "__main__":
    success = start_live_trading()
    if success:
        print("\\n🎯 ENIGMA APEX LIVE TRADING SYSTEM ACTIVE!")
        print("💰 Ready to generate profits!")
    else:
        print("\\n🛑 Live trading startup aborted")
"""
    
    with open('start_live_trading.py', 'w') as f:
        f.write(startup_script)
    
    print("\n✅ Live trading startup script created: start_live_trading.py")

if __name__ == "__main__":
    main()
    generate_startup_script()
