"""
🎯 6-CHART TRADING CONTROL PANEL
Universal Streamlit-based visual control system for multi-chart trading
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
import asyncio
import threading

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
    power_score: int
    confluence_level: str
    signal_color: str
    last_update: datetime

@dataclass
class SystemStatus:
    """Overall system status"""
    total_margin_remaining: float
    total_margin_percentage: float
    total_equity: float
    daily_profit_loss: float
    active_charts: int
    violation_alerts: List[str]
    emergency_stop_active: bool
    safety_ratio: float
    system_health: str

class StreamlitTradingDashboard:
    """
    Universal 6-Chart Trading Dashboard
    Streamlit-based visual control system
    """
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        self.setup_logging()
        
    def setup_page_config(self):
        """Configure Streamlit page"""
        # Only set page config if not already set
        try:
            st.set_page_config(
                page_title="6-Chart Trading Control Panel",
                page_icon="🎯",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except:
            pass  # Page config already set by main app
        
        # Custom CSS
        st.markdown("""
        <style>
        .main > div {
            padding: 1rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        }
        .safe-status {
            background-color: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
        .warning-status {
            background-color: #ffc107;
            color: black;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
        .danger-status {
            background-color: #dc3545;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
        .chart-box {
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .chart-box-safe {
            border-color: #28a745;
            background-color: #d4edda;
        }
        .chart-box-warning {
            border-color: #ffc107;
            background-color: #fff3cd;
        }
        .chart-box-danger {
            border-color: #dc3545;
            background-color: #f8d7da;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'charts_data' not in st.session_state:
            st.session_state.charts_data = self.create_default_charts()
        
        if 'system_status' not in st.session_state:
            st.session_state.system_status = SystemStatus(
                total_margin_remaining=0.0,
                total_margin_percentage=100.0,
                total_equity=0.0,
                daily_profit_loss=0.0,
                active_charts=0,
                violation_alerts=[],
                emergency_stop_active=False,
                safety_ratio=25.0,
                system_health="HEALTHY"
            )
        
        if 'user_config' not in st.session_state:
            st.session_state.user_config = {
                "trader_name": "Trader",
                "account_type": "Apex Trader Funding",
                "chart_layout": "2x3",
                "risk_management": "Conservative"
            }
        
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
    
    def create_default_charts(self) -> Dict[int, ChartStatus]:
        """Create default chart configurations"""
        default_charts = {
            1: ChartStatus(1, "ES-Primary", 25000, 0, 5000, 20000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            2: ChartStatus(2, "ES-Secondary", 50000, 0, 10000, 40000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            3: ChartStatus(3, "NQ-Primary", 25000, 0, 5000, 20000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            4: ChartStatus(4, "NQ-Secondary", 50000, 0, 10000, 40000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            5: ChartStatus(5, "YM-Primary", 25000, 0, 5000, 20000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            6: ChartStatus(6, "RTY-Primary", 25000, 0, 5000, 20000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now())
        }
        return default_charts
    
    def render_header(self):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title("🎯 6-Chart Trading Control Panel")
            st.markdown(f"**{st.session_state.user_config['trader_name']}'s {st.session_state.user_config['account_type']} Dashboard**")
    
    def render_overall_margin_indicator(self):
        """Render the most important indicator - Overall Margin"""
        st.markdown("### 📊 OVERALL MARGIN REMAINING (MOST IMPORTANT)")
        
        # Calculate overall margin
        self.calculate_overall_margin()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            percentage = st.session_state.system_status.total_margin_percentage
            st.metric(
                label="Margin Percentage",
                value=f"{percentage:.1f}%",
                delta=f"{'Safe' if percentage > 70 else 'Warning' if percentage > 40 else 'Danger'}"
            )
        
        with col2:
            remaining = st.session_state.system_status.total_margin_remaining
            st.metric(
                label="Margin Remaining",
                value=f"${remaining:,.0f}",
                delta=f"${st.session_state.system_status.daily_profit_loss:,.2f} today"
            )
        
        with col3:
            equity = st.session_state.system_status.total_equity
            st.metric(
                label="Total Equity",
                value=f"${equity:,.0f}",
                delta=f"{st.session_state.system_status.active_charts} active charts"
            )
        
        with col4:
            health = st.session_state.system_status.system_health
            health_color = "safe-status" if health == "HEALTHY" else "warning-status" if health == "WARNING" else "danger-status"
            st.markdown(f'<div class="{health_color}">{health}</div>', unsafe_allow_html=True)
        
        # Overall margin status bar
        percentage = st.session_state.system_status.total_margin_percentage
        if percentage >= 70:
            color = "#28a745"
            status = "SAFE TRADING"
        elif percentage >= 40:
            color = "#ffc107"
            status = "CAUTION"
        else:
            color = "#dc3545"
            status = "DANGER - STOP TRADING"
        
        st.markdown(f"""
        <div style="background-color: {color}; color: {'white' if percentage < 40 else 'black'}; 
                    padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin: 10px 0;">
            {status} - {percentage:.1f}% MARGIN REMAINING
        </div>
        """, unsafe_allow_html=True)
    
    def render_chart_grid(self):
        """Render 6-chart grid with status boxes"""
        st.markdown("### 📊 Individual Chart Controls")
        
        # Create 2 rows of 3 charts each
        row1_cols = st.columns(3)
        row2_cols = st.columns(3)
        
        chart_columns = row1_cols + row2_cols
        
        for i, (chart_id, chart_data) in enumerate(st.session_state.charts_data.items()):
            with chart_columns[i]:
                self.render_individual_chart(chart_id, chart_data)
    
    def render_individual_chart(self, chart_id: int, chart_data: ChartStatus):
        """Render individual chart control box"""
        # Determine status styling
        if chart_data.margin_percentage >= 70:
            box_class = "chart-box-safe"
            status_text = "🟢 SAFE TRADING"
        elif chart_data.margin_percentage >= 40:
            box_class = "chart-box-warning"
            status_text = "🟡 MARGINAL"
        else:
            box_class = "chart-box-danger"
            status_text = "🔴 NO TRADE"
        
        # Chart container
        with st.container():
            st.markdown(f'<div class="chart-box {box_class}">', unsafe_allow_html=True)
            
            # Chart header with toggle
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**{chart_data.account_name}**")
            with col2:
                chart_data.is_active = st.checkbox("ON", value=chart_data.is_active, key=f"chart_{chart_id}_toggle")
            
            # Status display
            st.markdown(f"**{status_text}**")
            
            # Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Margin %", f"{chart_data.margin_percentage:.1f}%")
                st.metric("Balance", f"${chart_data.account_balance:,.0f}")
            with col2:
                st.metric("Remaining", f"${chart_data.margin_remaining:,.0f}")
                pnl_delta = "⬆️" if chart_data.daily_pnl >= 0 else "⬇️"
                st.metric("Daily P&L", f"${chart_data.daily_pnl:,.2f}", delta=pnl_delta)
            
            # Signal information
            if chart_data.power_score > 0:
                st.markdown(f"**Power Score:** {chart_data.power_score}%")
            if chart_data.confluence_level != "L0":
                st.markdown(f"**Confluence:** {chart_data.confluence_level}")
            if chart_data.last_signal != "NONE":
                st.markdown(f"**Signal:** {chart_data.last_signal}")
            
            # Positions
            if chart_data.open_positions > 0:
                st.markdown(f"**Open Positions:** {chart_data.open_positions}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_control_buttons(self):
        """Render main control buttons"""
        st.markdown("### 🎮 System Controls")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True, key="dash_emergency_stop"):
                self.emergency_stop_all()
        
        with col2:
            if st.button("⏸️ PAUSE ALL", use_container_width=True, key="dash_pause_all"):
                self.pause_all_charts()
        
        with col3:
            if st.button("▶️ RESUME ALL", use_container_width=True, key="dash_resume_all"):
                self.resume_all_charts()
        
        with col4:
            monitoring_text = "🛑 STOP MONITORING" if st.session_state.monitoring_active else "🔄 START MONITORING"
            if st.button(monitoring_text, use_container_width=True, key="dash_toggle_monitoring"):
                self.toggle_monitoring()
        
        with col5:
            if st.button("📊 REFRESH DATA", use_container_width=True, key="dash_refresh_data"):
                self.refresh_all_data()
    
    def render_sidebar_settings(self):
        """Render sidebar configuration"""
        st.sidebar.title("⚙️ Configuration")
        
        # User settings
        st.sidebar.markdown("### 👤 User Settings")
        st.session_state.user_config["trader_name"] = st.sidebar.text_input(
            "Trader Name", 
            value=st.session_state.user_config["trader_name"],
            key="dashboard_trader_name"
        )
        
        st.session_state.user_config["account_type"] = st.sidebar.selectbox(
            "Account Type",
            ["Apex Trader Funding", "FTMO", "MyForexFunds", "TopStep", "The5%ers", "Other"],
            index=0,
            key="dashboard_account_type"
        )
        
        st.session_state.user_config["chart_layout"] = st.sidebar.selectbox(
            "Chart Layout",
            ["2x3", "3x2", "1x6"],
            index=0,
            key="dashboard_chart_layout"
        )
        
        st.session_state.user_config["risk_management"] = st.sidebar.selectbox(
            "Risk Management",
            ["Conservative", "Moderate", "Aggressive"],
            index=0,
            key="dashboard_risk_management"
        )
import threading

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
    power_score: int
    confluence_level: str
    signal_color: str
    last_update: datetime

@dataclass
class SystemStatus:
    """Overall system status"""
    total_margin_remaining: float
    total_margin_percentage: float
    total_equity: float
    daily_profit_loss: float
    active_charts: int
    violation_alerts: List[str]
    emergency_stop_active: bool
    safety_ratio: float
    system_health: str

class StreamlitTradingDashboard:
    """
    Universal 6-Chart Trading Dashboard
    Streamlit-based visual control system
    """
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        self.setup_logging()
        
    def setup_page_config(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="6-Chart Trading Control Panel",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main > div {
            padding: 1rem;
        }
        .stMetric {
            background-color: #f0f2f6;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
        }
        .safe-status {
            background-color: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
        .warning-status {
            background-color: #ffc107;
            color: black;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
        .danger-status {
            background-color: #dc3545;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
        .chart-box {
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .chart-box-safe {
            border-color: #28a745;
            background-color: #d4edda;
        }
        .chart-box-warning {
            border-color: #ffc107;
            background-color: #fff3cd;
        }
        .chart-box-danger {
            border-color: #dc3545;
            background-color: #f8d7da;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'charts_data' not in st.session_state:
            st.session_state.charts_data = self.create_default_charts()
        
        if 'system_status' not in st.session_state:
            st.session_state.system_status = SystemStatus(
                total_margin_remaining=0.0,
                total_margin_percentage=100.0,
                total_equity=0.0,
                daily_profit_loss=0.0,
                active_charts=0,
                violation_alerts=[],
                emergency_stop_active=False,
                safety_ratio=25.0,
                system_health="HEALTHY"
            )
        
        if 'user_config' not in st.session_state:
            st.session_state.user_config = {
                "trader_name": "Trader",
                "account_type": "Apex Trader Funding",
                "chart_layout": "2x3",
                "risk_management": "Conservative"
            }
        
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
    
    def create_default_charts(self) -> Dict[int, ChartStatus]:
        """Create default chart configurations"""
        default_charts = {
            1: ChartStatus(1, "ES-Primary", 25000, 0, 5000, 20000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            2: ChartStatus(2, "ES-Secondary", 50000, 0, 10000, 40000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            3: ChartStatus(3, "NQ-Primary", 25000, 0, 5000, 20000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            4: ChartStatus(4, "NQ-Secondary", 50000, 0, 10000, 40000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            5: ChartStatus(5, "YM-Primary", 25000, 0, 5000, 20000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now()),
            6: ChartStatus(6, "RTY-Primary", 25000, 0, 5000, 20000, 80.0, 0, True, "SAFE", "NONE", 0, "L0", "NONE", datetime.now())
        }
        return default_charts
    
    def render_header(self):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title("🎯 6-Chart Trading Control Panel")
            st.markdown(f"**{st.session_state.user_config['trader_name']}'s {st.session_state.user_config['account_type']} Dashboard**")
    
    def render_overall_margin_indicator(self):
        """Render the most important indicator - Overall Margin"""
        st.markdown("### 📊 OVERALL MARGIN REMAINING (MOST IMPORTANT)")
        
        # Calculate overall margin
        self.calculate_overall_margin()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            percentage = st.session_state.system_status.total_margin_percentage
            st.metric(
                label="Margin Percentage",
                value=f"{percentage:.1f}%",
                delta=f"{'Safe' if percentage > 70 else 'Warning' if percentage > 40 else 'Danger'}"
            )
        
        with col2:
            remaining = st.session_state.system_status.total_margin_remaining
            st.metric(
                label="Margin Remaining",
                value=f"${remaining:,.0f}",
                delta=f"${st.session_state.system_status.daily_profit_loss:,.2f} today"
            )
        
        with col3:
            equity = st.session_state.system_status.total_equity
            st.metric(
                label="Total Equity",
                value=f"${equity:,.0f}",
                delta=f"{st.session_state.system_status.active_charts} active charts"
            )
        
        with col4:
            health = st.session_state.system_status.system_health
            health_color = "safe-status" if health == "HEALTHY" else "warning-status" if health == "WARNING" else "danger-status"
            st.markdown(f'<div class="{health_color}">{health}</div>', unsafe_allow_html=True)
        
        # Overall margin status bar
        percentage = st.session_state.system_status.total_margin_percentage
        if percentage >= 70:
            color = "#28a745"
            status = "SAFE TRADING"
        elif percentage >= 40:
            color = "#ffc107"
            status = "CAUTION"
        else:
            color = "#dc3545"
            status = "DANGER - STOP TRADING"
        
        st.markdown(f"""
        <div style="background-color: {color}; color: {'white' if percentage < 40 else 'black'}; 
                    padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; font-weight: bold; margin: 10px 0;">
            {status} - {percentage:.1f}% MARGIN REMAINING
        </div>
        """, unsafe_allow_html=True)
    
    def render_chart_grid(self):
        """Render 6-chart grid with status boxes"""
        st.markdown("### 📊 Individual Chart Controls")
        
        # Create 2 rows of 3 charts each
        row1_cols = st.columns(3)
        row2_cols = st.columns(3)
        
        chart_columns = row1_cols + row2_cols
        
        for i, (chart_id, chart_data) in enumerate(st.session_state.charts_data.items()):
            with chart_columns[i]:
                self.render_individual_chart(chart_id, chart_data)
    
    def render_individual_chart(self, chart_id: int, chart_data: ChartStatus):
        """Render individual chart control box"""
        # Determine status styling
        if chart_data.margin_percentage >= 70:
            box_class = "chart-box-safe"
            status_text = "🟢 SAFE TRADING"
        elif chart_data.margin_percentage >= 40:
            box_class = "chart-box-warning"
            status_text = "🟡 MARGINAL"
        else:
            box_class = "chart-box-danger"
            status_text = "🔴 NO TRADE"
        
        # Chart container
        with st.container():
            st.markdown(f'<div class="chart-box {box_class}">', unsafe_allow_html=True)
            
            # Chart header with toggle
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**{chart_data.account_name}**")
            with col2:
                chart_data.is_active = st.checkbox("ON", value=chart_data.is_active, key=f"chart_{chart_id}_toggle")
            
            # Status display
            st.markdown(f"**{status_text}**")
            
            # Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Margin %", f"{chart_data.margin_percentage:.1f}%")
                st.metric("Balance", f"${chart_data.account_balance:,.0f}")
            with col2:
                st.metric("Remaining", f"${chart_data.margin_remaining:,.0f}")
                pnl_delta = "⬆️" if chart_data.daily_pnl >= 0 else "⬇️"
                st.metric("Daily P&L", f"${chart_data.daily_pnl:,.2f}", delta=pnl_delta)
            
            # Signal information
            if chart_data.power_score > 0:
                st.markdown(f"**Power Score:** {chart_data.power_score}%")
            if chart_data.confluence_level != "L0":
                st.markdown(f"**Confluence:** {chart_data.confluence_level}")
            if chart_data.last_signal != "NONE":
                st.markdown(f"**Signal:** {chart_data.last_signal}")
            
            # Positions
            if chart_data.open_positions > 0:
                st.markdown(f"**Open Positions:** {chart_data.open_positions}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_control_buttons(self):
        """Render main control buttons"""
        st.markdown("### 🎮 System Controls")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
                self.emergency_stop_all()
        
        with col2:
            if st.button("⏸️ PAUSE ALL", use_container_width=True):
                self.pause_all_charts()
        
        with col3:
            if st.button("▶️ RESUME ALL", use_container_width=True):
                self.resume_all_charts()
        
        with col4:
            monitoring_text = "🛑 STOP MONITORING" if st.session_state.monitoring_active else "🔄 START MONITORING"
            if st.button(monitoring_text, use_container_width=True):
                self.toggle_monitoring()
        
        with col5:
            if st.button("📊 REFRESH DATA", use_container_width=True):
                self.refresh_all_data()
    
    def render_sidebar_settings(self):
        """Render sidebar configuration"""
        st.sidebar.title("⚙️ Configuration")
        
        # User settings
        st.sidebar.markdown("### 👤 User Settings")
        st.session_state.user_config["trader_name"] = st.sidebar.text_input(
            "Trader Name", 
            value=st.session_state.user_config["trader_name"]
        )
        
        st.session_state.user_config["account_type"] = st.sidebar.selectbox(
            "Account Type",
            ["Apex Trader Funding", "FTMO", "MyForexFunds", "TopStep", "Other"],
            index=0
        )
        
        # System settings
        st.sidebar.markdown("### ⚙️ System Settings")
        st.session_state.system_status.safety_ratio = st.sidebar.slider(
            "Safety Ratio (%)", 
            min_value=5, 
            max_value=90, 
            value=int(st.session_state.system_status.safety_ratio),
            help="Conservative position sizing multiplier"
        )
        
        # Chart layout
        layout = st.sidebar.selectbox(
            "Chart Layout",
            ["2x3 (6 charts)", "1x6 (6 charts)", "3x2 (6 charts)"],
            index=0,
            key="dashboard_chart_layout"
        )
        
        # Risk management
        risk_mode = st.sidebar.selectbox(
            "Risk Management",
            ["Conservative", "Moderate", "Aggressive"],
            index=0,
            key="dashboard_risk_mode"
        )
        
        # Emergency controls
        st.sidebar.markdown("### 🚨 Emergency Controls")
        if st.sidebar.button("🛑 EMERGENCY STOP ALL", type="primary", key="dashboard_emergency_stop"):
            self.emergency_stop_all()
        
        if st.session_state.system_status.emergency_stop_active:
            if st.sidebar.button("🔄 RESET EMERGENCY STOP", key="dashboard_reset_emergency"):
                self.reset_emergency_stop()
        
        # Status information
        st.sidebar.markdown("### 📊 System Status")
        st.sidebar.write(f"Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}")
        st.sidebar.write(f"Active Charts: {st.session_state.system_status.active_charts}")
        st.sidebar.write(f"System Health: {st.session_state.system_status.system_health}")
        
        # Violation alerts
        if st.session_state.system_status.violation_alerts:
            st.sidebar.markdown("### ⚠️ Alerts")
            for alert in st.session_state.system_status.violation_alerts[-5:]:  # Show last 5
                st.sidebar.warning(alert)
    
    def render_performance_charts(self):
        """Render performance visualization charts"""
        if st.checkbox("📈 Show Performance Charts", value=False):
            st.markdown("### 📈 Performance Analytics")
            
            # Create sample data for charts
            dates = pd.date_range(start=datetime.now()-timedelta(days=30), end=datetime.now(), freq='D')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Equity curve
                equity_data = []
                base_equity = 150000
                for i, date in enumerate(dates):
                    equity_data.append({
                        'Date': date,
                        'Equity': base_equity + np.random.cumsum(np.random.normal(50, 200))[0]
                    })
                
                equity_df = pd.DataFrame(equity_data)
                fig_equity = px.line(equity_df, x='Date', y='Equity', title='Portfolio Equity Curve')
                st.plotly_chart(fig_equity, use_container_width=True)
            
            with col2:
                # Daily P&L
                pnl_data = []
                for date in dates[-14:]:  # Last 14 days
                    pnl_data.append({
                        'Date': date.strftime('%m-%d'),
                        'PnL': np.random.normal(100, 300)
                    })
                
                pnl_df = pd.DataFrame(pnl_data)
                fig_pnl = px.bar(pnl_df, x='Date', y='PnL', title='Daily P&L (Last 14 Days)',
                               color='PnL', color_continuous_scale=['red', 'yellow', 'green'])
                st.plotly_chart(fig_pnl, use_container_width=True)
            
            # Chart-by-chart performance
            st.markdown("#### Individual Chart Performance")
            chart_performance = []
            for chart_id, chart_data in st.session_state.charts_data.items():
                chart_performance.append({
                    'Chart': chart_data.account_name,
                    'Daily P&L': chart_data.daily_pnl,
                    'Margin Used %': (chart_data.margin_used / chart_data.account_balance) * 100,
                    'Status': chart_data.risk_level
                })
            
            perf_df = pd.DataFrame(chart_performance)
            st.dataframe(perf_df, use_container_width=True)
    
    def calculate_overall_margin(self):
        """Calculate overall system margin status"""
        active_charts = [chart for chart in st.session_state.charts_data.values() if chart.is_active]
        
        if not active_charts:
            st.session_state.system_status.total_equity = 0
            st.session_state.system_status.total_margin_remaining = 0
            st.session_state.system_status.total_margin_percentage = 0
            st.session_state.system_status.active_charts = 0
            return
        
        total_equity = sum(chart.account_balance for chart in active_charts)
        total_remaining = sum(chart.margin_remaining for chart in active_charts)
        total_pnl = sum(chart.daily_pnl for chart in active_charts)
        
        percentage = (total_remaining / total_equity * 100) if total_equity > 0 else 0
        
        st.session_state.system_status.total_equity = total_equity
        st.session_state.system_status.total_margin_remaining = total_remaining
        st.session_state.system_status.total_margin_percentage = percentage
        st.session_state.system_status.daily_profit_loss = total_pnl
        st.session_state.system_status.active_charts = len(active_charts)
        
        # Determine system health
        if percentage >= 70:
            st.session_state.system_status.system_health = "HEALTHY"
        elif percentage >= 40:
            st.session_state.system_status.system_health = "WARNING"
        else:
            st.session_state.system_status.system_health = "DANGER"
    
    def emergency_stop_all(self):
        """Emergency stop all trading"""
        st.session_state.system_status.emergency_stop_active = True
        
        for chart_data in st.session_state.charts_data.values():
            chart_data.is_active = False
            chart_data.open_positions = 0
            chart_data.last_signal = "STOPPED"
        
        st.session_state.system_status.violation_alerts.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] EMERGENCY STOP ACTIVATED - ALL TRADING HALTED"
        )
        
        st.error("🛑 EMERGENCY STOP ACTIVATED - ALL TRADING HALTED")
        st.balloons()  # Visual feedback
    
    def reset_emergency_stop(self):
        """Reset emergency stop"""
        st.session_state.system_status.emergency_stop_active = False
        
        for chart_data in st.session_state.charts_data.values():
            chart_data.is_active = True
            chart_data.last_signal = "NONE"
        
        st.session_state.system_status.violation_alerts.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Emergency stop reset - System ready"
        )
        
        st.success("🔄 Emergency stop reset - System ready")
    
    def pause_all_charts(self):
        """Pause all chart monitoring"""
        for chart_data in st.session_state.charts_data.values():
            chart_data.is_active = False
        
        st.session_state.monitoring_active = False
        st.info("⏸️ All charts paused")
    
    def resume_all_charts(self):
        """Resume all chart monitoring"""
        if not st.session_state.system_status.emergency_stop_active:
            for chart_data in st.session_state.charts_data.values():
                chart_data.is_active = True
            
            st.session_state.monitoring_active = True
            st.success("▶️ All charts resumed")
        else:
            st.error("Cannot resume - Emergency stop is active")
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        st.session_state.monitoring_active = not st.session_state.monitoring_active
        status = "started" if st.session_state.monitoring_active else "stopped"
        st.info(f"🔄 Monitoring {status}")
    
    def refresh_all_data(self):
        """Refresh all chart data (simulate real data)"""
        import random
        
        for chart_data in st.session_state.charts_data.values():
            if chart_data.is_active:
                # Simulate margin changes
                change = random.uniform(-2, 2)
                chart_data.margin_percentage = max(10, min(95, chart_data.margin_percentage + change))
                chart_data.margin_remaining = chart_data.account_balance * (chart_data.margin_percentage / 100)
                
                # Simulate P&L changes
                pnl_change = random.uniform(-100, 100)
                chart_data.daily_pnl += pnl_change
                
                # Simulate signals
                chart_data.power_score = random.randint(0, 100)
                chart_data.confluence_level = random.choice(["L0", "L1", "L2", "L3", "L4"])
                chart_data.signal_color = random.choice(["NONE", "GREEN", "RED", "BLUE"])
                chart_data.last_signal = random.choice(["NONE", "BULLISH", "BEARISH", "CONFLUENCE"])
                
                chart_data.last_update = datetime.now()
        
        st.session_state.last_update = datetime.now()
        st.success("📊 Data refreshed")
    
    def run(self):
        """Main dashboard rendering method"""
        # Auto-refresh every 5 seconds if monitoring is active
        if st.session_state.monitoring_active:
            placeholder = st.empty()
            
            # Auto-refresh logic would go here
            # For now, just show a status
            st.info("🔄 Live monitoring active - Data updates automatically")
        
        # Render all dashboard components
        self.render_header()
        self.render_overall_margin_indicator()
        self.render_chart_grid()
        self.render_control_buttons()
        self.render_sidebar_settings()
        self.render_performance_charts()
        
        # Footer
        st.markdown("---")
        st.markdown("🎯 **Universal 6-Chart Trading Control Panel** | Built with Streamlit")

def main():
    """Main entry point"""
    dashboard = StreamlitTradingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
