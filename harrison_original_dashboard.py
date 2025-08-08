"""
🎯 HARRISON'S ORIGINAL DASHBOARD
Exact replica of Harrison's clean dashboard interface
As seen at: https://flopchamp-enig-systemapex-compliance-guardian-streamlit-e2zsng.streamlit.app/
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Page configuration - Harrison's original style
st.set_page_config(
    page_title="Apex Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class ChartData:
    """Harrison's original chart data structure"""
    chart_id: int
    name: str
    is_enabled: bool
    status_color: str  # "green", "yellow", "red"
    margin_percentage: float
    daily_pnl: float
    position_size: float
    power_score: int
    signal_strength: str
    last_update: datetime

class HarrisonOriginalDashboard:
    """Harrison's Original Dashboard - Clean and Simple"""
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_styling()
        
    def setup_styling(self):
        """Harrison's original CSS styling"""
        st.markdown("""
        <style>
        /* Harrison's clean styling */
        .main > div {
            padding: 1rem;
        }
        
        .stMetric {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
        }
        
        /* Chart status boxes */
        .chart-container {
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: white;
        }
        
        .chart-safe {
            border-color: #28a745;
            background-color: #d4edda;
        }
        
        .chart-warning {
            border-color: #ffc107;
            background-color: #fff3cd;
        }
        
        .chart-danger {
            border-color: #dc3545;
            background-color: #f8d7da;
        }
        
        /* Status indicators */
        .status-safe {
            background-color: #28a745;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-align: center;
            font-weight: bold;
        }
        
        .status-warning {
            background-color: #ffc107;
            color: black;
            padding: 8px 16px;
            border-radius: 20px;
            text-align: center;
            font-weight: bold;
        }
        
        .status-danger {
            background-color: #dc3545;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-align: center;
            font-weight: bold;
        }
        
        /* Overall margin bar */
        .margin-bar {
            height: 40px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 18px;
            margin: 15px 0;
        }
        
        .margin-safe { background-color: #28a745; }
        .margin-warning { background-color: #ffc107; color: black; }
        .margin-danger { background-color: #dc3545; }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
        }
        
        /* Header styling */
        .dashboard-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(90deg, #1f4e79, #2d5aa0);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize session state with Harrison's original structure"""
        if 'charts' not in st.session_state:
            st.session_state.charts = self.create_default_charts()
        
        if 'overall_margin_percentage' not in st.session_state:
            st.session_state.overall_margin_percentage = 75.0
        
        if 'system_active' not in st.session_state:
            st.session_state.system_active = False
        
        if 'emergency_stop' not in st.session_state:
            st.session_state.emergency_stop = False
        
        if 'total_equity' not in st.session_state:
            st.session_state.total_equity = 150000.0
        
        if 'daily_pnl' not in st.session_state:
            st.session_state.daily_pnl = 0.0
    
    def create_default_charts(self) -> Dict[int, ChartData]:
        """Create Harrison's original 6-chart setup"""
        chart_names = [
            "ES-Primary", "NQ-Primary", "YM-Primary",
            "RTY-Primary", "CL-Primary", "GC-Primary"
        ]
        
        charts = {}
        for i in range(6):
            chart_id = i + 1
            charts[chart_id] = ChartData(
                chart_id=chart_id,
                name=chart_names[i],
                is_enabled=True,
                status_color="green",
                margin_percentage=75.0,
                daily_pnl=0.0,
                position_size=0.0,
                power_score=0,
                signal_strength="None",
                last_update=datetime.now()
            )
        
        return charts
    
    def render_header(self):
        """Harrison's original header design"""
        st.markdown("""
        <div class="dashboard-header">
            <h1>🎯 Apex Trading Dashboard</h1>
            <h3>6-Chart Visual Control Panel</h3>
            <p>Clean • Simple • Effective</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Time and status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**📅 {datetime.now().strftime('%Y-%m-%d')}**")
        
        with col2:
            if st.session_state.emergency_stop:
                st.markdown('<div class="status-danger">🚨 EMERGENCY STOP</div>', unsafe_allow_html=True)
            elif st.session_state.system_active:
                st.markdown('<div class="status-safe">✅ SYSTEM ACTIVE</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-warning">⏸️ SYSTEM PAUSED</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"**🕐 {datetime.now().strftime('%H:%M:%S')}**")
    
    def render_overall_margin(self):
        """Harrison's signature overall margin indicator"""
        st.markdown("## 📊 OVERALL MARGIN REMAINING")
        st.markdown("### (MOST IMPORTANT INDICATOR)")
        
        # Calculate overall margin
        self.calculate_overall_margin()
        
        percentage = st.session_state.overall_margin_percentage
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Margin Percentage",
                f"{percentage:.1f}%",
                delta="Safe" if percentage > 70 else "Warning" if percentage > 40 else "Danger"
            )
        
        with col2:
            margin_amount = st.session_state.total_equity * (percentage / 100)
            st.metric(
                "Margin Available",
                f"${margin_amount:,.0f}",
                delta=f"${st.session_state.daily_pnl:,.2f} today"
            )
        
        with col3:
            st.metric(
                "Total Equity",
                f"${st.session_state.total_equity:,.0f}",
                delta=f"{len([c for c in st.session_state.charts.values() if c.is_enabled])} active"
            )
        
        with col4:
            risk_level = "LOW" if percentage > 70 else "MEDIUM" if percentage > 40 else "HIGH"
            st.metric("Risk Level", risk_level)
        
        # Harrison's signature margin bar
        if percentage >= 70:
            bar_class = "margin-safe"
            status_text = "SAFE TO TRADE"
        elif percentage >= 40:
            bar_class = "margin-warning"
            status_text = "TRADE WITH CAUTION"
        else:
            bar_class = "margin-danger"
            status_text = "STOP TRADING - DANGER ZONE"
        
        st.markdown(f"""
        <div class="margin-bar {bar_class}">
            {status_text} - {percentage:.1f}% MARGIN REMAINING
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(percentage / 100, text=f"Margin: {percentage:.1f}%")
    
    def render_chart_grid(self):
        """Harrison's original 6-chart grid layout"""
        st.markdown("## 📊 Chart Status Grid")
        
        # 2 rows of 3 charts each - Harrison's preferred layout
        row1_cols = st.columns(3)
        row2_cols = st.columns(3)
        
        # First row (Charts 1-3)
        for i, col in enumerate(row1_cols):
            chart_id = i + 1
            chart = st.session_state.charts[chart_id]
            with col:
                self.render_chart_box(chart)
        
        # Second row (Charts 4-6)
        for i, col in enumerate(row2_cols):
            chart_id = i + 4
            chart = st.session_state.charts[chart_id]
            with col:
                self.render_chart_box(chart)
    
    def render_chart_box(self, chart: ChartData):
        """Harrison's individual chart box design"""
        # Determine status class
        if chart.margin_percentage >= 70:
            container_class = "chart-safe"
            status_icon = "🟢"
            status_text = "SAFE"
        elif chart.margin_percentage >= 40:
            container_class = "chart-warning"
            status_icon = "🟡"
            status_text = "CAUTION"
        else:
            container_class = "chart-danger"
            status_icon = "🔴"
            status_text = "DANGER"
        
        # Chart container
        with st.container():
            st.markdown(f'<div class="chart-container {container_class}">', unsafe_allow_html=True)
            
            # Chart header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{chart.name}**")
                st.markdown(f"{status_icon} **{status_text}**")
            with col2:
                chart.is_enabled = st.checkbox(
                    "ON", 
                    value=chart.is_enabled,
                    key=f"chart_{chart.chart_id}_enable"
                )
            
            # Chart metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Margin", f"{chart.margin_percentage:.1f}%")
                st.metric("Position", f"{chart.position_size:.1f}")
            with col2:
                st.metric("P&L", f"${chart.daily_pnl:,.2f}")
                st.metric("Power", f"{chart.power_score}%")
            
            # Signal information
            if chart.signal_strength != "None":
                st.markdown(f"**Signal:** {chart.signal_strength}")
            
            st.caption(f"Updated: {chart.last_update.strftime('%H:%M:%S')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_controls(self):
        """Harrison's control buttons"""
        st.markdown("## 🎮 System Controls")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚀 START SYSTEM", disabled=st.session_state.system_active):
                st.session_state.system_active = True
                st.session_state.emergency_stop = False
                st.success("System started!")
                st.rerun()
        
        with col2:
            if st.button("⏸️ PAUSE SYSTEM", disabled=not st.session_state.system_active):
                st.session_state.system_active = False
                st.warning("System paused!")
                st.rerun()
        
        with col3:
            if st.button("🚨 EMERGENCY STOP", type="primary"):
                self.emergency_stop()
        
        with col4:
            if st.button("🔄 REFRESH DATA"):
                self.refresh_data()
    
    def render_sidebar(self):
        """Harrison's sidebar configuration"""
        st.sidebar.header("⚙️ Dashboard Settings")
        
        # User info
        st.sidebar.subheader("👤 Trader Profile")
        trader_name = st.sidebar.text_input("Trader Name", value="Harrison")
        account_size = st.sidebar.number_input("Account Size", value=150000, min_value=1000)
        
        # Chart settings
        st.sidebar.subheader("📊 Chart Settings")
        chart_layout = st.sidebar.selectbox("Layout", ["2x3 Grid", "3x2 Grid", "Single Row"])
        auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
        refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 5)
        
        # Risk settings
        st.sidebar.subheader("⚖️ Risk Management")
        safety_threshold = st.sidebar.slider("Safety Threshold (%)", 30, 90, 70)
        max_daily_loss = st.sidebar.number_input("Max Daily Loss", value=2000)
        
        # System status
        st.sidebar.subheader("📊 System Status")
        st.sidebar.metric("Active Charts", len([c for c in st.session_state.charts.values() if c.is_enabled]))
        st.sidebar.metric("System Health", "HEALTHY" if st.session_state.overall_margin_percentage > 60 else "WARNING")
        
        # Quick actions
        st.sidebar.subheader("⚡ Quick Actions")
        if st.sidebar.button("📊 Reset All Charts"):
            self.reset_all_charts()
        
        if st.sidebar.button("💾 Save Configuration"):
            st.sidebar.success("Configuration saved!")
        
        if st.sidebar.button("📤 Export Data"):
            st.sidebar.info("Data export feature coming soon!")
    
    def calculate_overall_margin(self):
        """Calculate overall margin percentage"""
        active_charts = [chart for chart in st.session_state.charts.values() if chart.is_enabled]
        
        if active_charts:
            avg_margin = sum(chart.margin_percentage for chart in active_charts) / len(active_charts)
            st.session_state.overall_margin_percentage = avg_margin
            
            # Calculate total P&L
            total_pnl = sum(chart.daily_pnl for chart in active_charts)
            st.session_state.daily_pnl = total_pnl
        else:
            st.session_state.overall_margin_percentage = 100.0
            st.session_state.daily_pnl = 0.0
    
    def emergency_stop(self):
        """Harrison's emergency stop function"""
        st.session_state.emergency_stop = True
        st.session_state.system_active = False
        
        # Disable all charts
        for chart in st.session_state.charts.values():
            chart.is_enabled = False
            chart.position_size = 0.0
            chart.signal_strength = "STOPPED"
        
        st.error("🚨 EMERGENCY STOP ACTIVATED!")
        st.balloons()
        st.rerun()
    
    def refresh_data(self):
        """Refresh all chart data with simulated updates"""
        import random
        
        for chart in st.session_state.charts.values():
            if chart.is_enabled:
                # Simulate margin changes
                change = random.uniform(-2.0, 2.0)
                chart.margin_percentage = max(20, min(95, chart.margin_percentage + change))
                
                # Simulate P&L changes
                pnl_change = random.uniform(-50, 50)
                chart.daily_pnl += pnl_change
                
                # Simulate power score
                chart.power_score = random.randint(0, 100)
                
                # Update signal
                signals = ["None", "Bullish", "Bearish", "Neutral"]
                chart.signal_strength = random.choice(signals)
                
                # Update timestamp
                chart.last_update = datetime.now()
        
        st.success("📊 All charts refreshed!")
        st.rerun()
    
    def reset_all_charts(self):
        """Reset all charts to default state"""
        st.session_state.charts = self.create_default_charts()
        st.session_state.overall_margin_percentage = 75.0
        st.session_state.daily_pnl = 0.0
        st.success("🔄 All charts reset to default!")
    
    def render_performance_summary(self):
        """Harrison's performance summary section"""
        st.markdown("## 📈 Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            win_rate = 68.5
            st.metric("Win Rate", f"{win_rate}%", delta="↗️")
        
        with col2:
            profit_factor = 1.45
            st.metric("Profit Factor", f"{profit_factor:.2f}", delta="Good")
        
        with col3:
            max_drawdown = 4.2
            st.metric("Max Drawdown", f"{max_drawdown}%", delta="Low")
        
        with col4:
            total_trades = 142
            st.metric("Total Trades", f"{total_trades}", delta="+12 today")
    
    def run(self):
        """Main dashboard run method"""
        # Render all components in Harrison's preferred order
        self.render_header()
        
        st.divider()
        
        self.render_overall_margin()
        
        st.divider()
        
        self.render_chart_grid()
        
        st.divider()
        
        self.render_controls()
        
        st.divider()
        
        self.render_performance_summary()
        
        # Sidebar
        self.render_sidebar()
        
        # Auto-refresh if system is active
        if st.session_state.system_active and not st.session_state.emergency_stop:
            time.sleep(0.1)
            st.rerun()

def main():
    """Main entry point"""
    dashboard = HarrisonOriginalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
