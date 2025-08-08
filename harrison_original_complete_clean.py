"""
TRAINING WHEELS FOR PROP FIRM TRADERS
Advanced trading assistance system for prop firm traders
- Multi-prop firm support (FTMO, MyForexFunds, The5ers, etc.)
- ERM (Enigma Reversal Momentum) Signal Detection
- NinjaTrader + Tradovate Integration
- Real Connection Testing (Demo/Test/Live modes)
- Multi-account futures trading management
- OCR signal reading capabilities
- Professional margin monitoring
- Emergency stop protection
- First Principal algo enhancement system
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

# Enhanced imports for professional features
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import cv2
    import pytesseract
    from PIL import Image, ImageGrab
    import mss
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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
except ImportError:
    WINDOWS_API_AVAILABLE = False

# Desktop notifications
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

# Audio alerts
try:
    import winsound
    AUDIO_AVAILABLE = True
    AUDIO_TYPE = "winsound"
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
        """Send desktop notification using available library"""
        try:
            # Choose icon based on priority
            icon_map = {
                "critical": "error",
                "high": "warning", 
                "medium": "info",
                "low": "info"
            }
            
            if NOTIFICATIONS_TYPE == "plyer":
                plyer.notification.notify(
                    title=f"🎯 Training Wheels - {title}",
                    message=message,
                    app_name="Training Wheels Pro",
                    timeout=10 if priority == "critical" else 5
                )
            elif NOTIFICATIONS_TYPE == "win10toast":
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(
                    title=f"🎯 Training Wheels - {title}",
                    msg=message,
                    duration=10 if priority == "critical" else 5,
                    threaded=True
                )
        except Exception as e:
            logging.error(f"Failed to send desktop notification: {e}")
    
    def _play_alert_sound(self, priority: str):
        """Play audio alert based on priority"""
        try:
            if AUDIO_TYPE == "winsound":
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
            
            elif AUDIO_TYPE == "pygame":
                # Pygame sound implementation (fallback)
                pass
                
        except Exception as e:
            logging.error(f"Failed to play alert sound: {e}")
    
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
        """Connect to NinjaTrader via ATM interface"""
        try:
            # Check if NinjaTrader process is running
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'ninjatrader' in proc.info['name'].lower():
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
            page_title="Training Wheels - Professional Trading Dashboard",
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
                "connections_configured": False
            }
        
        # Prop firm configurations
        if 'prop_firms' not in st.session_state:
            st.session_state.prop_firms = self.create_prop_firm_configs()
        
        if 'selected_prop_firm' not in st.session_state:
            st.session_state.selected_prop_firm = "FTMO"
        
        # ERM (Enigma Reversal Momentum) settings
        if 'erm_settings' not in st.session_state:
            st.session_state.erm_settings = {
                "enabled": False,
                "lookback_periods": 10,
                "atr_multiplier": 2.0,
                "min_time_elapsed": 300,  # seconds
                "auto_reverse_trade": False,
                "alert_sound": True
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
    
    def create_prop_firm_configs(self) -> Dict[str, PropFirmConfig]:
        """Create prop firm configurations for different firms"""
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
        
        ERM Formula:
        - Momentum Velocity = (Current Price - Entry Price) / Time Elapsed
        - Price Distance = abs(Current Price - Entry Price) / ATR
        - ERM Value = (Price Distance * Momentum Velocity) / ATR Multiplier
        """
        chart = st.session_state.charts.get(chart_id)
        if not chart or not chart.current_enigma_signal:
            return None
        
        signal = chart.current_enigma_signal
        time_elapsed = (datetime.now() - signal.signal_time).total_seconds()
        
        if time_elapsed < st.session_state.erm_settings["min_time_elapsed"]:
            return None
        
        # Calculate components
        price_distance = abs(current_price - signal.entry_price)
        momentum_velocity = price_distance / time_elapsed if time_elapsed > 0 else 0
        
        # Estimate ATR for normalization
        atr = self.estimate_atr(chart_id)
        
        if atr > 0:
            normalized_distance = price_distance / atr
            erm_value = (normalized_distance * momentum_velocity) / st.session_state.erm_settings["atr_multiplier"]
        else:
            erm_value = 0
        
        # Determine if reversal is triggered
        threshold = st.session_state.erm_settings["atr_multiplier"]
        is_reversal = erm_value > threshold
        
        # Determine reversal direction
        if signal.signal_type == "LONG" and is_reversal:
            reversal_direction = "SHORT"
        elif signal.signal_type == "SHORT" and is_reversal:
            reversal_direction = "LONG"
        else:
            reversal_direction = "NONE"
        
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
            st.markdown('<h1 class="header-title">TRAINING WHEELS</h1>', unsafe_allow_html=True)
            st.markdown('<h2 class="header-subtitle">Professional Prop Firm Trading Platform</h2>', unsafe_allow_html=True)
        
        with col3:
            # Real-time system status
            current_time = datetime.now().strftime('%H:%M:%S')
            st.markdown(f'<div style="text-align: right; font-size: 1.1rem; font-weight: 600;">TIME: {current_time}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
                value=st.session_state.erm_settings["enabled"]
            )
            
            st.markdown("---")
            
            # System Controls
            st.subheader("🎮 System Controls")
            
            if st.button("🔄 Refresh All Data", use_container_width=True):
                # Refresh all chart data
                for chart_id, chart in st.session_state.charts.items():
                    chart.last_update = datetime.now()
                    # Simulate some data changes
                    chart.power_score = np.random.randint(60, 95)
                    chart.daily_pnl += np.random.uniform(-50, 50)
                st.success("All data refreshed!")
                st.rerun()
            
            # Monitoring toggle
            st.session_state.monitoring_active = st.toggle(
                "🔍 Active Monitoring",
                value=st.session_state.monitoring_active
            )
            
            st.markdown("---")
            
            # Connection Testing
            st.subheader("🔗 Connections")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Test NT", use_container_width=True):
                    if self.ninja_connector.connect_via_socket():
                        st.success("NinjaTrader Connected!")
                        self.notification_manager.send_system_status_alert("NinjaTrader connection successful")
                    else:
                        st.error("NT Connection Failed")
                        self.notification_manager.send_connection_lost_alert("NinjaTrader")
            
            with col2:
                if st.button("Test TV", use_container_width=True):
                    if self.tradovate_connector.authenticate("demo", "demo"):
                        st.success("Tradovate Connected!")
                        self.notification_manager.send_system_status_alert("Tradovate connection successful")
                    else:
                        st.error("TV Connection Failed")
                        self.notification_manager.send_connection_lost_alert("Tradovate")
            
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
    
    def render_connection_setup_modal(self):
        """Render comprehensive connection setup interface"""
        st.markdown("---")
        st.header("🔗 Connection Configuration")
        st.markdown("Configure your NinjaTrader and Tradovate connections")
        
        # Tabs for different connection types
        tab1, tab2, tab3 = st.tabs(["NinjaTrader Setup", "Tradovate Setup", "Test Connections"])
        
        with tab1:
            self.render_ninjatrader_setup()
        
        with tab2:
            self.render_tradovate_setup()
        
        with tab3:
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
        """Main dashboard run method with real-time data refresh"""
        # Auto-refresh real data every 30 seconds
        self.refresh_real_time_data()
        
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
        
        # Auto-refresh and data simulation
        if st.session_state.system_running:
            self.simulate_data_updates()
            time.sleep(0.1)  # Smooth updates
            st.rerun()
        
        # Footer
        st.markdown("---")
        selected_firm = st.session_state.get('selected_prop_firm', 'FTMO')
        trader_name = getattr(st.session_state.user_config, 'trader_name', 'Professional Trader')
        st.markdown(f"🎯 **Training Wheels for Prop Firm Traders** | {trader_name} | {selected_firm} Challenge Dashboard")
        
        # Show ERM status in footer
        if st.session_state.erm_settings.get("enabled", False):
            active_signals = len([s for s in st.session_state.active_enigma_signals.values() if hasattr(s, 'is_active') and s.is_active])
            st.markdown(f"🧠 **ERM System Active** - Monitoring {active_signals} Enigma Signals | First Principal Enhancement System")

def main():
    """Main application entry point"""
    dashboard = TrainingWheelsDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
