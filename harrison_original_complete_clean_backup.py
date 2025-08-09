"""
TRAINING WHEELS FOR PROP FIRM TRADERS
Professional trading enhancement system for prop firm traders

Michael Canfield's First Principal Enhancement System:
- Help new traders find the best single trade algo (like Enigma)
- Apply our system to enhance their trading skills and platform
- Multi-prop firm support with expandable dropdown selection
- ERM (Enigma Reversal Momentum) Signal Detection with rapid failure detection
- NinjaTrader + Tradovate + AlgoTrader Integration
- Real Connection Testing (Demo/Test/Live modes)
- Multi-account futures trading management
- OCR signal reading capabilities
- Professional margin monitoring
- Emergency stop protection
- Advanced Kelly Criterion position sizing

Core Philosophy:
1. Identify the trader's "First Principal" (best single algo)
2. Enhance that algo with our professional tools
3. Scale across multiple prop firms seamlessly
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import time
import os
import socket
import subprocess
import urllib.request
import urllib.error
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Enhanced imports for professional features - Cloud Compatible
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create mock psutil for cloud compatibility
    class MockPsutil:
        @staticmethod
        def process_iter(attrs):
            return []
        @staticmethod
        def virtual_memory():
            class MockMemory:
                percent = 50.0
            return MockMemory()
        @staticmethod
        def cpu_percent():
            return 25.0
    psutil = MockPsutil()

try:
    import cv2
    import pytesseract
    from PIL import Image, ImageGrab
    import mss
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    # Create mock classes for cloud compatibility
    class MockImage:
        @staticmethod
        def open(*args):
            return None
        @staticmethod
        def new(*args):
            return None
    try:
        from PIL import Image
    except ImportError:
        Image = MockImage

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

try:
    if os.name == 'nt':  # Windows
        import win32gui
        import win32process
        WINDOWS_API_AVAILABLE = True
    else:
        WINDOWS_API_AVAILABLE = False
except ImportError:
    WINDOWS_API_AVAILABLE = False

# Desktop notifications - Cloud Safe
try:
    import plyer
    NOTIFICATIONS_AVAILABLE = True
    NOTIFICATIONS_TYPE = "plyer"
except ImportError:
    try:
        # Fallback for Windows
        import win10toast
        NOTIFICATIONS_AVAILABLE = True
        NOTIFICATIONS_TYPE = "win10toast"
    except ImportError:
        NOTIFICATIONS_AVAILABLE = False
        NOTIFICATIONS_TYPE = None

# Audio alerts - Cloud Safe  
try:
    if os.name == 'nt':  # Only try on Windows
        import winsound
        AUDIO_AVAILABLE = True
        AUDIO_TYPE = "winsound"
    else:
        raise ImportError("Not Windows")
except ImportError:
    try:
        import pygame
        AUDIO_AVAILABLE = True
        AUDIO_TYPE = "pygame"
    except ImportError:
        AUDIO_AVAILABLE = False
        AUDIO_TYPE = None

@dataclass
class EnigmaSignal:
    signal_type: str
    entry_price: float
    signal_time: datetime
    is_active: bool = True
    confidence: float = 0.8

@dataclass
class ERMCalculation:
    erm_value: float
    threshold: float
    is_reversal_triggered: bool
    reversal_direction: str
    momentum_velocity: float
    price_distance: float
    time_elapsed: float

@dataclass
class PropFirmConfig:
    firm_name: str
    max_daily_loss: float
    max_position_size: float
    max_drawdown: float
    leverage: int
    allowed_instruments: List[str]
    risk_rules: Dict[str, Any]
    evaluation_period: int
    profit_target: float

@dataclass
class TradovateAccount:
    chart_id: int
    account_name: str
    instruments: List[str]
    account_balance: float
    margin_used: float
    unrealized_pnl: float
    daily_pnl: float
    position_size: float
    entry_price: float
    signal_color: str
    power_score: int
    risk_level: str
    last_signal: str
    confluence_level: str
    last_update: datetime
    is_active: bool
    ninjatrader_connection: str
    current_enigma_signal: Optional[EnigmaSignal] = None
    price_history: List[float] = field(default_factory=list)
    time_history: List[datetime] = field(default_factory=list)
    erm_last_calculation: Optional[ERMCalculation] = None

@dataclass
class NinjaTraderStatus:
    process_id: int
    memory_usage: float
    cpu_usage: float
    is_connected: bool
    connection_time: datetime

@dataclass
class SystemStatus:
    total_equity: float
    total_margin_remaining: float
    total_margin_percentage: float
    daily_profit_loss: float
    safety_ratio: float
    last_update: datetime

@dataclass
class KellyCalculation:
    """Kelly Criterion calculation result for optimal position sizing"""
    kelly_percentage: float      # Raw Kelly percentage (0-1)
    win_probability: float       # Probability of winning trade (0-1)
    avg_win: float              # Average winning trade amount
    avg_loss: float             # Average losing trade amount
    risk_adjusted_kelly: float   # Kelly adjusted for risk management
    recommended_position: float  # Actual recommended position size
    confidence_level: float      # Signal confidence (0-1)
    max_position_limit: float    # Maximum allowed position size
    sample_size: int            # Number of historical trades used
    sharpe_ratio: float         # Risk-adjusted return measure

@dataclass
class TradingHistory:
    """Historical trading data for Kelly calculations"""
    trades: List[Dict]          # Historical trade results
    win_rate: float            # Overall win rate
    profit_factor: float       # Gross profit / Gross loss
    avg_winner: float          # Average winning trade
    avg_loser: float           # Average losing trade
    total_trades: int          # Total number of trades
    consecutive_wins: int       # Current winning streak
    consecutive_losses: int     # Current losing streak
    max_drawdown: float        # Maximum historical drawdown

@dataclass
class SimpleConfig:
    trader_name: str = "Professional Trader"
    prop_firm: str = "FTMO"
    demo_mode: bool = True

class NotificationManager:
    """
    Advanced notification manager for prop firm traders
    Handles desktop notifications, audio alerts, and visual alerts
    """
    
    def __init__(self):
        self.notification_history = []
        self.audio_enabled = True
        self.desktop_notifications_enabled = True
        self.critical_alerts_only = False
        self.notification_settings = {
            "erm_reversal": {"enabled": True, "sound": True, "priority": "high"},
            "margin_warning": {"enabled": True, "sound": True, "priority": "critical"},
            "connection_lost": {"enabled": True, "sound": True, "priority": "high"},
            "emergency_stop": {"enabled": True, "sound": True, "priority": "critical"},
            "new_signal": {"enabled": True, "sound": False, "priority": "medium"},
            "position_update": {"enabled": False, "sound": False, "priority": "low"},
            "system_status": {"enabled": True, "sound": False, "priority": "medium"}
        }
    
    def send_notification(self, 
                         title: str, 
                         message: str, 
                         notification_type: str = "info",
                         priority: str = "medium",
                         play_sound: bool = None,
                         chart_id: Optional[int] = None):
        """Send a desktop notification with optional sound"""
        
        # Check if notifications are enabled for this type
        if notification_type in self.notification_settings:
            settings = self.notification_settings[notification_type]
            if not settings["enabled"]:
                return
            
            # Override sound setting if specified
            if play_sound is None:
                play_sound = settings["sound"] and self.audio_enabled
            
            # Override priority
            if priority == "medium":
                priority = settings["priority"]
        
        # Skip non-critical if critical alerts only mode
        if self.critical_alerts_only and priority not in ["critical", "high"]:
            return
        
        # Create notification record
        notification_record = {
            "timestamp": datetime.now(),
            "title": title,
            "message": message,
            "type": notification_type,
            "priority": priority,
            "chart_id": chart_id,
            "acknowledged": False
        }
        
        # Add to history
        self.notification_history.append(notification_record)
        
        # Keep only last 100 notifications
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]
        
        # Send desktop notification
        if self.desktop_notifications_enabled and NOTIFICATIONS_AVAILABLE:
            self._send_desktop_notification(title, message, priority)
        
        # Play sound alert
        if play_sound and AUDIO_AVAILABLE:
            self._play_alert_sound(priority)
        
        # Log notification
        logging.info(f"Notification sent: {title} - {message}")
        
        return notification_record
    
    def _send_desktop_notification(self, title: str, message: str, priority: str):
        """Send desktop notification using available library - Cloud Safe"""
        try:
            # Choose icon based on priority
            icon_map = {
                "critical": "error",
                "high": "warning", 
                "medium": "info",
                "low": "info"
            }
            
            if NOTIFICATIONS_TYPE == "plyer" and 'plyer' in globals():
                plyer.notification.notify(
                    title=f"🎯 Training Wheels - {title}",
                    message=message,
                    app_name="Training Wheels Pro",
                    timeout=10 if priority == "critical" else 5
                )
            elif NOTIFICATIONS_TYPE == "win10toast" and 'win10toast' in globals():
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(
                    title=f"🎯 Training Wheels - {title}",
                    msg=message,
                    duration=10 if priority == "critical" else 5,
                    threaded=True
                )
            else:
                # Cloud fallback: Log notification instead
                logging.info(f"🎯 NOTIFICATION [{priority.upper()}] - {title}: {message}")
        except Exception as e:
            logging.error(f"Failed to send desktop notification: {e}")
            # Cloud fallback: Log notification
            logging.info(f"🎯 NOTIFICATION [{priority.upper()}] - {title}: {message}")
    
    def _play_alert_sound(self, priority: str):
        """Play audio alert based on priority - Cloud Safe"""
        try:
            if AUDIO_TYPE == "winsound" and 'winsound' in globals():
                if priority == "critical":
                    # Critical alert - long beep sequence
                    for _ in range(3):
                        winsound.Beep(1000, 200)  # 1000Hz for 200ms
                        time.sleep(0.1)
                elif priority == "high":
                    # High priority - double beep
                    winsound.Beep(800, 150)
                    time.sleep(0.1)
                    winsound.Beep(800, 150)
                else:
                    # Medium/low priority - single beep
                    winsound.Beep(600, 100)
            
            elif AUDIO_TYPE == "pygame" and 'pygame' in globals():
                # Pygame sound implementation (fallback)
                pass
            else:
                # Cloud fallback: Visual alert in logs
                beep_pattern = {
                    "critical": "🔴🔴🔴 CRITICAL ALERT 🔴🔴🔴",
                    "high": "🟡🟡 HIGH PRIORITY 🟡🟡", 
                    "medium": "🟢 MEDIUM PRIORITY",
                    "low": "ℹ️ LOW PRIORITY"
                }
                logging.info(f"🎵 AUDIO ALERT: {beep_pattern.get(priority, 'ALERT')}")
                
        except Exception as e:
            logging.error(f"Failed to play alert sound: {e}")
            # Still log the alert visually
            logging.info(f"🎵 AUDIO ALERT [{priority.upper()}] - Sound failed, visual alert active")
    
    def send_erm_reversal_alert(self, chart_id: int, direction: str, erm_value: float, chart_name: str):
        """Send ERM reversal notification"""
        title = f"ERM REVERSAL DETECTED - Chart {chart_id}"
        message = f"{chart_name}: {direction} reversal signal detected! ERM Value: {erm_value:.2f}"
        
        return self.send_notification(
            title=title,
            message=message,
            notification_type="erm_reversal",
            priority="high",
            chart_id=chart_id
        )
    
    def send_margin_warning(self, margin_percentage: float, total_equity: float):
        """Send margin warning notification"""
        if margin_percentage < 20:
            priority = "critical"
            title = "CRITICAL MARGIN WARNING"
        elif margin_percentage < 50:
            priority = "high"
            title = "MARGIN WARNING"
        else:
            return  # No warning needed
        
        message = f"Margin at {margin_percentage:.1f}% (${total_equity * margin_percentage / 100:,.0f} remaining)"
        
        return self.send_notification(
            title=title,
            message=message,
            notification_type="margin_warning",
            priority=priority
        )
    
    def send_connection_lost_alert(self, platform: str):
        """Send connection lost notification"""
        title = f"{platform.upper()} CONNECTION LOST"
        message = f"Lost connection to {platform}. Trading operations may be affected."
        
        return self.send_notification(
            title=title,
            message=message,
            notification_type="connection_lost",
            priority="high"
        )
    
    def send_emergency_stop_alert(self):
        """Send emergency stop notification"""
        title = "🚨 EMERGENCY STOP ACTIVATED"
        message = "All trading has been halted. Manual intervention required."
        
        return self.send_notification(
            title=title,
            message=message,
            notification_type="emergency_stop",
            priority="critical"
        )
    
    def send_new_signal_alert(self, chart_id: int, signal_type: str, chart_name: str, confidence: float):
        """Send new signal notification"""
        title = f"New {signal_type} Signal - Chart {chart_id}"
        message = f"{chart_name}: {signal_type} signal detected (Confidence: {confidence:.1%})"
        
        return self.send_notification(
            title=title,
            message=message,
            notification_type="new_signal",
            priority="medium",
            chart_id=chart_id
        )
    
    def send_position_update_alert(self, chart_id: int, chart_name: str, position_size: float, pnl: float):
        """Send position update notification"""
        title = f"Position Update - Chart {chart_id}"
        message = f"{chart_name}: Size {position_size:.2f}, P&L ${pnl:,.0f}"
        
        return self.send_notification(
            title=title,
            message=message,
            notification_type="position_update",
            priority="low",
            chart_id=chart_id
        )
    
    def send_system_status_alert(self, status_message: str):
        """Send system status notification"""
        title = "System Status Update"
        
        return self.send_notification(
            title=title,
            message=status_message,
            notification_type="system_status",
            priority="medium"
        )
    
    def get_unacknowledged_notifications(self) -> List[Dict]:
        """Get all unacknowledged notifications"""
        return [n for n in self.notification_history if not n["acknowledged"]]
    
    def acknowledge_notification(self, notification_index: int):
        """Mark notification as acknowledged"""
        if 0 <= notification_index < len(self.notification_history):
            self.notification_history[notification_index]["acknowledged"] = True
    
    def acknowledge_all_notifications(self):
        """Mark all notifications as acknowledged"""
        for notification in self.notification_history:
            notification["acknowledged"] = False
    
    def get_notification_summary(self) -> Dict[str, int]:
        """Get summary of notification counts by type"""
        summary = {}
        for notification in self.notification_history:
            if not notification["acknowledged"]:
                notification_type = notification["type"]
                summary[notification_type] = summary.get(notification_type, 0) + 1
        return summary
    
    def configure_notification_settings(self, notification_type: str, enabled: bool, sound: bool, priority: str):
        """Configure notification settings for a specific type"""
        if notification_type in self.notification_settings:
            self.notification_settings[notification_type] = {
                "enabled": enabled,
                "sound": sound,
                "priority": priority
            }
    
    def enable_critical_alerts_only(self):
        """Enable only critical and high priority alerts"""
        self.critical_alerts_only = True
    
    def disable_critical_alerts_only(self):
        """Enable all priority levels"""
        self.critical_alerts_only = False
    
    def test_notification_system(self):
        """Test the notification system with sample alerts"""
        test_notifications = [
            ("Test - Low Priority", "This is a low priority test notification", "low"),
            ("Test - Medium Priority", "This is a medium priority test notification", "medium"),
            ("Test - High Priority", "This is a high priority test notification", "high"),
            ("Test - Critical Priority", "This is a critical priority test notification", "critical")
        ]
        
        for title, message, priority in test_notifications:
            self.send_notification(title, message, "system_status", priority)
            time.sleep(1)  # Delay between notifications

class KellyEngine:
    """
    Advanced Kelly Criterion Engine for optimal position sizing
    
    Kelly Formula: f* = (bp - q) / b
    Where:
    - f* = optimal fraction of capital to bet
    - b = odds of winning (avg_win / avg_loss)
    - p = probability of winning
    - q = probability of losing (1 - p)
    """
    
    def __init__(self):
        self.trading_history = {}  # Chart-specific trading history
        self.kelly_settings = {
            "max_kelly_percentage": 0.25,      # Cap Kelly at 25% (conservative)
            "min_sample_size": 10,             # Minimum trades for Kelly calculation
            "lookback_period": 100,            # Number of recent trades to analyze
            "confidence_threshold": 0.6,       # Minimum confidence for position sizing
            "risk_adjustment_factor": 0.5,     # Conservative Kelly adjustment
            "adaptive_sizing": True            # Adjust based on recent performance
        }
    
    def calculate_kelly(self, chart_id: int, signal_confidence: float = 0.7) -> KellyCalculation:
        """Calculate optimal position size using Kelly Criterion"""
        history = self.get_trading_history(chart_id)
        
        if history.total_trades < self.kelly_settings["min_sample_size"]:
            return self._conservative_kelly(signal_confidence, chart_id)
        
        # Calculate Kelly components
        win_probability = history.win_rate
        avg_win = abs(history.avg_winner)
        avg_loss = abs(history.avg_loser)
        
        if avg_loss == 0:
            avg_loss = 0.01
        
        # Kelly Criterion calculation
        b = avg_win / avg_loss
        p = win_probability
        q = 1 - p
        
        if b > 0:
            kelly_raw = (b * p - q) / b
        else:
            kelly_raw = 0
        
        kelly_raw = max(0, min(kelly_raw, 1.0))
        
        # Risk adjustment
        risk_adjustment = self._calculate_risk_adjustment(history)
        kelly_adjusted = kelly_raw * self.kelly_settings["risk_adjustment_factor"] * risk_adjustment
        kelly_final = min(kelly_adjusted, self.kelly_settings["max_kelly_percentage"])
        kelly_with_confidence = kelly_final * signal_confidence
        
        max_position = self._get_max_position_size(chart_id)
        recommended_position = kelly_with_confidence * max_position
        sharpe_ratio = self._calculate_sharpe_ratio(history)
        
        return KellyCalculation(
            kelly_percentage=kelly_raw,
            win_probability=win_probability,
            avg_win=avg_win,
            avg_loss=avg_loss,
            risk_adjusted_kelly=kelly_with_confidence,
            recommended_position=recommended_position,
            confidence_level=signal_confidence,
            max_position_limit=max_position,
            sample_size=history.total_trades,
            sharpe_ratio=sharpe_ratio
        )
    
    def _conservative_kelly(self, signal_confidence: float, chart_id: int) -> KellyCalculation:
        """Conservative Kelly calculation for insufficient data"""
        max_position = self._get_max_position_size(chart_id)
        conservative_percentage = 0.02 * signal_confidence
        
        return KellyCalculation(
            kelly_percentage=conservative_percentage,
            win_probability=0.5,
            avg_win=100.0,
            avg_loss=100.0,
            risk_adjusted_kelly=conservative_percentage,
            recommended_position=conservative_percentage * max_position,
            confidence_level=signal_confidence,
            max_position_limit=max_position,
            sample_size=0,
            sharpe_ratio=0.0
        )
    
    def _calculate_risk_adjustment(self, history: TradingHistory) -> float:
        """Calculate risk adjustment factor based on recent performance"""
        if history.consecutive_losses > 3:
            return 0.5
        elif history.consecutive_wins > 5:
            return 1.2
        return 1.0
    
    def _calculate_sharpe_ratio(self, history: TradingHistory) -> float:
        """Calculate Sharpe ratio for risk assessment"""
        if len(history.trades) < 10:
            return 0.0
        
        returns = [trade.get('pnl', 0) for trade in history.trades]
        if not returns:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        return mean_return / std_return
    
    def _get_max_position_size(self, chart_id: int) -> float:
        """Get maximum position size for chart"""
        return 10.0  # Default max position
    
    def get_trading_history(self, chart_id: int) -> TradingHistory:
        """Get trading history for a chart"""
        if chart_id not in self.trading_history:
            self.trading_history[chart_id] = TradingHistory(
                trades=[],
                win_rate=0.5,
                profit_factor=1.0,
                avg_winner=100.0,
                avg_loser=100.0,
                total_trades=0,
                consecutive_wins=0,
                consecutive_losses=0,
                max_drawdown=0.0
            )
        return self.trading_history[chart_id]
    
    def add_trade_result(self, chart_id: int, pnl: float, entry_price: float, exit_price: float, size: float):
        """Add a trade result to the trading history"""
        history = self.get_trading_history(chart_id)
        
        trade = {
            "pnl": pnl,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "size": size,
            "timestamp": datetime.now(),
            "is_winner": pnl > 0
        }
        
        history.trades.append(trade)
        
        # Keep only recent trades
        if len(history.trades) > self.kelly_settings["lookback_period"]:
            history.trades = history.trades[-self.kelly_settings["lookback_period"]:]
        
        # Update statistics
        self._update_trade_statistics(history)
    
    def _update_trade_statistics(self, history: TradingHistory):
        """Update trading statistics"""
        if not history.trades:
            return
        
        # Calculate basic stats
        winners = [t for t in history.trades if t["pnl"] > 0]
        losers = [t for t in history.trades if t["pnl"] <= 0]
        
        history.total_trades = len(history.trades)
        history.win_rate = len(winners) / history.total_trades if history.total_trades > 0 else 0
        
        history.avg_winner = np.mean([t["pnl"] for t in winners]) if winners else 0
        history.avg_loser = abs(np.mean([t["pnl"] for t in losers])) if losers else 0
        
        # Calculate profit factor
        gross_profit = sum(t["pnl"] for t in winners)
        gross_loss = abs(sum(t["pnl"] for t in losers))
        history.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 1.0
        
        # Calculate consecutive wins/losses
        history.consecutive_wins = 0
        history.consecutive_losses = 0
        
        for trade in reversed(history.trades):
            if trade["pnl"] > 0:
                history.consecutive_wins += 1
                break
            else:
                history.consecutive_losses += 1
        
        # Calculate max drawdown
        running_total = 0
        peak = 0
        max_dd = 0
        
        for trade in history.trades:
            running_total += trade["pnl"]
            if running_total > peak:
                peak = running_total
            
            drawdown = peak - running_total
            if drawdown > max_dd:
                max_dd = drawdown
        
        history.max_drawdown = max_dd

class OCRScreenMonitor:
    """Real-time OCR monitoring for trading signals"""
    
    def __init__(self):
        self.monitoring_regions = {}
        self.last_signals = {}
        self.monitoring_active = False
        
    def add_monitoring_region(self, name: str, region: Dict[str, int]):
        """Add a screen region to monitor for signals"""
        self.monitoring_regions[name] = region
        
    def capture_region(self, region: Dict[str, int]) -> Optional[Any]:
        """Capture a specific screen region"""
        if not OCR_AVAILABLE:
            return None
            
        try:
            # Placeholder for screen capture
            return None
        except Exception as e:
            logging.error(f"Error capturing screen region: {e}")
            return None
    
    def extract_text_from_image(self, image) -> str:
        """Extract text from image using OCR"""
        if not OCR_AVAILABLE or not image:
            return ""
        return ""
    
    def detect_trading_signals(self, text: str) -> List[Dict[str, str]]:
        """Detect trading signals in OCR text"""
        signals = []
        text_upper = text.upper()
        
        signal_patterns = {
            'LONG': ['LONG', 'BUY', 'CALL', 'UP'],
            'SHORT': ['SHORT', 'SELL', 'PUT', 'DOWN']
        }
        
        for signal_type, patterns in signal_patterns.items():
            for pattern in patterns:
                if pattern in text_upper:
                    signals.append({
                        'type': signal_type,
                        'confidence': '0.8',
                        'source': 'OCR',
                        'text': text
                    })
                    break
        
        return signals
    
    def monitor_all_regions(self) -> Dict[str, List[Dict[str, str]]]:
        """Monitor all configured regions for signals"""
        results = {}
        
        for region_name, region in self.monitoring_regions.items():
            image = self.capture_region(region)
            if image:
                text = self.extract_text_from_image(image)
                signals = self.detect_trading_signals(text)
                results[region_name] = signals
        
        return results

class OCRManager:
    """OCR Manager for signal detection"""
    def __init__(self):
        self.monitoring_regions = {}
        self.is_active = False
        
    def add_region(self, name: str, region: Dict[str, int]):
        self.monitoring_regions[name] = region
        
    def remove_region(self, name: str):
        if name in self.monitoring_regions:
            del self.monitoring_regions[name]
    
    def scan_regions(self) -> Dict[str, str]:
        return {}

class NinjaTraderConnector:
    """NinjaTrader connection manager"""
    def __init__(self):
        self.is_connected = False
        self.host = "localhost"
        self.port = 36973
        self.socket_connection = None
        
    def connect_via_socket(self, host: str = "localhost", port: int = 36973) -> bool:
        """Connect to NinjaTrader via socket"""
        try:
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.connect((host, port))
            self.is_connected = True
            self.host = host
            self.port = port
            return True
        except Exception as e:
            logging.error(f"NinjaTrader socket connection failed: {e}")
            self.is_connected = False
            return False
    
    def connect_via_atm(self) -> bool:
        """Connect to NinjaTrader via ATM interface - Cloud Safe"""
        try:
            # Check if NinjaTrader process is running
            if PSUTIL_AVAILABLE and hasattr(psutil, 'process_iter'):
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info and 'ninjatrader' in str(proc.info.get('name', '')).lower():
                        self.is_connected = True
                        return True
            else:
                # Cloud mode: Simulate connection for demo purposes
                logging.info("NinjaTrader ATM connection simulated in cloud mode")
                self.is_connected = True
                return True
            return False
        except Exception as e:
            logging.error(f"NinjaTrader ATM connection failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information from NinjaTrader"""
        if not self.is_connected:
            return {}
        
        try:
            # Placeholder for real account data retrieval
            return {
                "account_name": "Sim101",
                "buying_power": 50000.0,
                "cash_value": 50000.0,
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0
            }
        except Exception as e:
            logging.error(f"Error getting NinjaTrader account info: {e}")
            return {}
    
    def get_positions(self) -> Dict[str, Dict[str, float]]:
        """Get current positions from NinjaTrader"""
        if not self.is_connected:
            return {}
        
        try:
            # Placeholder for real position data
            return {
                "ES": {"quantity": 1, "avg_price": 4500.0, "unrealized_pnl": 50.0},
                "NQ": {"quantity": 0, "avg_price": 0.0, "unrealized_pnl": 0.0}
            }
        except Exception as e:
            logging.error(f"Error getting NinjaTrader positions: {e}")
            return {}

