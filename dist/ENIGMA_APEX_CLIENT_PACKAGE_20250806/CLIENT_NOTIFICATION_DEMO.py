"""
Enigma Apex Notification Demo for Client Presentations
Quick demo to show Windows notifications in action
"""

import asyncio
import sys
import os

# Add system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'system'))

from system.desktop_notifier import DesktopNotifier

async def demo_enigma_notifications():
    """Demonstrate Enigma Apex notifications for clients"""
    
    print("🎯 ENIGMA APEX DEMO")
    print("=" * 50)
    print("This will show your client the notification system in action...")
    print("Watch for Windows toast notifications in the bottom-right corner!")
    print()
    
    notifier = DesktopNotifier()
    
    # Demo 1: Strong Buy Signal
    print("📡 Demo 1: Strong Buy Signal...")
    signal_data = {
        'symbol': 'ES',
        'type': 'Strong Buy Signal',
        'power_score': 92,
        'direction': 'LONG',
        'confluence_level': 'L3',
        'signal_color': 'STRONG GREEN'
    }
    await notifier.send_signal_notification(signal_data)
    await asyncio.sleep(3)
    
    # Demo 2: Trade Entry
    print("💼 Demo 2: Automated Trade Entry...")
    trade_data = {
        'symbol': 'NQ',
        'action': 'BUY',
        'price': '16,275.50',
        'quantity': '3 contracts'
    }
    await notifier.send_trade_notification(trade_data, 'entry')
    await asyncio.sleep(3)
    
    # Demo 3: Profitable Exit
    print("💰 Demo 3: Profitable Trade Exit...")
    exit_data = {
        'symbol': 'NQ',
        'action': 'SELL',
        'price': '16,295.25',
        'pnl': '+$1,487.50'
    }
    await notifier.send_trade_notification(exit_data, 'exit')
    await asyncio.sleep(3)
    
    # Demo 4: Risk Management Alert
    print("⚠️ Demo 4: Risk Management Alert...")
    risk_data = {
        'risk_level': '18',
        'account_risk': '15',
        'max_risk': '20'
    }
    await notifier.send_risk_notification(risk_data, 'medium')
    await asyncio.sleep(2)
    
    # Show final stats
    stats = notifier.get_notification_stats()
    print(f"\n✅ Demo Complete!")
    print(f"📊 Total notifications sent: {stats['total_notifications']}")
    print(f"🎯 Your client just saw live Enigma Apex notifications!")
    print(f"💡 These notifications appear automatically during live trading")

def main():
    """Main demo function"""
    try:
        print("Starting Enigma Apex notification demo...")
        print("Press Ctrl+C to stop\n")
        
        asyncio.run(demo_enigma_notifications())
        
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    main()
