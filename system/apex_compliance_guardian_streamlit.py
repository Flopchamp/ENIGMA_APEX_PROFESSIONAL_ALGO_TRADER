"""
🛡️ APEX COMPLIANCE GUARDIAN - STREAMLIT EDITION WITH ALGOBOX ALGOBARS
Modern web-based interface for prop trader compliance monitoring with AlgoBox candle technology
Training Wheels for Apex Trader Funding Rules + AlgoBar Chart Analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import json
import time
import random
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import sqlite3

# Page configuration
st.set_page_config(
    page_title="🛡️ Apex Compliance Guardian + AlgoBars",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class ApexRules:
    """Apex Trader Funding rule configurations - OFFICIAL APEX 3.0 RULES"""
    
    # EVALUATION PHASE RULES (Official Apex 3.0)
    evaluation_target: float = 8.0  # 8% profit target
    evaluation_max_daily_loss: float = 5.0  # 5% max daily loss
    evaluation_trailing_threshold: float = 5.0  # 5% trailing threshold (from high water mark)
    evaluation_minimum_days: int = 5  # Minimum 5 trading days
    evaluation_max_days: int = 30  # Maximum 30 calendar days
    
    # PERFORMANCE ACCOUNT (PA) RULES (Official Apex 3.0)
    pa_target: float = 5.0  # 5% profit target
    pa_max_daily_loss: float = 5.0  # 5% max daily loss
    pa_trailing_threshold: float = 5.0  # 5% trailing threshold
    pa_minimum_days: int = 5  # Minimum 5 trading days
    
    # LIVE ACCOUNT RULES (Official Apex 3.0)
    live_max_daily_loss: float = 5.0  # 5% max daily loss
    live_trailing_threshold: float = 5.0  # 5% trailing threshold
    live_scaling_enabled: bool = True  # Live account scaling available
    
    # CONSISTENCY RULE (Official Apex 3.0 - CRITICAL)
    consistency_rule: float = 30.0  # 30% max single day profit of total profit
    consistency_applies_to: str = "all_phases"  # Applies to Evaluation, PA, and Live
    
    # NEWS/HIGH IMPACT EVENTS
    news_restricted_trading: bool = True  # No trading during high impact news
    news_buffer_minutes: int = 15  # 15 min before/after news events
    
    # WEEKEND/HOLIDAY RULES
    weekend_holding_allowed: bool = False  # No weekend position holding
    
    # MAXIMUM POSITION SIZES
    max_contracts_per_trade: int = 10  # Maximum contracts per single trade
    max_total_contracts: int = 20  # Maximum total contracts across all positions
    
    # Platform Settings
    platform: str = "Tradovate"  # Default platform
    safety_ratio: float = 80.0  # 80% safety margin (configurable 5-90%)
    
    # OFFICIAL APEX VIOLATION CONSEQUENCES
    violation_lockout_hours: int = 24  # 24-hour lockout after violation
    max_violations_allowed: int = 0  # ZERO tolerance - any violation = account breach

@dataclass
class TradeData:
    """Current trade and account data"""
    account_balance: float = 25000.0
    daily_pnl: float = 0.0
    total_pnl: float = 0.0
    open_positions: int = 0
    max_daily_profit: float = 0.0
    drawdown_from_high: float = 0.0
    is_locked_out: bool = False
    lockout_until: Optional[datetime] = None
    last_update: datetime = datetime.now()

@dataclass
class AlgoBarSettings:
    """AlgoBox AlgoBar configuration settings"""
    algo_bar_size: int = 4  # Price movement threshold (e.g., 4 ticks)
    symbol: str = "ES"  # Trading symbol
    chart_type: str = "Tide"  # Tide, Wave, or Ripple
    show_volume: bool = True
    show_delta: bool = True
    color_scheme: str = "Bull/Bear"  # Bull/Bear, Green/Red, Custom
    body_style: str = "Filled"  # Filled, Outline, Hollow
    wick_style: str = "Standard"  # Standard, Thin, Thick
    show_imbalance_zones: bool = True
    no_repainting: bool = True  # WYSIWYG principle

class AlgoBarEngine:
    """AlgoBox AlgoBar calculation engine - Price-based bars without time distortion"""
    
    def __init__(self, settings: AlgoBarSettings):
        self.settings = settings
        self.current_bar = None
        self.completed_bars = []
        self.price_threshold = settings.algo_bar_size
        self.tick_data = []
        
    def add_tick(self, price: float, volume: int, delta: int = 0, timestamp: datetime = None):
        """Add new tick data and process AlgoBar formation"""
        if timestamp is None:
            timestamp = datetime.now()
            
        tick = {
            'price': price,
            'volume': volume,
            'delta': delta,
            'timestamp': timestamp
        }
        
        self.tick_data.append(tick)
        self.process_algo_bar(tick)
        
    def process_algo_bar(self, tick: Dict):
        """Process tick data to form AlgoBars based on price movement thresholds"""
        price = tick['price']
        
        if self.current_bar is None:
            # Start new bar
            self.current_bar = {
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': tick['volume'],
                'delta': tick['delta'],
                'start_time': tick['timestamp'],
                'end_time': tick['timestamp'],
                'tick_count': 1,
                'price_range': 0
            }
            return
            
        # Update current bar
        self.current_bar['high'] = max(self.current_bar['high'], price)
        self.current_bar['low'] = min(self.current_bar['low'], price)
        self.current_bar['close'] = price
        self.current_bar['volume'] += tick['volume']
        self.current_bar['delta'] += tick['delta']
        self.current_bar['end_time'] = tick['timestamp']
        self.current_bar['tick_count'] += 1
        
        # Calculate price range from open
        price_range = abs(price - self.current_bar['open'])
        self.current_bar['price_range'] = price_range
        
        # Check if bar should complete based on price movement threshold
        if price_range >= self.price_threshold:
            self.complete_current_bar()
            
    def complete_current_bar(self):
        """Complete current AlgoBar and start new one - No repainting principle"""
        if self.current_bar is None:
            return
            
        # Finalize bar (WYSIWYG - never changes once completed)
        completed_bar = self.current_bar.copy()
        
        # Determine bar color (bullish/bearish) - never changes
        completed_bar['is_bullish'] = completed_bar['close'] > completed_bar['open']
        completed_bar['bar_type'] = 'bullish' if completed_bar['is_bullish'] else 'bearish'
        
        # Add market structure analysis
        completed_bar['market_speed'] = self.calculate_market_speed(completed_bar)
        completed_bar['volatility'] = self.calculate_volatility(completed_bar)
        
        self.completed_bars.append(completed_bar)
        
        # Start new bar with current price as open
        self.current_bar = {
            'open': completed_bar['close'],
            'high': completed_bar['close'],
            'low': completed_bar['close'],
            'close': completed_bar['close'],
            'volume': 0,
            'delta': 0,
            'start_time': completed_bar['end_time'],
            'end_time': completed_bar['end_time'],
            'tick_count': 0,
            'price_range': 0
        }
        
    def calculate_market_speed(self, bar: Dict) -> str:
        """Calculate market speed based on AlgoBar formation rate"""
        time_duration = (bar['end_time'] - bar['start_time']).total_seconds()
        if time_duration == 0:
            return "Instant"
        
        ticks_per_second = bar['tick_count'] / time_duration
        
        if ticks_per_second > 10:
            return "Very Fast"
        elif ticks_per_second > 5:
            return "Fast"
        elif ticks_per_second > 2:
            return "Moderate"
        else:
            return "Slow"
            
    def calculate_volatility(self, bar: Dict) -> float:
        """Calculate volatility measure for the bar"""
        if bar['open'] == 0:
            return 0
        return abs(bar['high'] - bar['low']) / bar['open'] * 100
        
    def get_recent_bars(self, count: int = 50) -> List[Dict]:
        """Get recent completed AlgoBars"""
        return self.completed_bars[-count:] if self.completed_bars else []

class ApexComplianceGuardian:
    """Main compliance guardian with AlgoBar integration"""
    
    def __init__(self):
        self.rules = ApexRules()
        self.trade_data = TradeData()
        self.algo_settings = AlgoBarSettings()
        self.algo_engine = AlgoBarEngine(self.algo_settings)
        self.violations = []
        self.alerts = []
        self.monitoring_active = False
        
        # Initialize session state
        if 'guardian' not in st.session_state:
            st.session_state.guardian = self
            st.session_state.monitoring_active = False
            st.session_state.alerts = []
            st.session_state.violations = []
            st.session_state.algo_bars = []
            
        # Setup logging
        logging.basicConfig(
            filename='apex_compliance.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.load_settings()
        
    def add_alert(self, message: str, level: str = "INFO"):
        """Add alert to the system"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert = {
            'timestamp': timestamp,
            'message': message,
            'level': level,
            'full_time': datetime.now()
        }
        
        if 'alerts' not in st.session_state:
            st.session_state.alerts = []
            
        st.session_state.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(st.session_state.alerts) > 100:
            st.session_state.alerts = st.session_state.alerts[-100:]
            
        # Log to file
        logging.info(f"{level}: {message}")
        
    def simulate_market_data(self):
        """Simulate realistic market data for AlgoBar formation"""
        # Generate realistic price movement
        base_price = 4580.25  # ES futures example
        
        # Market volatility simulation with trends
        volatility = random.uniform(0.5, 2.0)
        
        # Add trend bias
        if not hasattr(self, 'trend_direction'):
            self.trend_direction = random.choice([1, -1])
            self.trend_strength = random.uniform(0.1, 0.3)
            self.trend_duration = random.randint(50, 200)
            self.trend_counter = 0
            
        # Change trend occasionally
        self.trend_counter += 1
        if self.trend_counter >= self.trend_duration:
            self.trend_direction = random.choice([1, -1])
            self.trend_strength = random.uniform(0.1, 0.3)
            self.trend_duration = random.randint(50, 200)
            self.trend_counter = 0
        
        # Calculate price change with trend bias
        trend_component = self.trend_direction * self.trend_strength
        noise_component = random.gauss(0, volatility)
        price_change = trend_component + noise_component
        
        # Current price with trend
        if not hasattr(self, 'current_price'):
            self.current_price = base_price
            
        self.current_price += price_change
        
        # Ensure realistic price bounds
        self.current_price = max(4500, min(4700, self.current_price))
        
        # Volume simulation (heavier during market hours)
        current_time = datetime.now()
        market_open = current_time.replace(hour=9, minute=30)
        market_close = current_time.replace(hour=16, minute=0)
        
        is_market_hours = market_open <= current_time <= market_close
        
        # More realistic volume patterns
        if is_market_hours:
            # Higher volume during first and last hour
            hour = current_time.hour
            if hour in [9, 15]:  # Opening and closing hours
                volume = random.randint(200, 800)
            elif hour in [10, 14]:  # Active hours
                volume = random.randint(100, 400)
            else:  # Mid-day
                volume = random.randint(50, 200)
        else:
            volume = random.randint(5, 50)  # Overnight/after hours
        
        # Delta (order flow) simulation with bias
        if price_change > 0:
            # Bullish bias in delta
            delta = random.randint(int(volume * 0.3), volume)
        else:
            # Bearish bias in delta
            delta = random.randint(-volume, int(-volume * 0.3))
        
        # Add tick to AlgoBar engine
        self.algo_engine.add_tick(
            price=self.current_price,
            volume=volume,
            delta=delta,
            timestamp=current_time
        )
        
        # Update trade data simulation
        self.update_trade_data()
        
    def update_trade_data(self):
        """Update trade data with realistic simulation"""
        # Simulate P&L changes based on position and market movement
        if hasattr(self, 'last_price') and hasattr(self, 'current_price'):
            price_diff = self.current_price - self.last_price
            if self.trade_data.open_positions > 0:
                # ES futures: $50 per point per contract
                pnl_change = price_diff * self.trade_data.open_positions * 50
                self.trade_data.daily_pnl += pnl_change
                
        if hasattr(self, 'current_price'):
            self.last_price = self.current_price
        
        # Update max daily profit for drawdown calculation
        if self.trade_data.daily_pnl > self.trade_data.max_daily_profit:
            self.trade_data.max_daily_profit = self.trade_data.daily_pnl
            
        # Calculate trailing drawdown from high water mark
        if self.trade_data.max_daily_profit > 0:
            current_drawdown = (self.trade_data.max_daily_profit - self.trade_data.daily_pnl) / self.trade_data.account_balance * 100
            self.trade_data.drawdown_from_high = max(0, current_drawdown)
        
        # Update total P&L (simulate account growth over time)
        if not hasattr(self, 'total_pnl_initialized'):
            self.trade_data.total_pnl = 1500.0  # Starting with some historical profit
            self.total_pnl_initialized = True
        
        # Add daily P&L to total (simplified)
        if self.trade_data.daily_pnl != 0:
            self.trade_data.total_pnl = max(0, self.trade_data.total_pnl + (self.trade_data.daily_pnl * 0.01))
            
        # Simulate position changes based on market activity
        if random.random() < 0.03:  # 3% chance of position change
            old_positions = self.trade_data.open_positions
            
            # Simulate realistic position changes
            if old_positions == 0:
                # Enter new position
                self.trade_data.open_positions = random.randint(1, min(5, self.rules.max_total_contracts))
                self.add_alert(f"📈 NEW POSITION: {self.trade_data.open_positions} contracts @ ${self.current_price:.2f}", "INFO")
            elif random.random() < 0.3:
                # Close all positions
                self.trade_data.open_positions = 0
                pnl_on_close = (self.current_price - getattr(self, 'entry_price', self.current_price)) * old_positions * 50
                self.add_alert(f"🔒 POSITION CLOSED: {old_positions} contracts, P&L: ${pnl_on_close:.2f}", "SUCCESS" if pnl_on_close > 0 else "WARNING")
            else:
                # Adjust position size
                self.trade_data.open_positions = max(0, min(self.rules.max_total_contracts, 
                                                           old_positions + random.randint(-2, 2)))
                
        # Store entry price for P&L calculation
        if self.trade_data.open_positions > 0 and not hasattr(self, 'entry_price'):
            self.entry_price = self.current_price
        elif self.trade_data.open_positions == 0:
            if hasattr(self, 'entry_price'):
                delattr(self, 'entry_price')
            
        self.trade_data.last_update = datetime.now()
        
    def check_compliance(self):
        """Check all Apex compliance rules"""
        if not st.session_state.monitoring_active:
            return
            
        safety_ratio = self.rules.safety_ratio / 100.0
        account_balance = self.trade_data.account_balance
        
        # Check if already locked out
        if self.trade_data.is_locked_out:
            current_time = datetime.now()
            if self.trade_data.lockout_until and current_time < self.trade_data.lockout_until:
                return  # Still locked out
            else:
                # Reset lockout
                self.trade_data.is_locked_out = False
                self.add_alert("🔓 Trading lockout expired - monitoring resumed", "INFO")
        
        # 1. DAILY LOSS LIMIT (5% - APEX OFFICIAL RULE)
        daily_loss_limit_percentage = self.rules.evaluation_max_daily_loss
        daily_loss_limit_amount = account_balance * daily_loss_limit_percentage / 100
        safety_loss_limit = daily_loss_limit_amount * safety_ratio
        
        if self.trade_data.daily_pnl <= -safety_loss_limit:
            self.trigger_violation(
                "DAILY LOSS LIMIT", 
                f"Daily loss ${abs(self.trade_data.daily_pnl):,.2f} exceeded {safety_ratio*100:.0f}% of ${daily_loss_limit_amount:,.2f} limit"
            )
            
        # 2. TRAILING DRAWDOWN (5% FROM HIGH WATER MARK)
        trailing_threshold_percentage = self.rules.evaluation_trailing_threshold
        safety_trailing_limit = trailing_threshold_percentage * safety_ratio
        
        if self.trade_data.drawdown_from_high >= safety_trailing_limit:
            self.trigger_violation(
                "TRAILING DRAWDOWN", 
                f"Drawdown {self.trade_data.drawdown_from_high:.2f}% exceeded {safety_ratio*100:.0f}% of {trailing_threshold_percentage}% limit"
            )
            
        # 3. CONSISTENCY RULE (30% - APEX OFFICIAL RULE)
        if account_balance > 0 and self.trade_data.total_pnl > 0:
            daily_profit_percentage = (self.trade_data.daily_pnl / self.trade_data.total_pnl) * 100
            consistency_limit = self.rules.consistency_rule
            safety_consistency_limit = consistency_limit * safety_ratio
            
            if daily_profit_percentage > safety_consistency_limit:
                self.trigger_violation(
                    "CONSISTENCY RULE", 
                    f"Daily profit {daily_profit_percentage:.1f}% of total profit exceeded {safety_ratio*100:.0f}% of {consistency_limit}% limit"
                )
        
        # 4. POSITION SIZE LIMITS (APEX OFFICIAL RULE)
        if self.trade_data.open_positions > self.rules.max_total_contracts:
            self.trigger_violation(
                "POSITION SIZE LIMIT", 
                f"Open positions {self.trade_data.open_positions} exceeded maximum {self.rules.max_total_contracts} contracts"
            )
        
        # 5. WEEKEND HOLDING RESTRICTIONS (APEX OFFICIAL RULE)
        current_time = datetime.now()
        if current_time.weekday() >= 5 and self.trade_data.open_positions > 0:  # Saturday/Sunday
            if not self.rules.weekend_holding_allowed:
                self.trigger_violation(
                    "WEEKEND HOLDING", 
                    "Positions must be closed before weekend - Apex rule violation"
                )
        
        # 6. NEWS EVENT RESTRICTIONS (APEX OFFICIAL RULE)
        if self.rules.news_restricted_trading:
            # Simulate news events for demo
            if random.random() < 0.001:  # 0.1% chance per check
                self.add_alert("📰 HIGH IMPACT NEWS DETECTED - Trading restricted for 15 minutes", "WARNING")
                
        # 7. EARLY WARNING SYSTEM
        self.check_early_warnings(safety_ratio)
                
    def trigger_violation(self, rule_type: str, message: str):
        """Trigger rule violation response"""
        violation_record = {
            'timestamp': datetime.now().isoformat(),
            'rule_type': rule_type,
            'message': message,
            'account_balance': self.trade_data.account_balance,
            'daily_pnl': self.trade_data.daily_pnl,
            'safety_ratio': self.rules.safety_ratio
        }
        
        if 'violations' not in st.session_state:
            st.session_state.violations = []
            
        st.session_state.violations.append(violation_record)
        
        self.add_alert(f"🚨 APEX RULE VIOLATION: {rule_type}", "ERROR")
        self.add_alert(f"💥 {message}", "ERROR")
        self.add_alert(f"⚡ EXECUTING EMERGENCY PROTOCOL", "ERROR")
        
        # Emergency actions
        self.emergency_stop_all()
        self.force_lockout()
        
        # Stop monitoring
        st.session_state.monitoring_active = False
        
        # Show critical alert
        st.error(f"🚨 CRITICAL: {rule_type} VIOLATION DETECTED!")
        st.error(f"Details: {message}")
        st.error("All positions closed and account locked!")
        
    def emergency_stop_all(self):
        """Emergency stop all trades"""
        self.add_alert("🛑 EMERGENCY STOP: Closing all positions immediately", "ERROR")
        self.trade_data.open_positions = 0
        self.add_alert("✅ All positions closed successfully", "SUCCESS")
        
    def force_lockout(self):
        """Force trading lockout"""
        self.trade_data.is_locked_out = True
        
        # Calculate next reset time
        current_time = datetime.now()
        lockout_hours = self.rules.violation_lockout_hours
        self.trade_data.lockout_until = current_time + timedelta(hours=lockout_hours)
        
        self.add_alert(f"🔒 TRADING LOCKED OUT for {lockout_hours} hours", "ERROR")
        self.add_alert(f"⏰ Lockout until: {self.trade_data.lockout_until.strftime('%Y-%m-%d %H:%M')} EST", "ERROR")
        
    def check_early_warnings(self, safety_ratio):
        """Early warning system to prevent violations"""
        account_balance = self.trade_data.account_balance
        
        # Warning thresholds (75% of safety limit)
        warning_threshold = 0.75
        
        # Daily loss warning
        daily_loss_limit = account_balance * self.rules.evaluation_max_daily_loss / 100 * safety_ratio
        if self.trade_data.daily_pnl <= -(daily_loss_limit * warning_threshold):
            self.add_alert(f"⚠️ APPROACHING DAILY LOSS LIMIT: {abs(self.trade_data.daily_pnl):,.2f} / {daily_loss_limit:,.2f}", "WARNING")
        
        # Drawdown warning
        dd_limit = self.rules.evaluation_trailing_threshold * safety_ratio
        if self.trade_data.drawdown_from_high >= (dd_limit * warning_threshold):
            self.add_alert(f"⚠️ APPROACHING DRAWDOWN LIMIT: {self.trade_data.drawdown_from_high:.2f}% / {dd_limit:.2f}%", "WARNING")
        
        # Position size warning
        if self.trade_data.open_positions >= (self.rules.max_total_contracts * warning_threshold):
            self.add_alert(f"⚠️ HIGH POSITION COUNT: {self.trade_data.open_positions} / {self.rules.max_total_contracts}", "WARNING")
        
    def save_settings(self):
        """Save current settings"""
        settings = {
            'safety_ratio': self.rules.safety_ratio,
            'platform': self.rules.platform,
            'algo_bar_size': self.algo_settings.algo_bar_size,
            'chart_type': self.algo_settings.chart_type,
            'rules': asdict(self.rules),
            'algo_settings': asdict(self.algo_settings)
        }
        
        try:
            with open('apex_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            self.add_alert("💾 Settings saved successfully", "SUCCESS")
        except Exception as e:
            self.add_alert(f"❌ Failed to save settings: {str(e)}", "ERROR")
            
    def load_settings(self):
        """Load saved settings"""
        try:
            with open('apex_settings.json', 'r') as f:
                settings = json.load(f)
            self.rules.safety_ratio = settings.get('safety_ratio', 80.0)
            self.rules.platform = settings.get('platform', 'Tradovate')
            self.algo_settings.algo_bar_size = settings.get('algo_bar_size', 4)
            self.algo_settings.chart_type = settings.get('chart_type', 'Tide')
        except FileNotFoundError:
            pass

def create_algobar_chart(guardian: ApexComplianceGuardian, chart_type: str = "Tide"):
    """Create AlgoBox-style AlgoBar chart"""
    bars = guardian.algo_engine.get_recent_bars(100)
    
    if not bars:
        st.info("📊 Start monitoring to see AlgoBar charts")
        return None
        
    # Convert to DataFrame
    df = pd.DataFrame(bars)
    df['datetime'] = pd.to_datetime(df['start_time'])
    
    # Create candlestick chart
    fig = go.Figure()
    
    # AlgoBar candlesticks - No repainting, WYSIWYG principle
    colors = ['green' if bar['is_bullish'] else 'red' for bar in bars]
    
    fig.add_trace(go.Candlestick(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name=f"AlgoBars ({chart_type})",
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444',
        increasing_fillcolor='rgba(0, 255, 136, 0.3)',
        decreasing_fillcolor='rgba(255, 68, 68, 0.3)'
    ))
    
    # Add volume bars if enabled
    if guardian.algo_settings.show_volume:
        fig.add_trace(go.Bar(
            x=df['datetime'],
            y=df['volume'],
            name='Volume',
            marker_color='rgba(128, 128, 128, 0.5)',
            yaxis='y2',
            opacity=0.6
        ))
    
    # Add delta (order flow) if enabled
    if guardian.algo_settings.show_delta:
        delta_colors = ['green' if d > 0 else 'red' for d in df['delta']]
        fig.add_trace(go.Bar(
            x=df['datetime'],
            y=df['delta'],
            name='Cumulative Delta',
            marker_color=delta_colors,
            yaxis='y3',
            opacity=0.7
        ))
    
    # Add market structure lines
    if len(bars) > 10:
        # Support and resistance levels
        highs = df['high'].rolling(window=10).max()
        lows = df['low'].rolling(window=10).min()
        
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=highs,
            mode='lines',
            name='Resistance',
            line=dict(color='red', width=1, dash='dash'),
            opacity=0.5
        ))
        
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=lows,
            mode='lines',
            name='Support',
            line=dict(color='green', width=1, dash='dash'),
            opacity=0.5
        ))
    
    # Chart layout with AlgoBox styling
    fig.update_layout(
        title=f"🔄 AlgoBox {chart_type} Chart - Price-Based AlgoBars (No Time Distortion)",
        xaxis_title="Bar Sequence (Price-Movement Based)",
        yaxis_title="Price",
        template="plotly_dark",
        height=600,
        showlegend=True,
        yaxis2=dict(
            title="Volume",
            overlaying='y',
            side='right',
            position=0.9
        ),
        yaxis3=dict(
            title="Delta",
            overlaying='y',
            side='right',
            position=1.0
        )
    )
    
    # Add market structure annotations
    if len(bars) > 0:
        latest_bar = bars[-1]
        fig.add_annotation(
            x=df['datetime'].iloc[-1],
            y=latest_bar['high'],
            text=f"Speed: {latest_bar['market_speed']}<br>Volatility: {latest_bar['volatility']:.2f}%<br>Volume: {latest_bar['volume']}<br>Delta: {latest_bar['delta']:+d}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="yellow",
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="yellow"
        )
        
        # Add price level annotations
        current_price = latest_bar['close']
        fig.add_hline(y=current_price, line_dash="solid", line_color="cyan", 
                     annotation_text=f"Current: ${current_price:.2f}")
    
    return fig

