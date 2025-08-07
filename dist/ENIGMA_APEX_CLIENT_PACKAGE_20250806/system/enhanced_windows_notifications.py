#!/usr/bin/env python3
"""
🔔 ENHANCED WINDOWS 10 NOTIFICATION SYSTEM
Professional notification system using Windows 10 native notifications and pygame audio
"""

import pygame
import asyncio
import json
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sys
import os

# Windows-specific imports
try:
    from win10toast import ToastNotifier
    from plyer import notification
    import winsound
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("⚠️ Windows-specific libraries not available")

class EnhancedWindowsNotificationSystem:
    """Advanced notification system using Windows 10 native features and pygame"""
    
    def __init__(self):
        self.pygame_initialized = False
        self.notification_settings = {
            'windows_toast': True,
            'pygame_audio': True,
            'system_sound': True,
            'visual_flash': True,
            'console_output': True
        }
        
        # Initialize pygame mixer for audio
        self.init_pygame_audio()
        
        # Initialize Windows 10 toast notifier
        if WINDOWS_AVAILABLE:
            self.toast_notifier = ToastNotifier()
        
        # Create notification history
        self.notification_history = []
        
        # Sound frequency mappings for different alert types
        self.sound_frequencies = {
            'CRITICAL': 800,    # High frequency for critical alerts
            'HIGH': 600,        # Medium-high for high priority
            'MEDIUM': 500,      # Medium frequency
            'LOW': 400,         # Lower frequency for info
            'SUCCESS': 350,     # Lower tone for success
            'ERROR': 900,       # Very high for errors
            'WARNING': 650      # High for warnings
        }
        
        # Create custom sound directory
        self.create_custom_sounds()
    
    def init_pygame_audio(self):
        """Initialize pygame mixer for better audio control"""
        try:
            pygame.mixer.init(
                frequency=22050,    # Sample rate
                size=-16,          # 16-bit signed samples
                channels=2,        # Stereo
                buffer=512         # Small buffer for low latency
            )
            self.pygame_initialized = True
            print("✅ Pygame audio initialized successfully")
        except Exception as e:
            print(f"⚠️ Pygame audio initialization failed: {e}")
            self.pygame_initialized = False
    
    def create_custom_sounds(self):
        """Create custom notification sounds using pygame"""
        if not self.pygame_initialized:
            return
            
        self.custom_sounds = {}
        
        try:
            # Create different sound types
            sound_types = {
                'error': [800, 850, 900],      # Rising alarm
                'warning': [600, 650, 600],    # Alert pattern
                'success': [400, 450, 500],    # Success chime
                'info': [500, 500, 500],       # Neutral beep
                'critical': [900, 800, 900, 800, 900]  # Urgent alarm
            }
            
            for sound_type, frequencies in sound_types.items():
                self.custom_sounds[sound_type] = frequencies
                
        except Exception as e:
            print(f"⚠️ Custom sound creation failed: {e}")
    
    def play_pygame_sound(self, alert_type: str, duration: float = 0.3):
        """Play custom sound using pygame"""
        if not self.pygame_initialized or not self.notification_settings['pygame_audio']:
            return
            
        try:
            sound_type = alert_type.lower()
            frequencies = self.custom_sounds.get(sound_type, [500])
            
            # Create and play sound in a separate thread to avoid blocking
            threading.Thread(
                target=self._generate_pygame_tone,
                args=(frequencies, duration),
                daemon=True
            ).start()
            
        except Exception as e:
            print(f"⚠️ Pygame sound playback failed: {e}")
    
    def _generate_pygame_tone(self, frequencies: List[int], duration: float):
        """Generate tone using pygame (runs in separate thread)"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate / len(frequencies))
            
            for freq in frequencies:
                # Generate sine wave using numpy
                import numpy as np
                
                # Create time array
                t = np.linspace(0, duration / len(frequencies), frames)
                
                # Generate sine wave
                wave = np.sin(2 * np.pi * freq * t) * 0.3  # 30% volume
                
                # Convert to 16-bit integers
                wave_int = (wave * 32767).astype(np.int16)
                
                # Create stereo array
                stereo_wave = np.array([wave_int, wave_int]).T
                
                # Create and play sound
                sound = pygame.sndarray.make_sound(stereo_wave)
                sound.play()
                pygame.time.wait(int(duration * 1000 / len(frequencies)))  # Wait in milliseconds
                
        except Exception as e:
            print(f"⚠️ Tone generation failed: {e}")
            # Fallback to simple beep
            try:
                import os
                if os.name == 'nt':  # Windows
                    import winsound
                    winsound.Beep(frequencies[0] if frequencies else 800, int(duration * 1000))
            except:
                pass
    
    def show_windows_toast(self, title: str, message: str, alert_type: str, duration: int = 5):
        """Show Windows 10 native toast notification"""
        if not WINDOWS_AVAILABLE or not self.notification_settings['windows_toast']:
            return
            
        try:
            # Choose icon based on alert type
            icon_path = None  # Use default system icon
            
            # For custom icons, you could add:
            # if alert_type == 'ERROR':
            #     icon_path = "error_icon.ico"
            
            # Show toast notification
            self.toast_notifier.show_toast(
                title=title,
                msg=message,
                icon_path=icon_path,
                duration=duration,
                threaded=True  # Non-blocking
            )
            
            print(f"✅ Windows toast notification sent: {title}")
            
        except Exception as e:
            print(f"⚠️ Windows toast notification failed: {e}")
    
    def play_system_sound(self, alert_type: str):
        """Play Windows system sound"""
        if not WINDOWS_AVAILABLE or not self.notification_settings['system_sound']:
            return
            
        try:
            import winsound
            
            # Map alert types to Windows system sounds
            sound_map = {
                'ERROR': winsound.SND_ALIAS,
                'CRITICAL': winsound.SND_ALIAS,
                'WARNING': winsound.SND_ALIAS,
                'SUCCESS': winsound.SND_ALIAS,
                'INFO': winsound.SND_ALIAS,
                'HIGH': winsound.SND_ALIAS,
                'MEDIUM': winsound.SND_ALIAS,
                'LOW': winsound.SND_ALIAS
            }
            
            # Play different system sounds based on type
            if alert_type in ['ERROR', 'CRITICAL']:
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
            elif alert_type == 'WARNING':
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
            elif alert_type == 'SUCCESS':
                winsound.PlaySound("SystemDefault", winsound.SND_ALIAS | winsound.SND_ASYNC)
            else:
                winsound.PlaySound("SystemDefault", winsound.SND_ALIAS | winsound.SND_ASYNC)
            
        except Exception as e:
            print(f"⚠️ System sound failed: {e}")
    
    def show_plyer_notification(self, title: str, message: str, timeout: int = 5):
        """Show cross-platform notification using plyer"""
        if not self.notification_settings['windows_toast']:
            return
            
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Enigma Apex",
                timeout=timeout,
                app_icon=None  # Use default icon
            )
            
        except Exception as e:
            print(f"⚠️ Plyer notification failed: {e}")
    
    def flash_screen(self, alert_type: str):
        """Flash screen for critical alerts (Windows specific)"""
        if not WINDOWS_AVAILABLE or not self.notification_settings['visual_flash']:
            return
            
        try:
            if alert_type in ['ERROR', 'CRITICAL']:
                # Flash screen for critical alerts
                import ctypes
                from ctypes import wintypes
                
                # Flash window info structure
                class FLASHWINFO(ctypes.Structure):
                    _fields_ = [
                        ('cbSize', wintypes.UINT),
                        ('hwnd', wintypes.HWND),
                        ('dwFlags', wintypes.DWORD),
                        ('uCount', wintypes.UINT),
                        ('dwTimeout', wintypes.DWORD)
                    ]
                
                # Get console window handle
                hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                
                if hwnd != 0:
                    # Flash window
                    flash_info = FLASHWINFO()
                    flash_info.cbSize = ctypes.sizeof(FLASHWINFO)
                    flash_info.hwnd = hwnd
                    flash_info.dwFlags = 0x0000000C  # FLASHW_ALL | FLASHW_TIMERNOFG
                    flash_info.uCount = 3  # Flash 3 times
                    flash_info.dwTimeout = 0  # Use default cursor blink rate
                    
                    ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))
                    
        except Exception as e:
            print(f"⚠️ Screen flash failed: {e}")
    
    def send_enhanced_notification(self, title: str, message: str, alert_type: str, priority: str = "MEDIUM"):
        """Send notification through all enabled channels"""
        
        notification_data = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'alert_type': alert_type,
            'priority': priority
        }
        
        # Add to history
        self.notification_history.append(notification_data)
        
        # Keep only last 100 notifications
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]
        
        try:
            # Console output
            if self.notification_settings['console_output']:
                self.print_console_notification(notification_data)
            
            # Windows 10 toast notification
            if WINDOWS_AVAILABLE and self.notification_settings['windows_toast']:
                self.show_windows_toast(title, message, alert_type)
                
                # Also try plyer as backup
                self.show_plyer_notification(title, message)
            
            # Pygame audio notification
            if self.pygame_initialized and self.notification_settings['pygame_audio']:
                self.play_pygame_sound(alert_type)
            
            # System sound as backup
            if WINDOWS_AVAILABLE and self.notification_settings['system_sound']:
                self.play_system_sound(alert_type)
            
            # Visual flash for critical alerts
            if priority == 'CRITICAL' or alert_type == 'ERROR':
                self.flash_screen(alert_type)
            
            print(f"✅ Enhanced notification sent: {title}")
            
        except Exception as e:
            print(f"❌ Enhanced notification failed: {e}")
            # Fallback to basic console output
            print(f"📢 ALERT: {title} - {message}")
    
    def print_console_notification(self, notification_data: Dict):
        """Print formatted notification to console with colors"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        title = notification_data['title']
        message = notification_data['message']
        alert_type = notification_data['alert_type']
        priority = notification_data['priority']
        
        # ANSI color codes for console output
        colors = {
            'CRITICAL': '\033[91m\033[1m',  # Bright red + bold
            'ERROR': '\033[91m',            # Red
            'WARNING': '\033[93m',          # Yellow
            'SUCCESS': '\033[92m',          # Green
            'INFO': '\033[94m',             # Blue
            'HIGH': '\033[95m',             # Magenta
            'MEDIUM': '\033[96m',           # Cyan
            'LOW': '\033[97m'               # White
        }
        reset = '\033[0m'
        
        color = colors.get(priority, colors.get(alert_type, ''))
        
        # Enhanced console output with borders
        border = "=" * 60
        print(f"\n{color}{border}{reset}")
        print(f"{color}🔔 [{timestamp}] {title}{reset}")
        print(f"{color}📝 {message}{reset}")
        print(f"{color}🏷️  Type: {alert_type} | Priority: {priority}{reset}")
        print(f"{color}{border}{reset}\n")
    
    def test_all_notifications(self):
        """Test all notification types"""
        
        test_notifications = [
            ("🔊 Audio Test", "Testing pygame audio notification", "INFO", "MEDIUM"),
            ("⚠️ Warning Test", "Testing warning notification", "WARNING", "HIGH"),
            ("🚨 Error Test", "Testing error notification", "ERROR", "CRITICAL"),
            ("✅ Success Test", "Testing success notification", "SUCCESS", "LOW"),
            ("🔔 System Test", "Testing all notification channels", "INFO", "HIGH")
        ]
        
        print("🧪 Testing Enhanced Notification System...")
        
        for title, message, alert_type, priority in test_notifications:
            self.send_enhanced_notification(title, message, alert_type, priority)
            time.sleep(2)  # Wait between notifications
        
        print("✅ Notification system test completed!")
    
    def get_notification_stats(self) -> Dict:
        """Get notification statistics"""
        
        if not self.notification_history:
            return {"total": 0, "by_type": {}, "by_priority": {}}
        
        stats = {
            "total": len(self.notification_history),
            "by_type": {},
            "by_priority": {},
            "last_24_hours": 0
        }
        
        # Count by type and priority
        for notif in self.notification_history:
            alert_type = notif['alert_type']
            priority = notif['priority']
            
            stats['by_type'][alert_type] = stats['by_type'].get(alert_type, 0) + 1
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Count last 24 hours
            notif_time = datetime.fromisoformat(notif['timestamp'])
            if (datetime.now() - notif_time).total_seconds() < 86400:
                stats['last_24_hours'] += 1
        
        return stats
    
    def cleanup(self):
        """Cleanup resources"""
        
        if self.pygame_initialized:
            try:
                pygame.mixer.quit()
                print("✅ Pygame audio cleaned up")
            except:
                pass

def main():
    """Test the enhanced notification system"""
    
    print("🚀 Starting Enhanced Windows 10 Notification System Test")
    
    # Create notification system
    notifier = EnhancedWindowsNotificationSystem()
    
    try:
        # Test all notification types
        notifier.test_all_notifications()
        
        # Show statistics
        stats = notifier.get_notification_stats()
        print(f"\n📊 Notification Statistics:")
        print(f"Total notifications: {stats['total']}")
        print(f"By type: {stats['by_type']}")
        print(f"By priority: {stats['by_priority']}")
        
        print("\n✅ Enhanced notification system is ready for production!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        notifier.cleanup()

if __name__ == "__main__":
    main()
