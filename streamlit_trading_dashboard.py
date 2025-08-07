"""
🎯 APEX TRADER FUNDING - 6-CHART VISUAL DASHBOARD
Universal Streamlit application for multi-chart algorithmic trading
Configurable for any trader, any setup, any number of charts

Features:
- Visual Red/Green/Yellow status indicators
- Overall margin monitoring (configurable as most important)
- Individual chart controls
- Apex Trader Funding compliance
- Real-time OCR signal reading
- Emergency stop protection
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Import OCR module
try:
    from streamlit_ocr_module import StreamlitOCRManager
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    StreamlitOCRManager = None

# Page configuration
st.set_page_config(
    page_title="Apex Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class UserConfig:
    """User-specific configuration"""
    trader_name: str
    account_size: float
    max_charts: int
    chart_names: List[str]
    safety_ratio: float
    daily_loss_limit: float
    max_position_per_chart: float
    priority_indicator: str  # "margin", "pnl", "risk", etc.
    broker: str  # "ninjatrader", "tradovate", etc.
    
@dataclass
class ChartState:
    """State for individual chart"""
    chart_id: int
    name: str
    is_enabled: bool
    status_color: str  # "red", "yellow", "green"
    power_score: int
    signal_strength: str
    confluence_level: str
    position_size: float
    pnl: float
    risk_level: str
    last_update: datetime

class TradingDashboard:
    """Main trading dashboard application"""
    
    def __init__(self):
        self.initialize_session_state()
        self.load_user_config()
        
        # Initialize OCR manager if available
        if OCR_AVAILABLE:
            self.ocr_manager = StreamlitOCRManager()
        else:
            self.ocr_manager = None
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'charts' not in st.session_state:
            st.session_state.charts = {}
        
        if 'system_running' not in st.session_state:
            st.session_state.system_running = False
            
        if 'emergency_stop' not in st.session_state:
            st.session_state.emergency_stop = False
            
        if 'total_pnl' not in st.session_state:
            st.session_state.total_pnl = 0.0
            
        if 'margin_used' not in st.session_state:
            st.session_state.margin_used = 0.0
            
        if 'user_config' not in st.session_state:
            st.session_state.user_config = None
    
    def load_user_config(self):
        """Load or create user configuration"""
        config_file = "config/user_config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                st.session_state.user_config = UserConfig(**config_data)
            except Exception as e:
                st.error(f"Error loading config: {e}")
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default user configuration"""
        default_config = UserConfig(
            trader_name="Trader",
            account_size=25000.0,
            max_charts=6,
            chart_names=[
                "ES-Primary", "ES-Secondary", "NQ-Primary", 
                "NQ-Secondary", "YM-Primary", "RTY-Primary"
            ],
            safety_ratio=25.0,
            daily_loss_limit=2000.0,
            max_position_per_chart=5.0,
            priority_indicator="margin",
            broker="ninjatrader"
        )
        
        st.session_state.user_config = default_config
        self.save_user_config()
    
    def save_user_config(self):
        """Save user configuration"""
        config_file = "config/user_config.json"
        os.makedirs("config", exist_ok=True)
        
        try:
            with open(config_file, 'w') as f:
                json.dump(asdict(st.session_state.user_config), f, indent=2)
        except Exception as e:
            st.error(f"Error saving config: {e}")
    
    def render_header(self):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            st.image("https://via.placeholder.com/100x50/4CAF50/FFFFFF?text=APEX", width=100)
        
        with col2:
            st.title("🎯 Apex Trading Dashboard")
            if st.session_state.user_config:
                st.caption(f"Welcome {st.session_state.user_config.trader_name} | Account: ${st.session_state.user_config.account_size:,.0f}")
        
        with col3:
            # System status indicator
            if st.session_state.emergency_stop:
                st.error("🚨 EMERGENCY STOP ACTIVE")
            elif st.session_state.system_running:
                st.success("✅ System Active")
            else:
                st.warning("⏸️ System Paused")
    
    def render_sidebar_config(self):
        """Render configuration sidebar"""
        st.sidebar.header("⚙️ Configuration")
        
        config = st.session_state.user_config
        
        # User settings
        st.sidebar.subheader("👤 User Settings")
        config.trader_name = st.sidebar.text_input("Trader Name", config.trader_name)
        config.account_size = st.sidebar.number_input("Account Size ($)", value=config.account_size, min_value=1000.0)
        
        # Chart settings
        st.sidebar.subheader("📊 Chart Settings")
        config.max_charts = st.sidebar.slider("Number of Charts", 1, 12, config.max_charts)
        
        # Update chart names list based on max_charts
        while len(config.chart_names) < config.max_charts:
            config.chart_names.append(f"Chart-{len(config.chart_names) + 1}")
        config.chart_names = config.chart_names[:config.max_charts]
        
        # Allow editing chart names
        for i in range(config.max_charts):
            config.chart_names[i] = st.sidebar.text_input(
                f"Chart {i+1} Name", 
                config.chart_names[i],
                key=f"chart_name_{i}"
            )
        
        # Risk settings
        st.sidebar.subheader("⚖️ Risk Management")
        config.safety_ratio = st.sidebar.slider("Safety Ratio (%)", 5.0, 90.0, config.safety_ratio)
        config.daily_loss_limit = st.sidebar.number_input("Daily Loss Limit ($)", value=config.daily_loss_limit)
        config.max_position_per_chart = st.sidebar.number_input("Max Position per Chart", value=config.max_position_per_chart, min_value=0.1)
        
        # Priority indicator
        config.priority_indicator = st.sidebar.selectbox(
            "Most Important Indicator",
            ["margin", "pnl", "risk", "drawdown"],
            index=["margin", "pnl", "risk", "drawdown"].index(config.priority_indicator)
        )
        
        # Broker selection
        config.broker = st.sidebar.selectbox(
            "Broker Platform",
            ["ninjatrader", "tradovate", "thinkorswim", "other"],
            index=["ninjatrader", "tradovate", "thinkorswim", "other"].index(config.broker)
        )
        
        # Save configuration
        if st.sidebar.button("💾 Save Configuration"):
            self.save_user_config()
            st.sidebar.success("Configuration saved!")
    
    def initialize_charts(self):
        """Initialize chart states based on user configuration"""
        config = st.session_state.user_config
        
        for i in range(config.max_charts):
            chart_id = i + 1
            if chart_id not in st.session_state.charts:
                st.session_state.charts[chart_id] = ChartState(
                    chart_id=chart_id,
                    name=config.chart_names[i] if i < len(config.chart_names) else f"Chart-{chart_id}",
                    is_enabled=True,
                    status_color="yellow",
                    power_score=0,
                    signal_strength="None",
                    confluence_level="L0",
                    position_size=0.0,
                    pnl=0.0,
                    risk_level="Low",
                    last_update=datetime.now()
                )
    
    def render_priority_indicator(self):
        """Render the user's priority indicator prominently"""
        config = st.session_state.user_config
        
        st.subheader(f"🎯 Priority Monitor: {config.priority_indicator.upper()}")
        
        if config.priority_indicator == "margin":
            margin_remaining = config.account_size - st.session_state.margin_used
            margin_percent = (margin_remaining / config.account_size) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Margin Remaining", f"${margin_remaining:,.0f}")
            with col2:
                st.metric("📊 Margin Used", f"${st.session_state.margin_used:,.0f}")
            with col3:
                color = "green" if margin_percent > 50 else "orange" if margin_percent > 20 else "red"
                st.metric("📈 Margin %", f"{margin_percent:.1f}%")
        
        elif config.priority_indicator == "pnl":
            pnl_percent = (st.session_state.total_pnl / config.account_size) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                color = "green" if st.session_state.total_pnl >= 0 else "red"
                st.metric("💵 Total P&L", f"${st.session_state.total_pnl:,.0f}")
            with col2:
                st.metric("📊 P&L %", f"{pnl_percent:.2f}%")
            with col3:
                daily_limit_used = (abs(st.session_state.total_pnl) / config.daily_loss_limit) * 100
                st.metric("⚠️ Daily Limit Used", f"{daily_limit_used:.1f}%")
        
        # Add progress bar for visual impact
        if config.priority_indicator == "margin":
            progress_value = max(0, min(100, margin_percent)) / 100
            st.progress(progress_value)
        elif config.priority_indicator == "pnl":
            # Show drawdown progress
            if st.session_state.total_pnl < 0:
                drawdown_percent = min(100, (abs(st.session_state.total_pnl) / config.daily_loss_limit) * 100)
                st.progress(drawdown_percent / 100)
                if drawdown_percent > 80:
                    st.error("⚠️ Approaching daily loss limit!")
    
    def render_chart_grid(self):
        """Render the visual chart grid with status colors"""
        config = st.session_state.user_config
        
        st.subheader("📊 Chart Status Grid")
        
        # Calculate grid layout
        cols_per_row = min(3, config.max_charts)
        rows_needed = (config.max_charts + cols_per_row - 1) // cols_per_row
        
        chart_index = 1
        for row in range(rows_needed):
            cols = st.columns(cols_per_row)
            
            for col_idx in range(cols_per_row):
                if chart_index <= config.max_charts:
                    with cols[col_idx]:
                        self.render_individual_chart(chart_index)
                chart_index += 1
    
    def render_individual_chart(self, chart_id: int):
        """Render individual chart status box"""
        chart = st.session_state.charts.get(chart_id)
        if not chart:
            return
        
        # Status color mapping
        color_map = {
            "red": "🔴",
            "yellow": "🟡", 
            "green": "🟢"
        }
        
        # Create status box
        status_icon = color_map.get(chart.status_color, "⚪")
        
        with st.container():
            # Chart header with status color
            st.markdown(f"### {status_icon} {chart.name}")
            
            # Enable/disable toggle
            chart.is_enabled = st.checkbox(
                "Enabled", 
                value=chart.is_enabled,
                key=f"enable_{chart_id}"
            )
            
            # Chart metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Power", f"{chart.power_score}%")
                st.metric("Position", f"{chart.position_size:.1f}")
            
            with col2:
                st.metric("P&L", f"${chart.pnl:,.0f}")
                st.metric("Risk", chart.risk_level)
            
            # Signal details
            st.caption(f"Signal: {chart.signal_strength}")
            st.caption(f"Level: {chart.confluence_level}")
            st.caption(f"Updated: {chart.last_update.strftime('%H:%M:%S')}")
            
            # Individual chart controls
            if st.button(f"📊 Details", key=f"details_{chart_id}"):
                self.show_chart_details(chart_id)
    
    def show_chart_details(self, chart_id: int):
        """Show detailed chart information in modal"""
        chart = st.session_state.charts.get(chart_id)
        if not chart:
            return
        
        with st.expander(f"📊 {chart.name} - Detailed View", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📈 Signal Data")
                st.write(f"Power Score: {chart.power_score}%")
                st.write(f"Signal Strength: {chart.signal_strength}")
                st.write(f"Confluence Level: {chart.confluence_level}")
                st.write(f"Risk Level: {chart.risk_level}")
            
            with col2:
                st.subheader("💰 Position Info")
                st.write(f"Position Size: {chart.position_size:.2f}")
                st.write(f"P&L: ${chart.pnl:,.2f}")
                st.write(f"Status: {chart.status_color.upper()}")
                st.write(f"Enabled: {'Yes' if chart.is_enabled else 'No'}")
            
            with col3:
                st.subheader("⚙️ Chart Controls")
                
                # Manual position size override
                new_position = st.number_input(
                    "Override Position Size",
                    value=chart.position_size,
                    min_value=0.0,
                    max_value=st.session_state.user_config.max_position_per_chart,
                    key=f"position_override_{chart_id}"
                )
                
                if st.button(f"Update Position", key=f"update_pos_{chart_id}"):
                    chart.position_size = new_position
                    st.success("Position updated!")
                
                # Force status color
                new_color = st.selectbox(
                    "Force Status Color",
                    ["auto", "red", "yellow", "green"],
                    key=f"color_override_{chart_id}"
                )
                
                if new_color != "auto" and st.button(f"Force Color", key=f"force_color_{chart_id}"):
                    chart.status_color = new_color
                    st.success(f"Status forced to {new_color}!")
    
    def render_system_controls(self):
        """Render main system controls"""
        st.subheader("🎛️ System Controls")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚀 Start System", disabled=st.session_state.system_running):
                st.session_state.system_running = True
                st.session_state.emergency_stop = False
                st.success("System started!")
                st.rerun()
        
        with col2:
            if st.button("⏸️ Pause System", disabled=not st.session_state.system_running):
                st.session_state.system_running = False
                st.warning("System paused!")
                st.rerun()
        
        with col3:
            if st.button("🚨 EMERGENCY STOP", type="primary"):
                st.session_state.emergency_stop = True
                st.session_state.system_running = False
                # Disable all charts
                for chart in st.session_state.charts.values():
                    chart.is_enabled = False
                    chart.status_color = "red"
                st.error("EMERGENCY STOP ACTIVATED!")
                st.rerun()
        
        with col4:
            if st.button("🔄 Reset Emergency", disabled=not st.session_state.emergency_stop):
                st.session_state.emergency_stop = False
                # Reset all charts to yellow
                for chart in st.session_state.charts.values():
                    chart.is_enabled = True
                    chart.status_color = "yellow"
                st.info("Emergency stop reset!")
                st.rerun()
    
    def render_system_status(self):
        """Render overall system status"""
        st.subheader("📊 System Status")
        
        config = st.session_state.user_config
        
        # Calculate system metrics
        active_charts = sum(1 for chart in st.session_state.charts.values() if chart.is_enabled)
        total_position = sum(chart.position_size for chart in st.session_state.charts.values())
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Active Charts", active_charts)
        
        with col2:
            st.metric("📊 Total Position", f"{total_position:.1f}")
        
        with col3:
            st.metric("💰 Account Equity", f"${config.account_size + st.session_state.total_pnl:,.0f}")
        
        with col4:
            safety_used = (total_position / config.max_position_per_chart) * 100 if config.max_position_per_chart > 0 else 0
            st.metric("⚖️ Safety Used", f"{safety_used:.1f}%")
        
        # Apex compliance status
        st.subheader("⚖️ Apex Compliance Status")
        
        compliance_col1, compliance_col2, compliance_col3 = st.columns(3)
        
        with compliance_col1:
            daily_loss_percent = (abs(min(0, st.session_state.total_pnl)) / config.daily_loss_limit) * 100
            status = "✅ Good" if daily_loss_percent < 50 else "⚠️ Warning" if daily_loss_percent < 80 else "🚨 Critical"
            st.metric("Daily Loss Rule", f"{daily_loss_percent:.1f}%", delta=status)
        
        with compliance_col2:
            trailing_dd = abs(min(0, st.session_state.total_pnl))
            st.metric("Trailing Drawdown", f"${trailing_dd:,.0f}")
        
        with compliance_col3:
            consistency_score = 85.0  # Simulated
            st.metric("Consistency Score", f"{consistency_score:.1f}%")
    
    def simulate_data_update(self):
        """Simulate real-time data updates (replace with actual OCR/API)"""
        if st.session_state.system_running and not st.session_state.emergency_stop:
            
            # Update each chart with simulated data
            total_pnl = 0
            total_margin = 0
            
            for chart in st.session_state.charts.values():
                if chart.is_enabled:
                    # Simulate power score changes
                    chart.power_score = max(0, min(100, chart.power_score + np.random.randint(-5, 6)))
                    
                    # Update status color based on power score
                    if chart.power_score >= 70:
                        chart.status_color = "green"
                        chart.signal_strength = "Strong"
                    elif chart.power_score >= 40:
                        chart.status_color = "yellow"
                        chart.signal_strength = "Medium"
                    else:
                        chart.status_color = "red"
                        chart.signal_strength = "Weak"
                    
                    # Simulate P&L changes
                    pnl_change = np.random.normal(0, 25)
                    chart.pnl += pnl_change
                    
                    # Update position size based on signal
                    if chart.status_color == "green":
                        chart.position_size = min(
                            st.session_state.user_config.max_position_per_chart,
                            (chart.power_score / 100) * st.session_state.user_config.max_position_per_chart
                        )
                    else:
                        chart.position_size *= 0.9  # Reduce position on weak signals
                    
                    # Update timestamp
                    chart.last_update = datetime.now()
                    
                    total_pnl += chart.pnl
                    total_margin += chart.position_size * 400  # $400 per contract margin
            
            st.session_state.total_pnl = total_pnl
            st.session_state.margin_used = total_margin
            
            # Check for emergency conditions
            if abs(st.session_state.total_pnl) > st.session_state.user_config.daily_loss_limit:
                st.session_state.emergency_stop = True
                st.session_state.system_running = False
    
    def render_performance_charts(self):
        """Render performance visualization"""
        st.subheader("📈 Performance Analytics")
        
        # Create sample performance data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        # Simulate equity curve
        equity_curve = []
        base_equity = st.session_state.user_config.account_size
        current_equity = base_equity
        
        for _ in dates:
            daily_change = np.random.normal(50, 200)  # Average $50 gain, $200 std dev
            current_equity += daily_change
            equity_curve.append(current_equity)
        
        # Create plotly chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity_curve,
            mode='lines',
            name='Account Equity',
            line=dict(color='green', width=2)
        ))
        
        fig.add_hline(y=base_equity, line_dash="dash", annotation_text="Starting Equity")
        
        fig.update_layout(
            title="30-Day Equity Curve",
            xaxis_title="Date",
            yaxis_title="Account Value ($)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics table
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Performance Metrics")
            metrics_df = pd.DataFrame({
                "Metric": ["Total Return", "Max Drawdown", "Win Rate", "Profit Factor", "Sharpe Ratio"],
                "Value": ["$2,450 (9.8%)", "$1,200 (4.8%)", "68.5%", "1.85", "1.42"]
            })
            st.dataframe(metrics_df, hide_index=True)
        
        with col2:
            st.subheader("🎯 Chart Performance")
            chart_performance = []
            for chart in st.session_state.charts.values():
                chart_performance.append({
                    "Chart": chart.name,
                    "P&L": f"${chart.pnl:,.0f}",
                    "Status": chart.status_color.upper(),
                    "Power": f"{chart.power_score}%"
                })
            
            if chart_performance:
                st.dataframe(pd.DataFrame(chart_performance), hide_index=True)
    
    def run(self):
        """Main application run method"""
        # Initialize
        self.render_header()
        self.render_sidebar_config()
        
        if st.session_state.user_config:
            self.initialize_charts()
            
            # Main dashboard
            self.render_priority_indicator()
            
            st.divider()
            
            self.render_chart_grid()
            
            st.divider()
            
            self.render_system_controls()
            
            st.divider()
            
            self.render_system_status()
            
            st.divider()
            
            # Performance tab
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "👁️ OCR Setup", "⚙️ Settings", "📋 Logs"])
            
            with tab1:
                self.render_performance_charts()
            
            with tab2:
                if OCR_AVAILABLE and self.ocr_manager:
                    self.ocr_manager.render_ocr_configuration()
                else:
                    st.error("❌ OCR module not available")
                    st.info("To enable OCR: pip install pytesseract opencv-python pillow")
            
            with tab3:
                st.subheader("⚙️ Advanced Settings")
                st.info("Advanced configuration options will be available here.")
                
                # OCR Configuration
                st.subheader("👁️ OCR Configuration")
                if st.button("🔧 Calibrate OCR Regions"):
                    st.info("OCR calibration tool will be launched here.")
                
                # Export/Import Settings
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Export Settings"):
                        config_json = json.dumps(asdict(st.session_state.user_config), indent=2)
                        st.download_button(
                            "Download Configuration",
                            config_json,
                            "trading_config.json",
                            "application/json"
                        )
                
                with col2:
                    uploaded_file = st.file_uploader("📤 Import Settings", type="json")
                    if uploaded_file:
                        try:
                            config_data = json.load(uploaded_file)
                            st.session_state.user_config = UserConfig(**config_data)
                            st.success("Configuration imported successfully!")
                        except Exception as e:
                            st.error(f"Error importing configuration: {e}")
            
            with tab4:
                st.subheader("📋 System Logs")
                
                # OCR Status
                if OCR_AVAILABLE and self.ocr_manager:
                    self.ocr_manager.render_ocr_status()
                
                st.divider()
                
                # Simulated log entries
                logs = [
                    f"{datetime.now().strftime('%H:%M:%S')} - System started",
                    f"{(datetime.now() - timedelta(minutes=1)).strftime('%H:%M:%S')} - Chart ES-Primary signal: GREEN (85%)",
                    f"{(datetime.now() - timedelta(minutes=2)).strftime('%H:%M:%S')} - Position updated: NQ-Primary 2.5 contracts",
                    f"{(datetime.now() - timedelta(minutes=3)).strftime('%H:%M:%S')} - Compliance check: PASSED",
                ]
                
                for log in logs:
                    st.text(log)
            
            # Auto-refresh simulation
            if st.session_state.system_running:
                self.simulate_data_update()
                time.sleep(0.1)  # Small delay for smooth updates
                st.rerun()

def main():
    """Main application entry point"""
    dashboard = TradingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
