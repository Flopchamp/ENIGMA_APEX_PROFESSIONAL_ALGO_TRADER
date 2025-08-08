"""
🎯 STREAMLIT 6-CHART TRADING CONTROL PANEL
Universal visual control system for multi-chart algorithmic trading
Works with any trader's setup - configurable for different accounts and strategies
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import logging
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import threading
import asyncio

# Configure page
st.set_page_config(
    page_title="🎯 Multi-Chart Trading Control Panel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class ChartStatus:
    """Individual chart status data"""
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
    signal_strength: int
    confluence_level: str
    last_update: datetime

@dataclass
class SystemConfig:
    """System-wide configuration"""
    trader_name: str
    total_charts: int
    safety_ratio: float
    emergency_stop_active: bool
    account_size: float
    daily_loss_limit: float
    apex_compliance_enabled: bool

class StreamlitTradingControlPanel:
    """
    Streamlit-based 6-Chart Trading Control Panel
    Universal system for any trader's multi-account setup
    """
    
    def __init__(self):
        self.initialize_session_state()
        self.load_configuration()
        self.setup_logging()
        
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        # Chart data
        if 'chart_data' not in st.session_state:
            st.session_state.chart_data = {}
            
        # System status
        if 'system_config' not in st.session_state:
            st.session_state.system_config = SystemConfig(
                trader_name="",  # Will be set by user
                total_charts=6,
                safety_ratio=25.0,
                emergency_stop_active=False,
                account_size=25000.0,
                daily_loss_limit=2000.0,
                apex_compliance_enabled=True
            )
            
        # System state
        if 'is_monitoring' not in st.session_state:
            st.session_state.is_monitoring = False
            
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
            
        # Initialize charts if empty
        if not st.session_state.chart_data:
            self.initialize_charts()
    
    def load_configuration(self):
        """Load user configuration"""
        try:
            with open('config/streamlit_config.json', 'r') as f:
                config_data = json.load(f)
                
            # Update session state with saved config
            for key, value in config_data.items():
                if hasattr(st.session_state.system_config, key):
                    setattr(st.session_state.system_config, key, value)
                    
        except FileNotFoundError:
            # Create default config
            self.save_configuration()
    
    def save_configuration(self):
        """Save current configuration"""
        import os
        os.makedirs('config', exist_ok=True)
        
        config_data = asdict(st.session_state.system_config)
        with open('config/streamlit_config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def initialize_charts(self):
        """Initialize chart data with configurable accounts"""
        default_charts = [
            {"id": 1, "name": "Chart-1", "balance": 25000},
            {"id": 2, "name": "Chart-2", "balance": 25000},
            {"id": 3, "name": "Chart-3", "balance": 25000},
            {"id": 4, "name": "Chart-4", "balance": 25000},
            {"id": 5, "name": "Chart-5", "balance": 25000},
            {"id": 6, "name": "Chart-6", "balance": 25000}
        ]
        
        for chart_config in default_charts:
            st.session_state.chart_data[chart_config["id"]] = ChartStatus(
                chart_id=chart_config["id"],
                account_name=chart_config["name"],
                account_balance=chart_config["balance"],
                daily_pnl=0.0,
                margin_used=0.0,
                margin_remaining=chart_config["balance"] * 0.8,
                margin_percentage=80.0,
                open_positions=0,
                is_active=True,
                risk_level="SAFE",
                last_signal="NONE",
                signal_strength=0,
                confluence_level="L0",
                last_update=datetime.now()
            )
    
    def create_header(self):
        """Create main header"""
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #1f1f1f, #2d2d2d); border-radius: 10px; margin-bottom: 20px;'>
            <h1 style='color: #00ff88; margin: 0;'>🎯 Multi-Chart Trading Control Panel</h1>
            <h3 style='color: #ffffff; margin: 5px 0;'>Universal OCR + Apex Compliance System</h3>
            <p style='color: #ffaa00; margin: 0;'>Visual Training Wheels for Professional Prop Trading</p>
        </div>
        """, unsafe_allow_html=True)
    
    def create_overall_margin_indicator(self):
        """Create the MOST IMPORTANT indicator - Overall margin remaining"""
        # Calculate totals
        total_balance = sum(chart.account_balance for chart in st.session_state.chart_data.values() if chart.is_active)
        total_remaining = sum(chart.margin_remaining for chart in st.session_state.chart_data.values() if chart.is_active)
        total_pnl = sum(chart.daily_pnl for chart in st.session_state.chart_data.values())
        
        overall_percentage = (total_remaining / total_balance * 100) if total_balance > 0 else 0
        
        # Determine status color
        if overall_percentage >= 70:
            status_color = "#00ff88"
            status_text = "SAFE TRADING"
        elif overall_percentage >= 40:
            status_color = "#ffaa00"
            status_text = "CAUTION"
        else:
            status_color = "#ff4444"
            status_text = "DANGER"
        
        # Create columns for the margin indicator
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Overall Margin %",
                value=f"{overall_percentage:.1f}%",
                delta=None
            )
        
        with col2:
            st.metric(
                label="💰 Margin Remaining",
                value=f"${total_remaining:,.0f}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="📈 Daily P&L",
                value=f"${total_pnl:,.2f}",
                delta=f"${total_pnl:,.2f}" if total_pnl != 0 else None
            )
        
        with col4:
            # Status indicator
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: {status_color}; border-radius: 10px; color: black;'>
                <h3 style='margin: 0; font-weight: bold;'>{status_text}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        return overall_percentage, total_remaining, total_pnl
    
    def create_chart_grid(self):
        """Create 6-chart grid with Red/Green/Yellow status boxes"""
        st.subheader("📊 Individual Chart Status")
        
        # Create 2 rows of 3 charts each
        for row in range(2):
            cols = st.columns(3)
            
            for col_idx, col in enumerate(cols):
                chart_id = row * 3 + col_idx + 1
                
                if chart_id in st.session_state.chart_data:
                    self.create_chart_box(col, chart_id)
    
    def create_chart_box(self, container, chart_id: int):
        """Create individual chart control box"""
        chart_data = st.session_state.chart_data[chart_id]
        
        with container:
            # Chart header with on/off toggle
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{chart_data.account_name}**")
            
            with col2:
                is_active = st.toggle(
                    "Active",
                    value=chart_data.is_active,
                    key=f"toggle_chart_{chart_id}"
                )
                
                # Update chart status if toggle changed
                if is_active != chart_data.is_active:
                    st.session_state.chart_data[chart_id].is_active = is_active
                    st.rerun()
            
            # Determine status color based on margin percentage
            if chart_data.margin_percentage >= 70:
                status_color = "#00ff88"  # Green
                risk_text = "SAFE TRADING"
            elif chart_data.margin_percentage >= 40:
                status_color = "#ffaa00"  # Yellow
                risk_text = "MARGINAL"
            else:
                status_color = "#ff4444"  # Red
                risk_text = "NO TRADE"
            
            # Status box
            st.markdown(f"""
            <div style='
                padding: 20px; 
                background-color: {status_color}; 
                border-radius: 10px; 
                margin: 10px 0;
                text-align: center;
                color: black;
                font-weight: bold;
            '>
                <h4 style='margin: 0;'>{risk_text}</h4>
                <p style='margin: 5px 0;'>{chart_data.margin_percentage:.1f}% | ${chart_data.margin_remaining:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Chart details
            st.markdown(f"""
            **Balance:** ${chart_data.account_balance:,.0f}  
            **Daily P&L:** ${chart_data.daily_pnl:,.2f}  
            **Positions:** {chart_data.open_positions}  
            **Signal:** {chart_data.last_signal}  
            **Strength:** {chart_data.signal_strength}%  
            **Level:** {chart_data.confluence_level}
            """)
    
    def create_control_panel(self):
        """Create main control buttons and settings"""
        st.subheader("🎛️ System Controls")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
                self.emergency_stop_all()
        
        with col2:
            if st.session_state.is_monitoring:
                if st.button("⏸️ PAUSE ALL", use_container_width=True):
                    st.session_state.is_monitoring = False
                    st.success("All monitoring paused")
            else:
                if st.button("▶️ START ALL", use_container_width=True):
                    st.session_state.is_monitoring = True
                    st.success("All monitoring started")
        
        with col3:
            if st.button("🔄 REFRESH DATA", use_container_width=True):
                self.simulate_data_update()
                st.rerun()
        
        with col4:
            if st.button("💾 SAVE CONFIG", use_container_width=True):
                self.save_configuration()
                st.success("Configuration saved")
    
    def create_settings_sidebar(self):
        """Create settings sidebar"""
        with st.sidebar:
            st.header("⚙️ System Settings")
            
            # Trader identification
            trader_name = st.text_input(
                "Trader Name",
                value=st.session_state.system_config.trader_name,
                help="Enter your name or identifier"
            )
            
            if trader_name != st.session_state.system_config.trader_name:
                st.session_state.system_config.trader_name = trader_name
            
            # Safety settings
            st.subheader("🛡️ Safety Settings")
            
            safety_ratio = st.slider(
                "Safety Ratio (%)",
                min_value=5.0,
                max_value=90.0,
                value=st.session_state.system_config.safety_ratio,
                step=5.0,
                help="Conservative position sizing multiplier"
            )
            
            if safety_ratio != st.session_state.system_config.safety_ratio:
                st.session_state.system_config.safety_ratio = safety_ratio
            
            daily_loss_limit = st.number_input(
                "Daily Loss Limit ($)",
                min_value=500.0,
                max_value=10000.0,
                value=st.session_state.system_config.daily_loss_limit,
                step=100.0,
                help="Maximum allowed daily loss"
            )
            
            if daily_loss_limit != st.session_state.system_config.daily_loss_limit:
                st.session_state.system_config.daily_loss_limit = daily_loss_limit
            
            # Apex compliance
            st.subheader("⚖️ Apex Compliance")
            
            apex_enabled = st.checkbox(
                "Enable Apex Rules",
                value=st.session_state.system_config.apex_compliance_enabled,
                help="Enforce Apex Trader Funding rules"
            )
            
            if apex_enabled != st.session_state.system_config.apex_compliance_enabled:
                st.session_state.system_config.apex_compliance_enabled = apex_enabled
            
            # Chart configuration
            st.subheader("📊 Chart Configuration")
            
            if st.button("Configure Chart Names", use_container_width=True):
                self.show_chart_config_modal()
            
            # System status
            st.subheader("📡 System Status")
            
            status_color = "#00ff88" if st.session_state.is_monitoring else "#ffaa00"
            monitoring_status = "ACTIVE" if st.session_state.is_monitoring else "PAUSED"
            
            st.markdown(f"""
            <div style='padding: 10px; background-color: {status_color}; border-radius: 5px; text-align: center; color: black;'>
                <strong>{monitoring_status}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Last Update:** {st.session_state.last_update.strftime('%H:%M:%S')}")
            st.markdown(f"**Active Charts:** {sum(1 for c in st.session_state.chart_data.values() if c.is_active)}")
    
    def show_chart_config_modal(self):
        """Show chart configuration in expander"""
        with st.expander("Chart Name Configuration", expanded=True):
            st.write("Configure individual chart names and account details:")
            
            for chart_id in range(1, 7):
                if chart_id in st.session_state.chart_data:
                    chart_data = st.session_state.chart_data[chart_id]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input(
                            f"Chart {chart_id} Name",
                            value=chart_data.account_name,
                            key=f"chart_name_{chart_id}"
                        )
                    
                    with col2:
                        new_balance = st.number_input(
                            f"Chart {chart_id} Balance",
                            value=chart_data.account_balance,
                            min_value=1000.0,
                            step=1000.0,
                            key=f"chart_balance_{chart_id}"
                        )
                    
                    # Update if changed
                    if new_name != chart_data.account_name:
                        st.session_state.chart_data[chart_id].account_name = new_name
                    
                    if new_balance != chart_data.account_balance:
                        st.session_state.chart_data[chart_id].account_balance = new_balance
    
    def emergency_stop_all(self):
        """Emergency stop all trading activities"""
        st.session_state.system_config.emergency_stop_active = True
        st.session_state.is_monitoring = False
        
        # Stop all charts
        for chart_id in st.session_state.chart_data:
            st.session_state.chart_data[chart_id].is_active = False
            st.session_state.chart_data[chart_id].last_signal = "STOPPED"
        
        st.error("🛑 EMERGENCY STOP ACTIVATED - ALL TRADING HALTED")
        
        # Show detailed emergency message
        st.warning("""
        **Emergency Stop Procedures Executed:**
        - All chart monitoring stopped
        - All active charts disabled
        - Trading signals halted
        - Please review positions manually in your trading platform
        """)
    
    def simulate_data_update(self):
        """Simulate real-time data updates for demo purposes"""
        import random
        
        for chart_id, chart_data in st.session_state.chart_data.items():
            if chart_data.is_active and not st.session_state.system_config.emergency_stop_active:
                # Simulate margin changes
                change = random.uniform(-2, 2)
                new_margin = max(10, min(95, chart_data.margin_percentage + change))
                
                # Simulate P&L changes
                pnl_change = random.uniform(-50, 50)
                new_pnl = chart_data.daily_pnl + pnl_change
                
                # Simulate signal data
                signals = ["BULLISH", "BEARISH", "NONE", "CONFLUENCE", "DIVERGENCE"]
                signal = random.choice(signals)
                strength = random.randint(0, 100)
                
                levels = ["L0", "L1", "L2", "L3", "L4"]
                level = random.choice(levels)
                
                positions = random.randint(0, 3)
                
                # Update chart data
                st.session_state.chart_data[chart_id].margin_percentage = new_margin
                st.session_state.chart_data[chart_id].margin_remaining = chart_data.account_balance * (new_margin / 100)
                st.session_state.chart_data[chart_id].daily_pnl = new_pnl
                st.session_state.chart_data[chart_id].last_signal = signal
                st.session_state.chart_data[chart_id].signal_strength = strength
                st.session_state.chart_data[chart_id].confluence_level = level
                st.session_state.chart_data[chart_id].open_positions = positions
                st.session_state.chart_data[chart_id].last_update = datetime.now()
        
        st.session_state.last_update = datetime.now()
    
    def create_performance_dashboard(self):
        """Create performance dashboard with charts"""
        st.subheader("📈 Performance Dashboard")
        
        # Create sample performance data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        # Equity curve
        equity_data = []
        for chart_id, chart_data in st.session_state.chart_data.items():
            chart_equity = [chart_data.account_balance + random.uniform(-1000, 1000) for _ in dates]
            equity_data.append({
                'Date': dates,
                'Account': chart_data.account_name,
                'Equity': chart_equity
            })
        
        # Create plotly chart
        fig = go.Figure()
        
        for data in equity_data:
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=data['Equity'],
                mode='lines',
                name=data['Account']
            ))
        
        fig.update_layout(
            title="30-Day Account Equity Curves",
            xaxis_title="Date",
            yaxis_title="Account Equity ($)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_accounts = len([c for c in st.session_state.chart_data.values() if c.is_active])
            st.metric("Active Accounts", total_accounts)
        
        with col2:
            total_equity = sum(c.account_balance for c in st.session_state.chart_data.values())
            st.metric("Total Equity", f"${total_equity:,.0f}")
        
        with col3:
            total_daily_pnl = sum(c.daily_pnl for c in st.session_state.chart_data.values())
            st.metric("Total Daily P&L", f"${total_daily_pnl:,.2f}")
    
    def run(self):
        """Main application entry point"""
        # Create header
        self.create_header()
        
        # Create settings sidebar
        self.create_settings_sidebar()
        
        # Main content area
        overall_margin, total_remaining, total_pnl = self.create_overall_margin_indicator()
        
        st.divider()
        
        # Chart grid
        self.create_chart_grid()
        
        st.divider()
        
        # Control panel
        self.create_control_panel()
        
        st.divider()
        
        # Performance dashboard
        self.create_performance_dashboard()
        
        # Auto-refresh if monitoring is active
        if st.session_state.is_monitoring:
            time.sleep(2)
            self.simulate_data_update()
            st.rerun()

def main():
    """Main entry point"""
    try:
        # Initialize the control panel
        control_panel = StreamlitTradingControlPanel()
        
        # Run the application
        control_panel.run()
        
    except Exception as e:
        st.error(f"Application Error: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()
