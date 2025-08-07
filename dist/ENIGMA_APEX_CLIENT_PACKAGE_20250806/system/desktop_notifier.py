"""
Desktop Notification System for Enigma Apex
Windows notification integration using wintoast and pygame
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os
import sys

# Windows notification support
try:
    import winsound
    WINDOWS_SOUND_AVAILABLE = True
except ImportError:
    WINDOWS_SOUND_AVAILABLE = False

# Try to import Windows toast notifications
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

class DesktopNotifier:
    """
    Desktop notification system for Enigma Apex
    Provides Windows notifications for trading signals and alerts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Notification statistics
        self.stats = {
            'total_notifications': 0,
            'signal_notifications': 0,
            'trade_notifications': 0,
            'risk_notifications': 0,
            'last_notification': None,
            'failed_notifications': 0
        }
        
        # Notification settings
        self.settings = {
            'enabled': True,
            'sound_enabled': True,
            'duration': 10,  # seconds
            'position': 'top-right'
        }
        
        self.logger.info("Desktop Notifier initialized")
    
    async def send_signal_notification(self, signal_data: Dict[str, Any]) -> bool:
        """Send notification for Enigma trading signal"""
        try:
            if not self.settings['enabled']:
                return False
            
            # Extract signal information
            symbol = signal_data.get('symbol', 'Unknown')
            signal_type = signal_data.get('type', 'Signal')
            power_score = signal_data.get('power_score', 0)
            direction = signal_data.get('direction', 'Unknown')
            confluence_level = signal_data.get('confluence_level', 'L1')
            signal_color = signal_data.get('signal_color', 'NEUTRAL')
            
            # Create notification title and message
            title = f"🎯 Enigma Apex - {signal_type}"
            message = f"Symbol: {symbol}\nPower Score: {power_score}\nDirection: {direction}\nConfluence: {confluence_level}\nSignal: {signal_color}"
            
            # Send notification
            success = await self._send_notification(title, message, 'signal')
            
            if success:
                self.stats['signal_notifications'] += 1
                self.logger.info(f"Signal notification sent for {symbol}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending signal notification: {e}")
            self.stats['failed_notifications'] += 1
            return False
    
    async def send_trade_notification(self, trade_data: Dict[str, Any], alert_type: str) -> bool:
        """Send notification for trade events"""
        try:
            if not self.settings['enabled']:
                return False
            
            symbol = trade_data.get('symbol', 'Unknown')
            action = trade_data.get('action', 'Trade')
            price = trade_data.get('price', 'Unknown')
            quantity = trade_data.get('quantity', 'Unknown')
            
            # Create notification based on alert type
            if alert_type == 'entry':
                title = f"📈 Trade Entry - {symbol}"
                message = f"Action: {action}\nPrice: {price}\nQuantity: {quantity}\nStatus: Executed"
            elif alert_type == 'exit':
                title = f"📉 Trade Exit - {symbol}"
                pnl = trade_data.get('pnl', 'Unknown')
                message = f"Action: {action}\nPrice: {price}\nP&L: {pnl}\nStatus: Closed"
            else:
                title = f"💼 Trade Update - {symbol}"
                message = f"Action: {action}\nPrice: {price}\nType: {alert_type}"
            
            success = await self._send_notification(title, message, 'trade')
            
            if success:
                self.stats['trade_notifications'] += 1
                self.logger.info(f"Trade notification sent for {symbol} - {alert_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending trade notification: {e}")
            self.stats['failed_notifications'] += 1
            return False
    
    async def send_risk_notification(self, risk_data: Dict[str, Any], severity: str) -> bool:
        """Send notification for risk alerts"""
        try:
            if not self.settings['enabled']:
                return False
            
            risk_level = risk_data.get('risk_level', 'Unknown')
            account_risk = risk_data.get('account_risk', 'Unknown')
            max_risk = risk_data.get('max_risk', 'Unknown')
            
            # Create notification based on severity
            if severity == 'high':
                title = "🚨 HIGH RISK ALERT"
                message = f"Risk Level: {risk_level}%\nAccount Risk: {account_risk}%\nMax Allowed: {max_risk}%\nACTION REQUIRED!"
            elif severity == 'medium':
                title = "⚠️ RISK WARNING"
                message = f"Risk Level: {risk_level}%\nAccount Risk: {account_risk}%\nMax Allowed: {max_risk}%\nMonitor closely"
            else:
                title = "ℹ️ Risk Update"
                message = f"Risk Level: {risk_level}%\nAccount Risk: {account_risk}%\nStatus: Normal"
            
            success = await self._send_notification(title, message, 'risk')
            
            if success:
                self.stats['risk_notifications'] += 1
                self.logger.info(f"Risk notification sent - {severity} severity")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending risk notification: {e}")
            self.stats['failed_notifications'] += 1
            return False
    
    async def _send_notification(self, title: str, message: str, notification_type: str) -> bool:
        """Send the actual notification using available system"""
        try:
            # Update statistics
            self.stats['total_notifications'] += 1
            self.stats['last_notification'] = datetime.now().isoformat()
            
            # Try plyer first (best cross-platform support)
            if PLYER_AVAILABLE:
                try:
                    notification.notify(
                        title=title,
                        message=message,
                        app_name="Enigma Apex",
                        timeout=self.settings['duration']
                    )
                    
                    # Play sound if enabled
                    if self.settings['sound_enabled'] and WINDOWS_SOUND_AVAILABLE:
                        winsound.MessageBeep(winsound.MB_OK)
                    
                    self.logger.info(f"Notification sent via plyer: {title}")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"Plyer notification failed: {e}")
            
            # Fallback to Windows msg command
            try:
                # Use Windows msg command as fallback
                import subprocess
                
                # Combine title and message for msg command
                full_message = f"{title}\n\n{message}"
                
                # Send message to current user session
                result = subprocess.run([
                    'msg', '*', full_message
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    self.logger.info(f"Notification sent via msg command: {title}")
                    return True
                else:
                    self.logger.warning(f"msg command failed: {result.stderr}")
                    
            except Exception as e:
                self.logger.warning(f"msg command notification failed: {e}")
            
            # Final fallback - console notification
            print(f"\n🔔 ENIGMA APEX NOTIFICATION 🔔")
            print(f"Title: {title}")
            print(f"Message: {message}")
            print(f"Type: {notification_type}")
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 50)
            
            self.logger.info(f"Notification displayed in console: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"All notification methods failed: {e}")
            self.stats['failed_notifications'] += 1
            return False
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        return {
            **self.stats,
            'settings': self.settings,
            'plyer_available': PLYER_AVAILABLE,
            'windows_sound_available': WINDOWS_SOUND_AVAILABLE
        }
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update notification settings"""
        self.settings.update(new_settings)
        self.logger.info(f"Notification settings updated: {new_settings}")
    
    async def test_notification(self) -> bool:
        """Test notification system"""
        test_data = {
            'symbol': 'ES',
            'type': 'Test Signal',
            'power_score': 85,
            'direction': 'LONG',
            'confluence_level': 'L3',
            'signal_color': 'GREEN'
        }
        
        return await self.send_signal_notification(test_data)

# Test function for standalone execution
async def test_desktop_notifier():
    """Test the desktop notifier system"""
    print("🧪 Testing Desktop Notifier...")
    
    notifier = DesktopNotifier()
    
    # Test signal notification
    print("📡 Testing signal notification...")
    signal_success = await notifier.test_notification()
    print(f"Signal notification: {'✅ Success' if signal_success else '❌ Failed'}")
    
    # Test trade notification
    print("💼 Testing trade notification...")
    trade_data = {
        'symbol': 'NQ',
        'action': 'BUY',
        'price': '16250.00',
        'quantity': '2',
        'pnl': '+$450.00'
    }
    trade_success = await notifier.send_trade_notification(trade_data, 'entry')
    print(f"Trade notification: {'✅ Success' if trade_success else '❌ Failed'}")
    
    # Test risk notification
    print("⚠️ Testing risk notification...")
    risk_data = {
        'risk_level': '15',
        'account_risk': '12',
        'max_risk': '20'
    }
    risk_success = await notifier.send_risk_notification(risk_data, 'medium')
    print(f"Risk notification: {'✅ Success' if risk_success else '❌ Failed'}")
    
    # Show statistics
    stats = notifier.get_notification_stats()
    print(f"\n📊 Notification Statistics:")
    print(f"Total notifications: {stats['total_notifications']}")
    print(f"Signal notifications: {stats['signal_notifications']}")
    print(f"Trade notifications: {stats['trade_notifications']}")
    print(f"Risk notifications: {stats['risk_notifications']}")
    print(f"Failed notifications: {stats['failed_notifications']}")
    
    return signal_success and trade_success and risk_success

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎯 Enigma Apex Desktop Notifier Test")
    print("=" * 50)
    
    try:
        result = asyncio.run(test_desktop_notifier())
        print(f"\n🎉 Test Result: {'All notifications working!' if result else 'Some notifications failed'}")
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"💥 Test error: {e}")
        import traceback
        traceback.print_exc()