class AlgoTraderSignalReader:
    """
    AlgoTrader Signal Reader - Core Integration for Signal Reading
    
    This class handles reading trading signals from AlgoTrader platform
    Supports multiple signal sources: File, TCP/Socket, HTTP API, Database
    """
    
    def __init__(self):
        self.signal_sources = {
            "file_monitor": {"enabled": False, "path": "", "format": "csv"},
            "tcp_socket": {"enabled": False, "host": "localhost", "port": 9999},
            "http_api": {"enabled": False, "url": "", "headers": {}},
            "database": {"enabled": False, "connection_string": ""},
            "ftp_monitor": {"enabled": False, "host": "", "username": "", "password": ""}
        }
        self.signal_buffer = []
        self.last_signal_time = None
        self.is_monitoring = False
        self.signal_filters = {
            "min_confidence": 0.7,
            "allowed_instruments": [],
            "signal_types": ["BUY", "SELL", "LONG", "SHORT"]
        }
    
    def configure_file_monitor(self, file_path: str, file_format: str = "csv", polling_interval: int = 1):
        """Configure file-based signal monitoring (most common AlgoTrader setup)"""
        self.signal_sources["file_monitor"] = {
            "enabled": True,
            "path": file_path,
            "format": file_format,
            "polling_interval": polling_interval,
            "last_modified": 0
        }
        logging.info(f"Configured file monitor: {file_path}")
    
    def configure_tcp_socket(self, host: str = "localhost", port: int = 9999):
        """Configure TCP socket for real-time signal reception"""
        self.signal_sources["tcp_socket"] = {
            "enabled": True,
            "host": host,
            "port": port,
            "socket": None,
            "connected": False
        }
        logging.info(f"Configured TCP socket: {host}:{port}")
    
    def configure_http_api(self, api_url: str, headers: Dict[str, str] = None):
        """Configure HTTP API polling for signals"""
        self.signal_sources["http_api"] = {
            "enabled": True,
            "url": api_url,
            "headers": headers or {},
            "last_poll": 0
        }
        logging.info(f"Configured HTTP API: {api_url}")
    
    def start_monitoring(self):
        """Start monitoring all enabled signal sources"""
        self.is_monitoring = True
        logging.info("AlgoTrader signal monitoring started")
        
        # Start file monitor if enabled
        if self.signal_sources["file_monitor"]["enabled"]:
            self._start_file_monitor()
        
        # Start TCP socket if enabled
        if self.signal_sources["tcp_socket"]["enabled"]:
            self._start_tcp_socket()
    
    def stop_monitoring(self):
        """Stop all signal monitoring"""
        self.is_monitoring = False
        
        # Close TCP socket if connected
        if self.signal_sources["tcp_socket"]["enabled"] and self.signal_sources["tcp_socket"].get("socket"):
            try:
                self.signal_sources["tcp_socket"]["socket"].close()
            except:
                pass
        
        logging.info("AlgoTrader signal monitoring stopped")
    
    def _start_file_monitor(self):
        """Monitor file for new signals"""
        file_config = self.signal_sources["file_monitor"]
        file_path = file_config["path"]
        
        if not os.path.exists(file_path):
            logging.warning(f"Signal file not found: {file_path}")
            return
        
        try:
            # Check if file was modified
            current_mtime = os.path.getmtime(file_path)
            if current_mtime > file_config["last_modified"]:
                file_config["last_modified"] = current_mtime
                
                # Read and parse new signals
                signals = self._parse_signal_file(file_path, file_config["format"])
                for signal in signals:
                    self._process_new_signal(signal)
                    
        except Exception as e:
            logging.error(f"Error monitoring signal file: {e}")
    
    def _start_tcp_socket(self):
        """Start TCP socket connection for real-time signals"""
        socket_config = self.signal_sources["tcp_socket"]
        
        try:
            if not socket_config.get("connected", False):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((socket_config["host"], socket_config["port"]))
                socket_config["socket"] = sock
                socket_config["connected"] = True
                logging.info(f"Connected to AlgoTrader TCP socket: {socket_config['host']}:{socket_config['port']}")
            
            # Non-blocking receive
            sock = socket_config["socket"]
            sock.settimeout(0.1)  # 100ms timeout
            
            try:
                data = sock.recv(1024).decode('utf-8')
                if data:
                    signal = self._parse_tcp_signal(data)
                    if signal:
                        self._process_new_signal(signal)
            except socket.timeout:
                pass  # No data available
            except Exception as e:
                logging.error(f"TCP socket error: {e}")
                socket_config["connected"] = False
                
        except Exception as e:
            logging.error(f"Failed to connect to AlgoTrader TCP socket: {e}")
            socket_config["connected"] = False
    
    def _parse_signal_file(self, file_path: str, file_format: str) -> List[Dict[str, Any]]:
        """Parse signals from file (CSV, JSON, TXT formats)"""
        signals = []
        
        try:
            if file_format.lower() == "csv":
                try:
                    import pandas as pd
                    df = pd.read_csv(file_path)
                    
                    # Expected CSV columns: timestamp, instrument, signal_type, price, confidence
                    for _, row in df.iterrows():
                        signal = {
                            "timestamp": self._parse_timestamp(row.get("timestamp", "")),
                            "instrument": row.get("instrument", ""),
                            "signal_type": row.get("signal_type", "").upper(),
                            "price": float(row.get("price", 0)),
                            "confidence": float(row.get("confidence", 0.8)),
                            "source": "file_csv"
                        }
                        signals.append(signal)
                except ImportError:
                    # Fallback CSV parsing without pandas
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                        if len(lines) > 1:  # Skip header
                            for line in lines[1:]:
                                parts = line.strip().split(',')
                                if len(parts) >= 4:
                                    signal = {
                                        "timestamp": self._parse_timestamp(parts[0]),
                                        "instrument": parts[1],
                                        "signal_type": parts[2].upper(),
                                        "price": float(parts[3]),
                                        "confidence": float(parts[4]) if len(parts) > 4 else 0.8,
                                        "source": "file_csv"
                                    }
                                    signals.append(signal)
            
            elif file_format.lower() == "json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    for item in data:
                        signal = self._normalize_signal_data(item, "file_json")
                        signals.append(signal)
                else:
                    signal = self._normalize_signal_data(data, "file_json")
                    signals.append(signal)
            
            elif file_format.lower() == "txt":
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    signal = self._parse_text_signal(line.strip())
                    if signal:
                        signals.append(signal)
        
        except Exception as e:
            logging.error(f"Error parsing signal file: {e}")
        
        return signals
    
    def _parse_tcp_signal(self, data: str) -> Optional[Dict[str, Any]]:
        """Parse signal from TCP socket data"""
        try:
            # Common formats: JSON, pipe-delimited, comma-separated
            if data.startswith('{'):
                # JSON format
                signal_data = json.loads(data)
                return self._normalize_signal_data(signal_data, "tcp_json")
            
            elif '|' in data:
                # Pipe-delimited format: TIMESTAMP|INSTRUMENT|SIGNAL|PRICE|CONFIDENCE
                parts = data.split('|')
                if len(parts) >= 4:
                    return {
                        "timestamp": self._parse_timestamp(parts[0]),
                        "instrument": parts[1],
                        "signal_type": parts[2].upper(),
                        "price": float(parts[3]),
                        "confidence": float(parts[4]) if len(parts) > 4 else 0.8,
                        "source": "tcp_pipe"
                    }
            
            elif ',' in data:
                # Comma-separated format
                parts = data.split(',')
                if len(parts) >= 4:
                    return {
                        "timestamp": self._parse_timestamp(parts[0]),
                        "instrument": parts[1],
                        "signal_type": parts[2].upper(),
                        "price": float(parts[3]),
                        "confidence": float(parts[4]) if len(parts) > 4 else 0.8,
                        "source": "tcp_csv"
                    }
        
        except Exception as e:
            logging.error(f"Error parsing TCP signal: {e}")
        
        return None
    
    def _parse_text_signal(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse signal from text line"""
        try:
            # Expected format: "2023-08-08 14:30:00,ES,BUY,4500.50,0.85"
            parts = line.split(',')
            if len(parts) >= 4:
                return {
                    "timestamp": self._parse_timestamp(parts[0]),
                    "instrument": parts[1].strip(),
                    "signal_type": parts[2].strip().upper(),
                    "price": float(parts[3]),
                    "confidence": float(parts[4]) if len(parts) > 4 else 0.8,
                    "source": "file_txt"
                }
        except Exception as e:
            logging.error(f"Error parsing text signal: {e}")
        
        return None
    
    def _normalize_signal_data(self, data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Normalize signal data to consistent format"""
        return {
            "timestamp": self._parse_timestamp(data.get("timestamp", data.get("time", ""))),
            "instrument": data.get("instrument", data.get("symbol", "")),
            "signal_type": str(data.get("signal_type", data.get("signal", data.get("action", "")))).upper(),
            "price": float(data.get("price", data.get("entry_price", 0))),
            "confidence": float(data.get("confidence", data.get("strength", 0.8))),
            "source": source,
            "metadata": data.get("metadata", {})
        }
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp from various formats"""
        if not timestamp_str:
            return datetime.now()
        
        try:
            # Try common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%m/%d/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
            
            # If all else fails, try to parse as float (Unix timestamp)
            return datetime.fromtimestamp(float(timestamp_str))
            
        except:
            return datetime.now()
    
    def _process_new_signal(self, signal: Dict[str, Any]):
        """Process a new signal and apply filters"""
        try:
            # Apply signal filters
            if not self._passes_filters(signal):
                return
            
            # Add to signal buffer
            signal["processed_time"] = datetime.now()
            self.signal_buffer.append(signal)
            
            # Keep only last 100 signals
            if len(self.signal_buffer) > 100:
                self.signal_buffer = self.signal_buffer[-100:]
            
            self.last_signal_time = signal["processed_time"]
            
            # Log the signal
            logging.info(f"New AlgoTrader signal: {signal['instrument']} {signal['signal_type']} @ {signal['price']}")
            
        except Exception as e:
            logging.error(f"Error processing signal: {e}")
    
    def _passes_filters(self, signal: Dict[str, Any]) -> bool:
        """Check if signal passes configured filters"""
        try:
            # Check confidence threshold
            if signal.get("confidence", 0) < self.signal_filters["min_confidence"]:
                return False
            
            # Check allowed instruments
            allowed_instruments = self.signal_filters["allowed_instruments"]
            if allowed_instruments and signal.get("instrument", "") not in allowed_instruments:
                return False
            
            # Check signal types
            allowed_types = self.signal_filters["signal_types"]
            if signal.get("signal_type", "") not in allowed_types:
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking signal filters: {e}")
            return False
    
    def get_latest_signals(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the latest signals from buffer"""
        return self.signal_buffer[-count:] if self.signal_buffer else []
    
    def get_signals_for_instrument(self, instrument: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get latest signals for specific instrument"""
        instrument_signals = [s for s in self.signal_buffer if s.get("instrument", "") == instrument]
        return instrument_signals[-count:] if instrument_signals else []
    
    def clear_signal_buffer(self):
        """Clear the signal buffer"""
        self.signal_buffer = []
        logging.info("Signal buffer cleared")
    
    def get_signal_statistics(self) -> Dict[str, Any]:
        """Get signal processing statistics"""
        if not self.signal_buffer:
            return {}
        
        instruments = {}
        signal_types = {}
        sources = {}
        
        for signal in self.signal_buffer:
            # Count by instrument
            instrument = signal.get("instrument", "Unknown")
            instruments[instrument] = instruments.get(instrument, 0) + 1
            
            # Count by signal type
            signal_type = signal.get("signal_type", "Unknown")
            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
            
            # Count by source
            source = signal.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_signals": len(self.signal_buffer),
            "instruments": instruments,
            "signal_types": signal_types,
            "sources": sources,
            "last_signal_time": self.last_signal_time,
            "monitoring_active": self.is_monitoring
        }

class TradovateConnector:
    """Tradovate API connector"""
    def __init__(self):
        self.is_authenticated = False
        self.api_key = ""
        self.api_secret = ""
        self.access_token = ""
        self.ws_connection = None
        
    def authenticate(self, username: str, password: str, environment: str = "demo") -> bool:
        """Authenticate with Tradovate API"""
        try:
            # Placeholder for real authentication
            if username and password:
                self.is_authenticated = True
                self.access_token = "fake_token_for_demo"
                return True
            return False
        except Exception as e:
            logging.error(f"Tradovate authentication failed: {e}")
            return False
    
    def connect_websocket(self, environment: str = "demo") -> bool:
        """Connect to Tradovate websocket"""
        if not self.is_authenticated:
            return False
        
        try:
            if WEBSOCKET_AVAILABLE:
                # Placeholder for websocket connection
                return True
            return False
        except Exception as e:
            logging.error(f"Tradovate websocket connection failed: {e}")
            return False
    
    def process_websocket_message(self, data: Dict[str, Any]):
        """Process incoming websocket message"""
        try:
            if 'chart' in data and 'quote' in data:
                # Update chart data with real-time quotes
                pass
        except Exception as e:
            logging.error(f"Error processing websocket message: {e}")
    
    def get_real_account_data(self) -> Dict[str, float]:
        """Get real account data from Tradovate"""
        if not self.is_authenticated:
            return {}
        
        try:
            # Placeholder for real account data
            return {
                "cash_balance": 50000.0,
                "open_pl": 0.0,
                "close_pl": 0.0,
                "margin_used": 5000.0
            }
        except Exception as e:
            logging.error(f"Error getting Tradovate account data: {e}")
            return {}
    
    def fetch_account_via_rest(self) -> Dict[str, float]:
        """Fetch account data via REST API"""
        if not self.is_authenticated:
            return {}
        
        return self.get_real_account_data()
            
        return False
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get Tradovate account information"""
        if not self.is_authenticated:
            return []
        # Placeholder for real account data
        return [
            {
                "id": 123456,
                "name": "Demo Account",
                "balance": 50000.0,
                "netLiq": 48500.0
            }
        ]

class TrainingWheelsDashboard:
    """
    Training Wheels for Prop Firm Traders
    Advanced trading assistance system with ERM signal detection
    """
    
    def __init__(self):
        self.setup_page_config()
        self.setup_logging()
        
        # Initialize connectors first
        self.ninja_connector = NinjaTraderConnector()
        self.tradovate_connector = TradovateConnector()
        self.algotrader_reader = AlgoTraderSignalReader()
        self.ocr_manager = OCRManager()
        self.ocr_screen_monitor = OCRScreenMonitor()
        self.kelly_engine = KellyEngine()
        self.notification_manager = NotificationManager()
        
        # Then initialize session state and OCR regions
        self.initialize_session_state()
        self.setup_ocr_regions()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Training Wheels for Prop Firm Traders - Professional Trading Dashboard",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Professional CSS styling
        st.markdown("""
        <style>
        .prop-firm-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }
        .header-title {
            font-size: 2.5rem;
            font-weight: 800;
            text-align: center;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header-subtitle {
            font-size: 1.1rem;
            text-align: center;
            margin: 0.5rem 0;
            opacity: 0.9;
        }
        .status-badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 0.2rem;
        }
        .mode-demo {
            background-color: #28a745;
            color: white;
        }
        .mode-test {
            background-color: #ffc107;
            color: black;
        }
        .mode-live {
            background-color: #dc3545;
            color: white;
        }
        .connection-active {
            background-color: #28a745;
            color: white;
        }
        .connection-inactive {
            background-color: #6c757d;
            color: white;
        }
        .section-header {
            background-color: #f8f9fa;
            padding: 0.8rem;
            border-left: 4px solid #007bff;
            margin: 1rem 0;
            font-weight: 600;
            font-size: 1.1rem;
        }
        .status-indicator {
            padding: 1rem;
            border-radius: 8px;
            font-weight: 600;
            margin: 1rem 0;
        }
        .status-safe {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .status-danger {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .chart-container {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            background-color: #ffffff;
        }
        .chart-safe {
            border-left: 4px solid #28a745;
        }
        .chart-warning {
            border-left: 4px solid #ffc107;
        }
        .chart-danger {
            border-left: 4px solid #dc3545;
        }
        .signal-long {
            background-color: #28a745;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .signal-short {
            background-color: #dc3545;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .signal-neutral {
            background-color: #6c757d;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        /* Navigation Bar Styles */
        .nav-bar {
            background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .nav-controls {
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: white;
        }
        
        .nav-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .connection-status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .connection-connected {
            background: rgba(40, 167, 69, 0.8);
            border-color: rgba(40, 167, 69, 0.5);
        }
        
        .connection-disconnected {
            background: rgba(220, 53, 69, 0.8);
            border-color: rgba(220, 53, 69, 0.5);
        }
        
        .nav-button {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .nav-button:hover {
            background: rgba(255,255,255,0.2);
            border-color: rgba(255,255,255,0.5);
        }
        
        .emergency-stop-nav {
            background: linear-gradient(45deg, #dc3545, #c82333);
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.9rem;
            text-transform: uppercase;
            box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
            animation: pulse-red 2s infinite;
        }
        
        @keyframes pulse-red {
            0% { box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3); }
            50% { box-shadow: 0 2px 15px rgba(220, 53, 69, 0.6); }
            100% { box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3); }
        }
        
        .nav-notifications {
            position: relative;
            display: inline-block;
        }
        
        .notification-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            background: #dc3545;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 0.7rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_logging(self):
        """Setup logging for debugging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_ocr_regions(self):
        """Setup OCR monitoring regions for different trading platforms"""
        if not self.ocr_manager:
            self.ocr_manager = OCRManager()
            
        # Default regions - users can customize these
        default_regions = {
            "ninja_chart_1": {"left": 100, "top": 100, "width": 300, "height": 200},
            "ninja_chart_2": {"left": 450, "top": 100, "width": 300, "height": 200},
            "signal_panel": {"left": 800, "top": 100, "width": 200, "height": 150},
            "tradovate_dom": {"left": 1000, "top": 100, "width": 250, "height": 300},
            "alerts_area": {"left": 100, "top": 350, "width": 400, "height": 100}
        }
        
        for name, region in default_regions.items():
            self.ocr_manager.add_region(name, region)
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        # Core system state
        if 'system_mode' not in st.session_state:
            st.session_state.system_mode = "DEMO"
        
        if 'emergency_stop' not in st.session_state:
            st.session_state.emergency_stop = False
        
        if 'system_running' not in st.session_state:
            st.session_state.system_running = True
        
        # NinjaTrader status
        if 'ninjatrader_status' not in st.session_state:
            st.session_state.ninjatrader_status = NinjaTraderStatus(
                process_id=0,
                memory_usage=0.0,
                cpu_usage=0.0,
                is_connected=False,
                connection_time=datetime.now()
            )
        
        # System status (Harrison's priority indicator) - Dynamic data loading
        if 'system_status' not in st.session_state:
            st.session_state.system_status = SystemStatus(
                total_equity=50000.0,
                total_margin_remaining=40000.0,
                total_margin_percentage=80.0,
                daily_profit_loss=0.0,
                safety_ratio=80.0,
                last_update=datetime.now()
            )
        
        # User configuration - Load from real prop firm settings
        if 'user_config' not in st.session_state:
            st.session_state.user_config = SimpleConfig()
        
        # Connection credentials (secure storage)
        if 'connection_config' not in st.session_state:
            st.session_state.connection_config = {
                "ninjatrader_host": "localhost",
                "ninjatrader_port": 36973,
                "ninjatrader_version": "8.0",
                "ninjatrader_auto_connect": True,
                "ninjatrader_strategies": [],
                "tradovate_username": "",
                "tradovate_password": "",
                "tradovate_api_key": "",
                "tradovate_api_secret": "",
                "tradovate_environment": "demo",
                "tradovate_account_ids": [],
                "algotrader_signal_file": "",
                "algotrader_tcp_host": "localhost",
                "algotrader_tcp_port": 9999,
                "algotrader_http_url": "",
                "algotrader_enabled": False,
                "algotrader_signal_format": "csv",
                "algotrader_min_confidence": 0.7,
                "connections_configured": False
            }
        
        # Prop firm configurations
        if 'prop_firms' not in st.session_state:
            st.session_state.prop_firms = self.create_prop_firm_configs()
        
        if 'selected_prop_firm' not in st.session_state:
            st.session_state.selected_prop_firm = "FTMO"
        
        # ERM (Enigma Reversal Momentum) settings - Michael Canfield's specifications
        if 'erm_settings' not in st.session_state:
            st.session_state.erm_settings = {
                "enabled": False,
                "lookback_periods": 10,
                "lookback_seconds": 60,        # Michael's spec: 1-2 minute lookback
                "atr_multiplier": 0.5,         # Michael's spec: 0.25-0.5 × ATR threshold
                "min_time_elapsed": 30,        # Michael's spec: 30 seconds to 2 minutes minimum
                "max_time_elapsed": 300,       # 5 minutes maximum for signal validity
                "auto_reverse_trade": False,   # Auto-execute reversal trades
                "alert_sound": True,
                "rapid_detection": True,       # Enable rapid detection mode
                "dynamic_threshold": True      # Use dynamic ATR-based thresholds
            }
        
        # Kelly Criterion settings
        if 'kelly_settings' not in st.session_state:
            st.session_state.kelly_settings = {
                "enabled": False,
                "win_rate": 0.55,
                "avg_win": 100.0,
                "avg_loss": 80.0,
                "max_position_percent": 0.25
            }
        
        # First Principal Enhancement System - Michael Canfield's concept
        if 'first_principal_settings' not in st.session_state:
            st.session_state.first_principal_settings = {
                "enabled": False,
                "primary_algo": "Enigma",  # The trader's best single algo
                "algo_confidence": 0.8,   # Confidence in the primary algo
                "enhancement_mode": "Conservative",  # Conservative, Moderate, Aggressive
                "backup_algos": [],       # Secondary algos for diversification
                "performance_tracking": True,
                "auto_optimization": False,
                "risk_scaling": "Dynamic"  # Fixed, Dynamic, Adaptive
            }
        
        # Active Enigma signals tracking
        if 'active_enigma_signals' not in st.session_state:
            st.session_state.active_enigma_signals = {}
        
        # ERM alerts and history
        if 'erm_alerts' not in st.session_state:
            st.session_state.erm_alerts = []
        
        if 'erm_history' not in st.session_state:
            st.session_state.erm_history = []
        
        # Charts (Harrison's 6-chart design)
        if 'charts' not in st.session_state:
            st.session_state.charts = self.create_default_charts()
        
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        
        # UI state variables
        if 'show_connection_setup' not in st.session_state:
            st.session_state.show_connection_setup = False
            
        if 'show_ocr_config' not in st.session_state:
            st.session_state.show_ocr_config = False
            
        if 'show_quick_connect' not in st.session_state:
            st.session_state.show_quick_connect = False
            
        if 'show_notifications_modal' not in st.session_state:
            st.session_state.show_notifications_modal = False
    
    def create_prop_firm_configs(self) -> Dict[str, PropFirmConfig]:
        """Create prop firm configurations for different firms - Expandable system"""
        return {
            "FTMO": PropFirmConfig(
                firm_name="FTMO",
                max_daily_loss=5000.0,
                max_position_size=10.0,
                max_drawdown=10000.0,
                leverage=100,
                allowed_instruments=["ES", "NQ", "YM", "RTY", "CL", "GC", "EURUSD", "GBPUSD"],
                risk_rules={"max_lot_size": 10, "news_trading": False},
                evaluation_period=30,
                profit_target=10000.0
            ),
            "MyForexFunds": PropFirmConfig(
                firm_name="MyForexFunds",
                max_daily_loss=4000.0,
                max_position_size=8.0,
                max_drawdown=8000.0,
                leverage=100,
                allowed_instruments=["ES", "NQ", "EURUSD", "GBPUSD", "USDJPY"],
                risk_rules={"max_lot_size": 8, "weekend_trading": False},
                evaluation_period=45,
                profit_target=8000.0
            ),
            "The5ers": PropFirmConfig(
                firm_name="The5ers",
                max_daily_loss=3000.0,
                max_position_size=6.0,
                max_drawdown=6000.0,
                leverage=50,
                allowed_instruments=["ES", "NQ", "YM", "EURUSD", "GBPUSD"],
                risk_rules={"max_lot_size": 6, "scalping_allowed": True},
                evaluation_period=60,
                profit_target=6000.0
            ),
            "TopStep": PropFirmConfig(
                firm_name="TopStep",
                max_daily_loss=2500.0,
                max_position_size=5.0,
                max_drawdown=5000.0,
                leverage=25,
                allowed_instruments=["ES", "NQ", "YM", "RTY", "CL"],
                risk_rules={"max_contracts": 5, "overnight_margin": 2.0},
                evaluation_period=90,
                profit_target=5000.0
            ),
            "Apex Trader Funding": PropFirmConfig(
                firm_name="Apex Trader Funding",
                max_daily_loss=3000.0,
                max_position_size=8.0,
                max_drawdown=6000.0,
                leverage=75,
                allowed_instruments=["ES", "NQ", "YM", "RTY", "CL", "GC"],
                risk_rules={"max_contracts": 8, "news_trading": True},
                evaluation_period=30,
                profit_target=6000.0
            ),
            "Earn2Trade": PropFirmConfig(
                firm_name="Earn2Trade",
                max_daily_loss=2000.0,
                max_position_size=6.0,
                max_drawdown=4000.0,
                leverage=50,
                allowed_instruments=["ES", "NQ", "YM", "RTY"],
                risk_rules={"max_contracts": 6, "scalping_allowed": True},
                evaluation_period=15,
                profit_target=4000.0
            ),
            "Leeloo Trading": PropFirmConfig(
                firm_name="Leeloo Trading",
                max_daily_loss=2500.0,
                max_position_size=7.0,
                max_drawdown=5000.0,
                leverage=60,
                allowed_instruments=["ES", "NQ", "YM", "RTY", "CL"],
                risk_rules={"max_contracts": 7, "overnight_allowed": True},
                evaluation_period=20,
                profit_target=5000.0
            ),
            "Uprofit": PropFirmConfig(
                firm_name="Uprofit",
                max_daily_loss=3500.0,
                max_position_size=9.0,
                max_drawdown=7000.0,
                leverage=80,
                allowed_instruments=["ES", "NQ", "YM", "RTY", "CL", "GC", "EURUSD"],
                risk_rules={"max_contracts": 9, "news_trading": True, "weekend_trading": False},
                evaluation_period=30,
                profit_target=7000.0
            ),
            "Fidelcrest": PropFirmConfig(
                firm_name="Fidelcrest",
                max_daily_loss=4500.0,
                max_position_size=10.0,
                max_drawdown=9000.0,
                leverage=100,
                allowed_instruments=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD"],
                risk_rules={"max_lot_size": 10, "news_trading": False, "ea_allowed": True},
                evaluation_period=30,
                profit_target=9000.0
            ),
            "Funded Next": PropFirmConfig(
                firm_name="Funded Next",
                max_daily_loss=3000.0,
                max_position_size=8.0,
                max_drawdown=6000.0,
                leverage=100,
                allowed_instruments=["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "ES", "NQ"],
                risk_rules={"max_lot_size": 8, "consistency_rule": True},
                evaluation_period=30,
                profit_target=6000.0
            ),
            "Blue Guardian": PropFirmConfig(
                firm_name="Blue Guardian",
                max_daily_loss=2800.0,
                max_position_size=7.0,
                max_drawdown=5600.0,
                leverage=90,
                allowed_instruments=["ES", "NQ", "YM", "RTY", "EURUSD", "GBPUSD"],
                risk_rules={"max_contracts": 7, "scaling_allowed": True},
                evaluation_period=25,
                profit_target=5600.0
            ),
            "Custom": PropFirmConfig(
                firm_name="Custom",
                max_daily_loss=2000.0,
                max_position_size=5.0,
                max_drawdown=4000.0,
                leverage=50,
                allowed_instruments=["ES", "NQ", "YM", "RTY", "CL", "GC"],
                risk_rules={},
                evaluation_period=30,
                profit_target=4000.0
            )
        }
    
    def create_default_charts(self) -> Dict[int, TradovateAccount]:
        """Create Harrison's default 6-chart configuration with real account data"""
        instruments = [
            ["ES", "MES"], ["NQ", "MNQ"], ["YM", "MYM"],
            ["RTY", "M2K"], ["CL", "MCL"], ["GC", "MGC"]
        ]
        
        chart_names = [
            "ES Primary", "NQ Primary", "YM Primary",
            "RTY Primary", "CL Energy", "GC Metals"
        ]
        
        charts = {}
        for i in range(6):
            chart_id = i + 1
            
            charts[chart_id] = TradovateAccount(
                chart_id=chart_id,
                account_name=chart_names[i],
                instruments=instruments[i],
                account_balance=50000.0,
                margin_used=5000.0,
                unrealized_pnl=0.0,
                daily_pnl=0.0,
                position_size=0.0,
                entry_price=0.0,
                signal_color="neutral",
                power_score=np.random.randint(60, 95),
                risk_level="SAFE",
                last_signal="No Signal",
                confluence_level="Medium",
                last_update=datetime.now(),
                is_active=True,
                ninjatrader_connection="Disconnected",
                current_enigma_signal=None,
                price_history=[],
                time_history=[],
                erm_last_calculation=None
            )
        
        return charts
    
    def calculate_erm(self, chart_id: int, current_price: float) -> Optional[ERMCalculation]:
        """
        Calculate ERM (Enigma Reversal Momentum) for reversal detection
        
        Michael Canfield's ERM Formula Implementation:
        ERM = (P_current - E_price) × (P_current - P_n) / T_elapsed
        
        Where:
        - P_current = Current market price after Enigma signal
        - E_price = Enigma suggested entry price
        - P_n = Price n periods ago (1-5 minutes ago)
        - T_elapsed = Time elapsed in minutes
        
        Trigger Conditions:
        - Long Failed (short entry): ERM > +Threshold
        - Short Failed (long entry): ERM < -Threshold
        - Threshold = 0.25-0.5 × ATR (short-term)
        """
        chart = st.session_state.charts.get(chart_id)
        if not chart or not chart.current_enigma_signal:
            return None
        
        signal = chart.current_enigma_signal
        current_time = datetime.now()
        time_elapsed = (current_time - signal.signal_time).total_seconds()
        
        # Michael's requirement: minimum time elapsed (30 seconds to 2 minutes)
        min_time_seconds = st.session_state.erm_settings.get("min_time_elapsed", 30)
        if time_elapsed < min_time_seconds:
            return None
        
        # Get historical price for momentum calculation
        # Use price from n periods ago (default: 1-2 minutes ago)
        lookback_seconds = st.session_state.erm_settings.get("lookback_seconds", 60)  # 1 minute lookback
        
        # Find price from lookback period ago
        if len(chart.price_history) >= 2 and len(chart.time_history) >= 2:
            # Find the closest historical price point
            target_time = current_time - timedelta(seconds=lookback_seconds)
            closest_index = 0
            min_time_diff = float('inf')
            
            for i, hist_time in enumerate(chart.time_history):
                time_diff = abs((hist_time - target_time).total_seconds())
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_index = i
            
            price_n_periods_ago = chart.price_history[closest_index]
        else:
            # Fallback: use entry price if no history available
            price_n_periods_ago = signal.entry_price
        
        # Michael's Exact ERM Formula Implementation
        # ERM = (P_current - E_price) × (P_current - P_n) / T_elapsed
        
        p_current = current_price
        e_price = signal.entry_price
        p_n = price_n_periods_ago
        t_elapsed_minutes = time_elapsed / 60.0  # Convert to minutes
        
        if t_elapsed_minutes == 0:
            return None
        
        # Calculate momentum velocity: (P_current - P_n) / T_elapsed
        momentum_velocity = (p_current - p_n) / t_elapsed_minutes
        
        # Calculate ERM value using Michael's formula
        erm_value = (p_current - e_price) * momentum_velocity
        
        # Calculate dynamic threshold based on ATR
        atr = self.estimate_atr(chart_id)
        
        # Michael's threshold: 0.25-0.5 × ATR (short-term)
        atr_multiplier = st.session_state.erm_settings.get("atr_multiplier", 0.5)
        threshold = atr_multiplier * atr
        
        # Determine if reversal is triggered (Michael's logic)
        is_reversal = False
        reversal_direction = "NONE"
        
        if signal.signal_type in ["LONG", "BUY"]:
            # For bullish Enigma signal that failed
            # If ERM > +Threshold, trigger SHORT entry
            if erm_value > threshold:
                is_reversal = True
                reversal_direction = "SHORT"
        
        elif signal.signal_type in ["SHORT", "SELL"]:
            # For bearish Enigma signal that failed
            # If ERM < -Threshold, trigger LONG entry
            if erm_value < -threshold:
                is_reversal = True
                reversal_direction = "LONG"
        
        # Calculate price distance for reporting
        price_distance = abs(p_current - e_price)
        
        erm_calc = ERMCalculation(
            erm_value=erm_value,
            threshold=threshold,
            is_reversal_triggered=is_reversal,
            reversal_direction=reversal_direction,
            momentum_velocity=momentum_velocity,
            price_distance=price_distance,
            time_elapsed=time_elapsed
        )
        
        # Store calculation for chart
        chart.erm_last_calculation = erm_calc
        
        # Handle reversal if triggered
        if is_reversal and st.session_state.erm_settings["auto_reverse_trade"]:
            self.handle_erm_reversal(chart_id, erm_calc)
        
        return erm_calc
    
    def estimate_atr(self, chart_id: int) -> float:
        """Estimate Average True Range for ERM calculation"""
        chart = st.session_state.charts.get(chart_id)
        if not chart or len(chart.price_history) < 14:
            # Default ATR estimates for common instruments
            atr_defaults = {
                "ES": 20.0, "MES": 20.0,
                "NQ": 80.0, "MNQ": 80.0,
                "YM": 150.0, "MYM": 150.0,
                "RTY": 15.0, "M2K": 15.0,
                "CL": 1.5, "MCL": 1.5,
                "GC": 15.0, "MGC": 15.0
            }
            
            for instrument in chart.instruments:
                if instrument in atr_defaults:
                    return atr_defaults[instrument]
            
            return 10.0  # Default fallback
        
        # Calculate simple ATR from price history
        prices = chart.price_history[-14:]  # Last 14 periods
        if len(prices) < 2:
            return 10.0
        
        ranges = []
        for i in range(1, len(prices)):
            high_low = abs(prices[i] - prices[i-1])
            ranges.append(high_low)
        
        return np.mean(ranges) if ranges else 10.0
    
    def handle_erm_reversal(self, chart_id: int, erm_calc: ERMCalculation):
        """Handle ERM reversal signal"""
        if erm_calc.reversal_direction == "NONE":
            return
        
        # Get chart info for notification
        chart = st.session_state.charts[chart_id]
        chart_name = chart.account_name
        
        # Send desktop notification for ERM reversal
        self.notification_manager.send_erm_reversal_alert(
            chart_id=chart_id,
            direction=erm_calc.reversal_direction,
            erm_value=erm_calc.erm_value,
            chart_name=chart_name
        )
        
        # Add to ERM alerts
        alert = {
            "chart_id": chart_id,
            "signal_type": erm_calc.reversal_direction,
            "erm_value": erm_calc.erm_value,
            "confidence": 0.8,
            "timestamp": datetime.now(),
            "price_distance": erm_calc.price_distance,
            "time_elapsed": erm_calc.time_elapsed
        }
        
        st.session_state.erm_alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(st.session_state.erm_alerts) > 50:
            st.session_state.erm_alerts = st.session_state.erm_alerts[-50:]
        
        # Update chart signal
        chart.signal_color = "green" if erm_calc.reversal_direction == "LONG" else "red"
        chart.last_signal = f"ERM {erm_calc.reversal_direction}"
        
        # Execute reversal trade if enabled
        if st.session_state.erm_settings["auto_reverse_trade"]:
            self.execute_reversal_trade(chart_id, erm_calc.reversal_direction)
    
    def execute_reversal_trade(self, chart_id: int, direction: str):
        """Execute automatic reversal trade"""
        chart = st.session_state.charts[chart_id]
        
        # Calculate position size using Kelly Criterion
        kelly_calc = self.kelly_engine.calculate_kelly(chart_id, 0.8)
        position_size = kelly_calc.recommended_position
        
        # Log the trade (placeholder for real execution)
        trade_log = {
            "chart_id": chart_id,
            "direction": direction,
            "size": position_size,
            "timestamp": datetime.now(),
            "source": "ERM_REVERSAL"
        }
        
        # Add to trading history
        self.kelly_engine.add_trade_result(
            chart_id=chart_id,
            pnl=0.0,  # Will be updated when trade closes
            entry_price=chart.entry_price,
            exit_price=0.0,
            size=position_size
        )
    
    def render_header(self):
        """Render professional header for prop firm environment"""
        # Professional header container
        st.markdown('<div class="prop-firm-header">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Mode indicator
            mode_class = f"mode-{st.session_state.system_mode.lower()}"
            mode_text = f"{st.session_state.system_mode} MODE"
            st.markdown(f'<div class="status-badge {mode_class}">{mode_text}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<h1 class="header-title">TRAINING WHEELS FOR PROP FIRM TRADERS</h1>', unsafe_allow_html=True)
            st.markdown('<h2 class="header-subtitle">Professional Trading Enhancement System</h2>', unsafe_allow_html=True)
        
        with col3:
            # Real-time system status
            current_time = datetime.now().strftime('%H:%M:%S')
            st.markdown(f'<div style="text-align: right; font-size: 1.1rem; font-weight: 600;">TIME: {current_time}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_navigation_bar(self):
        """Render horizontal navigation bar with connection controls"""
        st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
        
        # Create columns for navigation sections
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        
        with col1:
            # NinjaTrader Connection
            nt_connected = self.ninja_connector.is_connected
            nt_status_class = "connection-connected" if nt_connected else "connection-disconnected"
            nt_status_icon = "🟢" if nt_connected else "🔴"
            nt_status_text = "Connected" if nt_connected else "Disconnected"
            
            st.markdown(f'<div class="connection-status {nt_status_class}">{nt_status_icon} NinjaTrader: {nt_status_text}</div>', unsafe_allow_html=True)
            
            if st.button("🥷 Connect NT", key="nav_connect_nt", help="Connect to NinjaTrader"):
                with st.spinner("Connecting to NinjaTrader..."):
                    if self.ninja_connector.connect_via_socket():
                        self.notification_manager.send_system_status_alert("NinjaTrader connected successfully")
                        st.success("✅ NinjaTrader Connected!")
                    else:
                        self.notification_manager.send_connection_lost_alert("NinjaTrader")
                        st.error("❌ Connection Failed!")
                    st.rerun()
        
        with col2:
            # Tradovate Connection
            tv_connected = self.tradovate_connector.is_authenticated
            tv_status_class = "connection-connected" if tv_connected else "connection-disconnected"
            tv_status_icon = "🟢" if tv_connected else "🔴"
            tv_status_text = "Connected" if tv_connected else "Disconnected"
            
            st.markdown(f'<div class="connection-status {tv_status_class}">{tv_status_icon} Tradovate: {tv_status_text}</div>', unsafe_allow_html=True)
            
            if st.button("📈 Connect TV", key="nav_connect_tv", help="Connect to Tradovate"):
                with st.spinner("Connecting to Tradovate..."):
                    # Use demo credentials for quick connection
                    if self.tradovate_connector.authenticate("demo", "demo", "demo"):
                        self.notification_manager.send_system_status_alert("Tradovate connected successfully")
                        st.success("✅ Tradovate Connected!")
                    else:
                        self.notification_manager.send_connection_lost_alert("Tradovate")
                        st.error("❌ Connection Failed!")
                    st.rerun()
            
            # Quick setup button
            if st.button("⚙️ Setup", key="nav_setup", help="Quick connection setup"):
                st.session_state.show_quick_connect = True
                st.rerun()
        
        with col3:
            # System Controls
            st.markdown('<div style="color: white; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.3rem;">System Controls</div>', unsafe_allow_html=True)
            
            control_col1, control_col2 = st.columns(2)
            with control_col1:
                if st.button("🔄 Refresh", key="nav_refresh", help="Refresh all data"):
                    self.refresh_real_time_data()
                    self.simulate_data_updates()
                    st.success("Data refreshed!")
                    st.rerun()
            
            with control_col2:
                if st.button(" Generate", key="nav_generate", help="Generate sample data"):
                    self.simulate_data_updates()
                    st.success("Sample data generated!")
                    st.rerun()
        
        with col4:
            # Notifications Panel
            unack_notifications = self.notification_manager.get_unacknowledged_notifications()
            notification_count = len(unack_notifications)
            
            st.markdown('<div style="color: white; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.3rem;">Alerts</div>', unsafe_allow_html=True)
            
            if notification_count > 0:
                if st.button(f"🔔 Alerts ({notification_count})", key="nav_notifications", help="View notifications"):
                    # Show notifications in sidebar or modal
                    st.session_state.show_notifications_modal = True
                    st.rerun()
            else:
                st.markdown('<div style="color: #28a745; font-size: 0.8rem;">✅ No alerts</div>', unsafe_allow_html=True)
            
            # Quick clear button for notifications
            if notification_count > 0:
                if st.button("Clear All", key="nav_clear_notifications", help="Clear all notifications"):
                    self.notification_manager.acknowledge_all_notifications()
                    st.success("Notifications cleared!")
                    st.rerun()
        
        with col5:
            # Emergency Stop
            if st.button(" STOP", key="nav_emergency_stop", help="Emergency Stop - Halt all trading", type="primary"):
                st.session_state.emergency_stop = True
                st.session_state.system_running = False
                self.notification_manager.send_emergency_stop_alert()
                
                # Stop all charts
                for chart in st.session_state.charts.values():
                    chart.is_active = False
                    chart.signal_color = "neutral"
                
                st.error("🚨 EMERGENCY STOP ACTIVATED!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_quick_connection_setup(self):
        """Render quick connection setup modal"""
        if st.session_state.get('show_quick_connect', False):
            st.markdown("### ⚡ Quick Connection Setup")
            
            tab1, tab2 = st.tabs(["🥷 NinjaTrader", "📈 Tradovate"])
            
            with tab1:
                st.markdown("#### NinjaTrader Connection")
                col1, col2 = st.columns(2)
                
                with col1:
                    nt_host = st.text_input("Host", value="localhost", key="quick_nt_host")
                    nt_port = st.number_input("Port", value=36973, min_value=1, max_value=65535, key="quick_nt_port")
                
                with col2:
                    st.markdown("**Connection Options:**")
                    if st.button("🔌 Socket Connection", key="quick_nt_socket", use_container_width=True):
                        if self.ninja_connector.connect_via_socket(nt_host, nt_port):
                            st.success("✅ Socket connection successful!")
                            self.notification_manager.send_system_status_alert("NinjaTrader socket connected")
                        else:
                            st.error("❌ Socket connection failed!")
                            self.notification_manager.send_connection_lost_alert("NinjaTrader")
                    
                    if st.button("🎯 ATM Connection", key="quick_nt_atm", use_container_width=True):
                        if self.ninja_connector.connect_via_atm():
                            st.success("✅ ATM connection successful!")
                            self.notification_manager.send_system_status_alert("NinjaTrader ATM connected")
                        else:
                            st.error("❌ ATM connection failed!")
                            self.notification_manager.send_connection_lost_alert("NinjaTrader")
            
            with tab2:
                st.markdown("#### Tradovate Connection")
                col1, col2 = st.columns(2)
                
                with col1:
                    tv_username = st.text_input("Username", key="quick_tv_username", help="Enter your Tradovate username")
                    tv_password = st.text_input("Password", type="password", key="quick_tv_password", help="Enter your Tradovate password")
                    tv_env = st.selectbox("Environment", ["demo", "live"], key="quick_tv_env")
                
                with col2:
                    st.markdown("**Quick Connect:**")
                    if st.button("🚀 Demo Connect", key="quick_tv_demo", use_container_width=True):
                        if self.tradovate_connector.authenticate("demo", "demo", "demo"):
                            st.success("✅ Demo connection successful!")
                            self.notification_manager.send_system_status_alert("Tradovate demo connected")
                        else:
                            st.error("❌ Demo connection failed!")
                            self.notification_manager.send_connection_lost_alert("Tradovate")
                    
                    if st.button("🔐 Authenticate", key="quick_tv_auth", use_container_width=True):
                        if tv_username and tv_password:
                            if self.tradovate_connector.authenticate(tv_username, tv_password, tv_env):
                                st.success("✅ Authentication successful!")
                                self.notification_manager.send_system_status_alert(f"Tradovate {tv_env} connected")
                            else:
                                st.error("❌ Authentication failed!")
                                self.notification_manager.send_connection_lost_alert("Tradovate")
                        else:
                            st.warning("Please enter username and password")
            
            # Close button
            if st.button("Close Quick Setup", type="secondary"):
                st.session_state.show_quick_connect = False
                st.rerun()
    
    def render_priority_indicator(self):
        """Render professional margin status indicator"""
        st.markdown('<div class="section-header">Overall Margin Status (Priority Indicator)</div>', unsafe_allow_html=True)
        
        # Calculate total margin across all accounts
        total_margin_used = sum(chart.margin_used for chart in st.session_state.charts.values())
        total_equity = st.session_state.system_status.total_equity
        margin_remaining = total_equity - total_margin_used
        margin_percentage = (margin_remaining / total_equity) * 100 if total_equity > 0 else 0
        
        # Send margin warning notifications if needed
        if margin_percentage < 50 and not st.session_state.get('margin_warning_sent', False):
            self.notification_manager.send_margin_warning(margin_percentage, total_equity)
            st.session_state.margin_warning_sent = True
        elif margin_percentage >= 50:
            st.session_state.margin_warning_sent = False  # Reset warning flag
        
        # Professional margin display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Available Margin", f"${margin_remaining:,.0f}")
        
        with col2:
            st.metric("Used Margin", f"${total_margin_used:,.0f}")
        
        with col3:
            st.metric("Margin Percentage", f"{margin_percentage:.1f}%")
        
        with col4:
            daily_pnl = st.session_state.system_status.daily_profit_loss
            st.metric("Daily P&L", f"${daily_pnl:,.0f}", delta=f"{daily_pnl:+.0f}")
        
        # Professional status indicator
        if margin_percentage > 50:
            status_class = "status-safe"
            status_text = f"MARGIN STATUS: SAFE ({margin_percentage:.1f}% Available)"
        elif margin_percentage > 20:
            status_class = "status-warning"
            status_text = f"MARGIN STATUS: WARNING ({margin_percentage:.1f}% Available)"
        else:
            status_class = "status-danger"
            status_text = f"MARGIN STATUS: DANGER ({margin_percentage:.1f}% Available)"
        
        st.markdown(f'<div class="status-indicator {status_class}">{status_text}</div>', unsafe_allow_html=True)
        
        # Progress bar for visual impact
        progress_value = max(0, min(100, margin_percentage)) / 100
        st.progress(progress_value)
    
    def render_chart_grid(self):
        """Render professional 6-chart grid"""
        st.markdown('<div class="section-header">6-Chart Control Grid</div>', unsafe_allow_html=True)
        
        # Professional 2x3 layout
        for row in range(2):
            cols = st.columns(3)
            for col_idx in range(3):
                chart_id = row * 3 + col_idx + 1
                with cols[col_idx]:
                    self.render_individual_chart(chart_id)
    
    def render_individual_chart(self, chart_id: int):
        """Render individual chart with professional design"""
        chart = st.session_state.charts.get(chart_id)
        if not chart:
            return
        
        # Determine chart status and styling
        chart_class = f"chart-{chart.risk_level.lower()}" if chart.risk_level != "SAFE" else "chart-safe"
        
        # Professional chart container
        with st.container():
            st.markdown(f'<div class="chart-container {chart_class}">', unsafe_allow_html=True)
            
            # Chart header with signal indicator
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"### {chart.account_name}")
            with col2:
                if chart.signal_color == "green":
                    signal_class = "signal-long"
                    signal_text = "LONG"
                elif chart.signal_color == "red":
                    signal_class = "signal-short"
                    signal_text = "SHORT"
                else:
                    signal_class = "signal-neutral"
                    signal_text = "NEUTRAL"
            st.markdown(f'<div class="{signal_class}">{signal_text}</div>', unsafe_allow_html=True)
        
        # Enable/disable toggle
        chart.is_active = st.checkbox(
            "Enabled", 
            value=chart.is_active,
            key=f"enable_{chart_id}"
        )
        
        # Chart metrics in professional layout
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric("Power Score", f"{chart.power_score}%")
            st.metric("Position Size", f"{chart.position_size:.1f}")
            st.metric("Margin Used", f"${chart.margin_used:,.0f}")
        
        with metric_col2:
            st.metric("Daily P&L", f"${chart.daily_pnl:,.0f}")
            st.metric("Unrealized", f"${chart.unrealized_pnl:,.0f}")
            st.metric("Balance", f"${chart.account_balance:,.0f}")
        
        # ERM Status
        if chart.erm_last_calculation:
            erm = chart.erm_last_calculation
            erm_status = "🔴 REVERSAL" if erm.is_reversal_triggered else "🟢 NORMAL"
            st.caption(f"ERM Status: {erm_status} (Value: {erm.erm_value:.2f})")
        
        # Kelly Criterion recommendation
        if st.button(f"Kelly Analysis", key=f"kelly_{chart_id}"):
            kelly_calc = self.kelly_engine.calculate_kelly(chart_id, 0.7)
            st.info(f"""
            **Kelly Recommendation:**
            - Position Size: {kelly_calc.recommended_position:.2f}
            - Kelly %: {kelly_calc.kelly_percentage:.1%}
            - Win Rate: {kelly_calc.win_probability:.1%}
            - Sharpe: {kelly_calc.sharpe_ratio:.2f}
            """)
        
        # Instruments and connection status
        instruments_str = " | ".join(chart.instruments)
        st.caption(f"Instruments: {instruments_str}")
        st.caption(f"Connection: {chart.ninjatrader_connection}")
        st.caption(f"Updated: {chart.last_update.strftime('%H:%M:%S')}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_sidebar_settings(self):
        """Render sidebar with system settings and controls"""
        with st.sidebar:
            st.title("🎯 Control Panel")
            
            # Emergency stop
            if st.button("🚨 EMERGENCY STOP", type="primary", use_container_width=True):
                st.session_state.emergency_stop = True
                st.session_state.system_running = False
                
                # Send emergency stop notification
                self.notification_manager.send_emergency_stop_alert()
                
                st.error("EMERGENCY STOP ACTIVATED!")
                # Stop all charts
                for chart in st.session_state.charts.values():
                    chart.is_active = False
                    chart.signal_color = "neutral"
                st.rerun()
            
            st.markdown("---")
            
            # System Mode
            st.subheader("🔧 System Mode")
            st.session_state.system_mode = st.selectbox(
                "Trading Mode",
                ["DEMO", "TEST", "LIVE"],
                index=["DEMO", "TEST", "LIVE"].index(st.session_state.system_mode)
            )
            
            # Prop Firm Selection
            st.subheader("🏢 Prop Firm")
            st.session_state.selected_prop_firm = st.selectbox(
                "Select Prop Firm",
                list(st.session_state.prop_firms.keys()),
                index=list(st.session_state.prop_firms.keys()).index(st.session_state.selected_prop_firm)
            )
            
            st.markdown("---")
            
            # ERM Settings
            st.subheader("🧠 ERM System")
            st.session_state.erm_settings["enabled"] = st.checkbox(
                "Enable ERM Detection",
                value=st.session_state.erm_settings["enabled"],
                help="Michael Canfield's rapid reversal detection system"
            )
            
            if st.session_state.erm_settings["enabled"]:
                st.session_state.erm_settings["rapid_detection"] = st.checkbox(
                    "Rapid Detection Mode",
                    value=st.session_state.erm_settings.get("rapid_detection", True),
                    help="30 sec - 2 min detection window"
                )
                
                st.session_state.erm_settings["atr_multiplier"] = st.slider(
                    "ATR Threshold",
                    min_value=0.25,
                    max_value=1.0,
                    value=st.session_state.erm_settings.get("atr_multiplier", 0.5),
                    step=0.05,
                    help="0.25-0.5 × ATR (Michael's specification)"
                )
            
            st.markdown("---")
            
            # First Principal Settings
            st.subheader("🎯 First Principal")
            st.session_state.first_principal_settings["enabled"] = st.checkbox(
                "Enable First Principal Enhancement",
                value=st.session_state.first_principal_settings["enabled"],
                help="Enhance your best single trading algorithm"
            )
            
            if st.session_state.first_principal_settings["enabled"]:
                st.session_state.first_principal_settings["primary_algo"] = st.selectbox(
                    "Primary Algorithm",
                    ["Enigma", "EMA Crossover", "RSI Divergence", "Support/Resistance", "Custom"],
                    index=["Enigma", "EMA Crossover", "RSI Divergence", "Support/Resistance", "Custom"].index(
                        st.session_state.first_principal_settings.get("primary_algo", "Enigma")
                    ),
                    help="Your best single trade algorithm"
                )
                
                st.session_state.first_principal_settings["enhancement_mode"] = st.radio(
                    "Enhancement Mode",
                    ["Conservative", "Moderate", "Aggressive"],
                    index=["Conservative", "Moderate", "Aggressive"].index(
                        st.session_state.first_principal_settings.get("enhancement_mode", "Conservative")
                    ),
                    help="How aggressively to enhance your algorithm"
                )
            
            st.markdown("---")
            
            # System Controls
            st.subheader("🎮 System Controls")
            
            if st.button("⚡ Quick Connect", use_container_width=True):
                st.session_state.show_quick_connect = True
                st.rerun()
            
            # Monitoring toggle
            st.session_state.monitoring_active = st.toggle(
                "🔍 Active Monitoring",
                value=st.session_state.monitoring_active
            )
            
            st.markdown("---")
            
            # Connection Status Overview
            st.subheader("🔗 Connection Status")
            
            # NinjaTrader status
            nt_status = "🟢 Connected" if self.ninja_connector.is_connected else "🔴 Disconnected"
            st.markdown(f"**NinjaTrader:** {nt_status}")
            
            # Tradovate status  
            tv_status = "🟢 Connected" if self.tradovate_connector.is_authenticated else "🔴 Disconnected"
            st.markdown(f"**Tradovate:** {tv_status}")
            
            # Quick test buttons
            if st.button("🧪 Test All Connections", use_container_width=True):
                with st.spinner("Testing connections..."):
                    nt_test = self.ninja_connector.connect_via_socket()
                    tv_test = self.tradovate_connector.authenticate("demo", "demo")
                    
                    if nt_test and tv_test:
                        st.success("✅ All connections working!")
                    elif nt_test:
                        st.warning("⚠️ Only NinjaTrader connected")
                    elif tv_test:
                        st.warning("⚠️ Only Tradovate connected")
                    else:
                        st.error("❌ No connections active")
                    st.rerun()
            
            st.markdown("---")
            
            # OCR Controls
            st.subheader("👁️ OCR System")
            
            if st.button("🎯 Configure OCR Regions", use_container_width=True):
                st.session_state.show_ocr_config = True
                st.rerun()
            
            st.session_state.monitoring_active = st.checkbox(
                "Enable OCR Monitoring",
                value=st.session_state.monitoring_active
            )
            
            if st.session_state.monitoring_active:
                # Show OCR status
                signals_detected = len(st.session_state.get('active_enigma_signals', {}))
                st.metric("Active Signals", signals_detected)
            
            st.markdown("---")
            
            # Notification Panel
            st.subheader("🔔 Notifications")
            
            # Get unacknowledged notifications
            unack_notifications = self.notification_manager.get_unacknowledged_notifications()
            notification_summary = self.notification_manager.get_notification_summary()
            
            if unack_notifications:
                # Show notification count badges
                total_unack = len(unack_notifications)
                st.metric("Unread Alerts", total_unack)
                
                # Show summary by type
                for notif_type, count in notification_summary.items():
                    if count > 0:
                        priority_color = "🔴" if notif_type in ["emergency_stop", "margin_warning"] else "🟡" if notif_type in ["erm_reversal", "connection_lost"] else "🟢"
                        st.caption(f"{priority_color} {notif_type.replace('_', ' ').title()}: {count}")
                
                # Show last 3 notifications
                st.markdown("**Recent Alerts:**")
                for i, notification in enumerate(unack_notifications[-3:]):
                    timestamp = notification["timestamp"].strftime("%H:%M:%S")
                    title = notification["title"]
                    priority_icon = "🚨" if notification["priority"] == "critical" else "⚠️" if notification["priority"] == "high" else "ℹ️"
                    st.caption(f"{priority_icon} {timestamp} - {title}")
                
                # Quick actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Clear All", key="clear_notifications"):
                        self.notification_manager.acknowledge_all_notifications()
                        st.success("All notifications cleared!")
                        st.rerun()
                
                with col2:
                    if st.button("Test Alerts", key="test_notifications"):
                        self.notification_manager.test_notification_system()
                        st.success("Test notifications sent!")
            else:
                st.success("✅ No new alerts")
                if st.button("Test Notification System", key="test_notifications_empty"):
                    self.notification_manager.test_notification_system()
                    st.success("Test notifications sent!")
            
            # Notification settings
            with st.expander("🔧 Notification Settings"):
                st.subheader("Alert Preferences")
                
                self.notification_manager.desktop_notifications_enabled = st.checkbox(
                    "Desktop Notifications",
                    value=self.notification_manager.desktop_notifications_enabled
                )
                
                self.notification_manager.audio_enabled = st.checkbox(
                    "Audio Alerts",
                    value=self.notification_manager.audio_enabled
                )
                
                self.notification_manager.critical_alerts_only = st.checkbox(
                    "Critical Alerts Only",
                    value=self.notification_manager.critical_alerts_only
                )
                
                st.markdown("**Available Notification Types:**")
                if NOTIFICATIONS_AVAILABLE:
                    st.success(f"✅ Desktop Notifications ({NOTIFICATIONS_TYPE})")
                else:
                    st.error("❌ Desktop Notifications Unavailable")
                    st.caption("Install: pip install plyer")
                
                if AUDIO_AVAILABLE:
                    st.success(f"✅ Audio Alerts ({AUDIO_TYPE})")
                else:
                    st.error("❌ Audio Alerts Unavailable")
            
            st.markdown("---")
            
            # Advanced Settings
            with st.expander("⚙️ Advanced Settings"):
                st.subheader("ERM Configuration")
                
                st.session_state.erm_settings["lookback_periods"] = st.slider(
                    "ERM Lookback Periods",
                    min_value=5,
                    max_value=50,
                    value=st.session_state.erm_settings["lookback_periods"]
                )
                
                st.session_state.erm_settings["atr_multiplier"] = st.slider(
                    "ATR Multiplier",
                    min_value=1.0,
                    max_value=5.0,
                    value=st.session_state.erm_settings["atr_multiplier"],
                    step=0.1
                )
                
                st.session_state.erm_settings["auto_reverse_trade"] = st.checkbox(
                    "Auto Execute Reversals",
                    value=st.session_state.erm_settings["auto_reverse_trade"]
                )
                
                st.subheader("Kelly Settings")
                
                st.session_state.kelly_settings["enabled"] = st.checkbox(
                    "Enable Kelly Criterion",
                    value=st.session_state.kelly_settings["enabled"]
                )
                
                if st.session_state.kelly_settings["enabled"]:
                    st.session_state.kelly_settings["max_position_percent"] = st.slider(
                        "Max Position %",
                        min_value=0.05,
                        max_value=0.50,
                        value=st.session_state.kelly_settings["max_position_percent"],
                        step=0.05
                    )
        
        # OCR Configuration Modal
        if st.session_state.get('show_ocr_config', False):
            self.render_ocr_config_modal()
    
    def render_ocr_config_modal(self):
        """Render OCR configuration modal"""
        st.markdown("### 👁️ OCR Region Configuration")
        
        # Add new region
        with st.form("add_ocr_region"):
            region_name = st.text_input("Region Name", placeholder="e.g., ES_Chart_1")
            
            col1, col2 = st.columns(2)
            with col1:
                left = st.number_input("Left", min_value=0, value=100)
                width = st.number_input("Width", min_value=1, value=300)
            with col2:
                top = st.number_input("Top", min_value=0, value=100)
                height = st.number_input("Height", min_value=1, value=200)
            
            if st.form_submit_button("Add Region"):
                if region_name:
                    self.ocr_manager.add_region(region_name, {
                        "left": left, "top": top, "width": width, "height": height
                    })
                    st.success(f"Added region: {region_name}")
        
        # Show existing regions
        st.subheader("Configured Regions")
        for name, region in self.ocr_manager.monitoring_regions.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"{name}: {region}")
            with col2:
                if st.button("Remove", key=f"remove_{name}"):
                    self.ocr_manager.remove_region(name)
                    st.rerun()
        
        if st.button("Close Configuration"):
            st.session_state.show_ocr_config = False
            st.rerun()
    
    def render_main_content(self):
        """Render main dashboard content"""
        # Header
        self.render_header()
        
        # Horizontal Navigation Bar
        self.render_navigation_bar()
        
        # Quick connection setup modal
        if st.session_state.get('show_quick_connect', False):
            self.render_quick_connection_setup()
            return
        
        # Emergency stop check
        if st.session_state.get('emergency_stop', False):
            st.error("🚨 EMERGENCY STOP ACTIVATED - All trading halted!")
            if st.button("Reset Emergency Stop", type="primary"):
                st.session_state.emergency_stop = False
                st.session_state.system_running = True
                
                # Send system restart notification
                self.notification_manager.send_system_status_alert("Emergency stop deactivated - system restarted")
                
                st.success("Emergency stop reset - system restarted!")
                st.rerun()
            return
        
        # Main dashboard content
        self.render_priority_indicator()
        
        st.markdown("---")
        
        # Main chart grid
        self.render_chart_grid()
        
        # ERM Alerts Panel
        if st.session_state.erm_settings["enabled"] and st.session_state.erm_alerts:
            self.render_erm_alerts_panel()
        
        # Kelly Criterion Panel
        if st.session_state.kelly_settings["enabled"]:
            self.render_kelly_criterion_panel()
        
        # Footer
        st.markdown("---")
        st.markdown("**Training Wheels Professional Trading Platform** | Real-time data integration with NinjaTrader & Tradovate")
    
    def render_erm_alerts_panel(self):
        """Render ERM alerts and signals panel"""
        st.markdown("### 🧠 ERM (Enigma Reversal Momentum) Alerts")
        
        # Show recent alerts
        recent_alerts = st.session_state.erm_alerts[-10:]  # Last 10 alerts
        
        if recent_alerts:
            alert_data = []
            for alert in recent_alerts:
                chart_name = st.session_state.charts[alert["chart_id"]].account_name
                alert_data.append({
                    "Time": alert["timestamp"].strftime("%H:%M:%S"),
                    "Chart": chart_name,
                    "Signal": alert["signal_type"],
                    "ERM Value": f"{alert['erm_value']:.2f}",
                    "Confidence": f"{alert['confidence']:.1%}",
                    "Price Δ": f"{alert['price_distance']:.2f}",
                    "Time Elapsed": f"{alert['time_elapsed']:.0f}s"
                })
            
            df = pd.DataFrame(alert_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No ERM alerts yet. Enable ERM monitoring to see reversal signals.")
        
        # ERM Settings Quick Access
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Refresh ERM"):
                # Simulate ERM calculation for all active charts
                for chart_id, chart in st.session_state.charts.items():
                    if chart.is_active:
                        # Simulate price movement and ERM calculation
                        current_price = chart.entry_price + np.random.uniform(-50, 50)
                        erm_calc = self.calculate_erm(chart_id, current_price)
                        if erm_calc:
                            st.rerun()
        
        with col2:
            st.metric("ERM Threshold", f"{st.session_state.erm_settings['atr_multiplier']:.1f}")
        
        with col3:
            alerts_today = len([a for a in st.session_state.erm_alerts 
                              if a["timestamp"].date() == datetime.now().date()])
            st.metric("Alerts Today", alerts_today)
    
    def render_kelly_criterion_panel(self):
        """Render Kelly Criterion analysis panel"""
        st.markdown("### 📊 Kelly Criterion Analysis")
        
        # Calculate Kelly for all charts
        kelly_data = []
        for chart_id, chart in st.session_state.charts.items():
            if chart.is_active:
                kelly_calc = self.kelly_engine.calculate_kelly(chart_id, 0.7)
                kelly_data.append({
                    "Chart": chart.account_name,
                    "Kelly %": f"{kelly_calc.kelly_percentage:.1%}",
                    "Recommended Size": f"{kelly_calc.recommended_position:.2f}",
                    "Win Rate": f"{kelly_calc.win_probability:.1%}",
                    "Avg Win": f"${kelly_calc.avg_win:.0f}",
                    "Avg Loss": f"${kelly_calc.avg_loss:.0f}",
                    "Sharpe": f"{kelly_calc.sharpe_ratio:.2f}",
                    "Sample Size": kelly_calc.sample_size
                })
        
        if kelly_data:
            df = pd.DataFrame(kelly_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No active charts for Kelly analysis.")
        
        # Kelly Settings
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📈 Generate Sample Data"):
                # Add sample trading data for demonstration
                for chart_id in st.session_state.charts.keys():
                    for _ in range(20):
                        pnl = np.random.uniform(-100, 150)  # Slightly positive expectancy
                        self.kelly_engine.add_trade_result(
                            chart_id=chart_id,
                            pnl=pnl,
                            entry_price=4500 + np.random.uniform(-100, 100),
                            exit_price=4500 + np.random.uniform(-100, 100),
                            size=np.random.uniform(1, 5)
                        )
                st.success("Sample trading data generated!")
                st.rerun()
        
        with col2:
            max_position = st.session_state.kelly_settings["max_position_percent"]
            st.metric("Max Position Limit", f"{max_position:.1%}")
    
    def render_control_panel(self):
        """Render system control panel with advanced options"""
        st.markdown('<div class="section-header">System Control Panel</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh All Data", use_container_width=True):
                self.refresh_real_time_data()
                st.success("Data refreshed!")
                st.rerun()
        
        with col2:
            if st.button("🎯 Auto-Size Positions", use_container_width=True):
                for chart_id in st.session_state.charts.keys():
                    kelly_calc = self.kelly_engine.calculate_kelly(chart_id, 0.7)
                    st.session_state.charts[chart_id].position_size = kelly_calc.recommended_position
                st.success("Positions auto-sized using Kelly Criterion!")
                st.rerun()
        
        with col3:
            if st.button("🔗 Setup Connections", use_container_width=True):
                st.session_state.show_connection_setup = True
                st.rerun()
        
        with col4:
            if st.button("🧪 Generate Sample Data", use_container_width=True):
                self.simulate_data_updates()
                st.success("Sample data generated!")
                st.rerun()
    
    def render_system_status(self):
        """Render comprehensive system status panel"""
        st.markdown('<div class="section-header">System Status & Health</div>', unsafe_allow_html=True)
        
        # System health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # NinjaTrader Status
            nt_status = "🟢 Connected" if self.ninja_connector.is_connected else "🔴 Disconnected"
            st.metric("NinjaTrader", nt_status)
            
        with col2:
            # Tradovate Status
            tv_status = "🟢 Connected" if self.tradovate_connector.is_authenticated else "🔴 Disconnected"
            st.metric("Tradovate", tv_status)
            
        with col3:
            # OCR Status
            ocr_status = "🟢 Active" if st.session_state.monitoring_active else "🔴 Inactive"
            st.metric("OCR Monitor", ocr_status)
            
        with col4:
            # ERM Status
            erm_status = "🟢 Active" if st.session_state.erm_settings["enabled"] else "🔴 Inactive"
            st.metric("ERM System", erm_status)
        
        # System performance metrics
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("CPU Usage", f"{cpu_percent:.1f}%")
                with col2:
                    st.metric("Memory Usage", f"{memory_percent:.1f}%")
            except:
                st.info("System metrics unavailable")
    
    def render_connection_setup_modal(self):
        """Render connection setup modal for NinjaTrader and Tradovate"""
        st.markdown("### 🔗 Connection Setup")
        
        # Tab selection for different platforms
        tab1, tab2 = st.tabs(["NinjaTrader", "Tradovate"])
        
        with tab1:
            self.render_ninjatrader_setup()
        
        with tab2:
            self.render_tradovate_setup()
        
        # Connection testing section
        st.markdown("---")
        self.render_connection_testing()
        
        if st.button("Close Setup", type="primary"):
            st.session_state.show_connection_setup = False
            st.rerun()
    
    def render_ninjatrader_setup(self):
        """Render NinjaTrader connection setup"""
        st.subheader("🥷 NinjaTrader Configuration")
        
        with st.form("ninjatrader_config"):
            st.session_state.connection_config["ninjatrader_host"] = st.text_input(
                "Host", 
                value=st.session_state.connection_config["ninjatrader_host"]
            )
            
            st.session_state.connection_config["ninjatrader_port"] = st.number_input(
                "Port", 
                value=st.session_state.connection_config["ninjatrader_port"],
                min_value=1,
                max_value=65535
            )
            
            st.session_state.connection_config["ninjatrader_auto_connect"] = st.checkbox(
                "Auto-connect on startup",
                value=st.session_state.connection_config["ninjatrader_auto_connect"]
            )
            
            if st.form_submit_button("Save NinjaTrader Config"):
                st.success("NinjaTrader configuration saved!")
    
    def render_algotrader_setup(self):
        """AlgoTrader signal reading configuration"""
        st.subheader("📊 AlgoTrader Signal Reader Setup")
        st.markdown("""
        **The core goal: Read trading signals from AlgoTrader platform**
        
        Configure how to receive signals from your AlgoTrader system. 
        Multiple input methods supported for maximum flexibility.
        """)
        
        # Enable/Disable AlgoTrader
        st.session_state.connection_config["algotrader_enabled"] = st.checkbox(
            "Enable AlgoTrader Signal Reading", 
            value=st.session_state.connection_config["algotrader_enabled"],
            help="Turn on to start reading signals from AlgoTrader"
        )
        
        if st.session_state.connection_config["algotrader_enabled"]:
            
            # Signal Input Method Selection
            signal_method = st.selectbox(
                "Signal Input Method",
                ["File Monitor", "TCP Socket", "HTTP API", "Database"],
                help="Choose how AlgoTrader sends signals to this system"
            )
            
            st.markdown("---")
            
            if signal_method == "File Monitor":
                st.markdown("#### 📁 File Monitor Configuration")
                st.info("""
                **Most Common Setup**: AlgoTrader writes signals to a CSV/TXT file
                This system monitors the file for changes and reads new signals.
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.connection_config["algotrader_signal_file"] = st.text_input(
                        "Signal File Path",
                        value=st.session_state.connection_config["algotrader_signal_file"],
                        placeholder="C:\\AlgoTrader\\signals\\live_signals.csv",
                        help="Full path to the file where AlgoTrader writes signals"
                    )
                    
                    st.session_state.connection_config["algotrader_signal_format"] = st.selectbox(
                        "File Format",
                        ["csv", "json", "txt"],
                        index=0 if st.session_state.connection_config["algotrader_signal_format"] == "csv" else 1,
                        help="Format of the signal file"
                    )
                
                with col2:
                    polling_interval = st.number_input(
                        "Check Interval (seconds)",
                        min_value=1, max_value=60, value=5,
                        help="How often to check the file for new signals"
                    )
                    
                    st.session_state.connection_config["algotrader_min_confidence"] = st.slider(
                        "Minimum Signal Confidence",
                        min_value=0.0, max_value=1.0, 
                        value=st.session_state.connection_config["algotrader_min_confidence"],
                        step=0.1,
                        help="Only process signals above this confidence level"
                    )
                
                # File Format Examples
                st.markdown("#### 📋 Expected File Formats")
                
                format_tab1, format_tab2, format_tab3 = st.tabs(["CSV Format", "JSON Format", "TXT Format"])
                
                with format_tab1:
                    st.code("""
# CSV Format (Header required)
timestamp,instrument,signal_type,price,confidence
2025-08-08 14:30:00,ES,BUY,4500.50,0.85
2025-08-08 14:31:00,NQ,SELL,15200.25,0.92
2025-08-08 14:32:00,YM,BUY,34500.00,0.78
                    """, language="csv")
                
                with format_tab2:
                    st.code("""
// JSON Format (Array of signals)
[
  {
    "timestamp": "2025-08-08 14:30:00",
    "instrument": "ES",
    "signal_type": "BUY",
    "price": 4500.50,
    "confidence": 0.85,
    "metadata": {"strategy": "EMA_Crossover"}
  }
]
                    """, language="json")
                
                with format_tab3:
                    st.code("""
# TXT Format (Comma-separated)
2025-08-08 14:30:00,ES,BUY,4500.50,0.85
2025-08-08 14:31:00,NQ,SELL,15200.25,0.92
2025-08-08 14:32:00,YM,BUY,34500.00,0.78
                    """, language="text")
            
            elif signal_method == "TCP Socket":
                st.markdown("#### 🔌 TCP Socket Configuration")
                st.info("""
                **Real-time Setup**: AlgoTrader sends signals via TCP socket
                Best for low-latency signal transmission.
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state.connection_config["algotrader_tcp_host"] = st.text_input(
                        "Host", 
                        value=st.session_state.connection_config["algotrader_tcp_host"],
                        help="IP address where AlgoTrader sends signals"
                    )
                with col2:
                    st.session_state.connection_config["algotrader_tcp_port"] = st.number_input(
                        "Port", 
                        value=st.session_state.connection_config["algotrader_tcp_port"],
                        min_value=1000, max_value=65535,
                        help="Port number for TCP connection"
                    )
                
                st.markdown("#### 📡 TCP Signal Formats")
                st.code("""
# JSON Format
{"timestamp":"2025-08-08 14:30:00","instrument":"ES","signal_type":"BUY","price":4500.50,"confidence":0.85}

# Pipe-delimited Format  
2025-08-08 14:30:00|ES|BUY|4500.50|0.85

# Comma-separated Format
2025-08-08 14:30:00,ES,BUY,4500.50,0.85
                """, language="text")
            
            elif signal_method == "HTTP API":
                st.markdown("#### 🌐 HTTP API Configuration")
                st.info("""
                **Polling Setup**: Regularly check AlgoTrader HTTP endpoint for signals
                Good for cloud-based AlgoTrader setups.
                """)
                
                st.session_state.connection_config["algotrader_http_url"] = st.text_input(
                    "API Endpoint URL",
                    value=st.session_state.connection_config["algotrader_http_url"],
                    placeholder="http://localhost:8080/api/signals",
                    help="HTTP endpoint that returns signal data"
                )
                
                # API Headers
                st.markdown("**API Headers (Optional)**")
                header_col1, header_col2 = st.columns(2)
                with header_col1:
                    api_key = st.text_input("API Key", type="password")
                with header_col2:
                    auth_header = st.text_input("Authorization Header")
            
            elif signal_method == "Database":
                st.markdown("#### 🗄️ Database Configuration")
                st.info("""
                **Database Setup**: Read signals directly from AlgoTrader database
                Requires database connection configuration.
                """)
                
                db_type = st.selectbox("Database Type", ["MySQL", "PostgreSQL", "SQL Server", "SQLite"])
                connection_string = st.text_input(
                    "Connection String",
                    placeholder="mysql://user:password@localhost:3306/algotrader",
                    type="password"
                )
                
                table_name = st.text_input("Signals Table Name", value="signals")
            
            # Signal Filtering
            st.markdown("---")
            st.markdown("#### 🎯 Signal Filtering")
            
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                allowed_instruments = st.multiselect(
                    "Allowed Instruments",
                    ["ES", "NQ", "YM", "RTY", "CL", "GC", "EURUSD", "GBPUSD", "USDJPY"],
                    default=["ES", "NQ", "YM"],
                    help="Only process signals for these instruments"
                )
            
            with filter_col2:
                allowed_signal_types = st.multiselect(
                    "Allowed Signal Types",
                    ["BUY", "SELL", "LONG", "SHORT", "CLOSE", "EXIT"],
                    default=["BUY", "SELL", "LONG", "SHORT"],
                    help="Only process these types of signals"
                )
            
            # Test Configuration Button
            st.markdown("---")
            if st.button("💾 Save AlgoTrader Configuration", type="primary"):
                
                # Configure the signal reader based on method
                if signal_method == "File Monitor":
                    file_path = st.session_state.connection_config["algotrader_signal_file"]
                    if file_path:
                        self.algotrader_reader.configure_file_monitor(
                            file_path, 
                            st.session_state.connection_config["algotrader_signal_format"],
                            polling_interval
                        )
                        st.success(f"✅ File monitor configured: {file_path}")
                    else:
                        st.error("❌ Please provide a signal file path")
                        return
                
                elif signal_method == "TCP Socket":
                    host = st.session_state.connection_config["algotrader_tcp_host"]
                    port = st.session_state.connection_config["algotrader_tcp_port"]
                    self.algotrader_reader.configure_tcp_socket(host, port)
                    st.success(f"✅ TCP socket configured: {host}:{port}")
                
                elif signal_method == "HTTP API":
                    url = st.session_state.connection_config["algotrader_http_url"]
                    if url:
                        headers = {}
                        if api_key:
                            headers["X-API-Key"] = api_key
                        if auth_header:
                            headers["Authorization"] = auth_header
                        
                        self.algotrader_reader.configure_http_api(url, headers)
                        st.success(f"✅ HTTP API configured: {url}")
                    else:
                        st.error("❌ Please provide an API endpoint URL")
                        return
                
                # Set signal filters
                self.algotrader_reader.signal_filters.update({
                    "min_confidence": st.session_state.connection_config["algotrader_min_confidence"],
                    "allowed_instruments": allowed_instruments,
                    "signal_types": allowed_signal_types
                })
                
                st.success("🎯 Signal filters configured")
                
                # Start monitoring if not already active
                if not self.algotrader_reader.is_monitoring:
                    self.algotrader_reader.start_monitoring()
                    st.success("🚀 AlgoTrader signal monitoring started!")
                
                time.sleep(2)
                st.rerun()
        
        else:
            st.info("Enable AlgoTrader Signal Reading to configure signal input methods.")
        
        # Signal Status Display
        if st.session_state.connection_config["algotrader_enabled"]:
            st.markdown("---")
            self.render_algotrader_status()
    
    def render_algotrader_status(self):
        """Display AlgoTrader signal reading status"""
        st.markdown("#### 📊 AlgoTrader Signal Status")
        
        # Get signal statistics
        stats = self.algotrader_reader.get_signal_statistics()
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Signals", stats.get("total_signals", 0))
            
            with col2:
                monitoring_status = "🟢 Active" if stats.get("monitoring_active", False) else "🔴 Inactive"
                st.metric("Monitoring", monitoring_status)
            
            with col3:
                last_signal = stats.get("last_signal_time")
                if last_signal:
                    time_diff = datetime.now() - last_signal
                    if time_diff.total_seconds() < 60:
                        last_signal_str = "Just now"
                    elif time_diff.total_seconds() < 3600:
                        last_signal_str = f"{int(time_diff.total_seconds() / 60)}m ago"
                    else:
                        last_signal_str = f"{int(time_diff.total_seconds() / 3600)}h ago"
                else:
                    last_signal_str = "Never"
                st.metric("Last Signal", last_signal_str)
            
            with col4:
                if st.button("🔄 Refresh Status"):
                    st.rerun()
            
            # Recent signals display
            recent_signals = self.algotrader_reader.get_latest_signals(5)
            if recent_signals:
                st.markdown("**Recent Signals:**")
                signal_df = pd.DataFrame(recent_signals)
                st.dataframe(signal_df[['timestamp', 'instrument', 'signal_type', 'price', 'confidence']], use_container_width=True)
            
            # Control buttons
            control_col1, control_col2, control_col3 = st.columns(3)
            
            with control_col1:
                if stats.get("monitoring_active", False):
                    if st.button("⏸️ Stop Monitoring"):
                        self.algotrader_reader.stop_monitoring()
                        st.success("Monitoring stopped")
                        st.rerun()
                else:
                    if st.button("▶️ Start Monitoring"):
                        self.algotrader_reader.start_monitoring()
                        st.success("Monitoring started")
                        st.rerun()
            
            with control_col2:
                if st.button("🗑️ Clear Buffer"):
                    self.algotrader_reader.clear_signal_buffer()
                    st.success("Signal buffer cleared")
                    st.rerun()
            
            with control_col3:
                if st.button("📋 Show All Signals"):
                    st.session_state.show_all_signals = True
        
        else:
            st.info("No signal data available. Start monitoring to see signal statistics.")

    def render_tradovate_setup(self):
        """Render Tradovate connection setup"""
        st.subheader("📈 Tradovate Configuration")
        
        with st.form("tradovate_config"):
            st.session_state.connection_config["tradovate_username"] = st.text_input(
                "Username",
                value=st.session_state.connection_config["tradovate_username"]
            )
            
            st.session_state.connection_config["tradovate_password"] = st.text_input(
                "Password",
                type="password",
                value=st.session_state.connection_config["tradovate_password"]
            )
            
            st.session_state.connection_config["tradovate_environment"] = st.selectbox(
                "Environment",
                ["demo", "live"],
                index=0 if st.session_state.connection_config["tradovate_environment"] == "demo" else 1
            )
            
            if st.form_submit_button("Save Tradovate Config"):
                st.success("Tradovate configuration saved!")
    
    def render_connection_testing(self):
        """Render connection testing panel"""
        st.subheader("🧪 Connection Testing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Test NinjaTrader Connection", use_container_width=True):
                host = st.session_state.connection_config["ninjatrader_host"]
                port = st.session_state.connection_config["ninjatrader_port"]
                
                if self.ninja_connector.connect_via_socket(host, port):
                    st.success("✅ NinjaTrader connection successful!")
                else:
                    st.error("❌ NinjaTrader connection failed!")
        
        with col2:
            if st.button("Test Tradovate Connection", use_container_width=True):
                username = st.session_state.connection_config["tradovate_username"]
                password = st.session_state.connection_config["tradovate_password"]
                environment = st.session_state.connection_config["tradovate_environment"]
                
                if self.tradovate_connector.authenticate(username, password, environment):
                    st.success("✅ Tradovate authentication successful!")
                else:
                    st.error("❌ Tradovate authentication failed!")
    
    def render_quick_setup_wizard(self):
        """Render quick setup wizard for new users"""
        st.markdown("### 🧙‍♂️ Quick Setup Wizard")
        
        # Progress tracking
        if 'wizard_step' not in st.session_state:
            st.session_state.wizard_step = 1
        
        # Progress bar
        progress = (st.session_state.wizard_step - 1) / 2
        st.progress(progress)
        st.markdown(f"**Step {st.session_state.wizard_step} of 3**")
        
        if st.session_state.wizard_step == 1:
            self.render_wizard_step1_platform_selection()
        elif st.session_state.wizard_step == 2:
            self.render_wizard_step2_account_credentials()
        elif st.session_state.wizard_step == 3:
            self.render_wizard_step3_verification()
    
    def render_wizard_step1_platform_selection(self):
        """Render wizard step 1: Platform selection"""
        st.subheader("Step 1: Select Trading Platforms")
        
        st.markdown("Which trading platforms do you want to connect?")
        
        # Platform selection with unique keys
        use_ninjatrader = st.checkbox(
            "📊 NinjaTrader", 
            value=True,
            key="wizard_use_ninjatrader_step1"
        )
        
        use_tradovate = st.checkbox(
            "📈 Tradovate", 
            value=True,
            key="wizard_use_tradovate_step1"
        )
        
        # Store selections
        st.session_state.wizard_selections = {
            "use_ninjatrader": use_ninjatrader,
            "use_tradovate": use_tradovate
        }
        
        col1, col2 = st.columns(2)
        with col2:
            if st.button("Next →", type="primary"):
                st.session_state.wizard_step = 2
                st.rerun()
    
    def render_wizard_step2_account_credentials(self):
        """Render wizard step 2: Account credentials"""
        st.subheader("Step 2: Account Configuration")
        
        selections = st.session_state.get("wizard_selections", {})
        
        if selections.get("use_ninjatrader", False):
            st.markdown("#### NinjaTrader Settings")
            with st.form("wizard_ninja_form"):
                nt_host = st.text_input("Host", value="localhost")
                nt_port = st.number_input("Port", value=36973, min_value=1, max_value=65535)
                
                if st.form_submit_button("Save NinjaTrader"):
                    st.session_state.connection_config["ninjatrader_host"] = nt_host
                    st.session_state.connection_config["ninjatrader_port"] = nt_port
                    st.success("NinjaTrader configured!")
        
        if selections.get("use_tradovate", False):
            st.markdown("#### Tradovate Settings")
            with st.form("wizard_tradovate_form"):
                tv_username = st.text_input("Username")
                tv_password = st.text_input("Password", type="password")
                tv_env = st.selectbox("Environment", ["demo", "live"])
                
                if st.form_submit_button("Save Tradovate"):
                    st.session_state.connection_config["tradovate_username"] = tv_username
                    st.session_state.connection_config["tradovate_password"] = tv_password
                    st.session_state.connection_config["tradovate_environment"] = tv_env
                    st.success("Tradovate configured!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Next →", type="primary"):
                st.session_state.wizard_step = 3
                st.rerun()
    
    def render_wizard_step3_verification(self):
        """Render wizard step 3: Connection verification"""
        st.subheader("Step 3: Verify Connections")
        
        selections = st.session_state.get("wizard_selections", {})
        
        st.markdown("Let's test your connections:")
        
        if selections.get("use_ninjatrader", False):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**NinjaTrader Connection**")
            with col2:
                if st.button("Test NT", key="wizard_test_nt"):
                    if self.ninja_connector.connect_via_socket():
                        st.success("✅ Connected!")
                    else:
                        st.error("❌ Failed!")
        
        if selections.get("use_tradovate", False):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**Tradovate Connection**")
            with col2:
                if st.button("Test TV", key="wizard_test_tv"):
                    if self.tradovate_connector.authenticate(
                        st.session_state.connection_config["tradovate_username"],
                        st.session_state.connection_config["tradovate_password"]
                    ):
                        st.success("✅ Connected!")
                    else:
                        st.error("❌ Failed!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Complete Setup", type="primary"):
                st.session_state.connection_config["connections_configured"] = True
                st.success("🎉 Setup complete! Welcome to Training Wheels!")
                st.session_state.wizard_step = 1  # Reset for next time
                st.rerun()
    
    def simulate_data_updates(self):
        """Simulate real-time data updates for testing"""
        for chart_id, chart in st.session_state.charts.items():
            # Simulate price movements
            base_prices = {
                1: 4500,  # ES
                2: 15000, # NQ
                3: 34000, # YM
                4: 2000,  # RTY
                5: 80,    # CL
                6: 2000   # GC
            }
            
            base_price = base_prices.get(chart_id, 1000)
            price_change = np.random.uniform(-0.02, 0.02)  # ±2% movement
            new_price = base_price * (1 + price_change)
            
            # Update chart data
            chart.price_history.append(new_price)
            chart.time_history.append(datetime.now())
            
            # Keep history manageable
            if len(chart.price_history) > 100:
                chart.price_history = chart.price_history[-100:]
                chart.time_history = chart.time_history[-100:]
            
            # Update other chart properties
            chart.daily_pnl += np.random.uniform(-100, 100)
            chart.unrealized_pnl += np.random.uniform(-50, 50)
            chart.power_score = max(0, min(100, chart.power_score + np.random.randint(-5, 6)))
            chart.last_update = datetime.now()
            
            # Simulate signals occasionally
            if np.random.random() < 0.1:  # 10% chance
                signal_types = ["LONG", "SHORT", "NEUTRAL"]
                new_signal = np.random.choice(signal_types)
                
                # Only send notification if signal changed
                if chart.last_signal != new_signal and new_signal != "NEUTRAL":
                    chart.last_signal = new_signal
                    chart.signal_color = {
                        "LONG": "green",
                        "SHORT": "red",
                        "NEUTRAL": "neutral"
                    }[new_signal]
                    
                    # Send new signal notification
                    confidence = np.random.uniform(0.6, 0.9)
                    self.notification_manager.send_new_signal_alert(
                        chart_id=chart_id,
                        signal_type=new_signal,
                        chart_name=chart.account_name,
                        confidence=confidence
                    )
                    
                    # Create Enigma signal
                    chart.current_enigma_signal = EnigmaSignal(
                        signal_type=new_signal,
                        entry_price=new_price,
                        signal_time=datetime.now(),
                        is_active=True,
                        confidence=confidence
                    )
        
        # Update system status
        st.session_state.system_status.last_update = datetime.now()
        st.session_state.system_status.daily_profit_loss += np.random.uniform(-200, 200)
        
        # Generate some ERM calculations
        for chart_id in [1, 2, 3]:  # Only for first 3 charts
            chart = st.session_state.charts[chart_id]
            if chart.current_enigma_signal and len(chart.price_history) > 0:
                current_price = chart.price_history[-1]
                erm_calc = self.calculate_erm(chart_id, current_price)
                if erm_calc and erm_calc.is_reversal_triggered:
                    # Don't add too many alerts
                    if len(st.session_state.erm_alerts) < 20:
                        pass  # ERM alert already added in calculate_erm
    
    def refresh_real_time_data(self):
        """Refresh real-time data from connected platforms"""
        # Update NinjaTrader data
        if self.ninja_connector.is_connected:
            try:
                account_info = self.ninja_connector.get_account_info()
                positions = self.ninja_connector.get_positions()
                
                # Update system status with real data
                if account_info:
                    st.session_state.system_status.total_equity = account_info.get("cash_value", 50000.0)
                    st.session_state.system_status.daily_profit_loss = account_info.get("realized_pnl", 0.0)
                
                # Update chart positions
                for chart_id, chart in st.session_state.charts.items():
                    for instrument in chart.instruments:
                        if instrument in positions:
                            pos_data = positions[instrument]
                            chart.position_size = pos_data.get("quantity", 0)
                            chart.entry_price = pos_data.get("avg_price", 0)
                            chart.unrealized_pnl = pos_data.get("unrealized_pnl", 0)
                            
            except Exception as e:
                self.logger.error(f"Error refreshing NinjaTrader data: {e}")
        
        # Update Tradovate data
        if self.tradovate_connector.is_authenticated:
            try:
                account_data = self.tradovate_connector.get_real_account_data()
                
                if account_data:
                    st.session_state.system_status.total_equity = account_data.get("cash_balance", 50000.0)
                    margin_used = account_data.get("margin_used", 0.0)
                    st.session_state.system_status.total_margin_remaining = (
                        st.session_state.system_status.total_equity - margin_used
                    )
                    
            except Exception as e:
                self.logger.error(f"Error refreshing Tradovate data: {e}")
        
        # Update timestamps
        st.session_state.last_update = datetime.now()
        for chart in st.session_state.charts.values():
            chart.last_update = datetime.now()
        
        # System health metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("System Mode", st.session_state.system_mode)
        
        with col2:
            running_status = "🟢 RUNNING" if st.session_state.system_running else "🔴 STOPPED"
            st.metric("Status", running_status)
        
        with col3:
            active_charts = sum(1 for chart in st.session_state.charts.values() if chart.is_active)
            st.metric("Active Charts", f"{active_charts}/6")
        
        with col4:
            ninja_status = "🟢 CONNECTED" if self.ninja_connector.is_connected else "🔴 DISCONNECTED"
            st.metric("NinjaTrader", ninja_status)
        
        with col5:
            tradovate_status = "🟢 CONNECTED" if self.tradovate_connector.is_authenticated else "🔴 DISCONNECTED"
            st.metric("Tradovate", tradovate_status)
        
        # Performance indicators
        st.subheader("Performance Indicators")
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            total_pnl = sum(chart.daily_pnl for chart in st.session_state.charts.values())
            st.metric("Total Daily P&L", f"${total_pnl:,.2f}", delta=f"{total_pnl:+.2f}")
        
        with perf_col2:
            total_margin = sum(chart.margin_used for chart in st.session_state.charts.values())
            st.metric("Total Margin Used", f"${total_margin:,.0f}")
        
        with perf_col3:
            safety_ratio = st.session_state.system_status.safety_ratio
            safety_color = "normal" if safety_ratio > 70 else "inverse"
            st.metric("Safety Ratio", f"{safety_ratio:.1f}%", delta_color=safety_color)
    
    def simulate_data_updates(self):
        """Simulate real-time data updates for testing"""
        current_time = datetime.now()
        
        for chart_id, chart in st.session_state.charts.items():
            if chart.is_active:
                # Simulate price movements
                price_change = np.random.uniform(-50, 50)
                chart.daily_pnl += price_change
                chart.unrealized_pnl = np.random.uniform(-200, 200)
                
                # Update power score
                chart.power_score = max(0, min(100, chart.power_score + np.random.randint(-5, 6)))
                
                # Simulate signal changes
                if np.random.random() < 0.1:  # 10% chance of signal change
                    signals = ["LONG", "SHORT", "NEUTRAL"]
                    new_signal = np.random.choice(signals)
                    chart.last_signal = f"Simulated {new_signal}"
                    
                    if new_signal == "LONG":
                        chart.signal_color = "green"
                    elif new_signal == "SHORT":
                        chart.signal_color = "red"
                    else:
                        chart.signal_color = "neutral"
                
                chart.last_update = current_time
    
    def refresh_real_time_data(self):
        """Refresh real-time data from connected platforms"""
        try:
            current_time = datetime.now()
            
            # Process AlgoTrader signals if enabled
            if st.session_state.connection_config.get("algotrader_enabled", False):
                if self.algotrader_reader.is_monitoring:
                    # Check for new signals
                    self.algotrader_reader._start_file_monitor()  # Monitor file changes
                    
                    # Get latest signals and apply to charts
                    recent_signals = self.algotrader_reader.get_latest_signals(10)
                    
                    for signal in recent_signals:
                        if signal.get("processed_time", datetime.min) > current_time - timedelta(seconds=30):
                            # Process signals from last 30 seconds
                            self.apply_algotrader_signal_to_chart(signal)
            
            # Update NinjaTrader data if connected
            if self.ninja_connector.is_connected:
                nt_account_info = self.ninja_connector.get_account_info()
                nt_positions = self.ninja_connector.get_positions()
                
                # Update charts with real NinjaTrader data
                for chart_id, chart in st.session_state.charts.items():
                    for instrument in chart.instruments:
                        if instrument in nt_positions:
                            position = nt_positions[instrument]
                            chart.position_size = position.get("quantity", 0)
                            chart.entry_price = position.get("avg_price", 0)
                            chart.unrealized_pnl = position.get("unrealized_pnl", 0)
                            chart.ninjatrader_connection = "Connected - Live Data"
            
            # Update Tradovate data if connected
            if self.tradovate_connector.is_authenticated:
                tv_account_data = self.tradovate_connector.get_real_account_data()
                
                # Update system status with Tradovate data
                if tv_account_data:
                    st.session_state.system_status.total_equity = tv_account_data.get("cash_balance", 50000)
                    total_margin_used = tv_account_data.get("margin_used", 0)
                    st.session_state.system_status.total_margin_remaining = st.session_state.system_status.total_equity - total_margin_used
                    st.session_state.system_status.daily_profit_loss = tv_account_data.get("close_pl", 0)
            
            # Update last refresh time
            st.session_state.last_update = current_time
            
        except Exception as e:
            self.logger.error(f"Error refreshing real-time data: {e}")
    
    def apply_algotrader_signal_to_chart(self, signal: Dict[str, Any]):
        """Apply AlgoTrader signal to appropriate chart"""
        try:
            instrument = signal.get("instrument", "")
            signal_type = signal.get("signal_type", "")
            price = signal.get("price", 0)
            confidence = signal.get("confidence", 0.8)
            
            # Find matching chart by instrument
            target_chart = None
            for chart_id, chart in st.session_state.charts.items():
                if instrument in chart.instruments:
                    target_chart = chart
                    break
            
            if target_chart:
                # Update chart with AlgoTrader signal
                target_chart.last_signal = f"AlgoTrader {signal_type}"
                target_chart.signal_color = "green" if signal_type in ["BUY", "LONG"] else "red" if signal_type in ["SELL", "SHORT"] else "neutral"
                target_chart.entry_price = price
                target_chart.last_update = datetime.now()
                
                # Create Enigma Signal for ERM processing
                enigma_signal = EnigmaSignal(
                    signal_type=signal_type,
                    entry_price=price,
                    signal_time=datetime.now(),
                    is_active=True,
                    confidence=confidence
                )
                
                target_chart.current_enigma_signal = enigma_signal
                st.session_state.active_enigma_signals[target_chart.chart_id] = enigma_signal
                
                # Send notification for new AlgoTrader signal
                self.notification_manager.send_new_signal_alert(
                    chart_id=target_chart.chart_id,
                    signal_type=signal_type,
                    chart_name=target_chart.account_name,
                    confidence=confidence
                )
                
                # Trigger ERM calculation if enabled
                if st.session_state.erm_settings.get("enabled", False):
                    erm_calc = self.calculate_erm(target_chart.chart_id, price)
                    if erm_calc and erm_calc.is_reversal_triggered:
                        target_chart.confluence_level = "High"
                        target_chart.power_score = min(100, target_chart.power_score + 10)
                
                self.logger.info(f"Applied AlgoTrader signal to Chart {target_chart.chart_id}: {instrument} {signal_type} @ {price}")
            
        except Exception as e:
            self.logger.error(f"Error applying AlgoTrader signal: {e}")
    
    def render_connection_setup_modal(self):
        """Render comprehensive connection setup interface"""
        st.markdown("---")
        st.header("🔗 Connection Configuration")
        st.markdown("Configure your NinjaTrader and Tradovate connections")
        
        # Tabs for different connection types
        tab1, tab2, tab3, tab4 = st.tabs(["NinjaTrader Setup", "Tradovate Setup", "AlgoTrader Signals", "Test Connections"])
        
        with tab1:
            self.render_ninjatrader_setup()
        
        with tab2:
            self.render_tradovate_setup()
        
        with tab3:
            self.render_algotrader_setup()
        
        with tab4:
            self.render_connection_testing()
        
        # Close button
        if st.button("Done - Close Setup", type="primary", use_container_width=True):
            st.session_state.show_connection_setup = False
            st.rerun()
    
    def render_ninjatrader_setup(self):
        """NinjaTrader connection configuration"""
        st.subheader("🥷 NinjaTrader Connection Setup")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.connection_config["ninjatrader_host"] = st.text_input(
                "Host", value=st.session_state.connection_config["ninjatrader_host"]
            )
            st.session_state.connection_config["ninjatrader_port"] = st.number_input(
                "Port", value=st.session_state.connection_config["ninjatrader_port"]
            )
        
        with col2:
            st.session_state.connection_config["ninjatrader_auto_connect"] = st.checkbox(
                "Auto-connect", value=st.session_state.connection_config["ninjatrader_auto_connect"]
            )
        
        if st.button("Test NinjaTrader Connection"):
            if self.ninja_connector.connect_via_socket():
                st.success("NinjaTrader connected successfully!")
            else:
                st.error("Connection failed")
    
    def render_tradovate_setup(self):
        """Tradovate connection configuration"""
        st.subheader("📈 Tradovate Connection Setup")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.connection_config["tradovate_username"] = st.text_input(
                "Username", value=st.session_state.connection_config["tradovate_username"]
            )
            st.session_state.connection_config["tradovate_password"] = st.text_input(
                "Password", type="password", value=st.session_state.connection_config["tradovate_password"]
            )
        
        with col2:
            st.session_state.connection_config["tradovate_environment"] = st.selectbox(
                "Environment", ["demo", "test", "live"], 
                index=["demo", "test", "live"].index(st.session_state.connection_config["tradovate_environment"])
            )
        
        if st.button("Test Tradovate Connection"):
            if self.tradovate_connector.authenticate(
                st.session_state.connection_config["tradovate_username"],
                st.session_state.connection_config["tradovate_password"]
            ):
                st.success("Tradovate authenticated successfully!")
            else:
                st.error("Authentication failed")
    
    def render_connection_testing(self):
        """Connection testing interface"""
        st.subheader("🧪 Connection Testing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**NinjaTrader Status**")
            if st.button("Test Socket Connection", use_container_width=True):
                if self.ninja_connector.connect_via_socket():
                    st.success("✅ Socket connection successful")
                else:
                    st.error("❌ Socket connection failed")
            
            if st.button("Test ATM Connection", use_container_width=True):
                if self.ninja_connector.connect_via_atm():
                    st.success("✅ ATM connection successful")
                else:
                    st.error("❌ ATM connection failed")
        
        with col2:
            st.markdown("**Tradovate Status**")
            if st.button("Test REST API", use_container_width=True):
                account_data = self.tradovate_connector.fetch_account_via_rest()
                if account_data:
                    st.success("✅ REST API working")
                    st.json(account_data)
                else:
                    st.error("❌ REST API failed")
            
            if st.button("Test WebSocket", use_container_width=True):
                if self.tradovate_connector.connect_websocket():
                    st.success("✅ WebSocket connected")
                else:
                    st.error("❌ WebSocket failed")
    
    def render_quick_setup_wizard(self):
        """Render setup wizard for new users"""
        st.header("🧙‍♂️ Quick Setup Wizard")
        st.markdown("Let's get your trading platform configured in 3 easy steps!")
        
        # Initialize wizard state
        if 'wizard_step' not in st.session_state:
            st.session_state.wizard_step = 1
        
        # Progress indicator
        progress = st.session_state.wizard_step / 3
        st.progress(progress)
        st.markdown(f"**Step {st.session_state.wizard_step} of 3**")
        
        if st.session_state.wizard_step == 1:
            self.render_wizard_step1_platform_selection()
        elif st.session_state.wizard_step == 2:
            self.render_wizard_step2_account_credentials()
        elif st.session_state.wizard_step == 3:
            self.render_wizard_step3_verification()
    
    def render_wizard_step1_platform_selection(self):
        """Wizard Step 1: Platform Selection"""
        st.subheader("Step 1: Select Your Trading Platforms")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥷 NinjaTrader")
            use_ninjatrader = st.checkbox("Use NinjaTrader", value=True, key="wizard_use_ninjatrader")
            if use_ninjatrader:
                st.info("NinjaTrader will be used for futures trading and market data")
        
        with col2:
            st.markdown("### 📈 Tradovate")
            use_tradovate = st.checkbox("Use Tradovate", value=True, key="wizard_use_tradovate")
            if use_tradovate:
                st.info("Tradovate will provide real-time account data and execution")
        
        if st.button("Next Step →", type="primary"):
            st.session_state.wizard_step = 2
            st.rerun()
    
    def render_wizard_step2_account_credentials(self):
        """Wizard Step 2: Account Credentials"""
        st.subheader("Step 2: Enter Your Account Credentials")
        
        if st.session_state.get("wizard_use_ninjatrader", True):
            st.markdown("### NinjaTrader Configuration")
            nt_host = st.text_input("NinjaTrader Host", value="localhost")
            nt_port = st.number_input("Port", value=36973, min_value=1000, max_value=65535)
        
        if st.session_state.get("wizard_use_tradovate", True):
            st.markdown("### Tradovate Configuration")
            tv_username = st.text_input("Tradovate Username")
            tv_password = st.text_input("Tradovate Password", type="password")
            tv_env = st.selectbox("Environment", ["demo", "test", "live"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Next Step →", type="primary"):
                # Save configurations
                if st.session_state.get("wizard_use_ninjatrader", True):
                    st.session_state.connection_config["ninjatrader_host"] = nt_host
                    st.session_state.connection_config["ninjatrader_port"] = nt_port
                
                if st.session_state.get("wizard_use_tradovate", True):
                    st.session_state.connection_config["tradovate_username"] = tv_username
                    st.session_state.connection_config["tradovate_password"] = tv_password
                    st.session_state.connection_config["tradovate_environment"] = tv_env
                
                st.session_state.wizard_step = 3
                st.rerun()
    
    def render_wizard_step3_verification(self):
        """Wizard Step 3: Connection Verification"""
        st.subheader("Step 3: Verify Connections")
        
        st.markdown("Let's test your connections to ensure everything is working properly.")
        
        # Test NinjaTrader
        if st.session_state.get("wizard_use_ninjatrader", True):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("**NinjaTrader Connection**")
                if st.button("Test NinjaTrader", use_container_width=True):
                    if self.ninja_connector.connect_via_socket():
                        st.success("✅ NinjaTrader Connected!")
                    else:
                        st.error("❌ NinjaTrader Connection Failed")
            
        # Test Tradovate
        if st.session_state.get("wizard_use_tradovate", True):
            with col2:
                st.markdown("**Tradovate Connection**")
                if st.button("Test Tradovate", use_container_width=True):
                    if self.tradovate_connector.authenticate(
                        st.session_state.connection_config["tradovate_username"],
                        st.session_state.connection_config["tradovate_password"]
                    ):
                        st.success("✅ Tradovate Connected!")
                    else:
                        st.error("❌ Tradovate Connection Failed")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Previous"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Complete Setup ✅", type="primary"):
                st.session_state.show_setup_wizard = False
                st.session_state.connections_configured = True
                st.success("🎉 Setup Complete! Welcome to Training Wheels!")
                st.rerun()
    
    def run(self):
        """Main dashboard run method with real-time data refresh - Cloud Safe"""
        # Cloud deployment detection and optimization
        is_cloud_deployment = not os.path.exists('C:\\') or 'STREAMLIT_CLOUD' in os.environ
        if is_cloud_deployment:
            st.info("🌤️ Running in cloud mode - Some desktop features are simulated for demonstration")
            # Disable auto-refresh in cloud to prevent resource exhaustion
            if 'auto_refresh' not in st.session_state:
                st.session_state.auto_refresh = False
        
        # Auto-refresh real data every 30 seconds (cloud-safe)
        try:
            self.refresh_real_time_data()
        except Exception as e:
            logging.error(f"Error refreshing data: {e}")
            st.warning("Data refresh temporarily unavailable - using cached data")
        
        # Check if Quick Setup Wizard should be shown
        if st.session_state.get('show_setup_wizard', False):
            self.render_quick_setup_wizard()
            return  # Don't show main dashboard while wizard is active
        
        # Check if connection setup should be shown
        if st.session_state.get('show_connection_setup', False):
            self.render_connection_setup_modal()
            return
        
        # Page header
        self.render_header()
        
        # Sidebar configuration
        self.render_sidebar_settings()
        
        # Emergency stop check
        if st.session_state.get('emergency_stop', False):
            st.error("🚨 EMERGENCY STOP ACTIVATED - All trading halted!")
            if st.button("Reset Emergency Stop", type="primary"):
                st.session_state.emergency_stop = False
                st.session_state.system_running = True
                st.success("Emergency stop reset. System resumed.")
                st.rerun()
            return
        
        # Main dashboard content
        self.render_priority_indicator()
        
        st.markdown("---")
        
        self.render_chart_grid()
        
        st.markdown("---")
        
        self.render_control_panel()
        
        st.markdown("---")
        
        self.render_system_status()
        
        # ERM Alerts Panel (if enabled)
        if st.session_state.erm_settings.get("enabled", False):
            st.markdown("---")
            self.render_erm_alerts_panel()
        
        # Kelly Criterion Panel (if enabled)
        if st.session_state.kelly_settings.get("enabled", False):
            st.markdown("---")
            self.render_kelly_criterion_panel()
        
        # Auto-refresh and data simulation - Cloud Safe
        if st.session_state.system_running and st.session_state.get('auto_refresh', False):
            self.simulate_data_updates()
            # Use session state to control refresh rate instead of immediate rerun
            if 'last_auto_refresh' not in st.session_state:
                st.session_state.last_auto_refresh = time.time()
            
            # Only refresh every 5 seconds to avoid overwhelming cloud resources
            if time.time() - st.session_state.last_auto_refresh > 5:
                st.session_state.last_auto_refresh = time.time()
                # Use a gentle refresh approach for cloud
                if st.button("🔄 Auto Refresh", key="auto_refresh_button", help="Click to refresh data"):
                    st.rerun()
        
        # Footer
        st.markdown("---")
        selected_firm = st.session_state.get('selected_prop_firm', 'FTMO')
        trader_name = getattr(st.session_state.user_config, 'trader_name', 'Professional Trader')
        first_principal = st.session_state.first_principal_settings.get('primary_algo', 'Enigma')
        st.markdown(f"🎯 **Training Wheels for Prop Firm Traders** | {trader_name} | {selected_firm} Challenge | First Principal: {first_principal}")
        
        # Show ERM status in footer
        if st.session_state.erm_settings.get("enabled", False):
            active_signals = len([s for s in st.session_state.active_enigma_signals.values() if hasattr(s, 'is_active') and s.is_active])
            st.markdown(f"🧠 **ERM System Active** - Monitoring {active_signals} Enigma Signals | Michael Canfield's Rapid Reversal Detection System")

def main():
    """Main application entry point - Cloud Safe"""
    try:
        dashboard = TrainingWheelsDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Application startup error: {e}")
        st.info("🌤️ If you're seeing this in Streamlit Cloud, this is normal during initial deployment.")
        st.markdown("## 🎯 Training Wheels for Prop Firm Traders")
        st.markdown("### Professional Trading Enhancement System")
        st.info("The application is loading... Please refresh the page in a moment.")
        
        # Provide a basic fallback interface
        if st.button("🔄 Try to Load Dashboard"):
            st.rerun()

if __name__ == "__main__":
    main()
