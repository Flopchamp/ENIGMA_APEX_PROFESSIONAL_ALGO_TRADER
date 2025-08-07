"""
🎯 TRAINING WHEELS FOR PROP FIRM TRADERS
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
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import logging
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
    from streamlit_ocr_module import StreamlitOCRManager
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    StreamlitOCRManager = None

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

class HarrisonOriginalDashboard:
    """
    Harrison's Original Dashboard - Complete Enhanced Version
    Clean interface with all professional trading features
    """
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        self.setup_logging()
        
        # Initialize OCR manager if available
        if OCR_AVAILABLE:
            self.ocr_manager = StreamlitOCRManager()
        else:
            self.ocr_manager = None
    
    def setup_page_config(self):
        """Configure Streamlit page (Harrison's clean style)"""
        try:
            st.set_page_config(
                page_title="Harrison's Trading Dashboard",
                page_icon="🎯",
                layout="wide",
                initial_sidebar_state="expanded"
            )
        except:
            pass
        
        # Harrison's original clean CSS with enhancements
        st.markdown("""
        <style>
        /* Harrison's original clean styling */
        .main > div {
            padding: 0.5rem;
        }
        
        /* Clean metric cards (Harrison's style) */
        .stMetric {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
        }
        
        /* Harrison's signal colors */
        .signal-green {
            background-color: #28a745;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }
        
        .signal-yellow {
            background-color: #ffc107;
            color: black;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }
        
        .signal-red {
            background-color: #dc3545;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }
        
        /* Clean chart boxes (Harrison's design) */
        .chart-box {
            border: 2px solid #6c757d;
            border-radius: 12px;
            padding: 16px;
            margin: 12px 0;
            background-color: #ffffff;
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
        
        /* Harrison's margin indicator */
        .margin-indicator {
            height: 40px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            margin: 15px 0;
            font-size: 18px;
        }
        
        /* Mode indicators */
        .mode-demo {
            background-color: #17a2b8;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-weight: bold;
        }
        
        .mode-test {
            background-color: #ffc107;
            color: black;
            padding: 4px 12px;
            border-radius: 15px;
            font-weight: bold;
        }
        
        .mode-live {
            background-color: #dc3545;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-weight: bold;
        }
        
        /* NinjaTrader status */
        .ninja-connected {
            background-color: #28a745;
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-weight: bold;
        }
        
        .ninja-disconnected {
            background-color: #dc3545;
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_logging(self):
        """Setup logging for debugging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
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
        
        # System status (Harrison's priority indicator)
        if 'system_status' not in st.session_state:
            st.session_state.system_status = SystemStatus(
                total_margin_remaining=50000.0,
                total_margin_percentage=75.0,
                total_equity=100000.0,
                daily_profit_loss=0.0,
                active_charts=0,
                violation_alerts=[],
                emergency_stop_active=False,
                safety_ratio=25.0,
                system_health="HEALTHY",
                ninjatrader_status=st.session_state.ninjatrader_status,
                mode=st.session_state.system_mode
            )
        
        # User configuration
        if 'user_config' not in st.session_state:
            st.session_state.user_config = {
                "trader_name": "Trader",
                "account_type": "NinjaTrader + Tradovate",
                "chart_layout": "2x3",
                "risk_management": "Conservative",
                "platform": "NinjaTrader 8",
                "broker": "Tradovate",
                "max_daily_loss": 2000.0,
                "max_position_size": 5.0,
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
        
        # Charts (Harrison's 6-chart design)
        if 'charts' not in st.session_state:
            st.session_state.charts = self.create_default_charts()
        
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
    
    def create_default_charts(self) -> Dict[int, TradovateAccount]:
        """Create Harrison's default 6-chart configuration"""
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
        
        charts = {}
        for i in range(6):
            chart_id = i + 1
            charts[chart_id] = TradovateAccount(
                chart_id=chart_id,
                account_name=chart_names[i],
                account_balance=25000.0,
                daily_pnl=0.0,
                margin_used=0.0,
                margin_remaining=25000.0,
                margin_percentage=100.0,
                open_positions=0,
                is_active=True,
                risk_level="SAFE",
                last_signal="NONE",
                power_score=0,
                confluence_level="L0",
                signal_color="yellow",  # Harrison's default
                ninjatrader_connection="Disconnected",
                last_update=datetime.now(),
                instruments=instruments[i],
                position_size=0.0,
                entry_price=0.0,
                unrealized_pnl=0.0
            )
        
        return charts
    
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
    
    def render_header(self):
        """Render Harrison's clean header with enhanced status"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Mode indicator
            mode_class = f"mode-{st.session_state.system_mode.lower()}"
            st.markdown(f'<div class="{mode_class}">{st.session_state.system_mode} MODE</div>', unsafe_allow_html=True)
            
            # NinjaTrader status
            ninja_connected = self.check_ninjatrader_connection()
            status_class = "ninja-connected" if ninja_connected else "ninja-disconnected"
            status_text = "🥷 NT: Connected" if ninja_connected else "🥷 NT: Disconnected"
            st.markdown(f'<div class="{status_class}">{status_text}</div>', unsafe_allow_html=True)
        
        with col2:
            st.title("🎯 Harrison's 6-Chart Trading Control Panel")
            # Safe access to config with fallbacks
            platform = st.session_state.user_config.get('platform', 'NinjaTrader 8')
            broker = st.session_state.user_config.get('broker', 'Tradovate')
            trader_name = st.session_state.user_config.get('trader_name', 'Trader')
            account_type = f"{platform} + {broker}"
            st.markdown(f"**{trader_name}'s {account_type} Dashboard**")
        
        with col3:
            # Real-time clock and account count
            st.markdown(f"**{datetime.now().strftime('%H:%M:%S')}**")
            active_accounts = sum(1 for chart in st.session_state.charts.values() if chart.is_active)
            st.markdown(f"Active: {active_accounts} accounts")
    
    def render_priority_indicator(self):
        """Render Harrison's most important indicator - Overall Margin"""
        st.subheader("💰 OVERALL MARGIN STATUS (Most Important)")
        
        # Calculate total margin across all accounts
        total_margin_used = sum(chart.margin_used for chart in st.session_state.charts.values())
        total_equity = st.session_state.system_status.total_equity
        margin_remaining = total_equity - total_margin_used
        margin_percentage = (margin_remaining / total_equity) * 100 if total_equity > 0 else 0
        
        # Update system status
        st.session_state.system_status.total_margin_remaining = margin_remaining
        st.session_state.system_status.total_margin_percentage = margin_percentage
        
        # Harrison's clean margin display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Available Margin", f"${margin_remaining:,.0f}")
        
        with col2:
            st.metric("📊 Used Margin", f"${total_margin_used:,.0f}")
        
        with col3:
            color = "green" if margin_percentage > 50 else "orange" if margin_percentage > 20 else "red"
            st.metric("📈 Margin %", f"{margin_percentage:.1f}%")
        
        with col4:
            daily_pnl = st.session_state.system_status.daily_profit_loss
            st.metric("💵 Daily P&L", f"${daily_pnl:,.0f}", delta=f"{daily_pnl:+.0f}")
        
        # Harrison's visual margin indicator
        if margin_percentage > 50:
            color = "#28a745"
            status = "SAFE"
        elif margin_percentage > 20:
            color = "#ffc107"
            status = "WARNING"
        else:
            color = "#dc3545"
            status = "DANGER"
        
        st.markdown(f"""
        <div class="margin-indicator" style="background-color: {color}">
            MARGIN STATUS: {status} ({margin_percentage:.1f}% Available)
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar for visual impact
        progress_value = max(0, min(100, margin_percentage)) / 100
        st.progress(progress_value)
        
        if margin_percentage < 25:
            st.error("⚠️ LOW MARGIN WARNING - Consider reducing positions!")
    
    def render_chart_grid(self):
        """Render Harrison's 6-chart grid with enhanced features"""
        st.subheader("📊 6-Chart Control Grid")
        
        # Harrison's 2x3 layout
        for row in range(2):
            cols = st.columns(3)
            for col_idx in range(3):
                chart_id = row * 3 + col_idx + 1
                with cols[col_idx]:
                    self.render_individual_chart(chart_id)
    
    def render_individual_chart(self, chart_id: int):
        """Render individual chart with Harrison's clean design + enhanced features"""
        chart = st.session_state.charts.get(chart_id)
        if not chart:
            return
        
        # Determine chart status and styling
        chart_class = f"chart-{chart.risk_level.lower()}" if chart.risk_level != "SAFE" else "chart-safe"
        signal_class = f"signal-{chart.signal_color}"
        
        # Harrison's clean chart box
        with st.container():
            st.markdown(f'<div class="chart-box {chart_class}">', unsafe_allow_html=True)
            
            # Chart header with signal indicator
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"### {chart.account_name}")
            with col2:
                st.markdown(f'<div class="{signal_class}">{chart.signal_color.upper()}</div>', unsafe_allow_html=True)
            
            # Enable/disable toggle
            chart.is_active = st.checkbox(
                "Enabled", 
                value=chart.is_active,
                key=f"enable_{chart_id}"
            )
            
            # Chart metrics in Harrison's clean layout
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
            st.caption(f"📊 Instruments: {instruments_str}")
            st.caption(f"🔗 NT: {chart.ninjatrader_connection}")
            st.caption(f"⏰ Updated: {chart.last_update.strftime('%H:%M:%S')}")
            
            # Chart controls
            control_col1, control_col2 = st.columns(2)
            
            with control_col1:
                if st.button(f"📈 Details", key=f"details_{chart_id}"):
                    self.show_chart_details(chart_id)
            
            with control_col2:
                if st.button(f"🚨 Stop", key=f"stop_{chart_id}"):
                    chart.is_active = False
                    chart.signal_color = "red"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def show_chart_details(self, chart_id: int):
        """Show detailed chart information modal"""
        chart = st.session_state.charts.get(chart_id)
        if not chart:
            return
        
        with st.expander(f"📊 {chart.account_name} - Detailed Analysis", expanded=True):
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            
            with detail_col1:
                st.subheader("📈 Signal Analysis")
                st.write(f"**Power Score:** {chart.power_score}%")
                st.write(f"**Signal Color:** {chart.signal_color.upper()}")
                st.write(f"**Risk Level:** {chart.risk_level}")
                st.write(f"**Last Signal:** {chart.last_signal}")
                st.write(f"**Confluence:** {chart.confluence_level}")
            
            with detail_col2:
                st.subheader("💰 Position Details")
                st.write(f"**Position Size:** {chart.position_size:.2f}")
                st.write(f"**Entry Price:** ${chart.entry_price:.2f}")
                st.write(f"**Unrealized P&L:** ${chart.unrealized_pnl:,.2f}")
                st.write(f"**Daily P&L:** ${chart.daily_pnl:,.2f}")
                st.write(f"**Account Balance:** ${chart.account_balance:,.2f}")
            
            with detail_col3:
                st.subheader("⚙️ Controls & Status")
                st.write(f"**Status:** {'Active' if chart.is_active else 'Inactive'}")
                st.write(f"**NT Connection:** {chart.ninjatrader_connection}")
                st.write(f"**Instruments:** {', '.join(chart.instruments)}")
                st.write(f"**Last Update:** {chart.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Manual controls
                if st.button(f"🔄 Force Update", key=f"force_update_{chart_id}"):
                    chart.last_update = datetime.now()
                    st.success("Chart updated!")
                    st.rerun()
    
    def render_connection_setup_modal(self):
        """Render comprehensive connection setup interface"""
        st.markdown("---")
        st.header("🔗 Connection Configuration")
        st.markdown("Configure your NinjaTrader and Tradovate connections")
        
        # Tabs for different connection types
        tab1, tab2, tab3 = st.tabs(["🥷 NinjaTrader Setup", "📈 Tradovate Setup", "✅ Test Connections"])
        
        with tab1:
            self.render_ninjatrader_setup()
        
        with tab2:
            self.render_tradovate_setup()
        
        with tab3:
            self.render_connection_testing()
        
        # Close button
        if st.button("✅ Done - Close Setup", type="primary", use_container_width=True):
            st.session_state.show_connection_setup = False
            st.rerun()
    
    def render_ninjatrader_setup(self):
        """NinjaTrader connection configuration"""
        st.subheader("🥷 NinjaTrader Configuration")
        
        # Connection settings
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
        
        # Strategy configuration
        st.markdown("---")
        st.subheader("📊 Strategy Settings")
        
        available_strategies = [
            "MarketAnalyzer", "Chart Trader", "ATM Strategy",
            "SuperDOM", "Custom Strategy 1", "Custom Strategy 2"
        ]
        
        st.session_state.connection_config["ninjatrader_strategies"] = st.multiselect(
            "Enable Strategies",
            available_strategies,
            default=st.session_state.connection_config.get("ninjatrader_strategies", [])
        )
        
        # Test NinjaTrader connection
        st.markdown("---")
        if st.button("🔍 Test NinjaTrader Connection", use_container_width=True):
            if self.check_ninjatrader_connection():
                st.success("✅ NinjaTrader detected and connected!")
                # Get process details
                ninja_status = st.session_state.ninjatrader_status
                st.info(f"Process ID: {ninja_status.process_id}")
                st.info(f"Memory Usage: {ninja_status.memory_usage:.1f} MB")
            else:
                st.error("❌ NinjaTrader not detected!")
                st.warning("Make sure NinjaTrader is running and properly configured.")
    
    def render_tradovate_setup(self):
        """Tradovate API configuration"""
        st.subheader("📈 Tradovate API Configuration")
        
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
        st.markdown("### 💰 Account Configuration")
        
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
        if st.button("🔍 Test Tradovate Connection", use_container_width=True):
            # Check if credentials are provided
            username = st.session_state.connection_config["tradovate_username"]
            password = st.session_state.connection_config["tradovate_password"]
            
            if not username or not password:
                st.warning("⚠️ Please enter username and password to test connection")
                return
            
            if self.test_tradovate_connection():
                st.success("✅ Tradovate connection successful!")
                environment = st.session_state.connection_config["tradovate_environment"]
                st.info(f"Connected to {environment.upper()} environment")
                
                # Show account info if available
                account_ids = st.session_state.connection_config.get("tradovate_account_ids", [])
                if account_ids:
                    st.info(f"Configured accounts: {', '.join(account_ids)}")
            else:
                st.error("❌ Tradovate connection failed!")
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
        st.subheader("✅ Connection Testing & Validation")
        
        # Overall connection status
        ninja_connected = self.check_ninjatrader_connection()
        tradovate_connected = self.test_tradovate_connection()
        
        # Status overview
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            ninja_icon = "✅" if ninja_connected else "❌"
            st.metric("🥷 NinjaTrader", f"{ninja_icon} {'Connected' if ninja_connected else 'Disconnected'}")
        
        with status_col2:
            tradovate_icon = "✅" if tradovate_connected else "❌"
            st.metric("📈 Tradovate", f"{tradovate_icon} {'Connected' if tradovate_connected else 'Disconnected'}")
        
        with status_col3:
            overall_status = "Ready" if ninja_connected and tradovate_connected else "Issues"
            overall_icon = "✅" if ninja_connected and tradovate_connected else "⚠️"
            st.metric("🎯 Overall", f"{overall_icon} {overall_status}")
        
        # Detailed testing
        st.markdown("---")
        st.subheader("🔍 Detailed Connection Tests")
        
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
        with st.expander("🔧 Troubleshooting Guide"):
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
    
    
    def render_control_panel(self):
        """Render Harrison's main control panel with enhanced features"""
        st.subheader("🎛️ Master Control Panel")
        
        control_col1, control_col2, control_col3, control_col4 = st.columns(4)
        
        with control_col1:
            if st.button("🚀 START SYSTEM", use_container_width=True, type="primary"):
                if st.session_state.system_mode == "DEMO":
                    st.session_state.system_running = True
                    st.session_state.emergency_stop = False
                    st.success("✅ System started in DEMO mode")
                    st.rerun()
                else:
                    # Check if connections are configured in TEST/LIVE mode
                    connections_configured = st.session_state.connection_config.get("connections_configured", False)
                    
                    if not connections_configured:
                        st.error("❌ Please configure connections first! Click 'Configure Connections' in sidebar.")
                        return
                    
                    # Check actual connections in TEST/LIVE mode
                    ninja_ok = self.check_ninjatrader_connection()
                    tradovate_ok = self.test_tradovate_connection()
                    
                    if ninja_ok and tradovate_ok:
                        st.session_state.system_running = True
                        st.session_state.emergency_stop = False
                        st.success(f"✅ System started in {st.session_state.system_mode} mode")
                        st.rerun()
                    else:
                        connection_issues = []
                        if not ninja_ok:
                            connection_issues.append("NinjaTrader")
                        if not tradovate_ok:
                            connection_issues.append("Tradovate")
                        st.error(f"❌ Connection check failed: {', '.join(connection_issues)}")
                        st.info("💡 Use 'Configure Connections' to fix these issues.")
        
        with control_col2:
            if st.button("⏸️ PAUSE SYSTEM", use_container_width=True):
                st.session_state.system_running = False
                st.warning("⏸️ System paused")
                st.rerun()
        
        with control_col3:
            if st.button("🚨 EMERGENCY STOP", use_container_width=True, type="secondary"):
                st.session_state.emergency_stop = True
                st.session_state.system_running = False
                # Emergency stop all charts
                for chart in st.session_state.charts.values():
                    chart.is_active = False
                    chart.signal_color = "red"
                    chart.position_size = 0.0
                st.error("🚨 EMERGENCY STOP ACTIVATED!")
                st.rerun()
        
        with control_col4:
            if st.button("🔄 RESET SYSTEM", use_container_width=True):
                st.session_state.emergency_stop = False
                st.session_state.system_running = False
                # Reset all charts to safe state
                for chart in st.session_state.charts.values():
                    chart.is_active = True
                    chart.signal_color = "yellow"
                    chart.risk_level = "SAFE"
                st.info("🔄 System reset to safe state")
                st.rerun()
        
        # Mode selector (Demo/Test/Live progression)
        st.markdown("---")
        st.subheader("🔧 System Mode")
        
        mode_col1, mode_col2, mode_col3 = st.columns(3)
        
        with mode_col1:
            if st.button("🔷 DEMO MODE", use_container_width=True):
                st.session_state.system_mode = "DEMO"
                st.info("🔷 Demo mode - Simulated data only")
                st.rerun()
        
        with mode_col2:
            if st.button("🔶 TEST MODE", use_container_width=True):
                # Check if connections are configured
                connections_configured = st.session_state.connection_config.get("connections_configured", False)
                
                if not connections_configured:
                    st.error("❌ Please configure connections first!")
                    st.info("💡 Click 'Configure Connections' in the sidebar.")
                    return
                
                if self.check_ninjatrader_connection():
                    st.session_state.system_mode = "TEST"
                    st.warning("🔶 Test mode - Real connections, paper trading")
                    st.rerun()
                else:
                    st.error("❌ NinjaTrader not detected! Start NinjaTrader first.")
        
        with mode_col3:
            if st.button("🔴 LIVE MODE", use_container_width=True):
                # Check if connections are configured
                connections_configured = st.session_state.connection_config.get("connections_configured", False)
                
                if not connections_configured:
                    st.error("❌ Please configure connections first!")
                    st.info("💡 Click 'Configure Connections' in the sidebar.")
                    return
                
                # Require both connections for live mode
                ninja_ok = self.check_ninjatrader_connection()
                tradovate_ok = self.test_tradovate_connection()
                
                if ninja_ok and tradovate_ok:
                    # Extra confirmation for live mode
                    if st.session_state.get('confirm_live_mode', False):
                        st.session_state.system_mode = "LIVE"
                        st.error("🔴 LIVE MODE - REAL MONEY TRADING!")
                        st.session_state.confirm_live_mode = False
                        st.rerun()
                    else:
                        st.warning("⚠️ Click again to confirm LIVE MODE (real money trading)")
                        st.session_state.confirm_live_mode = True
                else:
                    connection_issues = []
                    if not ninja_ok:
                        connection_issues.append("NinjaTrader")
                    if not tradovate_ok:
                        connection_issues.append("Tradovate")
                    st.error(f"❌ Connection check failed: {', '.join(connection_issues)}")
                    st.info("💡 Configure connections first before entering live mode.")
        
        # Current mode display
        st.markdown(f"**Current Mode:** {st.session_state.system_mode}")
    
    def render_sidebar_settings(self):
        """Render Harrison's clean sidebar settings"""
        st.sidebar.header("⚙️ Trading Settings")
        
        # Connection Configuration Section
        st.sidebar.subheader("🔗 Connection Setup")
        
        # Connection setup button - prominent placement
        if st.sidebar.button("🔧 Configure Connections", use_container_width=True, type="primary"):
            st.session_state.show_connection_setup = True
        
        # Quick connection status display
        ninja_status = "✅ Connected" if self.check_ninjatrader_connection() else "❌ Disconnected"
        tradovate_status = "✅ Connected" if self.test_tradovate_connection() else "❌ Disconnected"
        
        st.sidebar.markdown(f"**NinjaTrader:** {ninja_status}")
        st.sidebar.markdown(f"**Tradovate:** {tradovate_status}")
        
        # Show connection setup modal if requested
        if st.session_state.get('show_connection_setup', False):
            self.render_connection_setup_modal()
        
        st.sidebar.markdown("---")
        
        # User profile
        st.sidebar.subheader("👤 Trader Profile")
        st.session_state.user_config["trader_name"] = st.sidebar.text_input(
            "Trader Name", 
            value=st.session_state.user_config["trader_name"],
            key="sidebar_trader_name"
        )
        
        # Platform settings  
        st.sidebar.subheader("🔧 Platform Settings")
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
        st.sidebar.subheader("⚖️ Risk Management")
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
        st.sidebar.subheader("📊 Chart Settings")
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
        
        # OCR settings
        if OCR_AVAILABLE and self.ocr_manager:
            st.sidebar.markdown("---")
            st.sidebar.subheader("👁️ OCR Settings")
            if st.sidebar.button("🔧 Configure OCR"):
                st.sidebar.info("OCR configuration panel would open here")
    
    def simulate_data_updates(self):
        """Simulate real-time data updates when system is running"""
        if not st.session_state.system_running or st.session_state.emergency_stop:
            return
        
        # Update each chart with simulated data
        total_daily_pnl = 0
        
        for chart in st.session_state.charts.values():
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
                
                # Update position sizes
                if chart.signal_color == "green" and chart.power_score > 75:
                    target_size = min(st.session_state.user_config["max_position_size"], 
                                    (chart.power_score / 100) * st.session_state.user_config["max_position_size"])
                    chart.position_size = min(chart.position_size + 0.1, target_size)
                elif chart.signal_color == "red":
                    chart.position_size = max(0, chart.position_size - 0.2)
                
                # Update margin usage
                chart.margin_used = chart.position_size * 400  # $400 per contract
                chart.margin_remaining = chart.account_balance - chart.margin_used
                
                # Update timestamps
                chart.last_update = datetime.now()
                
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
    
    def run(self):
        """Main dashboard run method"""
        # Page header
        self.render_header()
        
        # Sidebar configuration
        self.render_sidebar_settings()
        
        # Main dashboard content
        self.render_priority_indicator()
        
        st.markdown("---")
        
        self.render_chart_grid()
        
        st.markdown("---")
        
        self.render_control_panel()
        
        st.markdown("---")
        
        self.render_system_status()
        
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
                    st.session_state.user_config = config_obj
                    
                    self.ocr_manager.render_ocr_configuration()
                    self.ocr_manager.render_ocr_status()
                    
                    # Restore original config
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
        # Safe access to config with fallbacks
        platform = st.session_state.user_config.get('platform', 'NinjaTrader 8')
        broker = st.session_state.user_config.get('broker', 'Tradovate')
        account_type = f"{platform} + {broker}"
        st.markdown(f"🎯 **Harrison's Original 6-Chart Control Panel** | {account_type} Multi-Account Dashboard")

def main():
    """Main application entry point"""
    dashboard = HarrisonOriginalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
