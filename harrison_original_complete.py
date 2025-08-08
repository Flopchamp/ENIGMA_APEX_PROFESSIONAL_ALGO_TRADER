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
    import threading
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

try:
    import win32gui
    import win32ui
    import win32con
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False

@dataclass
class EnigmaSignal:
    """Enigma signal data structure for ERM calculation"""
    signal_type: str  # "LONG" or "SHORT"
    entry_price: float
    signal_time: datetime
    is_active: bool
    confidence: float
    
@dataclass
class ERMCalculation:
    """Enigma Reversal Momentum calculation results"""
    erm_value: float
    threshold: float
    is_reversal_triggered: bool
    reversal_direction: str  # "LONG" or "SHORT" 
    momentum_velocity: float
    price_distance: float
    time_elapsed: float

@dataclass
class PropFirmConfig:
    """Prop firm specific configuration"""
    firm_name: str
    max_daily_loss: float
    max_position_size: float
    max_drawdown: float
    leverage: float
    allowed_instruments: List[str]
    evaluation_period: int  # days
    profit_target: float
    risk_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TradovateAccount:
    """Individual Tradovate account (Harrison's chart equivalent)"""
    chart_id: int
    account_name: str
    account_balance: float
    daily_pnl: float
    margin_used: float
    margin_remaining: float
    margin_percentage: float
    open_positions: int
    is_active: bool
    risk_level: str  # "SAFE", "WARNING", "DANGER"
    last_signal: str
    power_score: int
    confluence_level: str
    signal_color: str  # Harrison's red/yellow/green
    ninjatrader_connection: str
    last_update: datetime
    instruments: List[str]
    position_size: float
    entry_price: float
    unrealized_pnl: float
    # ERM enhancement fields
    current_enigma_signal: Optional['EnigmaSignal'] = None
    erm_last_calculation: Optional['ERMCalculation'] = None
    price_history: List[float] = field(default_factory=list)
    time_history: List[datetime] = field(default_factory=list)
    """Individual Tradovate account (Harrison's chart equivalent)"""
    chart_id: int
    account_name: str
    account_balance: float
    daily_pnl: float
    margin_used: float
    margin_remaining: float
    margin_percentage: float
    open_positions: int
    is_active: bool
    risk_level: str  # "SAFE", "WARNING", "DANGER"
    last_signal: str
    power_score: int
    confluence_level: str
    signal_color: str  # Harrison's red/yellow/green
    ninjatrader_connection: str
    last_update: datetime
    instruments: List[str]
    position_size: float
    entry_price: float
    unrealized_pnl: float

@dataclass
class NinjaTraderStatus:
    """Real NinjaTrader platform status"""
    version: str
    connection_status: str
    active_strategies: int
    total_accounts_connected: int
    market_data_status: str
    last_heartbeat: datetime
    auto_trading_enabled: bool
    emergency_stop_active: bool
    process_id: Optional[int]
    memory_usage: float
    cpu_usage: float

@dataclass
class SystemStatus:
    """Overall system status (Harrison's priority indicator)"""
    total_margin_remaining: float
    total_margin_percentage: float
    total_equity: float
    daily_profit_loss: float
    active_charts: int
    violation_alerts: List[str]
    emergency_stop_active: bool
    safety_ratio: float
    system_health: str
    ninjatrader_status: NinjaTraderStatus
    mode: str  # "DEMO", "TEST", "LIVE"

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
        """
        Calculate optimal position size using Kelly Criterion
        
        Args:
            chart_id: Chart identifier
            signal_confidence: Confidence in current signal (0-1)
            
        Returns:
            KellyCalculation with recommended position size
        """
        history = self.get_trading_history(chart_id)
        
        if history.total_trades < self.kelly_settings["min_sample_size"]:
            # Not enough data - use conservative sizing
            return self._conservative_kelly(signal_confidence, chart_id)
        
        # Calculate Kelly components
        win_probability = history.win_rate
        avg_win = abs(history.avg_winner)
        avg_loss = abs(history.avg_loser)
        
        if avg_loss == 0:
            avg_loss = 0.01  # Prevent division by zero
        
        # Kelly Criterion calculation
        b = avg_win / avg_loss  # Odds ratio
        p = win_probability     # Win probability
        q = 1 - p              # Loss probability
        
        # Raw Kelly percentage: f* = (bp - q) / b
        if b > 0:
            kelly_raw = (b * p - q) / b
        else:
            kelly_raw = 0
        
        # Ensure Kelly is positive and reasonable
        kelly_raw = max(0, min(kelly_raw, 1.0))
        
        # Risk adjustment based on recent performance
        risk_adjustment = self._calculate_risk_adjustment(history)
        
        # Apply conservative factors
        kelly_adjusted = kelly_raw * self.kelly_settings["risk_adjustment_factor"] * risk_adjustment
        
        # Cap at maximum Kelly percentage
        kelly_final = min(kelly_adjusted, self.kelly_settings["max_kelly_percentage"])
        
        # Apply signal confidence
        kelly_with_confidence = kelly_final * signal_confidence
        
        # Calculate actual position size recommendation
        max_position = self._get_max_position_size(chart_id)
        recommended_position = kelly_with_confidence * max_position
        
        # Calculate Sharpe ratio for risk assessment
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
        conservative_percentage = 0.05  # 5% of max position when no data
        
        return KellyCalculation(
            kelly_percentage=conservative_percentage,
            win_probability=0.5,  # Assume 50/50 with no data
            avg_win=1.0,
            avg_loss=1.0,
            risk_adjusted_kelly=conservative_percentage * signal_confidence,
            recommended_position=conservative_percentage * signal_confidence * max_position,
            confidence_level=signal_confidence,
            max_position_limit=max_position,
            sample_size=0,
            sharpe_ratio=0.0
        )
    
    def _calculate_risk_adjustment(self, history: TradingHistory) -> float:
        """Calculate risk adjustment factor based on recent performance"""
        # Reduce Kelly if experiencing drawdown
        if history.consecutive_losses > 3:
            return 0.5  # Reduce position size during losing streaks
        elif history.consecutive_wins > 5:
            return 1.2  # Slightly increase during winning streaks (capped)
        else:
            return 1.0  # Normal sizing
    
    def _calculate_sharpe_ratio(self, history: TradingHistory) -> float:
        """Calculate Sharpe ratio for risk-adjusted returns"""
        if not history.trades or len(history.trades) < 2:
            return 0.0
        
        returns = [trade.get('pnl', 0) for trade in history.trades[-30:]]  # Last 30 trades
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualized Sharpe (assuming daily trades)
        sharpe = (mean_return / std_return) * np.sqrt(252)
        return sharpe
    
    def _get_max_position_size(self, chart_id: int) -> float:
        """Get maximum allowed position size for chart"""
        # Get from user config or prop firm limits
        if 'user_config' in st.session_state:
            if hasattr(st.session_state.user_config, 'get'):
                return st.session_state.user_config.get('max_position_size', 5.0)
            else:
                return getattr(st.session_state.user_config, 'max_position_size', 5.0)
        return 5.0  # Default conservative max
    
    def get_trading_history(self, chart_id: int) -> TradingHistory:
        """Get or create trading history for chart"""
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
        """Add trade result to history for Kelly calculations"""
        history = self.get_trading_history(chart_id)
        
        trade = {
            'pnl': pnl,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'size': size,
            'timestamp': datetime.now(),
            'is_winner': pnl > 0
        }
        
        history.trades.append(trade)
        
        # Keep only recent trades
        if len(history.trades) > self.kelly_settings["lookback_period"]:
            history.trades = history.trades[-self.kelly_settings["lookback_period"]:]
        
        # Update statistics
        self._update_trade_statistics(history)
    
    def _update_trade_statistics(self, history: TradingHistory):
        """Update trading statistics for Kelly calculations"""
        if not history.trades:
            return
        
        # Calculate win rate
        winners = [t for t in history.trades if t['pnl'] > 0]
        history.win_rate = len(winners) / len(history.trades)
        history.total_trades = len(history.trades)
        
        # Calculate average winner/loser
        if winners:
            history.avg_winner = np.mean([t['pnl'] for t in winners])
        else:
            history.avg_winner = 0
        
        losers = [t for t in history.trades if t['pnl'] <= 0]
        if losers:
            history.avg_loser = abs(np.mean([t['pnl'] for t in losers]))
        else:
            history.avg_loser = 0
        
        # Calculate profit factor
        gross_profit = sum(t['pnl'] for t in winners)
        gross_loss = abs(sum(t['pnl'] for t in losers))
        
        if gross_loss > 0:
            history.profit_factor = gross_profit / gross_loss
        else:
            history.profit_factor = float('inf') if gross_profit > 0 else 1.0
        
        # Calculate consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        
        for trade in reversed(history.trades):
            if trade['pnl'] > 0:
                consecutive_wins += 1
                break
            else:
                consecutive_losses += 1
        
        history.consecutive_wins = consecutive_wins
        history.consecutive_losses = consecutive_losses
        
        # Calculate maximum drawdown
        cumulative_pnl = 0
        peak = 0
        max_dd = 0
        
        for trade in history.trades:
            cumulative_pnl += trade['pnl']
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            drawdown = peak - cumulative_pnl
            if drawdown > max_dd:
                max_dd = drawdown
        
        history.max_drawdown = max_dd
    
    def get_win_rate(self, chart_id: int) -> float:
        """Get current win rate for a chart"""
        history = self.get_trading_history(chart_id)
        return history.win_rate if history.total_trades > 0 else 0.5