def create_market_structure_analysis(guardian: ApexComplianceGuardian):
    """Create market structure analysis using AlgoBars"""
    bars = guardian.algo_engine.get_recent_bars(50)
    
    if not bars:
        return None
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Market Speed Analysis
        speeds = [bar['market_speed'] for bar in bars[-10:]]
        speed_counts = pd.Series(speeds).value_counts()
        
        fig = px.pie(
            values=speed_counts.values,
            names=speed_counts.index,
            title="Market Speed Distribution (Last 10 AlgoBars)",
            color_discrete_map={
                'Very Fast': '#ff4444',
                'Fast': '#ff8800',
                'Moderate': '#ffff00',
                'Slow': '#88ff88'
            }
        )
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Volatility Trend
        volatilities = [bar['volatility'] for bar in bars[-20:]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=volatilities,
            mode='lines+markers',
            name='Volatility %',
            line=dict(color='orange', width=2),
            marker=dict(size=6)
        ))
        
        # Add volatility zones
        avg_vol = sum(volatilities) / len(volatilities) if volatilities else 0
        fig.add_hline(y=avg_vol, line_dash="dash", line_color="orange", 
                     annotation_text=f"Avg: {avg_vol:.2f}%")
        fig.add_hline(y=avg_vol * 2, line_dash="dot", line_color="red", 
                     annotation_text="High Vol")
        
        fig.update_layout(
            title="Volatility Trend (Last 20 AlgoBars)",
            yaxis_title="Volatility %",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        # Bull/Bear Bar Distribution
        bullish_count = sum(1 for bar in bars[-20:] if bar['is_bullish'])
        bearish_count = len(bars[-20:]) - bullish_count
        
        fig = go.Figure(data=[
            go.Bar(x=['Bullish', 'Bearish'], y=[bullish_count, bearish_count],
                  marker_color=['#00ff88', '#ff4444'],
                  text=[f'{bullish_count}', f'{bearish_count}'],
                  textposition='auto')
        ])
        fig.update_layout(
            title="Bull/Bear Distribution (Last 20 AlgoBars)",
            template="plotly_dark",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

def create_pnl_performance_chart(guardian: ApexComplianceGuardian):
    """Create comprehensive P&L performance tracking"""
    # Initialize P&L history in session state
    if 'pnl_history' not in st.session_state:
        st.session_state.pnl_history = []
    
    # Add current P&L to history
    current_time = datetime.now()
    st.session_state.pnl_history.append({
        'time': current_time,
        'daily_pnl': guardian.trade_data.daily_pnl,
        'account_balance': guardian.trade_data.account_balance + guardian.trade_data.daily_pnl,
        'drawdown': guardian.trade_data.drawdown_from_high,
        'positions': guardian.trade_data.open_positions,
        'price': getattr(guardian, 'current_price', 4580.25)
    })
    
    # Keep only last 200 points for performance
    if len(st.session_state.pnl_history) > 200:
        st.session_state.pnl_history = st.session_state.pnl_history[-200:]
    
    if len(st.session_state.pnl_history) < 2:
        st.info("📈 Building P&L history... Start monitoring to see performance charts")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.pnl_history)
    df['datetime'] = pd.to_datetime(df['time'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily P&L Chart with Risk Zones
        fig = go.Figure()
        
        # Daily P&L line
        colors = ['green' if pnl >= 0 else 'red' for pnl in df['daily_pnl']]
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df['daily_pnl'],
            mode='lines+markers',
            name='Daily P&L',
            line=dict(color='cyan', width=2),
            marker=dict(size=4, color=colors)
        ))
        
        # Risk zones
        account_balance = guardian.trade_data.account_balance
        daily_loss_limit = account_balance * guardian.rules.evaluation_max_daily_loss / 100
        safety_limit = daily_loss_limit * (guardian.rules.safety_ratio / 100)
        
        fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.5)
        fig.add_hline(y=-safety_limit, line_dash="dash", line_color="orange", 
                     annotation_text=f"Warning Zone: -${safety_limit:,.0f}")
        fig.add_hline(y=-daily_loss_limit, line_dash="solid", line_color="red", 
                     annotation_text=f"Danger Zone: -${daily_loss_limit:,.0f}")
        
        # Fill risk zones
        fig.add_hrect(y0=-safety_limit, y1=-daily_loss_limit, 
                     fillcolor="orange", opacity=0.1, line_width=0)
        fig.add_hrect(y0=-daily_loss_limit, y1=-daily_loss_limit*2, 
                     fillcolor="red", opacity=0.1, line_width=0)
        
        fig.update_layout(
            title="📊 Daily P&L with Apex Risk Zones",
            xaxis_title="Time",
            yaxis_title="P&L ($)",
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Account Balance Growth
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df['account_balance'],
            mode='lines+markers',
            name='Account Balance',
            line=dict(color='#00ff88', width=3),
            marker=dict(size=4),
            fill='tonexty'
        ))
        
        # Add starting balance line
        fig.add_hline(y=guardian.trade_data.account_balance, line_dash="dash", 
                     line_color="white", opacity=0.5,
                     annotation_text=f"Starting: ${guardian.trade_data.account_balance:,.0f}")
        
        fig.update_layout(
            title="💰 Account Balance Growth",
            xaxis_title="Time",
            yaxis_title="Balance ($)",
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def create_risk_gauges(guardian: ApexComplianceGuardian):
    """Create comprehensive risk assessment gauges"""
    st.markdown("### 🎯 Risk Assessment Gauges")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Daily Loss Risk Gauge
        daily_loss_pct = abs(guardian.trade_data.daily_pnl) / guardian.trade_data.account_balance * 100
        max_loss_pct = guardian.rules.evaluation_max_daily_loss
        risk_pct = min(100, (daily_loss_pct / max_loss_pct) * 100)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = risk_pct,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Daily Loss Risk"},
            delta = {'reference': 0, 'position': "top"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75, 
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=250, font={'color': "white"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk level text
        if risk_pct < 50:
            st.success(f"🟢 Safe Zone: {risk_pct:.1f}%")
        elif risk_pct < 80:
            st.warning(f"🟡 Caution: {risk_pct:.1f}%")
        else:
            st.error(f"🔴 Danger: {risk_pct:.1f}%")
        
    with col2:
        # Drawdown Risk Gauge
        dd_risk_pct = min(100, (guardian.trade_data.drawdown_from_high / guardian.rules.evaluation_trailing_threshold) * 100)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = dd_risk_pct,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Drawdown Risk"},
            delta = {'reference': 0, 'position': "top"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75, 
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=250, font={'color': "white"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Drawdown text
        if dd_risk_pct < 50:
            st.success(f"🟢 Safe: {guardian.trade_data.drawdown_from_high:.2f}%")
        elif dd_risk_pct < 80:
            st.warning(f"🟡 Watch: {guardian.trade_data.drawdown_from_high:.2f}%")
        else:
            st.error(f"🔴 Critical: {guardian.trade_data.drawdown_from_high:.2f}%")
        
    with col3:
        # Position Size Risk
        pos_risk_pct = min(100, (guardian.trade_data.open_positions / guardian.rules.max_total_contracts) * 100)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = pos_risk_pct,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Position Size Risk"},
            delta = {'reference': 0, 'position': "top"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkorange"},
                'steps': [
                    {'range': [0, 70], 'color': "lightgray"},
                    {'range': [70, 90], 'color': "yellow"},
                    {'range': [90, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75, 
                    'value': 95
                }
            }
        ))
        fig.update_layout(height=250, font={'color': "white"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Position text
        st.info(f"📊 {guardian.trade_data.open_positions}/{guardian.rules.max_total_contracts} contracts")
        
    with col4:
        # Overall Safety Score
        safety_score = guardian.rules.safety_ratio
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = safety_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Safety Score"},
            delta = {'reference': 80, 'position': "top"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 50], 'color': "red"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75, 
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=250, font={'color': "white"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Safety text
        if safety_score >= 80:
            st.success(f"🛡️ High Safety: {safety_score}%")
        elif safety_score >= 60:
            st.warning(f"⚠️ Moderate: {safety_score}%")
        else:
            st.error(f"🚨 Low Safety: {safety_score}%")

def create_sidebar():
    """Create the configuration sidebar"""
    guardian = st.session_state.guardian
    
    st.sidebar.markdown("## ⚙️ Apex Compliance Configuration")
    
    # Risk Presets Dropdown (as specifically requested)
    st.sidebar.markdown("### 🎯 Risk Management Presets")
    
    risk_preset = st.sidebar.selectbox(
        "Choose Risk Profile",
        ["Conservative (90%)", "Moderate (70%)", "Aggressive (50%)", "Custom"],
        index=1,  # Default to Moderate
        help="Select your risk management level for Apex compliance"
    )
    
    # Apply preset
    if risk_preset == "Conservative (90%)":
        guardian.rules.safety_ratio = 90
    elif risk_preset == "Moderate (70%)":
        guardian.rules.safety_ratio = 70
    elif risk_preset == "Aggressive (50%)":
        guardian.rules.safety_ratio = 50
    
    # Safety Ratio Configuration
    new_safety_ratio = st.sidebar.slider(
        "Safety Ratio (%)",
        min_value=5,
        max_value=90,
        value=int(guardian.rules.safety_ratio),
        step=5,
        help="Percentage of official Apex limits to trigger warnings"
    )
    
    if new_safety_ratio != guardian.rules.safety_ratio:
        guardian.rules.safety_ratio = new_safety_ratio
        guardian.add_alert(f"🎯 Safety ratio updated to {new_safety_ratio}%", "INFO")
    
    # AlgoBox AlgoBar Settings
    st.sidebar.markdown("### 📊 AlgoBox AlgoBar Settings")
    
    new_algo_bar_size = st.sidebar.slider(
        "AlgoBar Size (Ticks)",
        min_value=1,
        max_value=20,
        value=guardian.algo_settings.algo_bar_size,
        help="Price movement threshold for new AlgoBar formation"
    )
    
    if new_algo_bar_size != guardian.algo_settings.algo_bar_size:
        guardian.algo_settings.algo_bar_size = new_algo_bar_size
        guardian.algo_engine.price_threshold = new_algo_bar_size
        guardian.add_alert(f"📊 AlgoBar size updated to {new_algo_bar_size} ticks", "INFO")
    
    chart_type = st.sidebar.selectbox(
        "Chart Type",
        ["Tide", "Wave", "Ripple"],
        index=["Tide", "Wave", "Ripple"].index(guardian.algo_settings.chart_type),
        help="AlgoBox chart timeframe: Tide=macro, Wave=intermediate, Ripple=micro"
    )
    
    if chart_type != guardian.algo_settings.chart_type:
        guardian.algo_settings.chart_type = chart_type
        guardian.add_alert(f"📈 Chart type changed to {chart_type}", "INFO")
    
    # Trading Platform
    platform = st.sidebar.selectbox(
        "Trading Platform",
        ["Tradovate", "NinjaTrader", "AlgoBox", "TradingView", "MetaTrader"],
        index=0
    )
    
    # AlgoBar Display Options
    st.sidebar.markdown("### 🎨 AlgoBar Display")
    
    guardian.algo_settings.show_volume = st.sidebar.checkbox("Show Volume", value=True)
    guardian.algo_settings.show_delta = st.sidebar.checkbox("Show Cumulative Delta", value=True)
    guardian.algo_settings.show_imbalance_zones = st.sidebar.checkbox("Show Imbalance Zones", value=True)
    
    color_scheme = st.sidebar.selectbox(
        "Color Scheme",
        ["Bull/Bear", "Green/Red", "Blue/Orange"],
        help="AlgoBar color scheme"
    )
    
    # Account Settings
    st.sidebar.markdown("### 💰 Account Configuration")
    
    new_balance = st.sidebar.number_input(
        "Account Balance ($)",
        min_value=1000.0,
        max_value=1000000.0,
        value=guardian.trade_data.account_balance,
        step=1000.0
    )
    
    if new_balance != guardian.trade_data.account_balance:
        guardian.trade_data.account_balance = new_balance
        guardian.add_alert(f"💰 Account balance updated to ${new_balance:,.2f}", "INFO")
    
    # Real-time monitoring toggle
    monitoring_enabled = st.sidebar.checkbox("🔄 Real-Time Monitoring", value=st.session_state.monitoring_active)
    
    if monitoring_enabled != st.session_state.monitoring_active:
        st.session_state.monitoring_active = monitoring_enabled
        if monitoring_enabled:
            guardian.add_alert("🚀 Real-time monitoring STARTED", "SUCCESS")
        else:
            guardian.add_alert("🛑 Real-time monitoring STOPPED", "WARNING")

def create_main_dashboard():
    """Create the main dashboard"""
    guardian = st.session_state.guardian
    
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0;'>🛡️ APEX COMPLIANCE GUARDIAN + ALGOBOX ALGOBARS</h1>
        <h3 style='color: #e8f4f8; margin: 5px 0;'>Training Wheels for Prop Traders + Price-Based AlgoBar Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Control Panel
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚀 START MONITORING" if not st.session_state.monitoring_active else "🛑 STOP MONITORING",
                    type="primary" if not st.session_state.monitoring_active else "secondary"):
            st.session_state.monitoring_active = not st.session_state.monitoring_active
            if st.session_state.monitoring_active:
                guardian.add_alert("🚀 Compliance + AlgoBar monitoring STARTED", "SUCCESS")
            else:
                guardian.add_alert("🛑 Monitoring STOPPED", "WARNING")
            st.rerun()
            
    with col2:
        if st.button("🛑 EMERGENCY STOP", type="secondary"):
            guardian.emergency_stop_all()
            st.rerun()
            
    with col3:
        if st.button("🔒 FORCE LOCKOUT", type="secondary"):
            guardian.force_lockout()
            st.rerun()
            
    with col4:
        if st.button("💾 SAVE SETTINGS", type="secondary"):
            guardian.save_settings()
            st.rerun()
    
    # Status Indicators
    st.markdown("### 📊 Real-Time Status")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Account Balance", f"${guardian.trade_data.account_balance:,.2f}")
        
    with col2:
        pnl_delta = guardian.trade_data.daily_pnl
        st.metric("Daily P&L", f"${guardian.trade_data.daily_pnl:,.2f}", 
                 delta=f"${pnl_delta:,.2f}")
        
    with col3:
        st.metric("Open Positions", guardian.trade_data.open_positions,
                 delta=f"Max: {guardian.rules.max_total_contracts}")
        
    with col4:
        dd_value = guardian.trade_data.drawdown_from_high
        dd_limit = guardian.rules.evaluation_trailing_threshold
        st.metric("Trailing Drawdown", f"{dd_value:.2f}%", delta=f"Limit: {dd_limit:.2f}%")
        
    with col5:
        # AlgoBar metrics
        recent_bars = guardian.algo_engine.get_recent_bars(10)
        if recent_bars:
            avg_speed = sum(1 for bar in recent_bars if bar['market_speed'] in ['Fast', 'Very Fast']) / len(recent_bars) * 100
            st.metric("Market Speed", f"{avg_speed:.0f}%", delta="Fast Bars")
        else:
            st.metric("Market Speed", "0%", delta="No Data")
        
    with col6:
        status_text = "🔒 LOCKED OUT" if guardian.trade_data.is_locked_out else "✅ ACTIVE"
        monitoring_status = "🟢 MONITORING" if st.session_state.monitoring_active else "🔴 STOPPED"
        st.metric("Status", status_text)
        st.caption(monitoring_status)

def create_alerts_panel():
    """Create the alerts and violations panel"""
    st.markdown("### 🚨 Compliance Alerts & Violations")
    
    tab1, tab2, tab3 = st.tabs(["📢 Recent Alerts", "🚨 Violations", "📊 AlgoBar Analysis"])
    
    with tab1:
        if 'alerts' in st.session_state and st.session_state.alerts:
            # Show last 10 alerts
            recent_alerts = st.session_state.alerts[-10:]
            
            for alert in reversed(recent_alerts):
                level = alert['level']
                message = alert['message']
                timestamp = alert['timestamp']
                
                if level == "ERROR":
                    st.error(f"[{timestamp}] {message}")
                elif level == "WARNING":
                    st.warning(f"[{timestamp}] {message}")
                elif level == "SUCCESS":
                    st.success(f"[{timestamp}] {message}")
                else:
                    st.info(f"[{timestamp}] {message}")
        else:
            st.info("No alerts yet. Start monitoring to see system alerts.")
            
    with tab2:
        if 'violations' in st.session_state and st.session_state.violations:
            violations_df = pd.DataFrame(st.session_state.violations)
            st.dataframe(violations_df, use_container_width=True)
        else:
            st.success("✅ No violations detected. Keep trading safely!")
            
    with tab3:
        guardian = st.session_state.guardian
        recent_bars = guardian.algo_engine.get_recent_bars(20)
        
        if recent_bars:
            st.markdown("#### 📈 Recent AlgoBar Performance")
            
            # Create summary table
            bar_data = []
            for i, bar in enumerate(recent_bars[-10:]):
                bar_data.append({
                    'Bar #': len(recent_bars) - 10 + i + 1,
                    'Type': '🟢 Bull' if bar['is_bullish'] else '🔴 Bear',
                    'Price Range': f"{bar['open']:.2f} - {bar['close']:.2f}",
                    'Volume': bar['volume'],
                    'Delta': bar['delta'],
                    'Speed': bar['market_speed'],
                    'Volatility': f"{bar['volatility']:.2f}%"
                })
            
            df = pd.DataFrame(bar_data)
            st.dataframe(df, use_container_width=True)
            
            # AlgoBar insights
            bullish_pct = sum(1 for bar in recent_bars if bar['is_bullish']) / len(recent_bars) * 100
            avg_volatility = sum(bar['volatility'] for bar in recent_bars) / len(recent_bars)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Bullish Bars", f"{bullish_pct:.1f}%")
            with col2:
                st.metric("Avg Volatility", f"{avg_volatility:.2f}%")
            with col3:
                fast_bars = sum(1 for bar in recent_bars if bar['market_speed'] in ['Fast', 'Very Fast'])
                st.metric("Fast Bars", fast_bars)
        else:
            st.info("Start monitoring to see AlgoBar analysis")

def main():
    """Main Streamlit application"""
    # Initialize guardian
    if 'guardian' not in st.session_state:
        st.session_state.guardian = ApexComplianceGuardian()
        
    guardian = st.session_state.guardian
    
    # Auto-update when monitoring is active
    if st.session_state.get('monitoring_active', False):
        guardian.simulate_market_data()
        guardian.check_compliance()
        
        # Auto-refresh every 2 seconds
        time.sleep(0.1)
        st.rerun()
    
    # Create sidebar
    create_sidebar()
    
    # Main content
    create_main_dashboard()
    
    # P&L Performance Section
    st.markdown("### 📈 Performance Analytics")
    create_pnl_performance_chart(guardian)
    
    # Risk Assessment Section
    create_risk_gauges(guardian)
    
    # AlgoBar Charts
    st.markdown("### � AlgoBox AlgoBar Charts")
    
    # Chart type tabs
    tab1, tab2, tab3 = st.tabs(["🌊 Tide Chart (Macro)", "📊 Wave Chart (Intermediate)", "💧 Ripple Chart (Micro)"])
    
    with tab1:
        st.markdown("#### Tide Chart - Macro Trend Analysis")
        chart = create_algobar_chart(guardian, "Tide")
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        # Market structure analysis
        st.markdown("#### Market Structure Analysis")
        create_market_structure_analysis(guardian)
        
    with tab2:
        st.markdown("#### Wave Chart - Intermediate Structure")
        chart = create_algobar_chart(guardian, "Wave")
        if chart:
            st.plotly_chart(chart, use_container_width=True)
            
        # Wave-specific metrics
        bars = guardian.algo_engine.get_recent_bars(30)
        if bars:
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_vol = sum(bar['volume'] for bar in bars[-10:]) / 10
                st.metric("Avg Volume (10 bars)", f"{avg_vol:.0f}")
            with col2:
                total_delta = sum(bar['delta'] for bar in bars[-10:])
                st.metric("Net Delta (10 bars)", f"{total_delta:+d}")
            with col3:
                speed_trend = len([bar for bar in bars[-5:] if bar['market_speed'] in ['Fast', 'Very Fast']])
                st.metric("Fast Bars (Last 5)", speed_trend)
            
    with tab3:
        st.markdown("#### Ripple Chart - Micro Entry Analysis")
        chart = create_algobar_chart(guardian, "Ripple")
        if chart:
            st.plotly_chart(chart, use_container_width=True)
            
        # Ripple-specific analysis
        bars = guardian.algo_engine.get_recent_bars(20)
        if bars:
            st.markdown("##### Micro Structure Signals")
            col1, col2 = st.columns(2)
            
            with col1:
                # Recent bar analysis
                if len(bars) >= 3:
                    last_3_bars = bars[-3:]
                    bullish_momentum = sum(1 for bar in last_3_bars if bar['is_bullish'])
                    
                    if bullish_momentum >= 2:
                        st.success("🟢 Bullish Momentum: 3-bar trend")
                    elif bullish_momentum <= 1:
                        st.error("🔴 Bearish Momentum: 3-bar trend")
                    else:
                        st.warning("🟡 Mixed Signals: No clear trend")
                        
            with col2:
                # Volume profile
                recent_volumes = [bar['volume'] for bar in bars[-5:]]
                avg_recent = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0
                older_volumes = [bar['volume'] for bar in bars[-10:-5]] if len(bars) >= 10 else []
                avg_older = sum(older_volumes) / len(older_volumes) if older_volumes else avg_recent
                
                volume_change = ((avg_recent - avg_older) / avg_older * 100) if avg_older > 0 else 0
                
                if volume_change > 20:
                    st.success(f"📈 Volume Surge: +{volume_change:.1f}%")
                elif volume_change < -20:
                    st.warning(f"📉 Volume Drop: {volume_change:.1f}%")
                else:
                    st.info(f"📊 Volume Stable: {volume_change:+.1f}%")
    
    # Alerts panel
    create_alerts_panel()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🛡️ <strong>Apex Compliance Guardian + AlgoBox AlgoBars</strong> - Training Wheels + Price-Based Analysis</p>
        <p><em>AlgoBars: Price-Movement Based | No Time Distortion | No Repainting | WYSIWYG Principle</em></p>
        <p><em>Tide = Macro Trends | Wave = Intermediate Structure | Ripple = Micro Entries</em></p>
        <p><em>Always test with demo accounts first. Never risk more than you can afford to lose.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
