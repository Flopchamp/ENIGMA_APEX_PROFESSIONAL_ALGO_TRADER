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
        
        # Market volatility simulation
        volatility = random.uniform(0.5, 2.0)
        price_change = random.gauss(0, volatility)
        
        # Current price with trend
        if not hasattr(self, 'current_price'):
            self.current_price = base_price
            
        self.current_price += price_change
        
        # Volume simulation (heavier during market hours)
        current_time = datetime.now()
        market_open = current_time.replace(hour=9, minute=30)
        market_close = current_time.replace(hour=16, minute=0)
        
        is_market_hours = market_open <= current_time <= market_close
        volume = random.randint(50, 500) if is_market_hours else random.randint(10, 100)
        
        # Delta (order flow) simulation
        delta = random.randint(-volume//2, volume//2)
        
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
        if hasattr(self, 'last_price'):
            price_diff = self.current_price - self.last_price
            if self.trade_data.open_positions > 0:
                pnl_change = price_diff * self.trade_data.open_positions * 50  # $50 per point ES
                self.trade_data.daily_pnl += pnl_change
                
        self.last_price = self.current_price
        
        # Update max daily profit
        if self.trade_data.daily_pnl > self.trade_data.max_daily_profit:
            self.trade_data.max_daily_profit = self.trade_data.daily_pnl
            
        # Calculate trailing drawdown
        if self.trade_data.max_daily_profit > 0:
            current_drawdown = (self.trade_data.max_daily_profit - self.trade_data.daily_pnl) / self.trade_data.account_balance * 100
            self.trade_data.drawdown_from_high = max(0, current_drawdown)
            
        # Simulate position changes
        if random.random() < 0.02:  # 2% chance of position change
            self.trade_data.open_positions = random.randint(0, self.rules.max_total_contracts + 2)
            
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
            yaxis='y2'
        ))
    
    # Add delta (order flow) if enabled
    if guardian.algo_settings.show_delta:
        delta_colors = ['green' if d > 0 else 'red' for d in df['delta']]
        fig.add_trace(go.Bar(
            x=df['datetime'],
            y=df['delta'],
            name='Cumulative Delta',
            marker_color=delta_colors,
            yaxis='y3'
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
            text=f"Speed: {latest_bar['market_speed']}<br>Volatility: {latest_bar['volatility']:.2f}%",
            showarrow=True,
            arrowhead=2,
            arrowcolor="yellow",
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="yellow"
        )
    
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
            title="Market Speed Distribution (Last 10 AlgoBars)"
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
            line=dict(color='orange', width=2)
        ))
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
                  marker_color=['green', 'red'])
        ])
        fig.update_layout(
            title="Bull/Bear Distribution (Last 20 AlgoBars)",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

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
        <p style='color: #b8d4e3; margin: 0;'>FOR: Harrison Aloo & Michael Canfield | Platform: Tradovate + AlgoBox Technology</p>
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
    
    # AlgoBar Charts
    st.markdown("### 📈 AlgoBox AlgoBar Charts")
    
    # Chart type tabs
    tab1, tab2, tab3 = st.tabs(["🌊 Tide Chart", "📊 Wave Chart", "💧 Ripple Chart"])
    
    with tab1:
        chart = create_algobar_chart(guardian, "Tide")
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        # Market structure analysis
        create_market_structure_analysis(guardian)
        
    with tab2:
        chart = create_algobar_chart(guardian, "Wave")
        if chart:
            st.plotly_chart(chart, use_container_width=True)
            
    with tab3:
        chart = create_algobar_chart(guardian, "Ripple")
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    
    # Alerts panel
    create_alerts_panel()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🛡️ <strong>Apex Compliance Guardian + AlgoBox AlgoBars</strong> - Training Wheels + Price-Based Analysis</p>
        <p><em>AlgoBars: Price-Movement Based | No Time Distortion | No Repainting | WYSIWYG Principle</em></p>
        <p><em>Always test with demo accounts first. Never risk more than you can afford to lose.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