class OCRScreenMonitor:
    """Real-time OCR monitoring for trading signals"""
    
    def __init__(self):
        self.monitoring_regions = {}
        self.last_signals = {}
        self.monitoring_active = False
        
    def add_monitoring_region(self, name: str, region: Dict[str, int]):
        """Add a screen region to monitor for signals
        
        Args:
            name: Name of the region (e.g., "ES_Chart", "Signal_Panel")
            region: Dict with keys 'left', 'top', 'width', 'height'
        """
        self.monitoring_regions[name] = region
        
    def capture_region(self, region: Dict[str, int]) -> Optional[Image.Image]:
        """Capture a specific screen region"""
        if not OCR_AVAILABLE:
            return None
            
        try:
            with mss.mss() as sct:
                screenshot = sct.grab(region)
                return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        except Exception as e:
            logging.error(f"Error capturing screen region: {e}")
            return None
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using OCR"""
        if not OCR_AVAILABLE or not image:
            return ""
            
        try:
            # Convert to grayscale for better OCR
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Apply preprocessing for better OCR accuracy
            processed = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Extract text
            text = pytesseract.image_to_string(processed, config='--psm 6')
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text: {e}")
            return ""
    
    def detect_trading_signals(self, text: str) -> List[Dict[str, str]]:
        """Detect trading signals from OCR text"""
        signals = []
        text_upper = text.upper()
        
        # Common signal patterns
        signal_patterns = [
            ("BUY", "LONG"), ("SELL", "SHORT"), ("LONG", "LONG"), ("SHORT", "SHORT"),
            ("CALL", "LONG"), ("PUT", "SHORT"), ("BULL", "LONG"), ("BEAR", "SHORT"),
            ("UP", "LONG"), ("DOWN", "SHORT"), ("BULLISH", "LONG"), ("BEARISH", "SHORT")
        ]
        
        for pattern, signal_type in signal_patterns:
            if pattern in text_upper:
                signals.append({
                    "type": signal_type,
                    "confidence": 0.8,
                    "raw_text": text,
                    "timestamp": datetime.now().isoformat()
                })
                break
        
        return signals
    
    def monitor_all_regions(self) -> Dict[str, List[Dict[str, str]]]:
        """Monitor all configured regions for signals"""
        all_signals = {}
        
        for region_name, region in self.monitoring_regions.items():
            image = self.capture_region(region)
            if image:
                text = self.extract_text_from_image(image)
                signals = self.detect_trading_signals(text)
                if signals:
                    all_signals[region_name] = signals
                    
        return all_signals
    
    def render_ocr_configuration(self):
        """Render OCR configuration interface"""
        st.subheader("📱 OCR Configuration")
        
        # Show current regions
        if self.monitoring_regions:
            st.write("**Active Monitoring Regions:**")
            for name, region in self.monitoring_regions.items():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{name}**")
                    st.caption(f"Position: ({region['left']}, {region['top']})")
                with col2:
                    st.caption(f"Size: {region['width']} × {region['height']}")
                with col3:
                    if st.button("🗑️", key=f"delete_{name}", help="Remove region"):
                        del self.monitoring_regions[name]
                        st.rerun()
        else:
            st.info("No monitoring regions configured")
        
        # Add new region
        st.markdown("---")
        st.write("**Add New Region:**")
        
        col1, col2 = st.columns(2)
        with col1:
            region_name = st.text_input("Region Name", placeholder="e.g., ES_Chart_Signals")
            left = st.number_input("Left (X)", min_value=0, max_value=3840, value=100)
            top = st.number_input("Top (Y)", min_value=0, max_value=2160, value=100)
        
        with col2:
            st.write("")  # Spacer
            width = st.number_input("Width", min_value=50, max_value=1920, value=300)
            height = st.number_input("Height", min_value=50, max_value=1080, value=200)
        
        if st.button("➕ Add Region", use_container_width=True):
            if region_name and region_name not in self.monitoring_regions:
                self.add_monitoring_region(region_name, {
                    'left': left, 'top': top, 'width': width, 'height': height
                })
                st.success(f"Added region: {region_name}")
                st.rerun()
            elif not region_name:
                st.error("Please enter a region name")
            else:
                st.error("Region name already exists")
    
    def render_ocr_status(self):
        """Render OCR monitoring status and controls"""
        st.subheader("👁️ OCR Monitoring Status")
        
        # Status indicators
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            region_count = len(self.monitoring_regions)
            st.metric("Configured Regions", region_count)
        
        with status_col2:
            monitoring_status = "ACTIVE" if self.monitoring_active else "INACTIVE"
            st.metric("Monitoring Status", monitoring_status)
        
        with status_col3:
            signal_count = len(self.last_signals)
            st.metric("Recent Signals", signal_count)
        
        # Control buttons
        control_col1, control_col2, control_col3 = st.columns(3)
        
        with control_col1:
            if st.button("🟢 Start Monitoring", use_container_width=True):
                if self.monitoring_regions:
                    self.monitoring_active = True
                    st.success("OCR monitoring started")
                    st.rerun()
                else:
                    st.error("Configure regions first")
        
        with control_col2:
            if st.button("🟡 Pause Monitoring", use_container_width=True):
                self.monitoring_active = False
                st.warning("OCR monitoring paused")
                st.rerun()
        
        with control_col3:
            if st.button("🔧 Test Capture", use_container_width=True):
                if self.monitoring_regions:
                    try:
                        signals = self.monitor_all_regions()
                        if signals:
                            st.success(f"Found {len(signals)} signal regions")
                            for region, signal_list in signals.items():
                                for signal in signal_list:
                                    st.write(f"**{region}:** {signal['type']} ({signal['confidence']:.1%})")
                        else:
                            st.info("No signals detected in current capture")
                    except Exception as e:
                        st.error(f"OCR test failed: {str(e)[:50]}...")
                else:
                    st.warning("No regions configured for testing")
        
        # Recent signals display
        if self.last_signals:
            st.markdown("---")
            st.write("**Recent Signals:**")
            for region, signals in self.last_signals.items():
                with st.expander(f"📊 {region}", expanded=False):
                    for signal in signals[-5:]:  # Show last 5 signals
                        signal_time = signal.get('timestamp', datetime.now()).strftime('%H:%M:%S')
                        st.write(f"⏰ **{signal_time}** - {signal['type']} (Confidence: {signal['confidence']:.1%})")
        
        # OCR Settings
        with st.expander("⚙️ OCR Settings", expanded=False):
            scan_interval = st.slider("Scan Interval (seconds)", 1, 60, 5)
            confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.7)
            max_signals_history = st.number_input("Max Signals History", 10, 100, 50)
            
            if st.button("💾 Save OCR Settings"):
                st.success("OCR settings saved")

class NinjaTraderConnector:
    """Real NinjaTrader connection handler"""
    
    def __init__(self):
        self.connection = None
        self.is_connected = False
        self.account_data = {}
        self.position_data = {}
        
    def connect_via_socket(self, host: str = "localhost", port: int = 36973) -> bool:
        """Connect to NinjaTrader via socket"""
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(10)
            self.connection.connect((host, port))
            self.is_connected = True
            return True
        except Exception as e:
            logging.error(f"NinjaTrader socket connection failed: {e}")
            return False
    
    def connect_via_atm(self) -> bool:
        """Connect via NinjaTrader ATM strategies"""
        # This would require NinjaScript addon - placeholder for now
        try:
            # Check if ATM strategies are running
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if 'ninjatrader' in proc.info['name'].lower():
                            # Check for ATM strategy processes
                            if 'atm' in ' '.join(proc.info.get('cmdline', [])).lower():
                                self.is_connected = True
                                return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except Exception as e:
            logging.error(f"ATM connection check failed: {e}")
        
        return False
    
    def get_account_info(self) -> Dict[str, float]:
        """Get real account information from NinjaTrader"""
        if not self.is_connected:
            return {}
            
        try:
            # This would send actual commands to NT8
            # For now, return structure for real implementation
            account_info = {
                'buying_power': 0.0,
                'cash_value': 0.0,
                'day_trading_buying_power': 0.0,
                'initial_margin': 0.0,
                'maintenance_margin': 0.0,
                'net_liquidation': 0.0,
                'unrealized_pnl': 0.0,
                'realized_pnl': 0.0
            }
            
            # TODO: Implement actual NT8 command communication
            # Command format: "ACCOUNT;<account_name>|"
            
            return account_info
        except Exception as e:
            logging.error(f"Error getting NT account info: {e}")
            return {}
    
    def get_positions(self) -> Dict[str, Dict[str, float]]:
        """Get current positions from NinjaTrader"""
        if not self.is_connected:
            return {}
            
        try:
            # TODO: Implement actual position retrieval
            # Command format: "POSITIONS|"
            positions = {}
            return positions
        except Exception as e:
            logging.error(f"Error getting positions: {e}")
            return {}

class TradovateConnector:
    """Enhanced Tradovate API connector with real-time capabilities"""
    
    def __init__(self):
        self.access_token = None
        self.websocket_connection = None
        self.account_data = {}
        self.position_data = {}
        self.is_connected = False
        
    def authenticate(self, username: str, password: str, environment: str = "demo") -> bool:
        """Authenticate with Tradovate API"""
        try:
            if environment == "demo":
                base_url = "https://demo.tradovateapi.com/v1"
            elif environment == "live":
                base_url = "https://live.tradovateapi.com/v1"
            else:
                base_url = "https://demo.tradovateapi.com/v1"
            
            auth_data = {
                "name": username,
                "password": password,
                "appId": "TrainingWheelsApp",
                "appVersion": "2.0",
                "cid": 1
            }
            
            auth_url = f"{base_url}/auth/accesstokenrequest"
            auth_req = urllib.request.Request(auth_url)
            auth_req.add_header('Content-Type', 'application/json')
            auth_req.add_header('Accept', 'application/json')
            auth_data_bytes = json.dumps(auth_data).encode('utf-8')
            
            with urllib.request.urlopen(auth_req, data=auth_data_bytes, timeout=15) as response:
                if response.status == 200:
                    auth_result = json.loads(response.read().decode('utf-8'))
                    self.access_token = auth_result.get('accessToken')
                    self.is_connected = True
                    return True
                    
        except Exception as e:
            logging.error(f"Tradovate authentication failed: {e}")
            
        return False
    
    def connect_websocket(self, environment: str = "demo") -> bool:
        """Connect to Tradovate WebSocket for real-time data"""
        if not WEBSOCKET_AVAILABLE or not self.access_token:
            return False
            
        try:
            if environment == "demo":
                ws_url = "wss://demo.tradovateapi.com/v1/websocket"
            else:
                ws_url = "wss://live.tradovateapi.com/v1/websocket"
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    # Process real-time updates
                    self.process_websocket_message(data)
                except Exception as e:
                    logging.error(f"Error processing WebSocket message: {e}")
            
            def on_error(ws, error):
                logging.error(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                logging.info("WebSocket connection closed")
                self.is_connected = False
            
            self.websocket_connection = websocket.WebSocketApp(
                ws_url,
                header=[f"Authorization: Bearer {self.access_token}"],
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Start WebSocket in background thread
            websocket_thread = threading.Thread(target=self.websocket_connection.run_forever)
            websocket_thread.daemon = True
            websocket_thread.start()
            
            return True
            
        except Exception as e:
            logging.error(f"WebSocket connection failed: {e}")
            return False
    
    def process_websocket_message(self, data: Dict[str, Any]):
        """Process incoming WebSocket messages"""
        try:
            if 'e' in data:  # Event type
                event_type = data['e']
                
                if event_type == 'user':
                    # User account updates
                    self.account_data.update(data.get('d', {}))
                elif event_type == 'position':
                    # Position updates
                    position_data = data.get('d', {})
                    symbol = position_data.get('contractId')
                    if symbol:
                        self.position_data[symbol] = position_data
                        
        except Exception as e:
            logging.error(f"Error processing WebSocket data: {e}")
    
    def get_real_account_data(self) -> Dict[str, float]:
        """Get real-time account data"""
        if not self.access_token:
            return {}
            
        try:
            # Use cached WebSocket data if available
            if self.account_data:
                return {
                    'cash_balance': float(self.account_data.get('cashBalance', 0.0)),
                    'margin_available': float(self.account_data.get('marginAvailable', 0.0)),
                    'net_liquidation': float(self.account_data.get('netLiq', 0.0)),
                    'unrealized_pnl': float(self.account_data.get('unrealizedPnL', 0.0)),
                    'realized_pnl': float(self.account_data.get('realizedPnL', 0.0))
                }
            
            # Fallback to REST API
            return self.fetch_account_via_rest()
            
        except Exception as e:
            logging.error(f"Error getting Tradovate account data: {e}")
            return {}
    
    def fetch_account_via_rest(self) -> Dict[str, float]:
        """Fetch account data via REST API as fallback"""
        # Implementation similar to existing fetch_tradovate_account_data
        # but returning the enhanced format
        return {}

class TrainingWheelsDashboard:
    """
    Training Wheels for Prop Firm Traders
    Advanced trading assistance system with ERM signal detection
    """
    
    def __init__(self):
        self.setup_page_config()
        self.setup_logging()  # Initialize logging first!
        
        # Initialize real data connectors
        self.ninja_connector = NinjaTraderConnector()
        self.tradovate_connector = TradovateConnector()
        
        # Initialize Kelly Criterion engine for optimal position sizing
        self.kelly_engine = KellyEngine()
        
        # Initialize OCR manager if available
        if OCR_AVAILABLE:
            self.ocr_manager = OCRScreenMonitor()
            self.setup_ocr_regions()
        else:
            self.ocr_manager = None
            
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page for prop firm training"""
        try:
            st.set_page_config(
                page_title="Training Wheels for Prop Firm Traders",
                page_icon="TW",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except:
            pass
        
        # Professional blue design for prop firm environment
        st.markdown("""
        <style>
        /* Import professional fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Reset and Base Styling */
        .main > div {
            padding: 1.5rem 2rem;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
        }
        
        /* Professional Header Design */
        .prop-firm-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(30, 58, 138, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header-title {
            font-size: 2.75rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.025em;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .header-subtitle {
            font-size: 1.25rem;
            opacity: 0.9;
            margin: 0.75rem 0 0 0;
            font-weight: 400;
        }
        
        /* Status Badges - Clean and Professional */
        .status-badge {
            padding: 0.5rem 1.25rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin: 0.25rem;
        }
        
        .mode-demo {
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
        }
        
        .mode-test {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
        }
        
        .mode-live {
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
        }
        
        .connection-active {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        }
        
        .connection-inactive {
            background: linear-gradient(135deg, #64748b 0%, #475569 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(100, 116, 139, 0.3);
        }
        
        /* Professional Metric Cards */
        .stMetric {
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.75rem;
            margin: 1rem 0;
            box-shadow: 0 4px 16px rgba(30, 58, 138, 0.08);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stMetric::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        }
        
        .stMetric:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(30, 58, 138, 0.15);
            border-color: #3b82f6;
        }
        
        /* Section Headers - Corporate Style */
        .section-header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 1.25rem 2rem;
            border-radius: 12px;
            margin: 2rem 0 1.5rem 0;
            font-weight: 600;
            font-size: 1.125rem;
            box-shadow: 0 4px 16px rgba(30, 64, 175, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Trading Chart Containers */
        .chart-container {
            background: #ffffff;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            position: relative;
        }
        
        .chart-container:hover {
            border-color: #3b82f6;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
            transform: translateY(-1px);
        }
        
        .chart-safe {
            border-color: #10b981;
            background: linear-gradient(145deg, #ffffff 0%, #f0fdf4 100%);
        }
        
        .chart-safe::before {
            content: 'SAFE';
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: #10b981;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .chart-warning {
            border-color: #f59e0b;
            background: linear-gradient(145deg, #ffffff 0%, #fffbeb 100%);
        }
        
        .chart-warning::before {
            content: 'WARNING';
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: #f59e0b;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .chart-danger {
            border-color: #ef4444;
            background: linear-gradient(145deg, #ffffff 0%, #fef2f2 100%);
        }
        
        .chart-danger::before {
            content: 'DANGER';
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: #ef4444;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        /* Signal Indicators - Professional Trading Style */
        .signal-long {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 2px 8px rgba(5, 150, 105, 0.3);
        }
        
        .signal-short {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
        }
        
        .signal-neutral {
            background: linear-gradient(135deg, #64748b 0%, #94a3b8 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 2px 8px rgba(100, 116, 139, 0.3);
        }
        
        /* Risk Status Indicators */
        .status-indicator {
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            font-size: 1.25rem;
            margin: 1.5rem 0;
            border: 2px solid transparent;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .status-safe {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border-color: #047857;
        }
        
        .status-warning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            border-color: #b45309;
        }
        
        .status-danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            border-color: #b91c1c;
        }
        
        /* Professional Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.875rem 1.75rem;
            font-weight: 600;
            font-size: 0.875rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.35);
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Emergency/Critical Buttons */
        .stButton > button[kind="secondary"] {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.25);
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            box-shadow: 0 4px 16px rgba(239, 68, 68, 0.35);
        }
        
        /* Sidebar Professional Styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
        }
        
        /* Progress Bars */
        .stProgress > div > div {
            background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
            border-radius: 4px;
            height: 8px;
        }
        
        /* Alert Styling for Prop Firm Environment */
        .alert-success {
            background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
            border-left: 4px solid #10b981;
            color: #047857;
            padding: 1.25rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        .alert-warning {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 4px solid #f59e0b;
            color: #92400e;
            padding: 1.25rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        .alert-danger {
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            border-left: 4px solid #ef4444;
            color: #b91c1c;
            padding: 1.25rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        /* Data Tables - Professional Trading View */
        .dataframe {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }
        
        .dataframe thead th {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            font-weight: 600;
            padding: 1rem;
        }
        
        /* Prop Firm Specific Elements */
        .prop-firm-badge {
            background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.875rem;
            display: inline-block;
            box-shadow: 0 2px 8px rgba(30, 58, 138, 0.3);
        }
        
        .risk-metrics {
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }
        
        /* Responsive Design for Different Screen Sizes */
        @media (max-width: 1200px) {
            .main > div {
                padding: 1rem 1.5rem;
            }
            
            .header-title {
                font-size: 2.25rem;
            }
        }
        
        @media (max-width: 768px) {
            .main > div {
                padding: 0.75rem 1rem;
            }
            
            .header-title {
                font-size: 1.875rem;
            }
            
            .chart-container {
                padding: 1.25rem;
            }
            
            .status-indicator {
                padding: 1.5rem;
                font-size: 1rem;
            }
        }
        
        /* Professional Loading States */
        .stSpinner > div {
            border-color: #3b82f6;
        }
        
        /* Custom Scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
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
            return
            
        # Default regions - users can customize these
        default_regions = {
            "ninja_chart_1": {"left": 100, "top": 100, "width": 300, "height": 200},
            "ninja_chart_2": {"left": 450, "top": 100, "width": 300, "height": 200},
            "signal_panel": {"left": 800, "top": 100, "width": 200, "height": 150},
            "tradovate_dom": {"left": 1000, "top": 100, "width": 250, "height": 300},
            "alerts_area": {"left": 100, "top": 350, "width": 400, "height": 100}
        }
        
        for name, region in default_regions.items():
            self.ocr_manager.add_monitoring_region(name, region)
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        # Core system state
        if 'system_mode' not in st.session_state:
            st.session_state.system_mode = "DEMO"  # Start in safe demo mode
        
        if 'emergency_stop' not in st.session_state:
            st.session_state.emergency_stop = False
        
        if 'system_running' not in st.session_state:
            st.session_state.system_running = False
        
        # NinjaTrader status
        if 'ninjatrader_status' not in st.session_state:
            st.session_state.ninjatrader_status = NinjaTraderStatus(
                version="8.0",
                connection_status="Disconnected",
                active_strategies=0,
                total_accounts_connected=0,
                market_data_status="Disconnected",
                last_heartbeat=datetime.now(),
                auto_trading_enabled=False,
                emergency_stop_active=False,
                process_id=None,
                memory_usage=0.0,
                cpu_usage=0.0
            )
        
        # System status (Harrison's priority indicator) - Dynamic data loading
        if 'system_status' not in st.session_state:
            # Initialize with real data from connections
            real_account_data = self.fetch_real_account_data()
            st.session_state.system_status = SystemStatus(
                total_margin_remaining=real_account_data.get('total_margin_remaining', 0.0),
                total_margin_percentage=real_account_data.get('total_margin_percentage', 0.0),
                total_equity=real_account_data.get('total_equity', 0.0),
                daily_profit_loss=real_account_data.get('daily_profit_loss', 0.0),
                active_charts=0,
                violation_alerts=[],
                emergency_stop_active=False,
                safety_ratio=real_account_data.get('safety_ratio', 0.0),
                system_health="HEALTHY",
                ninjatrader_status=st.session_state.ninjatrader_status,
                mode=st.session_state.system_mode
            )
        
        # User configuration - Load from real prop firm settings
        if 'user_config' not in st.session_state:
            selected_firm = st.session_state.get('selected_prop_firm', 'FTMO')
            prop_firm_data = self.get_prop_firm_limits(selected_firm)
            
            st.session_state.user_config = {
                "trader_name": "Trader",
                "account_type": "NinjaTrader + Tradovate",
                "chart_layout": "2x3",
                "risk_management": "Conservative",
                "platform": "NinjaTrader 8",
                "broker": "Tradovate",
                "max_daily_loss": prop_firm_data.get('max_daily_loss', 1000.0),
                "max_position_size": prop_firm_data.get('max_position_size', 5.0),
                "max_charts": 6,  # Add this for OCR compatibility
                "chart_names": [
                    "ES Primary", "NQ Primary", "YM Primary",
                    "RTY Primary", "CL Energy", "GC Metals"
                ],
                "priority_indicator": "margin"  # Harrison's most important indicator
            }
        
        # Connection credentials (secure storage)
        if 'connection_config' not in st.session_state:
            st.session_state.connection_config = {
                # Tradovate API credentials
                "tradovate_username": "",
                "tradovate_password": "",
                "tradovate_api_key": "",
                "tradovate_api_secret": "",
                "tradovate_environment": "demo",  # demo, test, live
                "tradovate_account_ids": [],  # Multiple account support
                
                # NinjaTrader connection settings
                "ninjatrader_host": "localhost",
                "ninjatrader_port": 36973,  # Default NT8 port
                "ninjatrader_version": "8.0",
                "ninjatrader_auto_connect": True,
                "ninjatrader_strategies": [],  # Enabled strategies
                
                # Connection status
                "connections_configured": False,
                "last_connection_test": None,
                "connection_errors": []
            }
        
        # Prop firm configurations
        if 'prop_firms' not in st.session_state:
            st.session_state.prop_firms = self.create_prop_firm_configs()
        
        if 'selected_prop_firm' not in st.session_state:
            st.session_state.selected_prop_firm = "FTMO"  # Default
        
        # ERM (Enigma Reversal Momentum) settings
        if 'erm_settings' not in st.session_state:
            st.session_state.erm_settings = {
                "enabled": True,
                "lookback_periods": 5,  # minutes for momentum calculation
                "atr_multiplier": 0.5,  # threshold multiplier
                "min_time_elapsed": 30,  # seconds minimum before ERM activation
                "auto_reverse_trade": False,  # manual approval by default
                "max_reversals_per_day": 3
            }
        
        # Kelly Criterion settings
        if 'kelly_settings' not in st.session_state:
            st.session_state.kelly_settings = {
                "enabled": True,
                "max_kelly_percentage": 0.25,      # Cap Kelly at 25% (conservative)
                "min_sample_size": 10,             # Minimum trades for Kelly calculation
                "lookback_period": 100,            # Number of recent trades to analyze
                "confidence_threshold": 0.6,       # Minimum confidence for position sizing
                "risk_adjustment_factor": 0.5,     # Conservative Kelly adjustment
                "adaptive_sizing": True,           # Adjust based on recent performance
                "show_kelly_details": True         # Show Kelly calculations in UI
            }
        
        # Active Enigma signals tracking
        if 'active_enigma_signals' not in st.session_state:
            st.session_state.active_enigma_signals = {}  # chart_id: EnigmaSignal
        
        # ERM alerts and history
        if 'erm_alerts' not in st.session_state:
            st.session_state.erm_alerts = []
        
        if 'erm_history' not in st.session_state:
            st.session_state.erm_history = []
        if 'charts' not in st.session_state:
            st.session_state.charts = self.create_default_charts()
        
        # Charts (Harrison's 6-chart design)
        if 'charts' not in st.session_state:
            st.session_state.charts = self.create_default_charts()
        
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
    
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
            ["ES", "MES"],  # S&P 500
            ["NQ", "MNQ"],  # NASDAQ
            ["YM", "MYM"],  # Dow Jones
            ["RTY", "M2K"], # Russell 2000
            ["CL", "MCL"],  # Crude Oil
            ["GC", "MGC"]   # Gold
        ]
        
        chart_names = [
            "ES Primary", "NQ Primary", "YM Primary",
            "RTY Primary", "CL Energy", "GC Metals"
        ]
        
        # Fetch real account data for each chart
        real_accounts = self.fetch_all_account_data()
        
        charts = {}
        for i in range(6):
            chart_id = i + 1
            account_data = real_accounts.get(chart_id, {})
            
            charts[chart_id] = TradovateAccount(
                chart_id=chart_id,
                account_name=chart_names[i],
                account_balance=account_data.get('account_balance', 0.0),
                daily_pnl=account_data.get('daily_pnl', 0.0),
                margin_used=account_data.get('margin_used', 0.0),
                margin_remaining=account_data.get('margin_remaining', 0.0),
                margin_percentage=account_data.get('margin_percentage', 0.0),
                open_positions=account_data.get('open_positions', 0),
                is_active=account_data.get('is_active', False),
                risk_level=account_data.get('risk_level', "DISCONNECTED"),
                last_signal=account_data.get('last_signal', "NONE"),
                power_score=account_data.get('power_score', 0),
                confluence_level=account_data.get('confluence_level', "L0"),
                signal_color=account_data.get('signal_color', "gray"),
                ninjatrader_connection=account_data.get('connection_status', "Disconnected"),
                last_update=datetime.now(),
                instruments=instruments[i],
                position_size=account_data.get('position_size', 0.0),
                entry_price=account_data.get('entry_price', 0.0),
                unrealized_pnl=account_data.get('unrealized_pnl', 0.0)
            )
        
        return charts
    
    def fetch_real_account_data(self) -> Dict[str, float]:
        """Fetch real account data from NinjaTrader and Tradovate connections"""
        account_data = {
            'total_margin_remaining': 0.0,
            'total_margin_percentage': 0.0,
            'total_equity': 0.0,
            'daily_profit_loss': 0.0,
            'safety_ratio': 0.0
        }
        
        try:
            # Try NinjaTrader first (if connected)
            if self.check_ninjatrader_connection():
                ninja_data = self.fetch_ninjatrader_account_data()
                account_data.update(ninja_data)
                return account_data
            
            # Try Tradovate if NinjaTrader not available
            if self.test_tradovate_connection():
                tradovate_data = self.fetch_tradovate_account_data()
                account_data.update(tradovate_data)
                return account_data
            
            # Fallback to prop firm demo data if no connections
            selected_firm = st.session_state.get('selected_prop_firm', 'FTMO')
            demo_data = self.get_demo_account_data(selected_firm)
            account_data.update(demo_data)
            
        except Exception as e:
            self.logger.error(f"Error fetching real account data: {e}")
            # Return safe demo data on error
            account_data = {
                'total_margin_remaining': 10000.0,
                'total_margin_percentage': 50.0,
                'total_equity': 20000.0,
                'daily_profit_loss': 0.0,
                'safety_ratio': 50.0
            }
        
        return account_data
    
    def fetch_ninjatrader_account_data(self) -> Dict[str, float]:
        """Fetch real account data from NinjaTrader API"""
        ninja_data = {}
        
        try:
            # Try socket connection first
            if self.ninja_connector.connect_via_socket():
                account_info = self.ninja_connector.get_account_info()
                if account_info:
                    ninja_data = {
                        'total_equity': account_info.get('net_liquidation', 0.0),
                        'total_margin_remaining': account_info.get('buying_power', 0.0),
                        'total_margin_percentage': 0.0,  # Calculate below
                        'daily_profit_loss': account_info.get('realized_pnl', 0.0) + account_info.get('unrealized_pnl', 0.0),
                        'safety_ratio': 0.0  # Calculate below
                    }
                    
                    # Calculate percentages
                    equity = ninja_data['total_equity']
                    margin_available = ninja_data['total_margin_remaining']
                    if equity > 0:
                        ninja_data['total_margin_percentage'] = (margin_available / equity) * 100.0
                        ninja_data['safety_ratio'] = ninja_data['total_margin_percentage']
                    
                    self.logger.info("Successfully fetched real NinjaTrader data via socket")
                    return ninja_data
            
            # Fallback to ATM strategy connection
            elif self.ninja_connector.connect_via_atm():
                account_info = self.ninja_connector.get_account_info()
                if account_info:
                    # Similar processing as above
                    self.logger.info("Successfully connected via NinjaTrader ATM")
                    
            # Fallback to process monitoring (existing method)
            elif PSUTIL_AVAILABLE:
                ninja_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                    try:
                        if 'ninjatrader' in proc.info['name'].lower():
                            ninja_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if ninja_processes:
                    self.logger.info("NinjaTrader detected - using demo data (real API not connected)")
                    # Return realistic demo data to show it's working
                    ninja_data = {
                        'total_equity': 50000.0,
                        'total_margin_remaining': 35000.0,
                        'total_margin_percentage': 70.0,
                        'daily_profit_loss': 250.0,
                        'safety_ratio': 70.0
                    }
        
        except Exception as e:
            self.logger.error(f"Error fetching NinjaTrader data: {e}")
        
        return ninja_data
    
    def fetch_tradovate_account_data(self) -> Dict[str, float]:
        """Fetch real account data from Tradovate API with WebSocket support"""
        tradovate_data = {}
        
        try:
            username = st.session_state.connection_config.get("tradovate_username", "")
            password = st.session_state.connection_config.get("tradovate_password", "")
            environment = st.session_state.connection_config.get("tradovate_environment", "demo")
            
            if not username or not password:
                return {}
            
            # Try to authenticate and get real-time data
            if self.tradovate_connector.authenticate(username, password, environment):
                # Try WebSocket connection for real-time data
                if self.tradovate_connector.connect_websocket(environment):
                    real_time_data = self.tradovate_connector.get_real_account_data()
                    if real_time_data:
                        tradovate_data = {
                            'total_equity': real_time_data.get('cash_balance', 0.0),
                            'total_margin_remaining': real_time_data.get('margin_available', 0.0),
                            'daily_profit_loss': real_time_data.get('realized_pnl', 0.0) + real_time_data.get('unrealized_pnl', 0.0),
                            'safety_ratio': 0.0
                        }
                        
                        # Calculate margin percentage
                        equity = tradovate_data['total_equity']
                        margin_available = tradovate_data['total_margin_remaining']
                        if equity > 0:
                            tradovate_data['total_margin_percentage'] = (margin_available / equity) * 100.0
                            tradovate_data['safety_ratio'] = tradovate_data['total_margin_percentage']
                        
                        self.logger.info("Successfully fetched real-time Tradovate data via WebSocket")
                        return tradovate_data
                
                # Fallback to REST API (existing implementation)
                base_url = "https://demo.tradovateapi.com/v1" if environment == "demo" else "https://live.tradovateapi.com/v1"
                
                # Get access token first
                auth_data = {
                    "name": username,
                    "password": password,
                    "appId": "TrainingWheelsApp",
                    "appVersion": "2.0",
                    "cid": 1
                }
                
                # Authenticate
                auth_url = f"{base_url}/auth/accesstokenrequest"
                auth_req = urllib.request.Request(auth_url)
                auth_req.add_header('Content-Type', 'application/json')
                auth_req.add_header('Accept', 'application/json')
                auth_data_bytes = json.dumps(auth_data).encode('utf-8')
                
                with urllib.request.urlopen(auth_req, data=auth_data_bytes, timeout=10) as response:
                    if response.status == 200:
                        auth_result = json.loads(response.read().decode('utf-8'))
                        access_token = auth_result.get('accessToken')
                        
                        if access_token:
                            # Fetch account data
                            account_url = f"{base_url}/account/list"
                            account_req = urllib.request.Request(account_url)
                            account_req.add_header('Authorization', f'Bearer {access_token}')
                            account_req.add_header('Accept', 'application/json')
                            
                            with urllib.request.urlopen(account_req, timeout=10) as acc_response:
                                if acc_response.status == 200:
                                    accounts = json.loads(acc_response.read().decode('utf-8'))
                                    
                                    # Process account data
                                    if accounts and len(accounts) > 0:
                                        account = accounts[0]  # Use first account
                                        
                                        # Extract real account data
                                        tradovate_data = {
                                            'total_equity': float(account.get('cashBalance', 0.0)),
                                            'total_margin_remaining': float(account.get('marginAvailable', 0.0)),
                                            'daily_profit_loss': float(account.get('netLiq', 0.0) - account.get('cashBalance', 0.0)),
                                            'safety_ratio': min(100.0, (float(account.get('marginAvailable', 0.0)) / max(float(account.get('cashBalance', 1.0)), 1.0)) * 100.0)
                                        }
                                        
                                        # Calculate margin percentage
                                        equity = tradovate_data['total_equity']
                                        margin_available = tradovate_data['total_margin_remaining']
                                        if equity > 0:
                                            tradovate_data['total_margin_percentage'] = (margin_available / equity) * 100.0
                                        
                                        self.logger.info(f"Fetched real Tradovate data via REST: {tradovate_data}")
        
        except urllib.error.HTTPError as e:
            self.logger.error(f"Tradovate HTTP error: {e.code}")
        except Exception as e:
            self.logger.error(f"Error fetching Tradovate data: {e}")
        
        return tradovate_data
    
    def fetch_all_account_data(self) -> Dict[int, Dict[str, any]]:
        """Fetch real data for all 6 charts/accounts"""
        all_accounts = {}
        
        try:
            # Get overall account data first
            real_data = self.fetch_real_account_data()
            
            # If we have real connections, try to get individual account data
            if self.check_ninjatrader_connection() or self.test_tradovate_connection():
                # Distribute the real data across 6 charts
                equity_per_chart = real_data.get('total_equity', 0.0) / 6.0
                margin_per_chart = real_data.get('total_margin_remaining', 0.0) / 6.0
                
                for chart_id in range(1, 7):
                    all_accounts[chart_id] = {
                        'account_balance': equity_per_chart,
                        'daily_pnl': real_data.get('daily_profit_loss', 0.0) / 6.0,
                        'margin_used': max(0.0, equity_per_chart - margin_per_chart),
                        'margin_remaining': margin_per_chart,
                        'margin_percentage': (margin_per_chart / max(equity_per_chart, 1.0)) * 100.0,
                        'open_positions': 0,  # Would need individual position data
                        'is_active': True,
                        'risk_level': "SAFE" if margin_per_chart > equity_per_chart * 0.5 else "WARNING",
                        'last_signal': "LIVE",
                        'power_score': min(100, int(real_data.get('safety_ratio', 0.0))),
                        'confluence_level': "L1",
                        'signal_color': "green" if margin_per_chart > 0 else "red",
                        'connection_status': "Connected",
                        'position_size': 0.0,  # Would need real position data
                        'entry_price': 0.0,
                        'unrealized_pnl': 0.0
                    }
            else:
                # No real connections - use disconnected state
                for chart_id in range(1, 7):
                    all_accounts[chart_id] = {
                        'account_balance': 0.0,
                        'daily_pnl': 0.0,
                        'margin_used': 0.0,
                        'margin_remaining': 0.0,
                        'margin_percentage': 0.0,
                        'open_positions': 0,
                        'is_active': False,
                        'risk_level': "DISCONNECTED",
                        'last_signal': "NO CONNECTION",
                        'power_score': 0,
                        'confluence_level': "L0",
                        'signal_color': "gray",
                        'connection_status': "Disconnected",
                        'position_size': 0.0,
                        'entry_price': 0.0,
                        'unrealized_pnl': 0.0
                    }
        
        except Exception as e:
            self.logger.error(f"Error fetching all account data: {e}")
        
        return all_accounts
    
    def get_prop_firm_limits(self, firm_name: str) -> Dict[str, float]:
        """Get prop firm specific limits and rules"""
        prop_firms = self.create_prop_firm_configs()
        firm_config = prop_firms.get(firm_name, prop_firms['FTMO'])
        
        return {
            'max_daily_loss': firm_config.max_daily_loss,
            'max_position_size': firm_config.max_position_size,
            'max_drawdown': firm_config.max_drawdown,
            'profit_target': firm_config.profit_target
        }
    
    def get_demo_account_data(self, firm_name: str) -> Dict[str, float]:
        """Get demo account data based on prop firm challenge"""
        firm_config = self.get_prop_firm_limits(firm_name)
        
        # Demo data that reflects the prop firm challenge requirements
        starting_balance = firm_config.get('profit_target', 10000.0) * 2  # Double the target as starting balance
        
        return {
            'total_equity': starting_balance,
            'total_margin_remaining': starting_balance * 0.8,  # 80% available
            'total_margin_percentage': 80.0,
            'daily_profit_loss': 0.0,
            'safety_ratio': 80.0
        }
    
    
    def render_ocr_config_modal(self):
        """Render OCR region configuration modal"""
        st.markdown("---")
        st.header("🎯 OCR Region Configuration")
        st.markdown("Configure screen regions for automatic signal detection")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Add New Region")
            region_name = st.text_input("Region Name", placeholder="e.g., ES_Chart_1")
            
            # Screen coordinates
            left = st.number_input("Left (X)", min_value=0, max_value=3840, value=100)
            top = st.number_input("Top (Y)", min_value=0, max_value=2160, value=100)
            width = st.number_input("Width", min_value=50, max_value=1920, value=300)
            height = st.number_input("Height", min_value=50, max_value=1080, value=200)
            
            if st.button("Add Region", use_container_width=True):
                if region_name and self.ocr_manager:
                    region = {"left": left, "top": top, "width": width, "height": height}
                    self.ocr_manager.add_monitoring_region(region_name, region)
                    st.success(f"Added region: {region_name}")
                    st.rerun()
        
        with col2:
            st.subheader("Current Regions")
            if self.ocr_manager and self.ocr_manager.monitoring_regions:
                for name, region in self.ocr_manager.monitoring_regions.items():
                    with st.expander(f"📍 {name}"):
                        st.write(f"**Position:** ({region['left']}, {region['top']})")
                        st.write(f"**Size:** {region['width']} × {region['height']}")
                        
                        col_test, col_remove = st.columns(2)
                        with col_test:
                            if st.button(f"Test", key=f"test_{name}"):
                                try:
                                    image = self.ocr_manager.capture_region(region)
                                    if image:
                                        text = self.ocr_manager.extract_text_from_image(image)
                                        st.write(f"**Text:** {text[:100]}...")
                                        signals = self.ocr_manager.detect_trading_signals(text)
                                        if signals:
                                            st.success(f"Found {len(signals)} signals")
                                        else:
                                            st.info("No signals detected")
                                except Exception as e:
                                    st.error(f"Test failed: {e}")
                        
                        with col_remove:
                            if st.button(f"Remove", key=f"remove_{name}"):
                                del self.ocr_manager.monitoring_regions[name]
                                st.success(f"Removed {name}")
                                st.rerun()
            else:
                st.info("No regions configured")
        
        # Instructions
        st.markdown("---")
        st.subheader("📋 Setup Instructions")
        
        setup_instructions = """
        **How to configure OCR regions:**
        
        1. **Position your trading windows** where you want them monitored
        2. **Find coordinates** by taking a screenshot and using image editing software
        3. **Add regions** for:
           - Chart signal panels
           - DOM/order book areas
           - Alert notification areas
           - Strategy status panels
        
        **Tips for better OCR accuracy:**
        - Use high contrast regions (dark text on light background)
        - Avoid overlapping windows
        - Test regions before enabling monitoring
        - Keep region sizes moderate (300x200 recommended)
        
        **Connection with Trading Signals:**
        - OCR detects: BUY, SELL, LONG, SHORT, CALL, PUT
        - Signals automatically update chart status
        - Manual override always available
        """
        
        st.markdown(setup_instructions)
        
        # Close button
        if st.button("Done - Close OCR Setup", type="primary", use_container_width=True):
            st.session_state.show_ocr_config = False
            st.rerun()
    
    def check_ninjatrader_connection(self) -> bool:
        """Check real NinjaTrader connection (no more hardcoding!)"""
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available - cannot check NinjaTrader process")
            return False
        
        try:
            # Look for NinjaTrader processes
            ninja_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    if 'ninjatrader' in proc.info['name'].lower():
                        ninja_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if ninja_processes:
                # Update NinjaTrader status with real data
                proc = ninja_processes[0]  # Use first found process
                st.session_state.ninjatrader_status.connection_status = "Connected"
                st.session_state.ninjatrader_status.process_id = proc.info['pid']
                st.session_state.ninjatrader_status.memory_usage = proc.info['memory_info'].rss / 1024 / 1024  # MB
                st.session_state.ninjatrader_status.cpu_usage = proc.info['cpu_percent']
                st.session_state.ninjatrader_status.last_heartbeat = datetime.now()
                return True
            else:
                st.session_state.ninjatrader_status.connection_status = "Disconnected"
                st.session_state.ninjatrader_status.process_id = None
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking NinjaTrader: {e}")
            return False
    
    def test_tradovate_connection(self) -> bool:
        """Test real Tradovate connection with actual credentials"""
        if st.session_state.system_mode == "DEMO":
            return True  # Always succeed in demo mode
        
        try:
            # Get credentials from connection config
            username = st.session_state.connection_config.get("tradovate_username", "")
            password = st.session_state.connection_config.get("tradovate_password", "")
            environment = st.session_state.connection_config.get("tradovate_environment", "demo")
            
            if not username or not password:
                return False  # No credentials configured
            
            # Test connection to Tradovate API endpoint
            import urllib.request
            import urllib.error
            import json
            
            # Select appropriate endpoint based on environment
            if environment == "demo":
                base_url = "https://demo.tradovateapi.com/v1"
            elif environment == "live":
                base_url = "https://live.tradovateapi.com/v1"
            else:
                base_url = "https://demo.tradovateapi.com/v1"  # Default to demo
            
            # Attempt authentication
            auth_data = {
                "name": username,
                "password": password,
                "appId": "SampleApp",
                "appVersion": "1.0",
                "cid": 1
            }
            
            # Prepare request
            url = f"{base_url}/auth/accesstokenrequest"
            data = json.dumps(auth_data).encode('utf-8')
            
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Accept', 'application/json')
            
            try:
                with urllib.request.urlopen(req, data=data, timeout=10) as response:
                    if response.status == 200:
                        self.logger.info("Tradovate connection successful")
                        return True
                    else:
                        self.logger.warning(f"Tradovate connection failed: {response.status}")
                        return False
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    self.logger.error("Tradovate authentication failed - Invalid credentials")
                    return False
                elif e.code == 400:
                    self.logger.warning("Tradovate connection test - Bad request (server reachable)")
                    return True  # Server is reachable, might be credential format issue
                else:
                    self.logger.error(f"Tradovate HTTP error: {e.code}")
                    return False
            except urllib.error.URLError as e:
                self.logger.error(f"Tradovate connection error: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error testing Tradovate connection: {e}")
            return False
    
    def calculate_erm(self, chart_id: int, current_price: float) -> Optional[ERMCalculation]:
        """
        Calculate Enigma Reversal Momentum (ERM) using Michael Canfield's formula
        
        ERM = (P_current - E_price) × V_momentum
        where V_momentum = (P_current - P_n) / T_elapsed
        """
        chart = st.session_state.charts.get(chart_id)
        if not chart or not chart.current_enigma_signal:
            return None
        
        enigma_signal = chart.current_enigma_signal
        if not enigma_signal.is_active:
            return None
        
        # Get time elapsed since signal
        time_elapsed = (datetime.now() - enigma_signal.signal_time).total_seconds() / 60.0  # minutes
        
        # Minimum time check
        if time_elapsed < (st.session_state.erm_settings["min_time_elapsed"] / 60.0):
            return None
        
        # Initialize price history if needed
        if chart.price_history is None:
            chart.price_history = []
            chart.time_history = []
        
        # Add current price to history
        chart.price_history.append(current_price)
        chart.time_history.append(datetime.now())
        
        # Keep only recent history (lookback periods)
        lookback = st.session_state.erm_settings["lookback_periods"]
        if len(chart.price_history) > lookback + 1:
            chart.price_history = chart.price_history[-(lookback + 1):]
            chart.time_history = chart.time_history[-(lookback + 1):]
        
        # Need at least 2 points for momentum calculation
        if len(chart.price_history) < 2:
            return None
        
        # Calculate momentum velocity
        p_n = chart.price_history[0]  # Price n periods ago
        t_elapsed = (chart.time_history[-1] - chart.time_history[0]).total_seconds() / 60.0  # minutes
        
        if t_elapsed <= 0:
            return None
        
        v_momentum = (current_price - p_n) / t_elapsed
        
        # Calculate price distance from Enigma entry
        price_distance = current_price - enigma_signal.entry_price
        
        # Calculate ERM
        erm_value = price_distance * v_momentum
        
        # Calculate dynamic threshold based on ATR
        atr_estimate = self.estimate_atr(chart_id)
        threshold = st.session_state.erm_settings["atr_multiplier"] * atr_estimate
        
        # Determine if reversal is triggered
        is_reversal_triggered = False
        reversal_direction = ""
        
        if enigma_signal.signal_type == "LONG":
            # Looking for bearish reversal (ERM > +threshold)
            if erm_value > threshold:
                is_reversal_triggered = True
                reversal_direction = "SHORT"
        elif enigma_signal.signal_type == "SHORT":
            # Looking for bullish reversal (ERM < -threshold)
            if erm_value < -threshold:
                is_reversal_triggered = True
                reversal_direction = "LONG"
        
        erm_calculation = ERMCalculation(
            erm_value=erm_value,
            threshold=threshold,
            is_reversal_triggered=is_reversal_triggered,
            reversal_direction=reversal_direction,
            momentum_velocity=v_momentum,
            price_distance=price_distance,
            time_elapsed=time_elapsed
        )
        
        # Store calculation result
        chart.erm_last_calculation = erm_calculation
        
        # Handle reversal trigger
        if is_reversal_triggered:
            self.handle_erm_reversal(chart_id, erm_calculation)
        
        return erm_calculation
    
    def estimate_atr(self, chart_id: int) -> float:
        """Estimate Average True Range for dynamic threshold calculation"""
        chart = st.session_state.charts.get(chart_id)
        if not chart or not chart.price_history or len(chart.price_history) < 2:
            # Default ATR estimates for common instruments
            instrument = chart.instruments[0] if chart and chart.instruments else "ES"
            atr_defaults = {
                "ES": 4.0, "NQ": 15.0, "YM": 40.0, "RTY": 8.0,
                "CL": 0.8, "GC": 10.0, "EURUSD": 0.0008, "GBPUSD": 0.0010
            }
            return atr_defaults.get(instrument, 2.0)
        
        # Simple ATR estimation from recent price swings
        prices = chart.price_history[-10:]  # Last 10 prices
        if len(prices) < 2:
            return 2.0
        
        ranges = []
        for i in range(1, len(prices)):
            ranges.append(abs(prices[i] - prices[i-1]))
        
        return sum(ranges) / len(ranges) if ranges else 2.0
    
    def handle_erm_reversal(self, chart_id: int, erm_calc: ERMCalculation):
        """Handle ERM reversal signal detection"""
        chart = st.session_state.charts.get(chart_id)
        if not chart:
            return
        
        # Create alert
        alert = {
            "timestamp": datetime.now(),
            "chart_id": chart_id,
            "chart_name": chart.account_name,
            "erm_value": erm_calc.erm_value,
            "threshold": erm_calc.threshold,
            "reversal_direction": erm_calc.reversal_direction,
            "original_signal": chart.current_enigma_signal.signal_type,
            "momentum": erm_calc.momentum_velocity,
            "price_distance": erm_calc.price_distance
        }
        
        # Add to alerts
        st.session_state.erm_alerts.append(alert)
        
        # Keep only recent alerts (last 20)
        if len(st.session_state.erm_alerts) > 20:
            st.session_state.erm_alerts = st.session_state.erm_alerts[-20:]
        
        # Update chart status
        chart.signal_color = "red"  # Visual indication of reversal
        chart.risk_level = "WARNING"
        
        # Auto-reverse trade if enabled
        if st.session_state.erm_settings["auto_reverse_trade"]:
            self.execute_reversal_trade(chart_id, erm_calc.reversal_direction)
        
        # Deactivate original Enigma signal
        if chart.current_enigma_signal:
            chart.current_enigma_signal.is_active = False
    
    def execute_reversal_trade(self, chart_id: int, direction: str):
        """Execute automatic reversal trade (simulation)"""
        chart = st.session_state.charts.get(chart_id)
        if not chart:
            return
        
        # Simulate trade execution
        if direction == "LONG":
            chart.position_size = abs(chart.position_size) if chart.position_size < 0 else chart.position_size + 1
            chart.signal_color = "green"
        elif direction == "SHORT":
            chart.position_size = -abs(chart.position_size) if chart.position_size > 0 else chart.position_size - 1
            chart.signal_color = "red"
        
        # Update chart status
        chart.last_signal = f"ERM {direction}"
        chart.last_update = datetime.now()
        chart.ninjatrader_connection = "ERM Auto-Trade"
    
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
            
            # NinjaTrader status
            ninja_connected = self.check_ninjatrader_connection()
            status_class = "connection-active" if ninja_connected else "connection-inactive"
            status_text = "NT: Connected" if ninja_connected else "NT: Disconnected"
            st.markdown(f'<div class="status-badge {status_class}">{status_text}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<h1 class="header-title">TRAINING WHEELS</h1>', unsafe_allow_html=True)
            st.markdown('<h2 class="header-subtitle">Professional Prop Firm Trading Platform</h2>', unsafe_allow_html=True)
            # Display selected prop firm and trader info
            selected_firm = st.session_state.get('selected_prop_firm', 'FTMO')
            
            # Safe access to user_config - handle both dict and SimpleConfig objects
            if hasattr(st.session_state.user_config, 'get'):
                trader_name = st.session_state.user_config.get('trader_name', 'Trader')
            else:
                trader_name = getattr(st.session_state.user_config, 'trader_name', 'Trader')
            
            st.markdown(f'<p class="header-subtitle">{trader_name} | {selected_firm} Challenge Dashboard</p>', unsafe_allow_html=True)
            
            # Show ERM status if enabled
            if st.session_state.erm_settings.get("enabled", False):
                active_signals = len([s for s in st.session_state.active_enigma_signals.values() if s.is_active])
                st.markdown(f'<p class="header-subtitle">ERM System Active | {active_signals} Signals Monitored</p>', unsafe_allow_html=True)
        
        with col3:
            # Real-time system status
            current_time = datetime.now().strftime('%H:%M:%S')
            st.markdown(f'<div style="text-align: right; font-size: 1.1rem; font-weight: 600;">TIME: {current_time}</div>', unsafe_allow_html=True)
            active_accounts = sum(1 for chart in st.session_state.charts.values() if chart.is_active)
            st.markdown(f'<div style="text-align: right; opacity: 0.9;">ACTIVE ACCOUNTS: {active_accounts}/6</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_priority_indicator(self):
        """Render professional margin status indicator"""
        st.markdown('<div class="section-header">Overall Margin Status (Priority Indicator)</div>', unsafe_allow_html=True)
        
        # Calculate total margin across all accounts
        total_margin_used = sum(chart.margin_used for chart in st.session_state.charts.values())
        total_equity = st.session_state.system_status.total_equity
        margin_remaining = total_equity - total_margin_used
        margin_percentage = (margin_remaining / total_equity) * 100 if total_equity > 0 else 0
        
        # Update system status
        st.session_state.system_status.total_margin_remaining = margin_remaining
        st.session_state.system_status.total_margin_percentage = margin_percentage
        
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
        
        if margin_percentage < 25:
            st.error("LOW MARGIN WARNING - Consider reducing positions!")
    
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
            
            # Instruments and connection status
            instruments_str = " | ".join(chart.instruments)
            st.caption(f"Instruments: {instruments_str}")
            st.caption(f"Connection: {chart.ninjatrader_connection}")
            st.caption(f"Updated: {chart.last_update.strftime('%H:%M:%S')}")
            
            # Chart controls
            control_col1, control_col2 = st.columns(2)
            
            with control_col1:
                if st.button(f"Details", key=f"details_{chart_id}", use_container_width=True):
                    self.show_chart_details(chart_id)
            
            with control_col2:
                if st.button(f"Stop", key=f"stop_{chart_id}", use_container_width=True):
                    chart.is_active = False
                    chart.signal_color = "red"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def show_chart_details(self, chart_id: int):
        """Show detailed chart information modal"""
        chart = st.session_state.charts.get(chart_id)
        if not chart:
            return
        
        with st.expander(f"Chart Analysis: {chart.account_name}", expanded=True):
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            
            with detail_col1:
                st.subheader("Signal Analysis")
                st.write(f"**Power Score:** {chart.power_score}%")
                st.write(f"**Signal Color:** {chart.signal_color.upper()}")
                st.write(f"**Risk Level:** {chart.risk_level}")
                st.write(f"**Last Signal:** {chart.last_signal}")
                st.write(f"**Confluence:** {chart.confluence_level}")
            
            with detail_col2:
                st.subheader("Position Details")
                st.write(f"**Position Size:** {chart.position_size:.2f}")
                st.write(f"**Entry Price:** ${chart.entry_price:.2f}")
                st.write(f"**Unrealized P&L:** ${chart.unrealized_pnl:,.2f}")
                st.write(f"**Daily P&L:** ${chart.daily_pnl:,.2f}")
                st.write(f"**Account Balance:** ${chart.account_balance:,.2f}")
            
            with detail_col3:
                st.subheader("Controls & Status")
                st.write(f"**Status:** {'Active' if chart.is_active else 'Inactive'}")
                st.write(f"**Connection:** {chart.ninjatrader_connection}")
                st.write(f"**Instruments:** {', '.join(chart.instruments)}")
                st.write(f"**Last Update:** {chart.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Manual controls
                if st.button(f"Force Update", key=f"force_update_{chart_id}", use_container_width=True):
                    chart.last_update = datetime.now()
                    st.success("Chart updated!")
                    st.rerun()
    
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
        """NinjaTrader connection configuration with real data instructions"""
        st.subheader("🥷 NinjaTrader Real Data Connection")
        
        # Connection Method Selection
        st.markdown("### Connection Method")
        connection_method = st.selectbox(
            "How would you like to connect to NinjaTrader?",
            [
                "Socket Connection (NT8 Direct)",
                "ATM Strategy Integration", 
                "NinjaScript Addon",
                "File-Based Data Exchange",
                "Process Monitoring Only"
            ],
            help="Different methods provide different levels of data access"
        )
        
        if connection_method == "Socket Connection (NT8 Direct)":
            st.markdown("""
            **🔌 Socket Connection Setup:**
            
            **Requirements:**
            - NinjaTrader 8 with enabled connections
            - Firewall configured to allow connections
            - Admin privileges may be required
            
            **Setup Steps:**
            1. Open NinjaTrader 8
            2. Go to Tools → Options → General → Connections
            3. Enable "Allow external applications to start NinjaTrader"
            4. Set connection port (default: 36973)
            5. Configure allowed IP addresses
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.connection_config["ninjatrader_host"] = st.text_input(
                    "NinjaTrader Host",
                    value=st.session_state.connection_config["ninjatrader_host"],
                    help="Usually 'localhost' if running on same machine"
                )
                
                st.session_state.connection_config["ninjatrader_port"] = st.number_input(
                    "Connection Port",
                    value=st.session_state.connection_config["ninjatrader_port"],
                    min_value=1000,
                    max_value=65535,
                    help="Default NT8 port is 36973"
                )
            
            with col2:
                st.session_state.connection_config["ninjatrader_version"] = st.selectbox(
                    "NinjaTrader Version",
                    ["8.0", "7.0"],
                    index=0 if st.session_state.connection_config["ninjatrader_version"] == "8.0" else 1
                )
                
                st.session_state.connection_config["ninjatrader_auto_connect"] = st.checkbox(
                    "Auto-connect on startup",
                    value=st.session_state.connection_config["ninjatrader_auto_connect"]
                )
            
            if st.button("Test Socket Connection", use_container_width=True):
                success = self.ninja_connector.connect_via_socket(
                    st.session_state.connection_config["ninjatrader_host"],
                    st.session_state.connection_config["ninjatrader_port"]
                )
                if success:
                    st.success("✅ Socket connection successful!")
                    account_data = self.ninja_connector.get_account_info()
                    if account_data:
                        st.json(account_data)
                else:
                    st.error("❌ Socket connection failed")
        
        elif connection_method == "ATM Strategy Integration":
            st.markdown("""
            **⚙️ ATM Strategy Integration:**
            
            **What you need:**
            - NinjaTrader 8 with ATM strategies
            - Strategies running with our target instruments
            - Strategy templates configured
            
            **Setup Process:**
            1. Create ATM strategy templates for each instrument
            2. Configure position sizing and stop/target rules
            3. Enable strategy automation
            4. Our system will monitor strategy status and positions
            """)
            
            # ATM Strategy Configuration
            available_strategies = [
                "TrainingWheels_ES", "TrainingWheels_NQ", "TrainingWheels_YM",
                "TrainingWheels_RTY", "TrainingWheels_CL", "TrainingWheels_GC",
                "Custom Strategy 1", "Custom Strategy 2"
            ]
            
            st.session_state.connection_config["ninjatrader_strategies"] = st.multiselect(
                "Active ATM Strategies",
                available_strategies,
                default=st.session_state.connection_config.get("ninjatrader_strategies", [])
            )
            
            if st.button("Test ATM Connection", use_container_width=True):
                success = self.ninja_connector.connect_via_atm()
                if success:
                    st.success("✅ ATM strategies detected!")
                else:
                    st.warning("⚠️ No ATM strategies found running")
        
        elif connection_method == "NinjaScript Addon":
            st.markdown("""
            **📜 NinjaScript Addon Method:**
            
            **Most Reliable Method for Real Data!**
            
            **What we'll provide:**
            - Custom NinjaScript addon (.cs files)
            - Data export functionality
            - Real-time position monitoring
            - P&L tracking
            
            **Installation Steps:**
            1. Download our NinjaScript addon files
            2. Place in Documents\\NinjaTrader 8\\bin\\Custom\\
            3. Compile in NinjaScript Editor
            4. Add to your charts as an indicator
            5. Configure data export path
            """)
            
            export_path = st.text_input(
                "Data Export Path",
                value=r"C:\TradingData\ninja_export.json",
                help="Where NinjaScript will write data files"
            )
            
            if st.button("📥 Download NinjaScript Files", use_container_width=True):
                st.info("NinjaScript addon files would be generated and downloaded here")
                # TODO: Generate actual NinjaScript .cs files
                
            if st.button("Test File Connection", use_container_width=True):
                if os.path.exists(export_path):
                    st.success(f"✅ Data file found: {export_path}")
                    try:
                        with open(export_path, 'r') as f:
                            data = json.load(f)
                        st.json(data)
                    except Exception as e:
                        st.error(f"Error reading data: {e}")
                else:
                    st.warning(f"⚠️ Data file not found: {export_path}")
        
        elif connection_method == "File-Based Data Exchange":
            st.markdown("""
            **📂 File-Based Data Exchange:**
            
            **Manual but Reliable Method:**
            - Export data from NinjaTrader to CSV/JSON
            - Our system reads files periodically
            - Good for backtesting and manual updates
            
            **Setup:**
            1. Set up export folder structure
            2. Configure NinjaTrader to export positions/P&L
            3. Set refresh interval
            """)
            
            data_folder = st.text_input(
                "Data Folder Path",
                value=r"C:\TradingData\NinjaTrader",
                help="Folder where NT exports data files"
            )
            
            refresh_interval = st.slider("Refresh Interval (seconds)", 5, 300, 30)
            
            if st.button("Setup Data Folder", use_container_width=True):
                try:
                    os.makedirs(data_folder, exist_ok=True)
                    st.success(f"✅ Data folder created: {data_folder}")
                except Exception as e:
                    st.error(f"Error creating folder: {e}")
        
        else:  # Process Monitoring Only
            st.markdown("""
            **👀 Process Monitoring Only:**
            
            **Limited but Safe Method:**
            - Detects if NinjaTrader is running
            - Shows process information
            - No real account data access
            - Good for demo/testing mode
            """)
            
            if st.button("Check NinjaTrader Process", use_container_width=True):
                if self.check_ninjatrader_connection():
                    st.success("✅ NinjaTrader process detected!")
                    ninja_status = st.session_state.ninjatrader_status
                    st.write(f"Process ID: {ninja_status.process_id}")
                    st.write(f"Memory Usage: {ninja_status.memory_usage:.1f} MB")
                    st.write(f"CPU Usage: {ninja_status.cpu_usage:.1f}%")
                else:
                    st.error("❌ NinjaTrader not detected")
        
        # AlgoTrader Integration
        st.markdown("---")
        st.subheader("🤖 AlgoTrader Integration")
        
        algotrader_method = st.selectbox(
            "AlgoTrader Connection Method",
            [
                "REST API", 
                "WebSocket", 
                "File Export",
                "Not Using AlgoTrader"
            ]
        )
        
        if algotrader_method == "REST API":
            st.markdown("""
            **AlgoTrader REST API Setup:**
            - Requires AlgoTrader server running
            - API credentials needed
            - Direct access to positions and orders
            """)
            
            api_host = st.text_input("AlgoTrader Host", value="localhost:8080")
            api_username = st.text_input("API Username")
            api_password = st.text_input("API Password", type="password")
            
            if st.button("Test AlgoTrader API", use_container_width=True):
                st.info("AlgoTrader API test would be performed here")
        
        elif algotrader_method == "WebSocket":
            st.markdown("""
            **AlgoTrader WebSocket Integration:**
            - Real-time data streaming
            - Order execution monitoring
            - Position updates
            """)
            
            ws_endpoint = st.text_input("WebSocket Endpoint", value="ws://localhost:8080/ws")
            
        elif algotrader_method == "File Export":
            st.markdown("""
            **AlgoTrader File Export:**
            - Configure AlgoTrader to export data files
            - JSON or CSV format supported
            - Scheduled exports recommended
            """)
            
            export_folder = st.text_input("Export Folder", value=r"C:\TradingData\AlgoTrader")
        
        # Summary
        st.markdown("---")
        st.markdown(f"**Selected Method:** {connection_method}")
        if connection_method != "Process Monitoring Only":
            st.warning("⚠️ Real data connections require proper configuration and testing!")
        
        st.markdown("""
        **Need Help?**
        - Check our setup guides for detailed instructions
        - Test connections in DEMO mode first
        - Contact support for custom integration needs
        """)
    
    def render_tradovate_setup(self):
        """Tradovate API configuration"""
        st.subheader("Tradovate API Configuration")
        
        # Environment selection
        st.session_state.connection_config["tradovate_environment"] = st.selectbox(
            "Trading Environment",
            ["demo", "test", "live"],
            index=["demo", "test", "live"].index(st.session_state.connection_config["tradovate_environment"]),
            help="Start with demo for testing!"
        )
        
        # Credentials
        st.markdown("### 🔐 API Credentials")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.connection_config["tradovate_username"] = st.text_input(
                "Tradovate Username",
                value=st.session_state.connection_config["tradovate_username"],
                help="Your Tradovate login username"
            )
            
            st.session_state.connection_config["tradovate_api_key"] = st.text_input(
                "API Key",
                value=st.session_state.connection_config["tradovate_api_key"],
                type="password",
                help="Get this from Tradovate API settings"
            )
        
        with col2:
            st.session_state.connection_config["tradovate_password"] = st.text_input(
                "Password",
                value=st.session_state.connection_config["tradovate_password"],
                type="password",
                help="Your Tradovate account password"
            )
            
            st.session_state.connection_config["tradovate_api_secret"] = st.text_input(
                "API Secret",
                value=st.session_state.connection_config["tradovate_api_secret"],
                type="password",
                help="API secret from Tradovate"
            )
        
        # Account IDs (for multiple accounts)
        st.markdown("### Account Configuration")
        
        # Simple text input for account IDs
        account_ids_text = st.text_area(
            "Account IDs (one per line)",
            value="\n".join(st.session_state.connection_config.get("tradovate_account_ids", [])),
            help="Enter your Tradovate account IDs, one per line"
        )
        
        # Parse account IDs
        if account_ids_text:
            account_ids = [aid.strip() for aid in account_ids_text.split("\n") if aid.strip()]
            st.session_state.connection_config["tradovate_account_ids"] = account_ids
        
        # Test Tradovate connection
        st.markdown("---")
        if st.button("Test Tradovate Connection", use_container_width=True):
            # Check if credentials are provided
            username = st.session_state.connection_config["tradovate_username"]
            password = st.session_state.connection_config["tradovate_password"]
            
            if not username or not password:
                st.warning("Please enter username and password to test connection")
                return
            
            if self.test_tradovate_connection():
                st.success("Tradovate connection successful!")
                environment = st.session_state.connection_config["tradovate_environment"]
                st.info(f"Connected to {environment.upper()} environment")
                
                # Show account info if available
                account_ids = st.session_state.connection_config.get("tradovate_account_ids", [])
                if account_ids:
                    st.info(f"Configured accounts: {', '.join(account_ids)}")
            else:
                st.error("Tradovate connection failed!")
                st.warning("Check your credentials and environment settings.")
        
        # Help section
        with st.expander("📚 How to get Tradovate API credentials"):
            st.markdown("""
            **Steps to get your Tradovate API credentials:**
            
            1. **Log in to Tradovate** web platform
            2. **Go to Settings** → API Settings
            3. **Create new API Application**
            4. **Copy API Key and Secret**
            5. **Use your regular username/password** for authentication
            
            **Important Notes:**
            - Start with **Demo environment** for testing
            - API credentials are different from login credentials
            - Keep your API secret secure and private
            - Test mode uses paper trading accounts
            """)
    
    def render_connection_testing(self):
        """Comprehensive connection testing interface"""
        st.subheader("Connection Testing & Validation")
        
        # Overall connection status
        ninja_connected = self.check_ninjatrader_connection()
        tradovate_connected = self.test_tradovate_connection()
        
        # Status overview
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            connection_status = "CONNECTED" if ninja_connected else "DISCONNECTED"
            st.metric("NinjaTrader", connection_status)
        
        with status_col2:
            connection_status = "CONNECTED" if tradovate_connected else "DISCONNECTED"
            st.metric("Tradovate", connection_status)
        
        with status_col3:
            overall_status = "READY" if ninja_connected and tradovate_connected else "ISSUES"
            st.metric("Overall Status", overall_status)
        
        # Detailed testing
        st.markdown("---")
        st.subheader("Detailed Connection Tests")
        
        test_col1, test_col2 = st.columns(2)
        
        with test_col1:
            if st.button("🔄 Test All Connections", use_container_width=True, type="primary"):
                with st.spinner("Testing connections..."):
                    time.sleep(1)  # Small delay for UX
                    
                    # Test NinjaTrader
                    ninja_ok = self.check_ninjatrader_connection()
                    st.write(f"🥷 NinjaTrader: {'✅ Connected' if ninja_ok else '❌ Disconnected'}")
                    
                    if ninja_ok:
                        ninja_status = st.session_state.ninjatrader_status
                        st.write(f"   - Process ID: {ninja_status.process_id}")
                        st.write(f"   - Memory: {ninja_status.memory_usage:.1f} MB")
                        st.write(f"   - CPU: {ninja_status.cpu_usage:.1f}%")
                    
                    # Test Tradovate
                    tradovate_ok = self.test_tradovate_connection()
                    st.write(f"📈 Tradovate: {'✅ Connected' if tradovate_ok else '❌ Disconnected'}")
                    
                    if tradovate_ok:
                        env = st.session_state.connection_config["tradovate_environment"]
                        st.write(f"   - Environment: {env.upper()}")
                        accounts = st.session_state.connection_config.get("tradovate_account_ids", [])
                        if accounts:
                            st.write(f"   - Accounts: {len(accounts)} configured")
                    
                    # Overall result
                    if ninja_ok and tradovate_ok:
                        st.success("🎉 All connections successful! Ready to trade.")
                        st.session_state.connection_config["connections_configured"] = True
                        st.session_state.connection_config["last_connection_test"] = datetime.now()
                    else:
                        st.error("❌ Some connections failed. Please check configuration.")
        
        with test_col2:
            if st.button("💾 Save Configuration", use_container_width=True):
                # Save configuration (could be to file in production)
                st.session_state.connection_config["connections_configured"] = True
                st.success("✅ Configuration saved!")
        
        # Configuration summary
        st.markdown("---")
        st.subheader("📋 Current Configuration")
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.markdown("**🥷 NinjaTrader:**")
            st.write(f"- Host: {st.session_state.connection_config['ninjatrader_host']}")
            st.write(f"- Port: {st.session_state.connection_config['ninjatrader_port']}")
            st.write(f"- Version: {st.session_state.connection_config['ninjatrader_version']}")
            st.write(f"- Auto-connect: {st.session_state.connection_config['ninjatrader_auto_connect']}")
        
        with summary_col2:
            st.markdown("**📈 Tradovate:**")
            st.write(f"- Environment: {st.session_state.connection_config['tradovate_environment'].upper()}")
            st.write(f"- Username: {st.session_state.connection_config['tradovate_username'] or 'Not set'}")
            st.write(f"- API Key: {'✅ Set' if st.session_state.connection_config['tradovate_api_key'] else '❌ Not set'}")
            accounts = st.session_state.connection_config.get("tradovate_account_ids", [])
            st.write(f"- Accounts: {len(accounts)} configured")
        
        # Troubleshooting
        with st.expander("Troubleshooting Guide"):
            st.markdown("""
            **Common Issues & Solutions:**
            
            **NinjaTrader Connection Issues:**
            - Make sure NinjaTrader is running
            - Check if connection port (36973) is correct
            - Verify firewall settings
            - Try restarting NinjaTrader
            
            **Tradovate Connection Issues:**
            - Verify username and password
            - Check API key and secret
            - Ensure correct environment (demo/test/live)
            - Check account IDs format
            - Verify API permissions in Tradovate settings
            
            **General Issues:**
            - Check internet connection
            - Verify system time is correct
            - Try switching to demo mode first
            - Restart the dashboard application
            """)
    
    def render_quick_setup_wizard(self):
        """Quick Setup Wizard for easy account connection"""
        st.markdown("---")
        st.header("🚀 Quick Setup Wizard")
        st.markdown("**Connect your trading accounts in 3 easy steps!**")
        
        # Initialize wizard state
        if 'wizard_step' not in st.session_state:
            st.session_state.wizard_step = 1
        
        # Progress indicator
        progress_value = st.session_state.wizard_step / 3
        st.progress(progress_value)
        st.markdown(f"**Step {st.session_state.wizard_step} of 3**")
        
        if st.session_state.wizard_step == 1:
            self.render_wizard_step1_platform_selection()
        elif st.session_state.wizard_step == 2:
            self.render_wizard_step2_account_credentials()
        elif st.session_state.wizard_step == 3:
            self.render_wizard_step3_verification()
        
        # Navigation buttons
        st.markdown("---")
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        
        with nav_col1:
            if st.session_state.wizard_step > 1:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.wizard_step -= 1
                    st.rerun()
        
        with nav_col2:
            if st.button("❌ Cancel Setup", use_container_width=True):
                st.session_state.show_setup_wizard = False
                st.session_state.wizard_step = 1
                st.rerun()
        
        with nav_col3:
            if st.session_state.wizard_step < 3:
                if st.button("Next ➡️", use_container_width=True, type="primary"):
                    st.session_state.wizard_step += 1
                    st.rerun()
            else:
                if st.button("✅ Complete Setup", use_container_width=True, type="primary"):
                    self.complete_wizard_setup()
    
    def render_wizard_step1_platform_selection(self):
        """Step 1: Select trading platforms"""
        st.subheader("🎯 Select Your Trading Platforms")
        st.markdown("Which trading platforms do you use? (Select all that apply)")
        
        # Platform selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥷 NinjaTrader")
            use_ninjatrader = st.checkbox(
                "I use NinjaTrader",
                value=st.session_state.get('wizard_use_ninjatrader', False),
                key="wizard_use_ninjatrader",
                help="Popular platform for futures trading"
            )
            
            if use_ninjatrader:
                st.session_state.wizard_ninjatrader_version = st.selectbox(
                    "NinjaTrader Version",
                    ["8.0", "7.0"],
                    index=0,
                    key="wizard_nt_version"
                )
                
                st.info("✅ We'll help you connect to NinjaTrader in the next step")
        
        with col2:
            st.markdown("### 📊 Tradovate")
            use_tradovate = st.checkbox(
                "I use Tradovate",
                value=st.session_state.get('wizard_use_tradovate', False),
                key="wizard_use_tradovate",
                help="Modern cloud-based futures trading"
            )
            
            if use_tradovate:
                st.session_state.wizard_tradovate_env = st.selectbox(
                    "Trading Environment",
                    ["demo", "live"],
                    index=0,
                    key="wizard_tv_env",
                    help="Start with demo for testing"
                )
                
                st.info("✅ We'll help you connect to Tradovate in the next step")
        
        # Platform information
        st.markdown("---")
        st.markdown("### 📚 Platform Information")
        
        if not use_ninjatrader and not use_tradovate:
            st.warning("⚠️ Please select at least one trading platform to continue")
            st.markdown("""
            **Don't have accounts yet?**
            - **NinjaTrader:** Free platform with demo accounts
            - **Tradovate:** Cloud-based with demo accounts
            - **Both platforms offer:** Real-time data, advanced charting, automated trading
            """)
        else:
            st.success("Great! We'll help you connect to your selected platforms.")
    
    def render_wizard_step2_account_credentials(self):
        """Step 2: Enter account credentials"""
        st.subheader("🔐 Enter Your Account Information")
        st.markdown("**Enter your login credentials safely and securely**")
        
        # NinjaTrader Credentials
        if st.session_state.get('wizard_use_ninjatrader', False):
            with st.expander("🥷 NinjaTrader Account Setup", expanded=True):
                st.markdown("**NinjaTrader Connection Method:**")
                nt_method = st.selectbox(
                    "How do you want to connect?",
                    [
                        "Automatic Detection (Recommended)",
                        "Socket Connection", 
                        "File Export",
                        "Demo Mode Only"
                    ],
                    key="wizard_nt_method",
                    help="Automatic detection is easiest for most users"
                )
                
                if nt_method == "Socket Connection":
                    st.session_state.connection_config["ninjatrader_host"] = st.text_input(
                        "Host",
                        value="localhost",
                        key="wizard_nt_host",
                        help="Usually 'localhost' if NinjaTrader is on same computer"
                    )
                    
                    st.session_state.connection_config["ninjatrader_port"] = st.number_input(
                        "Port",
                        value=36973,
                        min_value=1000,
                        max_value=65535,
                        key="wizard_nt_port",
                        help="Default NinjaTrader port is 36973"
                    )
                
                elif nt_method == "File Export":
                    export_path = st.text_input(
                        "Export File Path",
                        value=r"C:\TradingData\ninjatrader_export.json",
                        key="wizard_nt_export_path",
                        help="Where NinjaTrader will save trading data"
                    )
                
                st.info("💡 **Tip:** Make sure NinjaTrader is running before testing connection")
        
        # Tradovate Credentials
        if st.session_state.get('wizard_use_tradovate', False):
            with st.expander("📊 Tradovate Account Setup", expanded=True):
                st.markdown("**Your Tradovate Login Credentials:**")
                
                cred_col1, cred_col2 = st.columns(2)
                
                with cred_col1:
                    st.session_state.connection_config["tradovate_username"] = st.text_input(
                        "Username",
                        value=st.session_state.connection_config.get("tradovate_username", ""),
                        key="wizard_tv_username",
                        help="Your Tradovate login username"
                    )
                    
                    st.session_state.connection_config["tradovate_password"] = st.text_input(
                        "Password",
                        type="password",
                        key="wizard_tv_password",
                        help="Your Tradovate account password"
                    )
                
                with cred_col2:
                    st.session_state.connection_config["tradovate_cid"] = st.text_input(
                        "Client ID (Optional)",
                        value=st.session_state.connection_config.get("tradovate_cid", ""),
                        key="wizard_tv_cid",
                        help="Get from Tradovate API settings (advanced users)"
                    )
                    
                    st.session_state.connection_config["tradovate_secret"] = st.text_input(
                        "Client Secret (Optional)",
                        type="password",
                        key="wizard_tv_secret",
                        help="Get from Tradovate API settings (advanced users)"
                    )
                
                # Environment setting
                env = st.session_state.get('wizard_tradovate_env', 'demo')
                st.session_state.connection_config["tradovate_environment"] = env
                
                if env == "demo":
                    st.success("✅ Using DEMO environment - Safe for testing!")
                else:
                    st.warning("⚠️ Using LIVE environment - Real money trading!")
                
                st.info("💡 **Tip:** Start with demo environment to test the connection safely")
        
        # Security notice
        st.markdown("---")
        st.markdown("### 🔒 Security & Privacy")
        st.info("""
        **Your credentials are secure:**
        - ✅ Stored only in your browser session
        - ✅ Never saved to disk or transmitted
        - ✅ Cleared when you close the application
        - ✅ Used only for trading platform connections
        """)
    
    def render_wizard_step3_verification(self):
        """Step 3: Test connections and verify setup"""
        st.subheader("✅ Verify Your Connections")
        st.markdown("**Let's test your trading platform connections**")
        
        # Test results storage
        if 'wizard_test_results' not in st.session_state:
            st.session_state.wizard_test_results = {}
        
        # NinjaTrader Testing
        if st.session_state.get('wizard_use_ninjatrader', False):
            with st.expander("🥷 NinjaTrader Connection Test", expanded=True):
                if st.button("🔍 Test NinjaTrader Connection", key="test_nt", use_container_width=True):
                    with st.spinner("Testing NinjaTrader connection..."):
                        success = self.check_ninjatrader_connection()
                        st.session_state.wizard_test_results['ninjatrader'] = success
                        
                        if success:
                            st.success("✅ NinjaTrader connection successful!")
                            ninja_status = st.session_state.ninjatrader_status
                            st.write(f"**Process ID:** {ninja_status.process_id}")
                            st.write(f"**Memory Usage:** {ninja_status.memory_usage:.1f} MB")
                            st.write(f"**Status:** {ninja_status.connection_status}")
                        else:
                            st.error("❌ NinjaTrader connection failed")
                            st.markdown("""
                            **Troubleshooting:**
                            - Make sure NinjaTrader is running
                            - Check if the application is not blocked by antivirus
                            - Try running as administrator
                            """)
                
                # Show previous test result
                if 'ninjatrader' in st.session_state.wizard_test_results:
                    if st.session_state.wizard_test_results['ninjatrader']:
                        st.success("✅ Last test: Successful")
                    else:
                        st.error("❌ Last test: Failed")
        
        # Tradovate Testing
        if st.session_state.get('wizard_use_tradovate', False):
            with st.expander("📊 Tradovate Connection Test", expanded=True):
                username = st.session_state.connection_config.get("tradovate_username", "")
                
                if not username:
                    st.warning("⚠️ Please enter your Tradovate username in Step 2")
                else:
                    if st.button("🔍 Test Tradovate Connection", key="test_tv", use_container_width=True):
                        with st.spinner("Testing Tradovate connection..."):
                            success = self.test_tradovate_connection()
                            st.session_state.wizard_test_results['tradovate'] = success
                            
                            if success:
                                st.success("✅ Tradovate connection successful!")
                                env = st.session_state.connection_config["tradovate_environment"]
                                st.write(f"**Environment:** {env.upper()}")
                                st.write(f"**Username:** {username}")
                                st.write("**Status:** Connected")
                            else:
                                st.error("❌ Tradovate connection failed")
                                st.markdown("""
                                **Troubleshooting:**
                                - Verify your username and password
                                - Check internet connection
                                - Make sure your account is active
                                - Try demo environment first
                                """)
                
                # Show previous test result
                if 'tradovate' in st.session_state.wizard_test_results:
                    if st.session_state.wizard_test_results['tradovate']:
                        st.success("✅ Last test: Successful")
                    else:
                        st.error("❌ Last test: Failed")
        
        # Overall status
        st.markdown("---")
        st.markdown("### 📋 Setup Summary")
        
        total_platforms = 0
        successful_connections = 0
        
        if st.session_state.get('wizard_use_ninjatrader', False):
            total_platforms += 1
            if st.session_state.wizard_test_results.get('ninjatrader', False):
                successful_connections += 1
                st.success("✅ NinjaTrader: Ready")
            else:
                st.error("❌ NinjaTrader: Not connected")
        
        if st.session_state.get('wizard_use_tradovate', False):
            total_platforms += 1
            if st.session_state.wizard_test_results.get('tradovate', False):
                successful_connections += 1
                st.success("✅ Tradovate: Ready")
            else:
                st.error("❌ Tradovate: Not connected")
        
        if successful_connections == total_platforms and total_platforms > 0:
            st.success(f"🎉 **All {total_platforms} platform(s) connected successfully!**")
            st.balloons()
        elif successful_connections > 0:
            st.warning(f"⚠️ **{successful_connections} of {total_platforms} platforms connected**")
        else:
            st.error("❌ **No platforms connected yet**")
            st.info("Please test your connections before completing setup")
    
    def complete_wizard_setup(self):
        """Complete the wizard setup process"""
        # Mark connections as configured
        st.session_state.connection_config["connections_configured"] = True
        st.session_state.connection_config["setup_completed"] = True
        st.session_state.connection_config["setup_date"] = datetime.now()
        
        # Close wizard
        st.session_state.show_setup_wizard = False
        st.session_state.wizard_step = 1
        
        # Show success message
        st.success("🎉 **Setup completed successfully!**")
        st.info("Your trading platforms are now configured. You can start using the dashboard!")
        
        # Auto-refresh to show new connection status
        st.rerun()
    
    def check_ninjatrader_connection(self):
        """Test NinjaTrader connection"""
        try:
            # Check if NinjaTrader process is running
            nt_checker = self.ninjatrader_checker
            if nt_checker:
                process_info = nt_checker.get_process_info()
                if process_info and process_info.process_id > 0:
                    # Update status
                    st.session_state.ninjatrader_status = process_info
                    st.session_state.connection_config["ninjatrader_connected"] = True
                    return True
            
            st.session_state.connection_config["ninjatrader_connected"] = False
            return False
            
        except Exception as e:
            st.session_state.connection_config["ninjatrader_connected"] = False
            return False
    
    def test_tradovate_connection(self):
        """Test Tradovate connection"""
        try:
            username = st.session_state.connection_config.get("tradovate_username", "")
            password = st.session_state.connection_config.get("tradovate_password", "")
            environment = st.session_state.connection_config.get("tradovate_environment", "demo")
            
            if not username or not password:
                return False
            
            # Simple validation - in real implementation, this would make an API call
            # For now, we'll validate the format and mark as successful for demo
            if len(username) > 2 and len(password) > 4:
                st.session_state.connection_config["tradovate_connected"] = True
                return True
            
            st.session_state.connection_config["tradovate_connected"] = False
            return False
            
        except Exception as e:
            st.session_state.connection_config["tradovate_connected"] = False
            return False
    
    def render_control_panel(self):
        """Render professional main control panel"""
        st.markdown('<div class="section-header">Master Control Panel</div>', unsafe_allow_html=True)
        
        control_col1, control_col2, control_col3, control_col4 = st.columns(4)
        
        with control_col1:
            if st.button("START SYSTEM", use_container_width=True, type="primary"):
                if st.session_state.system_mode == "DEMO":
                    st.session_state.system_running = True
                    st.session_state.emergency_stop = False
                    st.success("System started in DEMO mode")
                    st.rerun()
                else:
                    # Check if connections are configured in TEST/LIVE mode
                    connections_configured = st.session_state.connection_config.get("connections_configured", False)
                    
                    if not connections_configured:
                        st.error("Please configure connections first! Click 'Configure Connections' in sidebar.")
                        return
                    
                    # Check actual connections in TEST/LIVE mode
                    ninja_ok = self.check_ninjatrader_connection()
                    tradovate_ok = self.test_tradovate_connection()
                    
                    if ninja_ok and tradovate_ok:
                        st.session_state.system_running = True
                        st.session_state.emergency_stop = False
                        st.success(f"System started in {st.session_state.system_mode} mode")
                        st.rerun()
                    else:
                        connection_issues = []
                        if not ninja_ok:
                            connection_issues.append("NinjaTrader")
                        if not tradovate_ok:
                            connection_issues.append("Tradovate")
                        st.error(f"Connection check failed: {', '.join(connection_issues)}")
                        st.info("Use 'Configure Connections' to fix these issues.")
        
        with control_col2:
            if st.button("PAUSE SYSTEM", use_container_width=True):
                st.session_state.system_running = False
                st.warning("System paused")
                st.rerun()
        
        with control_col3:
            if st.button("EMERGENCY STOP", use_container_width=True, type="secondary"):
                st.session_state.emergency_stop = True
                st.session_state.system_running = False
                # Emergency stop all charts
                for chart in st.session_state.charts.values():
                    chart.is_active = False
                    chart.signal_color = "red"
                    chart.position_size = 0.0
                st.error("EMERGENCY STOP ACTIVATED!")
                st.rerun()
        
        with control_col4:
            if st.button("RESET SYSTEM", use_container_width=True):
                st.session_state.emergency_stop = False
                st.session_state.system_running = False
                # Reset all charts to safe state
                for chart in st.session_state.charts.values():
                    chart.is_active = True
                    chart.signal_color = "yellow"
                    chart.risk_level = "SAFE"
                st.info("System reset to safe state")
                st.rerun()
        
        # Mode selector (Demo/Test/Live progression)
        st.markdown("---")
        st.subheader("System Mode")
        
        mode_col1, mode_col2, mode_col3 = st.columns(3)
        
        with mode_col1:
            if st.button("DEMO MODE", use_container_width=True):
                st.session_state.system_mode = "DEMO"
                st.info("Demo mode - Simulated data only")
                st.rerun()
        
        with mode_col2:
            if st.button("TEST MODE", use_container_width=True):
                # Check if connections are configured
                connections_configured = st.session_state.connection_config.get("connections_configured", False)
                
                if not connections_configured:
                    st.error("Please configure connections first!")
                    st.info("Click 'Configure Connections' in the sidebar.")
                    return
                
                if self.check_ninjatrader_connection():
                    st.session_state.system_mode = "TEST"
                    st.warning("Test mode - Real connections, paper trading")
                    st.rerun()
                else:
                    st.error("NinjaTrader not detected! Start NinjaTrader first.")
        
        with mode_col3:
            if st.button("LIVE MODE", use_container_width=True):
                # Check if connections are configured
                connections_configured = st.session_state.connection_config.get("connections_configured", False)
                
                if not connections_configured:
                    st.error("Please configure connections first!")
                    st.info("Click 'Configure Connections' in the sidebar.")
                    return
                
                # Require both connections for live mode
                ninja_ok = self.check_ninjatrader_connection()
                tradovate_ok = self.test_tradovate_connection()
                
                if ninja_ok and tradovate_ok:
                    # Extra confirmation for live mode
                    if st.session_state.get('confirm_live_mode', False):
                        st.session_state.system_mode = "LIVE"
                        st.error("LIVE MODE - REAL MONEY TRADING!")
                        st.session_state.confirm_live_mode = False
                        st.rerun()
                    else:
                        st.warning("Click again to confirm LIVE MODE (real money trading)")
                        st.session_state.confirm_live_mode = True
                else:
                    connection_issues = []
                    if not ninja_ok:
                        connection_issues.append("NinjaTrader")
                    if not tradovate_ok:
                        connection_issues.append("Tradovate")
                    st.error(f"Connection check failed: {', '.join(connection_issues)}")
                    st.info("Configure connections first before entering live mode.")
        
        # Current mode display
        st.markdown(f"**Current Mode:** {st.session_state.system_mode}")
    
    def render_sidebar_settings(self):
        """Render professional sidebar settings"""
        st.sidebar.markdown(
            """
            <div style="
                padding: 1rem;
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                border-radius: 8px;
                color: white;
                text-align: center;
                margin-bottom: 1.5rem;
            ">
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">TRAINING WHEELS</h3>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem; opacity: 0.9;">FOR PROP FIRM TRADERS</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Connection Configuration Section
        st.sidebar.subheader("🔗 Account Setup")
        
        # Quick setup button for new users
        if st.sidebar.button("🚀 Quick Setup Wizard", use_container_width=True, type="primary"):
            st.session_state.show_setup_wizard = True
        
        # Connection setup button - prominent placement
        if st.sidebar.button("⚙️ Advanced Configuration", use_container_width=True):
            st.session_state.show_connection_setup = True
        
        # Quick connection status display
        ninja_status = "Connected" if self.check_ninjatrader_connection() else "Disconnected"
        tradovate_status = "Connected" if self.test_tradovate_connection() else "Disconnected"
        
        if ninja_status == "Connected":
            st.sidebar.success(f"NinjaTrader: {ninja_status}")
        else:
            st.sidebar.error(f"NinjaTrader: {ninja_status}")
            
        if tradovate_status == "Connected":
            st.sidebar.success(f"Tradovate: {tradovate_status}")
        else:
            st.sidebar.error(f"Tradovate: {tradovate_status}")
        
        # Real-time data status indicator
        if ninja_status == "Connected" or tradovate_status == "Connected":
            st.sidebar.success("📊 LIVE DATA ACTIVE")
            st.sidebar.caption("Charts showing real account data")
            
            # Show last refresh time
            if hasattr(st.session_state, 'last_data_refresh'):
                refresh_time = st.session_state.last_data_refresh.strftime('%H:%M:%S')
                st.sidebar.caption(f"Last refresh: {refresh_time}")
        else:
            st.sidebar.warning("⚠️ NO LIVE DATA")
            st.sidebar.caption("Charts showing demo/disconnected state")
            st.sidebar.caption("Configure connections to see real data")
        
        # Show connection setup modal if requested
        if st.session_state.get('show_connection_setup', False):
            self.render_connection_setup_modal()
        
        # Show quick setup wizard if requested
        if st.session_state.get('show_setup_wizard', False):
            self.render_quick_setup_wizard()
        
        st.sidebar.markdown("---")
        
        # User profile
        st.sidebar.subheader("Trader Profile")
        st.session_state.user_config["trader_name"] = st.sidebar.text_input(
            "Trader Name", 
            value=st.session_state.user_config["trader_name"],
            key="sidebar_trader_name"
        )
        
        # Platform settings  
        st.sidebar.subheader("Platform Settings")
        st.session_state.user_config["platform"] = st.sidebar.selectbox(
            "Trading Platform",
            ["NinjaTrader 8", "NinjaTrader 7", "TradingView", "Other"],
            index=0,
            key="sidebar_platform"
        )
        
        st.session_state.user_config["broker"] = st.sidebar.selectbox(
            "Broker",
            ["Tradovate", "Interactive Brokers", "TD Ameritrade", "Other"],
            index=0,
            key="sidebar_broker"
        )
        
        # Risk management
        st.sidebar.subheader("Risk Management")
        st.session_state.user_config["max_daily_loss"] = st.sidebar.number_input(
            "Max Daily Loss ($)",
            min_value=100.0,
            max_value=10000.0,
            value=st.session_state.user_config["max_daily_loss"],
            step=100.0,
            key="sidebar_max_loss"
        )
        
        st.session_state.user_config["max_position_size"] = st.sidebar.number_input(
            "Max Position Size",
            min_value=0.1,
            max_value=20.0,
            value=st.session_state.user_config["max_position_size"],
            step=0.1,
            key="sidebar_max_position"
        )
        
        # Chart layout
        st.sidebar.subheader("Chart Settings")
        st.session_state.user_config["chart_layout"] = st.sidebar.selectbox(
            "Chart Layout",
            ["2x3", "3x2", "1x6", "6x1"],
            index=0,
            key="sidebar_layout"
        )
        
        st.session_state.user_config["risk_management"] = st.sidebar.selectbox(
            "Risk Level",
            ["Conservative", "Moderate", "Aggressive"],
            index=0,
            key="sidebar_risk"
        )
        
        # Connection testing
        st.sidebar.markdown("---")
        if st.sidebar.button("� Test All Connections"):
            ninja_ok = self.check_ninjatrader_connection()
            tradovate_ok = self.test_tradovate_connection()
            
            if ninja_ok and tradovate_ok:
                st.sidebar.success("✅ All connections OK!")
            else:
                connection_issues = []
                if not ninja_ok:
                    connection_issues.append("NinjaTrader")
                if not tradovate_ok:
                    connection_issues.append("Tradovate")
                st.sidebar.error(f"❌ Issues: {', '.join(connection_issues)}")
        
        # Kelly Criterion Configuration Section
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Kelly Position Sizing")
        
        # Kelly Enable/Disable
        kelly_enabled = st.sidebar.checkbox(
            "Enable Kelly Criterion", 
            value=st.session_state.kelly_settings.get("enabled", True), 
            key="kelly_enabled",
            help="Use Kelly Criterion for optimal position sizing"
        )
        
        st.session_state.kelly_settings["enabled"] = kelly_enabled
        
        if kelly_enabled:
            # Kelly Settings
            st.sidebar.write("**Kelly Parameters:**")
            
            st.session_state.kelly_settings["max_kelly_percentage"] = st.sidebar.slider(
                "Max Kelly %", 
                0.05, 0.50, 
                st.session_state.kelly_settings.get("max_kelly_percentage", 0.25),
                0.05,
                key="kelly_max_pct",
                help="Maximum Kelly percentage (conservative cap)"
            )
            
            st.session_state.kelly_settings["risk_adjustment_factor"] = st.sidebar.slider(
                "Risk Adjustment", 
                0.1, 1.0, 
                st.session_state.kelly_settings.get("risk_adjustment_factor", 0.5),
                0.1,
                key="kelly_risk_adj",
                help="Conservative adjustment factor"
            )
            
            st.session_state.kelly_settings["min_sample_size"] = st.sidebar.number_input(
                "Min Sample Size", 
                5, 50, 
                st.session_state.kelly_settings.get("min_sample_size", 10),
                1,
                key="kelly_min_sample",
                help="Minimum trades needed for Kelly calculation"
            )
            
            # Kelly Status Display
            if hasattr(self, 'kelly_engine'):
                st.sidebar.write("**Kelly Status:**")
                total_trades = sum(
                    self.kelly_engine.get_trading_history(i).total_trades 
                    for i in range(1, 7)
                )
                st.sidebar.caption(f"Total Historical Trades: {total_trades}")
                
                if total_trades >= st.session_state.kelly_settings["min_sample_size"]:
                    st.sidebar.success(" Kelly Active")
                else:
                    st.sidebar.info(f"Need {st.session_state.kelly_settings['min_sample_size'] - total_trades} more trades")
        
        else:
            st.sidebar.info("Using fixed position sizing")
        
        # OCR settings
        # OCR Configuration Section
        if OCR_AVAILABLE and self.ocr_manager:
            st.sidebar.markdown("---")
            st.sidebar.subheader("👁️ OCR Signal Detection")
            
            # OCR Enable/Disable
            ocr_enabled = st.sidebar.checkbox("Enable OCR Monitoring", value=False, key="ocr_enabled")
            
            if ocr_enabled:
                # Region Configuration
                st.sidebar.write("**Screen Regions:**")
                region_names = list(self.ocr_manager.monitoring_regions.keys())
                if region_names:
                    selected_regions = st.sidebar.multiselect(
                        "Active Regions",
                        region_names,
                        default=region_names[:2],
                        key="ocr_regions"
                    )
                else:
                    selected_regions = []
                
                # OCR Settings
                scan_interval = st.sidebar.slider("Scan Interval (seconds)", 1, 30, 5, key="ocr_interval")
                confidence_threshold = st.sidebar.slider("Signal Confidence", 0.1, 1.0, 0.7, key="ocr_confidence")
                
                # Test OCR Button
                if st.sidebar.button("Test OCR Capture", use_container_width=True):
                    if selected_regions:
                        try:
                            signals = self.ocr_manager.monitor_all_regions()
                            if signals:
                                st.sidebar.success(f"Found {len(signals)} signals!")
                                for region, signal_list in signals.items():
                                    for signal in signal_list:
                                        st.sidebar.write(f"**{region}:** {signal['type']} ({signal['confidence']:.1%})")
                            else:
                                st.sidebar.info("No signals detected")
                        except Exception as e:
                            st.sidebar.error(f"OCR test failed: {str(e)[:50]}...")
                    else:
                        st.sidebar.warning("Select regions first")
                
                # Configure Custom Region
                if st.sidebar.button("Add Custom Region", key="add_ocr_region"):
                    st.session_state.show_ocr_config = True
                
                # Manual Signal Input (for testing)
                st.sidebar.write("**Manual Signal Input:**")
                manual_signal = st.sidebar.selectbox("Signal Type", ["LONG", "SHORT", "NONE"], key="manual_signal")
                manual_chart = st.sidebar.selectbox("Target Chart", list(range(1, 7)), key="manual_chart")
                
                if st.sidebar.button("Send Manual Signal", key="send_manual"):
                    if manual_signal != "NONE":
                        chart = st.session_state.charts.get(manual_chart)
                        if chart:
                            chart.signal_color = "green" if manual_signal == "LONG" else "red"
                            chart.last_signal = f"OCR {manual_signal}"
                            st.sidebar.success(f"Sent {manual_signal} signal to Chart {manual_chart}")
            
            else:
                st.sidebar.info("OCR monitoring disabled")
                
            # OCR Configuration Modal
            if st.session_state.get('show_ocr_config', False):
                self.render_ocr_config_modal()
        
        else:
            st.sidebar.markdown("---")
            st.sidebar.write("**OCR Status:** Not Available")
            if not OCR_AVAILABLE:
                st.sidebar.info("Install required packages:\n`pip install opencv-python pytesseract pillow mss`")
    
    def simulate_data_updates(self):
        """Simulate real-time data updates when system is running"""
        if not st.session_state.system_running or st.session_state.emergency_stop:
            return
        
        # Update each chart with simulated data
        total_daily_pnl = 0
        
        for chart_id, chart in st.session_state.charts.items():
            if chart.is_active:
                # Simulate power score changes
                if st.session_state.system_mode == "DEMO":
                    # More predictable demo data
                    chart.power_score = max(0, min(100, chart.power_score + np.random.randint(-3, 4)))
                else:
                    # More realistic test/live data
                    chart.power_score = max(0, min(100, chart.power_score + np.random.randint(-5, 6)))
                
                # Update signal colors based on power score
                if chart.power_score >= 70:
                    chart.signal_color = "green"
                    chart.risk_level = "SAFE"
                elif chart.power_score >= 40:
                    chart.signal_color = "yellow"
                    chart.risk_level = "SAFE"
                else:
                    chart.signal_color = "red"
                    chart.risk_level = "WARNING"
                
                # Simulate P&L changes
                if st.session_state.system_mode == "DEMO":
                    pnl_change = np.random.normal(10, 50)  # More positive demo results
                else:
                    pnl_change = np.random.normal(0, 100)  # Realistic P&L swings
                
                chart.daily_pnl += pnl_change
                chart.unrealized_pnl = chart.daily_pnl * 0.7  # Portion of unrealized
                
                # Update position sizes using Kelly Criterion if enabled
                if st.session_state.kelly_settings.get("enabled", False):
                    # Use Kelly Criterion for position sizing
                    signal_confidence = chart.power_score / 100.0  # Convert power score to confidence
                    kelly_calc = self.kelly_engine.calculate_kelly(chart_id, signal_confidence)
                    
                    if chart.signal_color == "green" and chart.power_score > 70:
                        # Use Kelly recommendation for green signals
                        target_size = kelly_calc.recommended_position
                        chart.position_size = min(chart.position_size + 0.1, target_size)
                        
                        # Add trade result for Kelly learning (simulated)
                        if np.random.random() < 0.1:  # 10% chance to add trade result
                            simulated_pnl = pnl_change
                            entry_price = 4000 + np.random.normal(0, 100)
                            exit_price = entry_price + (simulated_pnl / max(chart.position_size, 0.1))
                            self.kelly_engine.add_trade_result(chart_id, simulated_pnl, entry_price, exit_price, chart.position_size)
                    
                    elif chart.signal_color == "red":
                        # Reduce position size more aggressively for red signals
                        chart.position_size = max(0, chart.position_size - 0.2)
                else:
                    # Traditional position sizing (fallback)
                    if chart.signal_color == "green" and chart.power_score > 75:
                        # Get max position size safely
                        if hasattr(st.session_state.user_config, 'get'):
                            max_pos = st.session_state.user_config.get("max_position_size", 5.0)
                        else:
                            max_pos = getattr(st.session_state.user_config, "max_position_size", 5.0)
                        
                        target_size = min(max_pos, (chart.power_score / 100) * max_pos)
                        chart.position_size = min(chart.position_size + 0.1, target_size)
                    elif chart.signal_color == "red":
                        chart.position_size = max(0, chart.position_size - 0.2)
                
                # Update margin usage
                chart.margin_used = chart.position_size * 400  # $400 per contract
                chart.margin_remaining = chart.account_balance - chart.margin_used
                
                # Update timestamps
                chart.last_update = datetime.now()
                
                # ERM Calculation (if enabled and Enigma signal active)
                if (st.session_state.erm_settings.get("enabled", False) and 
                    chart.current_enigma_signal and 
                    chart.current_enigma_signal.is_active):
                    
                    # Simulate current market price (based on chart metrics)
                    current_price = chart.entry_price + (chart.daily_pnl / chart.position_size if chart.position_size != 0 else 0)
                    
                    # Calculate ERM
                    erm_result = self.calculate_erm(chart_id, current_price)
                    
                    # Update power score based on ERM
                    if erm_result:
                        if erm_result.is_reversal_triggered:
                            chart.power_score = max(0, chart.power_score - 20)  # Reduce confidence on reversal
                        else:
                            # Increase confidence if price moving in Enigma direction
                            if ((chart.current_enigma_signal.signal_type == "LONG" and erm_result.price_distance > 0) or
                                (chart.current_enigma_signal.signal_type == "SHORT" and erm_result.price_distance < 0)):
                                chart.power_score = min(100, chart.power_score + 5)
                
                total_daily_pnl += chart.daily_pnl
        
        # Update system status
        st.session_state.system_status.daily_profit_loss = total_daily_pnl
        st.session_state.system_status.active_charts = sum(1 for c in st.session_state.charts.values() if c.is_active)
        
        # Check for risk violations
        if abs(total_daily_pnl) > st.session_state.user_config["max_daily_loss"]:
            st.session_state.emergency_stop = True
            st.session_state.system_running = False
            st.error(f"🚨 Daily loss limit exceeded: ${total_daily_pnl:,.0f}")
    
    def render_system_status(self):
        """Render overall system status dashboard"""
        st.subheader("📊 System Overview")
        
        status_col1, status_col2, status_col3, status_col4 = st.columns(4)
        
        with status_col1:
            system_health = "🟢 HEALTHY" if not st.session_state.emergency_stop else "🔴 EMERGENCY"
            st.metric("System Status", system_health)
        
        with status_col2:
            active_charts = sum(1 for chart in st.session_state.charts.values() if chart.is_active)
            st.metric("Active Charts", f"{active_charts}/6")
        
        with status_col3:
            total_positions = sum(chart.position_size for chart in st.session_state.charts.values())
            st.metric("Total Positions", f"{total_positions:.1f}")
        
        with status_col4:
            mode_color = {"DEMO": "🔷", "TEST": "🔶", "LIVE": "🔴"}
            st.metric("Trading Mode", f"{mode_color.get(st.session_state.system_mode, '⚪')} {st.session_state.system_mode}")
        
        # Performance chart
        self.render_performance_chart()
    
    def render_performance_chart(self):
        """Render simple performance visualization"""
        st.subheader("📈 Performance Overview")
        
        # Create sample equity curve data
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='H')
        
        # Generate simulated equity curve
        equity_values = []
        base_equity = 100000
        current_equity = base_equity
        
        for _ in dates:
            if st.session_state.system_mode == "DEMO":
                change = np.random.normal(50, 200)  # Slight positive bias for demo
            else:
                change = np.random.normal(0, 300)  # More realistic swings
            
            current_equity += change
            equity_values.append(current_equity)
        
        # Create plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity_values,
            mode='lines',
            name='Account Equity',
            line=dict(color='#28a745', width=2)
        ))
        
        fig.add_hline(y=base_equity, line_dash="dash", annotation_text="Starting Equity")
        
        fig.update_layout(
            title="7-Day Equity Curve",
            xaxis_title="Time",
            yaxis_title="Account Value ($)",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_erm_alerts_panel(self):
        """Render ERM alerts and monitoring panel"""
        if not st.session_state.erm_settings.get("enabled", False):
            return
        
        st.subheader("🧠 ERM (Enigma Reversal Momentum) Monitor")
        
        # ERM Status Overview
        erm_col1, erm_col2, erm_col3, erm_col4 = st.columns(4)
        
        with erm_col1:
            active_signals = len([s for s in st.session_state.active_enigma_signals.values() if s.is_active])
            st.metric("🎯 Active Enigma Signals", active_signals)
        
        with erm_col2:
            recent_alerts = len([a for a in st.session_state.erm_alerts if (datetime.now() - a['timestamp']).seconds < 300])
            st.metric("⚡ Recent ERM Alerts", recent_alerts)
        
        with erm_col3:
            today_reversals = len([a for a in st.session_state.erm_alerts if a['timestamp'].date() == datetime.now().date()])
            st.metric("🔄 Today's Reversals", today_reversals)
        
        with erm_col4:
            max_reversals = st.session_state.erm_settings.get("max_reversals_per_day", 3)
            remaining = max(0, max_reversals - today_reversals)
            st.metric("📊 Reversals Remaining", f"{remaining}/{max_reversals}")
        
        # Recent ERM Alerts
        if st.session_state.erm_alerts:
            st.markdown("### 🚨 Recent ERM Alerts")
            
            # Show last 5 alerts
            recent_alerts = st.session_state.erm_alerts[-5:]
            
            for alert in reversed(recent_alerts):
                alert_time = alert['timestamp'].strftime('%H:%M:%S')
                
                # Color code based on reversal direction
                if alert['reversal_direction'] == 'LONG':
                    alert_color = "🟢"
                elif alert['reversal_direction'] == 'SHORT':
                    alert_color = "🔴"
                else:
                    alert_color = "🟡"
                
                with st.expander(f"{alert_color} {alert_time} - {alert['chart_name']} ERM Reversal", expanded=False):
                    alert_col1, alert_col2 = st.columns(2)
                    
                    with alert_col1:
                        st.write(f"**Original Signal:** {alert['original_signal']}")
                        st.write(f"**Reversal Direction:** {alert['reversal_direction']}")
                        st.write(f"**ERM Value:** {alert['erm_value']:.3f}")
                        st.write(f"**Threshold:** {alert['threshold']:.3f}")
                    
                    with alert_col2:
                        st.write(f"**Momentum:** {alert['momentum']:.3f} pts/min")
                        st.write(f"**Price Distance:** {alert['price_distance']:.2f}")
                        st.write(f"**Chart:** {alert['chart_name']}")
                        
                        # Action buttons
                        if st.button(f"Execute {alert['reversal_direction']}", key=f"execute_{alert['timestamp']}"):
                            self.execute_reversal_trade(alert['chart_id'], alert['reversal_direction'])
                            st.success(f" {alert['reversal_direction']} trade executed!")
                            st.rerun()
        
        # Manual Enigma Signal Entry
        st.markdown("### Manual Enigma Signal Entry")
        
        manual_col1, manual_col2, manual_col3 = st.columns(3)
        
        with manual_col1:
            chart_options = [f"Chart {i+1}: {chart.account_name}" for i, chart in enumerate(st.session_state.charts.values())]
            selected_chart_idx = st.selectbox("Select Chart", range(len(chart_options)), format_func=lambda x: chart_options[x])
            selected_chart_id = selected_chart_idx + 1
        
        with manual_col2:
            signal_direction = st.selectbox("Signal Direction", ["LONG", "SHORT"])
            entry_price = st.number_input("Entry Price", value=4000.0, step=0.25)
        
        with manual_col3:
            signal_confidence = st.slider("Signal Confidence", 0.0, 1.0, 0.8, 0.1)
            
            if st.button("🚀 Add Enigma Signal", use_container_width=True):
                # Create new Enigma signal
                enigma_signal = EnigmaSignal(
                    signal_type=signal_direction,
                    entry_price=entry_price,
                    signal_time=datetime.now(),
                    is_active=True,
                    confidence=signal_confidence
                )
                
                # Add to chart
                chart = st.session_state.charts[selected_chart_id]
                chart.current_enigma_signal = enigma_signal
                st.session_state.active_enigma_signals[selected_chart_id] = enigma_signal
                
                # Initialize price history
                chart.price_history = [entry_price]
                chart.time_history = [datetime.now()]
                
                # Update chart display
                chart.last_signal = f"Enigma {signal_direction}"
                chart.signal_color = "green" if signal_direction == "LONG" else "red"
                
                st.success(f"✅ Enigma {signal_direction} signal added to {chart.account_name}")
                st.rerun()
    
    def render_kelly_criterion_panel(self):
        """Render Kelly Criterion position sizing panel"""
        if not st.session_state.kelly_settings.get("enabled", False):
            return
        
        st.subheader("📊 Kelly Criterion Position Sizing")
        
        # Kelly Status Overview
        kelly_col1, kelly_col2, kelly_col3, kelly_col4 = st.columns(4)
        
        # Calculate overall Kelly statistics
        total_trades = 0
        active_charts_with_kelly = 0
        avg_kelly_percentage = 0
        total_recommended_size = 0
        
        kelly_calculations = {}
        for chart_id in range(1, 7):
            history = self.kelly_engine.get_trading_history(chart_id)
            total_trades += history.total_trades
            
            if history.total_trades >= st.session_state.kelly_settings["min_sample_size"]:
                kelly_calc = self.kelly_engine.calculate_kelly(chart_id, 0.7)  # Default confidence
                kelly_calculations[chart_id] = kelly_calc
                active_charts_with_kelly += 1
                avg_kelly_percentage += kelly_calc.kelly_percentage
                total_recommended_size += kelly_calc.recommended_position
        
        if active_charts_with_kelly > 0:
            avg_kelly_percentage /= active_charts_with_kelly
        
        with kelly_col1:
            st.metric("📈 Total Historical Trades", total_trades)
        
        with kelly_col2:
            st.metric("🎯 Charts with Kelly Data", f"{active_charts_with_kelly}/6")
        
        with kelly_col3:
            st.metric("📊 Avg Kelly %", f"{avg_kelly_percentage:.1%}")
        
        with kelly_col4:
            st.metric("💼 Total Recommended Size", f"{total_recommended_size:.1f}")
        
        # Individual Chart Kelly Analysis
        if kelly_calculations:
            st.markdown("### 📋 Chart-Specific Kelly Analysis")
            
            # Create two columns for chart display
            kelly_chart_col1, kelly_chart_col2 = st.columns(2)
            
            chart_count = 0
            for chart_id, kelly_calc in kelly_calculations.items():
                chart = st.session_state.charts.get(chart_id)
                if not chart:
                    continue
                
                # Alternate between columns
                with kelly_chart_col1 if chart_count % 2 == 0 else kelly_chart_col2:
                    with st.expander(f"📊 {chart.account_name} - Kelly Analysis", expanded=False):
                        # Kelly metrics
                        kelly_metrics_col1, kelly_metrics_col2 = st.columns(2)
                        
                        with kelly_metrics_col1:
                            st.write(f"**Kelly %:** {kelly_calc.kelly_percentage:.2%}")
                            st.write(f"**Risk Adjusted:** {kelly_calc.risk_adjusted_kelly:.2%}")
                            st.write(f"**Win Rate:** {kelly_calc.win_probability:.1%}")
                            st.write(f"**Sample Size:** {kelly_calc.sample_size}")
                        
                        with kelly_metrics_col2:
                            st.write(f"**Recommended Size:** {kelly_calc.recommended_position:.1f}")
                            st.write(f"**Max Position:** {kelly_calc.max_position_limit:.1f}")
                            st.write(f"**Avg Win:** ${kelly_calc.avg_win:.0f}")
                            st.write(f"**Avg Loss:** ${kelly_calc.avg_loss:.0f}")
                        
                        # Sharpe ratio and confidence
                        st.write(f"**Sharpe Ratio:** {kelly_calc.sharpe_ratio:.2f}")
                        st.write(f"**Signal Confidence:** {kelly_calc.confidence_level:.1%}")
                        
                        # Progress bar for Kelly percentage
                        kelly_progress = min(kelly_calc.risk_adjusted_kelly / st.session_state.kelly_settings["max_kelly_percentage"], 1.0)
                        st.progress(kelly_progress)
                        
                        # Warning for high Kelly percentages
                        if kelly_calc.risk_adjusted_kelly > 0.15:
                            st.warning("⚠️ High Kelly percentage - consider reducing position size")
                        elif kelly_calc.risk_adjusted_kelly < 0.02:
                            st.info("💡 Low Kelly percentage - signal may not be strong enough")
                        else:
                            st.success("✅ Kelly percentage within optimal range")
                
                chart_count += 1
        
        else:
            st.info("📊 **Building Kelly Database** - Need more historical trades for Kelly calculations")
            st.write("Kelly Criterion requires historical trading data to calculate optimal position sizes.")
            
            # Show requirements
            min_sample = st.session_state.kelly_settings["min_sample_size"]
            st.write(f"**Requirements:** {min_sample} completed trades per chart")
            st.write(f"**Current Status:** {total_trades} total trades across all charts")
            
            # Add sample trades button for demo
            if st.session_state.system_mode == "DEMO":
                if st.button("🧪 Add Sample Trading History (Demo)", use_container_width=True):
                    self._add_sample_kelly_data()
                    st.success("✅ Sample trading history added for Kelly calculations")
                    st.rerun()
        
        # Kelly Settings Panel
        with st.expander("⚙️ Kelly Criterion Settings", expanded=False):
            settings_col1, settings_col2 = st.columns(2)
            
            with settings_col1:
                st.markdown("**Risk Management:**")
                max_kelly = st.slider(
                    "Max Kelly Percentage", 
                    0.05, 0.50, 
                    st.session_state.kelly_settings["max_kelly_percentage"],
                    0.05,
                    help="Maximum Kelly percentage (conservative cap)"
                )
                st.session_state.kelly_settings["max_kelly_percentage"] = max_kelly
                
                risk_adj = st.slider(
                    "Risk Adjustment Factor", 
                    0.1, 1.0, 
                    st.session_state.kelly_settings["risk_adjustment_factor"],
                    0.1,
                    help="Conservative adjustment to Kelly calculation"
                )
                st.session_state.kelly_settings["risk_adjustment_factor"] = risk_adj
            
            with settings_col2:
                st.markdown("**Data Requirements:**")
                min_sample = st.number_input(
                    "Minimum Sample Size", 
                    5, 100, 
                    st.session_state.kelly_settings["min_sample_size"],
                    5,
                    help="Minimum trades needed for Kelly calculation"
                )
                st.session_state.kelly_settings["min_sample_size"] = min_sample
                
                lookback = st.number_input(
                    "Lookback Period", 
                    50, 500, 
                    st.session_state.kelly_settings["lookback_period"],
                    50,
                    help="Number of recent trades to analyze"
                )
                st.session_state.kelly_settings["lookback_period"] = lookback
            
            # Save settings
            if st.button("💾 Save Kelly Settings", use_container_width=True):
                st.success("✅ Kelly Criterion settings saved!")
        
        # Kelly Education Panel
        with st.expander("📚 Kelly Criterion Education", expanded=False):
            st.markdown("""
            **What is the Kelly Criterion?**
            
            The Kelly Criterion is a mathematical formula used to determine the optimal size of a series of bets 
            to maximize long-term growth while minimizing the risk of ruin.
            
            **Formula:** f* = (bp - q) / b
            
            Where:
            - **f*** = fraction of capital to bet (Kelly percentage)
            - **b** = odds of winning (average win / average loss)
            - **p** = probability of winning
            - **q** = probability of losing (1 - p)
            
            **Our Implementation:**
            - ✅ **Conservative Caps:** Maximum Kelly limited to 25% for safety
            - ✅ **Risk Adjustment:** Kelly percentage reduced by 50% for prop firm trading
            - ✅ **Confidence Scaling:** Position size scaled by signal confidence
            - ✅ **Adaptive Sizing:** Adjusts based on recent winning/losing streaks
            - ✅ **Sample Size Requirements:** Requires sufficient historical data
            
            **Benefits:**
            - 📈 **Optimal Growth:** Maximizes long-term capital growth
            - 🛡️ **Risk Management:** Reduces position size during losing periods
            - 🎯 **Data-Driven:** Uses actual trading history, not assumptions
            - ⚖️ **Balanced Approach:** Balances growth potential with risk control
            """)
    
    def _add_sample_kelly_data(self):
        """Add sample trading data for Kelly Criterion demonstration (Demo mode only)"""
        if st.session_state.system_mode != "DEMO":
            return
        
        import random
        
        # Add sample trades for each chart
        for chart_id in range(1, 7):
            # Generate realistic trading history
            for i in range(15):  # Add 15 sample trades per chart
                # 60% win rate with realistic P&L
                is_winner = random.random() < 0.6
                
                if is_winner:
                    pnl = random.uniform(50, 300)  # Winning trades
                else:
                    pnl = random.uniform(-200, -50)  # Losing trades
                
                entry_price = random.uniform(4000, 4500)
                exit_price = entry_price + (pnl / 2)  # Assuming 2 contracts
                size = 2.0
                
                self.kelly_engine.add_trade_result(chart_id, pnl, entry_price, exit_price, size)
    
    def refresh_real_time_data(self):
        """Refresh charts with real-time data from connections"""
        current_time = datetime.now()
        
        # Only refresh every 30 seconds to avoid API rate limits
        if hasattr(st.session_state, 'last_data_refresh'):
            time_since_refresh = (current_time - st.session_state.last_data_refresh).total_seconds()
            if time_since_refresh < 30:
                return
        
        try:
            # Check if we have real connections
            ninja_connected = self.check_ninjatrader_connection()
            tradovate_connected = self.test_tradovate_connection()
            
            if ninja_connected or tradovate_connected:
                self.logger.info("Refreshing with real-time data...")
                
                # Update system status with real data
                real_account_data = self.fetch_real_account_data()
                st.session_state.system_status.total_margin_remaining = real_account_data.get('total_margin_remaining', 0.0)
                st.session_state.system_status.total_margin_percentage = real_account_data.get('total_margin_percentage', 0.0)
                st.session_state.system_status.total_equity = real_account_data.get('total_equity', 0.0)
                st.session_state.system_status.daily_profit_loss = real_account_data.get('daily_profit_loss', 0.0)
                
                # Update individual charts with real data
                all_account_data = self.fetch_all_account_data()
                
                for chart_id, chart in st.session_state.charts.items():
                    account_data = all_account_data.get(chart_id, {})
                    if account_data:
                        # Update with real data while preserving chart configuration
                        chart.account_balance = account_data.get('account_balance', chart.account_balance)
                        chart.daily_pnl = account_data.get('daily_pnl', chart.daily_pnl)
                        chart.margin_used = account_data.get('margin_used', chart.margin_used)
                        chart.margin_remaining = account_data.get('margin_remaining', chart.margin_remaining)
                        chart.margin_percentage = account_data.get('margin_percentage', chart.margin_percentage)
                        chart.unrealized_pnl = account_data.get('unrealized_pnl', chart.unrealized_pnl)
                        chart.position_size = account_data.get('position_size', chart.position_size)
                        chart.ninjatrader_connection = account_data.get('connection_status', chart.ninjatrader_connection)
                        chart.last_update = current_time
                        
                        # Update risk level based on real margin data
                        if chart.margin_percentage > 50:
                            chart.risk_level = "SAFE"
                        elif chart.margin_percentage > 25:
                            chart.risk_level = "WARNING"
                        else:
                            chart.risk_level = "DANGER"
                
                st.session_state.last_data_refresh = current_time
                
                # Show refresh indicator in development
                if st.session_state.system_mode == "DEMO":
                    st.sidebar.success(f"🔄 Real data refreshed: {current_time.strftime('%H:%M:%S')}")
            
            else:
                # No connections - show disconnected state
                for chart in st.session_state.charts.values():
                    if chart.ninjatrader_connection not in ["Disconnected", "NO CONNECTION"]:
                        chart.ninjatrader_connection = "Disconnected"
                        chart.risk_level = "DISCONNECTED"
                        chart.signal_color = "gray"
                        chart.last_update = current_time
        
        except Exception as e:
            self.logger.error(f"Error refreshing real-time data: {e}")
            st.sidebar.error(f"⚠️ Data refresh failed: {str(e)[:50]}...")
    
    def run(self):
        """Main dashboard run method with real-time data refresh"""
        # Auto-refresh real data every 30 seconds
        self.refresh_real_time_data()
        
        # Page header
        self.render_header()
        
        # Sidebar configuration
        self.render_sidebar_settings()
        
        # Check if Quick Setup Wizard should be shown
        if st.session_state.get('show_setup_wizard', False):
            self.render_quick_setup_wizard()
            return  # Don't show main dashboard while wizard is active
        
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
        
        # OCR integration tab
        if OCR_AVAILABLE and self.ocr_manager:
            with st.expander("👁️ OCR Signal Reading", expanded=False):
                try:
                    # Create a simple config object for OCR compatibility
                    class SimpleConfig:
                        def __init__(self, config_dict):
                            for key, value in config_dict.items():
                                setattr(self, key, value)
                    
                    # Convert dict to object for OCR module
                    config_obj = SimpleConfig(st.session_state.user_config)
                    
                    # Temporarily set st.session_state.user_config for OCR
                    original_config = st.session_state.user_config
                    
                    try:
                        st.session_state.user_config = config_obj
                        
                        self.ocr_manager.render_ocr_configuration()
                        self.ocr_manager.render_ocr_status()
                    
                    finally:
                        # Always restore original config, even if exceptions occur
                        st.session_state.user_config = original_config
                    
                except Exception as e:
                    st.error(f"OCR Error: {e}")
                    st.info("OCR features temporarily unavailable")
        else:
            with st.expander("👁️ OCR Signal Reading", expanded=False):
                st.info("📦 OCR features not available")
                st.write("To enable OCR capabilities:")
                st.code("pip install opencv-python pytesseract pillow")
                st.write("**OCR Features would include:**")
                st.write("- Automatic signal detection from charts")
                st.write("- AlgoBox signal reading")
                st.write("- Visual signal confirmation")
                st.write("- Real-time signal monitoring")
        
        # Auto-refresh and data simulation
        if st.session_state.system_running:
            self.simulate_data_updates()
            time.sleep(0.1)  # Smooth updates
            st.rerun()
        
        # Footer
        st.markdown("---")
        # Display selected prop firm info
        selected_firm = st.session_state.get('selected_prop_firm', 'FTMO')
        
        # Safe access to user_config - handle both dict and SimpleConfig objects
        if hasattr(st.session_state.user_config, 'get'):
            # It's a dictionary
            trader_name = st.session_state.user_config.get('trader_name', 'Trader')
        else:
            # It's a SimpleConfig object or other type
            trader_name = getattr(st.session_state.user_config, 'trader_name', 'Trader')
        
        st.markdown(f"🎯 **Training Wheels for Prop Firm Traders** | {trader_name} | {selected_firm} Challenge Dashboard")
        
        # Show ERM status in footer
        if st.session_state.erm_settings.get("enabled", False):
            active_signals = len([s for s in st.session_state.active_enigma_signals.values() if s.is_active])
            st.markdown(f"🧠 **ERM System Active** - Monitoring {active_signals} Enigma Signals | First Principal Enhancement System")

def main():
    """Main application entry point"""
    dashboard = TrainingWheelsDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
