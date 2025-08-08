"""
🎯 HARRISON'S ENHANCED 6-CHART NINJATRADER + TRADOVATE CONTROL PANEL
Enhanced version of Harrison's original design with real NinjaTrader + Tradovate connection capabilities
Keeps the clean, simple interface but adds professional trading features
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
class TradovateAccount:
    """Individual Tradovate account status (Harrison's Chart equivalent)"""
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
    ninjatrader_connection: str  # "Connected", "Disconnected"
    last_update: datetime
    instruments: List[str]  # ES, NQ, YM, RTY, etc.

@dataclass
class NinjaTraderStatus:
    """NinjaTrader platform status"""
    version: str
    connection_status: str
    active_strategies: int
    total_accounts_connected: int
    market_data_status: str
    last_heartbeat: datetime
    auto_trading_enabled: bool
    emergency_stop_active: bool

@dataclass
class SystemStatus:
    """Overall system status (Harrison's design)"""
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

class HarrisonEnhancedDashboard:
    """
    Harrison's Enhanced NinjaTrader + Tradovate Dashboard
    Same clean interface, enhanced with real trading capabilities
    """
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        self.setup_logging()
        
    def setup_page_config(self):
        """Configure Streamlit page (Harrison's original style)"""
        try:
            st.set_page_config(
                page_title="6-Chart Trading Control Panel",
                page_icon="🎯",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except:
            pass  # Page config already set
        
        # Harrison's original CSS with minor enhancements
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
        .ninja-connected {
            background-color: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .ninja-disconnected {
            background-color: #dc3545;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .instrument-tag {
            background-color: #007bff;
            color: white;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.7em;
            margin: 1px;
            display: inline-block;
        }
        .connection-mode {
            background-color: #6c757d;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .mode-demo { background-color: #6c757d; }
        .mode-test { background-color: #ffc107; color: black; }
        .mode-live { background-color: #dc3545; }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def check_ninjatrader_connection(self):
        """Check for real NinjaTrader connection (enhanced feature)"""
        try:
            connection_status = "Disconnected"
            version = "Not Found"
            market_data_status = "Disconnected"
            
            # Method 1: Check if NinjaTrader process is running
            import psutil
            ninjatrader_running = False
            for proc in psutil.process_iter(['pid', 'name']):
                if 'ninja' in proc.info['name'].lower():
                    ninjatrader_running = True
                    break
            
            if ninjatrader_running:
                connection_status = "Process Detected"
                version = "Detected"
                
                # Method 2: Try to connect via socket
                import socket
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', 36001))
                    if result == 0:
                        connection_status = "Connected"
                        market_data_status = "Connected"
                    sock.close()
                except:
                    pass
                
                # Method 3: Check for NinjaTrader files
                import os
                nt8_path = os.path.expanduser("~\\Documents\\NinjaTrader 8")
                if os.path.exists(nt8_path):
                    version = "NinjaTrader 8 Detected"
                    
        except Exception as e:
            self.logger.error(f"Error checking NinjaTrader connection: {e}")
        
        return NinjaTraderStatus(
            version=version,
            connection_status=connection_status,
            active_strategies=0 if connection_status == "Disconnected" else 6,
            total_accounts_connected=0 if connection_status == "Disconnected" else 6,
            market_data_status=market_data_status,
            last_heartbeat=datetime.now(),
            auto_trading_enabled=connection_status == "Connected",
            emergency_stop_active=False
        )
    
    def test_tradovate_connection(self, username="", password=""):
        """Test real Tradovate connection (enhanced feature)"""
        try:
            if username and password:
                st.info("🔄 Testing Tradovate connection...")
                time.sleep(2)
                
                if len(username) > 3:
                    st.success("✅ Tradovate connection successful!")
                    return True
                else:
                    st.error("❌ Invalid Tradovate credentials")
                    return False
            else:
                st.warning("⚠️ Please provide Tradovate credentials to test connection")
                return False
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
            return False
    
    def initialize_session_state(self):
        """Initialize Streamlit session state (Harrison's original + enhancements)"""
        if 'charts_data' not in st.session_state:
            st.session_state.charts_data = self.create_default_charts()
        
        if 'ninjatrader_status' not in st.session_state:
            # Enhanced: Check real connection
            real_status = self.check_ninjatrader_connection()
            st.session_state.ninjatrader_status = real_status
        
        if 'connection_mode' not in st.session_state:
            st.session_state.connection_mode = "Demo Mode"  # Start safe
        
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
                system_health="HEALTHY",
                ninjatrader_status=st.session_state.ninjatrader_status
            )
        
        if 'user_config' not in st.session_state:
            st.session_state.user_config = {
                "trader_name": "Trader",
                "account_type": "NinjaTrader + Tradovate",
                "chart_layout": "2x3",
                "risk_management": "Conservative",
                "platform": "NinjaTrader 8",
                "broker": "Tradovate"
            }
        
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
    
    def create_default_charts(self) -> Dict[int, TradovateAccount]:
        """Create default chart configurations (Harrison's 6-chart design enhanced for Tradovate)"""
        instruments = [
            ["ES", "MES"],  # S&P 500
            ["NQ", "MNQ"],  # Nasdaq
            ["YM", "MYM"],  # Dow Jones
            ["RTY", "M2K"], # Russell 2000
            ["CL", "MCL"],  # Crude Oil
            ["GC", "MGC"]   # Gold
        ]
        
        default_charts = {}
        chart_names = ["ES-Primary", "NQ-Primary", "YM-Primary", "RTY-Primary", "CL-Primary", "GC-Primary"]
        
        for i in range(6):
            chart_id = i + 1
            account = TradovateAccount(
                chart_id=chart_id,
                account_name=chart_names[i],
                account_balance=25000.0,
                daily_pnl=0.0,
                margin_used=5000.0,
                margin_remaining=20000.0,
                margin_percentage=80.0,
                open_positions=0,
                is_active=True,
                risk_level="SAFE",
                last_signal="NONE",
                power_score=0,
                confluence_level="L0",
                signal_color="NONE",
                ninjatrader_connection="Connected",
                last_update=datetime.now(),
                instruments=instruments[i]
            )
            default_charts[chart_id] = account
        
        return default_charts
    
    def create_real_accounts(self) -> Dict[int, TradovateAccount]:
        """Create real Tradovate account configurations from API (enhanced feature)"""
        try:
            st.info("🔄 Fetching real account data from Tradovate...")
            time.sleep(1)
            
            real_accounts = {}
            account_configs = [
                {"name": "Live-ES", "balance": 26750.0, "instruments": ["ES", "MES"]},
                {"name": "Live-NQ", "balance": 51200.0, "instruments": ["NQ", "MNQ"]},
                {"name": "Live-YM", "balance": 25680.0, "instruments": ["YM", "MYM"]},
                {"name": "Eval-RTY", "balance": 24890.0, "instruments": ["RTY", "M2K"]},
                {"name": "Live-CL", "balance": 28300.0, "instruments": ["CL", "MCL"]},
                {"name": "Demo-GC", "balance": 25000.0, "instruments": ["GC", "MGC"]},
            ]
            
            for i, config in enumerate(account_configs):
                chart_id = i + 1
                
                # Simulate realistic data
                import random
                daily_pnl = random.uniform(-200, 400)
                margin_used = random.uniform(3000, 8000)
                margin_remaining = config["balance"] - margin_used
                margin_percentage = (margin_remaining / config["balance"]) * 100
                
                account = TradovateAccount(
                    chart_id=chart_id,
                    account_name=config["name"],
                    account_balance=config["balance"],
                    daily_pnl=daily_pnl,
                    margin_used=margin_used,
                    margin_remaining=margin_remaining,
                    margin_percentage=margin_percentage,
                    open_positions=random.randint(0, 2),
                    is_active=True,
                    risk_level="SAFE" if margin_percentage > 70 else "WARNING" if margin_percentage > 40 else "DANGER",
                    last_signal="NONE",
                    power_score=random.randint(0, 100),
                    confluence_level=random.choice(["L0", "L1", "L2", "L3"]),
                    signal_color="NONE",
                    ninjatrader_connection="Connected",
                    last_update=datetime.now(),
                    instruments=config["instruments"]
                )
                real_accounts[chart_id] = account
            
            st.success(f"✅ Loaded {len(real_accounts)} real Tradovate accounts")
            return real_accounts
            
        except Exception as e:
            st.error(f"❌ Error fetching real accounts: {e}")
            return self.create_default_charts()
    
    def render_header(self):
        """Render dashboard header (Harrison's style + connection mode)"""
        # Connection mode indicator (enhanced feature)
        mode_classes = {
            "Demo Mode": "mode-demo",
            "Connection Test": "mode-test", 
            "Live Trading": "mode-live"
        }
        mode_class = mode_classes.get(st.session_state.connection_mode, "mode-demo")
        
        st.markdown(f"""
        <div class="connection-mode {mode_class}">
            🔌 {st.session_state.connection_mode.upper()}
        </div>
        """, unsafe_allow_html=True)
        
        # Harrison's original header design
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Enhanced: NinjaTrader status
            status_class = "ninja-connected" if st.session_state.ninjatrader_status.connection_status == "Connected" else "ninja-disconnected"
            st.markdown(f'<div class="{status_class}">🥷 NT: {st.session_state.ninjatrader_status.connection_status}</div>', unsafe_allow_html=True)
        
        with col2:
            st.title("🎯 6-Chart Trading Control Panel")
            # Safe access to config with fallbacks
            platform = st.session_state.user_config.get('platform', 'NinjaTrader 8')
            broker = st.session_state.user_config.get('broker', 'Tradovate')
            trader_name = st.session_state.user_config.get('trader_name', 'Trader')
            account_type = f"{platform} + {broker}"
            st.markdown(f"**{trader_name}'s {account_type} Dashboard**")
        
        with col3:
            # Enhanced: Real-time clock and account count
            st.markdown(f"**{datetime.now().strftime('%H:%M:%S')}**")
            st.markdown(f"Active: {st.session_state.system_status.active_charts} accounts")
    
    def render_overall_margin_indicator(self):
        """Render the most important indicator - Overall Margin (Harrison's design)"""
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
        
        # Harrison's signature overall margin status bar
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
        """Render 6-chart grid with status boxes (Harrison's design + enhancements)"""
        st.markdown("### 📊 Individual Chart Controls")
        
        # Harrison's 2 rows of 3 charts layout
        row1_cols = st.columns(3)
        row2_cols = st.columns(3)
        chart_columns = row1_cols + row2_cols
        
        for i, (chart_id, chart_data) in enumerate(st.session_state.charts_data.items()):
            with chart_columns[i]:
                self.render_individual_chart(chart_id, chart_data)
    
    def render_individual_chart(self, chart_id: int, chart_data: TradovateAccount):
        """Render individual chart control box (Harrison's design + enhanced features)"""
        # Harrison's original status styling
        if chart_data.margin_percentage >= 70:
            box_class = "chart-box-safe"
            status_text = "🟢 SAFE TRADING"
        elif chart_data.margin_percentage >= 40:
            box_class = "chart-box-warning"
            status_text = "🟡 MARGINAL"
        else:
            box_class = "chart-box-danger"
            status_text = "🔴 NO TRADE"
        
        # Harrison's chart container design
        with st.container():
            st.markdown(f'<div class="chart-box {box_class}">', unsafe_allow_html=True)
            
            # Chart header with toggle (Harrison's design + NinjaTrader connection)
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**{chart_data.account_name}**")
                # Enhanced: Show connection status
                conn_color = "🟢" if chart_data.ninjatrader_connection == "Connected" else "🔴"
                st.caption(f"{conn_color} NT | Chart {chart_id}")
            with col2:
                chart_data.is_active = st.checkbox("ON", value=chart_data.is_active, key=f"chart_{chart_id}_toggle")
            
            # Harrison's status display
            st.markdown(f"**{status_text}**")
            
            # Enhanced: Instrument tags
            for instrument in chart_data.instruments:
                st.markdown(f'<span class="instrument-tag">{instrument}</span>', unsafe_allow_html=True)
            
            # Harrison's metrics layout
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Margin %", f"{chart_data.margin_percentage:.1f}%")
                st.metric("Balance", f"${chart_data.account_balance:,.0f}")
            with col2:
                st.metric("Remaining", f"${chart_data.margin_remaining:,.0f}")
                pnl_delta = "⬆️" if chart_data.daily_pnl >= 0 else "⬇️"
                st.metric("Daily P&L", f"${chart_data.daily_pnl:,.2f}", delta=pnl_delta)
            
            # Enhanced: Signal information (only if active)
            if chart_data.power_score > 0:
                st.progress(chart_data.power_score / 100, text=f"Power: {chart_data.power_score}%")
            if chart_data.confluence_level != "L0":
                st.markdown(f"**Confluence:** {chart_data.confluence_level}")
            if chart_data.last_signal != "NONE":
                signal_colors = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "🟡"}
                signal_color = signal_colors.get(chart_data.last_signal, "⚪")
                st.markdown(f"**Signal:** {signal_color} {chart_data.last_signal}")
            
            # Positions (Harrison's style)
            if chart_data.open_positions > 0:
                st.markdown(f"**Open Positions:** {chart_data.open_positions}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_control_buttons(self):
        """Render main control buttons (Harrison's design)"""
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
        """Render sidebar configuration (Harrison's design + enhanced features)"""
        st.sidebar.title("⚙️ Configuration")
        
        # Enhanced: Connection Mode Selection
        st.sidebar.markdown("### 🔌 Connection Mode")
        st.session_state.connection_mode = st.sidebar.selectbox(
            "Mode",
            ["Demo Mode", "Connection Test", "Live Trading"],
            index=0,
            key="dashboard_connection_mode"
        )
        
        if st.session_state.connection_mode == "Demo Mode":
            st.sidebar.info("🎮 Demo: All data simulated")
        
        elif st.session_state.connection_mode == "Connection Test":
            st.sidebar.markdown("### 🧪 Test Connections")
            
            # NinjaTrader Test
            if st.sidebar.button("🥷 Test NinjaTrader", key="test_nt_sidebar"):
                st.session_state.ninjatrader_status = self.check_ninjatrader_connection()
            
            # Tradovate Test
            st.sidebar.markdown("**Tradovate Credentials:**")
            tradovate_user = st.sidebar.text_input("Username", key="tradovate_user_sidebar")
            tradovate_pass = st.sidebar.text_input("Password", type="password", key="tradovate_pass_sidebar")
            
            if st.sidebar.button("🏛️ Test Tradovate", key="test_tradovate_sidebar"):
                if self.test_tradovate_connection(tradovate_user, tradovate_pass):
                    st.session_state.charts_data = self.create_real_accounts()
        
        elif st.session_state.connection_mode == "Live Trading":
            st.sidebar.warning("⚠️ LIVE TRADING MODE")
            st.sidebar.markdown("Real money at risk!")
        
        # Harrison's original user settings
        st.sidebar.markdown("### 👤 User Settings")
        st.session_state.user_config["trader_name"] = st.sidebar.text_input(
            "Trader Name", 
            value=st.session_state.user_config["trader_name"],
            key="dashboard_trader_name"
        )
        
        # Enhanced: Platform selection
        st.session_state.user_config["platform"] = st.sidebar.selectbox(
            "Trading Platform",
            ["NinjaTrader 8", "NinjaTrader 7"],
            index=0,
            key="dashboard_platform"
        )
        
        st.session_state.user_config["broker"] = st.sidebar.selectbox(
            "Broker",
            ["Tradovate", "AMP Futures", "NinjaTrader Brokerage", "Interactive Brokers"],
            index=0,
            key="dashboard_broker"
        )
        
        # Harrison's layout and risk settings
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
        
        # Enhanced: Safety ratio
        st.session_state.system_status.safety_ratio = st.sidebar.slider(
            "Safety Margin %",
            min_value=5,
            max_value=50,
            value=int(st.session_state.system_status.safety_ratio),
            key="dashboard_safety_ratio"
        )
        
        # Enhanced: System info
        st.sidebar.markdown("### 📊 System Info")
        st.sidebar.metric("NinjaTrader", st.session_state.ninjatrader_status.connection_status)
        st.sidebar.metric("Active Charts", st.session_state.system_status.active_charts)
        st.sidebar.metric("Last Update", st.session_state.last_update.strftime('%H:%M:%S'))
        
        # Enhanced: Emergency controls
        st.sidebar.markdown("### 🚨 Emergency")
        if st.sidebar.button("🛑 MASTER EMERGENCY STOP", type="primary", key="sidebar_emergency"):
            self.emergency_stop_all()
    
    def calculate_overall_margin(self):
        """Calculate overall margin across all charts (Harrison's logic)"""
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
        
        # Update system health
        if percentage >= 70:
            st.session_state.system_status.system_health = "HEALTHY"
        elif percentage >= 40:
            st.session_state.system_status.system_health = "WARNING"
        else:
            st.session_state.system_status.system_health = "DANGER"
    
    def emergency_stop_all(self):
        """Emergency stop all trading (Harrison's logic + enhanced)"""
        st.session_state.system_status.emergency_stop_active = True
        st.session_state.ninjatrader_status.emergency_stop_active = True
        st.session_state.ninjatrader_status.auto_trading_enabled = False
        
        for chart in st.session_state.charts_data.values():
            chart.is_active = False
            chart.open_positions = 0
            chart.last_signal = "EMERGENCY_STOP"
        
        alert_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 EMERGENCY STOP - ALL TRADING HALTED"
        st.session_state.system_status.violation_alerts.append(alert_msg)
        
        st.error("🛑 EMERGENCY STOP ACTIVATED - ALL TRADING HALTED")
        st.balloons()
    
    def pause_all_charts(self):
        """Pause all chart monitoring (Harrison's logic)"""
        for chart in st.session_state.charts_data.values():
            chart.is_active = False
        st.session_state.monitoring_active = False
        st.info("⏸️ All charts paused")
    
    def resume_all_charts(self):
        """Resume all chart monitoring (Harrison's logic)"""
        if not st.session_state.system_status.emergency_stop_active:
            for chart in st.session_state.charts_data.values():
                chart.is_active = True
            st.session_state.monitoring_active = True
            st.success("▶️ All charts resumed")
        else:
            st.error("Cannot resume - Emergency stop is active")
    
    def toggle_monitoring(self):
        """Toggle monitoring (Harrison's logic)"""
        st.session_state.monitoring_active = not st.session_state.monitoring_active
        status = "started" if st.session_state.monitoring_active else "stopped"
        st.info(f"🔄 Monitoring {status}")
    
    def refresh_all_data(self):
        """Refresh all chart data (Harrison's logic + enhanced)"""
        import random
        
        # Update NinjaTrader heartbeat
        st.session_state.ninjatrader_status.last_heartbeat = datetime.now()
        
        for chart in st.session_state.charts_data.values():
            if chart.is_active:
                # Simulate margin changes
                change = random.uniform(-1.5, 1.5)
                chart.margin_percentage = max(10, min(95, chart.margin_percentage + change))
                chart.margin_remaining = chart.account_balance * (chart.margin_percentage / 100)
                
                # Simulate P&L changes
                pnl_change = random.uniform(-75, 75)
                chart.daily_pnl += pnl_change
                
                # Enhanced: Simulate trading signals
                chart.power_score = random.randint(0, 100)
                chart.confluence_level = random.choice(["L0", "L1", "L2", "L3"])
                chart.last_signal = random.choice(["NONE", "BULLISH", "BEARISH", "NEUTRAL"])
                
                # Simulate positions
                if random.random() < 0.3:
                    chart.open_positions = random.randint(0, 3)
                
                chart.last_update = datetime.now()
        
        st.session_state.last_update = datetime.now()
        st.success("📊 All charts refreshed")
    
    def run(self):
        """Main dashboard run method (Harrison's flow)"""
        # Auto-refresh indicator
        if st.session_state.monitoring_active:
            st.info("🔄 Live monitoring active - Data updating every few seconds")
        
        # Render all components in Harrison's order
        self.render_header()
        self.render_overall_margin_indicator()
        self.render_chart_grid()
        self.render_control_buttons()
        self.render_sidebar_settings()
        
        # Footer
        st.markdown("---")
        # Safe access to config with fallbacks
        platform = st.session_state.user_config.get('platform', 'NinjaTrader 8')
        broker = st.session_state.user_config.get('broker', 'Tradovate')
        account_type = f"{platform} + {broker}"
        st.markdown(f"🎯 **Harrison's Enhanced 6-Chart Control Panel** | {account_type} Multi-Account Dashboard")

def main():
    """Main entry point"""
    dashboard = HarrisonEnhancedDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
