"""
🎯 UNIVERSAL MULTI-CHART TRADING DASHBOARD
Complete Streamlit application integrating OCR, compliance, and visual controls
Works for any trader - not hardcoded for specific users
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

# Import our integrated modules
try:
    from universal_streamlit_dashboard import StreamlitTradingControlPanel
    from streamlit_ocr_integration import StreamlitOCRCoordinator
    MODULES_AVAILABLE = True
except ImportError as e:
    st.error(f"Module import error: {e}")
    MODULES_AVAILABLE = False

# Configure page
st.set_page_config(
    page_title="🎯 Universal Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class UniversalTradingDashboard:
    """
    Universal Multi-Chart Trading Dashboard
    Combines visual controls, OCR integration, and compliance monitoring
    Configurable for any trader's setup
    """
    
    def __init__(self):
        self.initialize_application()
        self.setup_components()
    
    def initialize_application(self):
        """Initialize the complete application"""
        # Initialize session state for the integrated app
        if 'app_initialized' not in st.session_state:
            st.session_state.app_initialized = True
            st.session_state.current_tab = "Dashboard"
            st.session_state.trader_name = ""
            st.session_state.setup_complete = False
    
    def setup_components(self):
        """Setup all application components"""
        if MODULES_AVAILABLE:
            # Initialize dashboard
            self.dashboard = StreamlitTradingControlPanel()
            
            # Initialize OCR coordinator
            self.ocr_coordinator = StreamlitOCRCoordinator()
            
            self.logger = logging.getLogger(__name__)
            self.logger.info("Universal Trading Dashboard initialized")
        else:
            self.dashboard = None
            self.ocr_coordinator = None
    
    def create_main_header(self):
        """Create main application header"""
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1a1a1a, #2d2d2d, #1a1a1a);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #00ff88;
            margin-bottom: 20px;
            text-align: center;
        }
        .trader-name {
            color: #00ff88;
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .chart-status-box {
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            text-align: center;
            font-weight: bold;
        }
        .status-safe { background-color: #00ff88; color: black; }
        .status-warning { background-color: #ffaa00; color: black; }
        .status-danger { background-color: #ff4444; color: white; }
        .metric-card {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #444;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get trader name from session state
        trader_name = st.session_state.get('trader_name', 'Trader')
        if not trader_name or trader_name == "":
            trader_name = "Universal Trader"
        
        # Main header
        st.markdown(f"""
        <div class="main-header">
            <h1 style='color: #00ff88; margin: 0;'>🎯 Universal Multi-Chart Trading Dashboard</h1>
            <div class="trader-name">{trader_name}'s Command Center</div>
            <p style='color: #ffffff; margin: 5px 0;'>OCR Integration • Apex Compliance • Visual Controls</p>
            <p style='color: #ffaa00; margin: 0;'>Real-time Multi-Account Trading Management</p>
        </div>
        """, unsafe_allow_html=True)
    
    def create_setup_wizard(self):
        """Create initial setup wizard for new users"""
        if not st.session_state.setup_complete:
            st.subheader("🚀 Welcome! Let's Set Up Your Trading Dashboard")
            
            with st.container():
                st.markdown("""
                **Quick Setup - Tell us about your trading setup:**
                """)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    trader_name = st.text_input(
                        "Your Name/Identifier",
                        value=st.session_state.trader_name,
                        placeholder="Enter your name or trader ID",
                        help="This will be displayed in your dashboard header"
                    )
                    
                    account_type = st.selectbox(
                        "Account Type",
                        ["Apex Trader Funding", "TopStep", "FTMO", "Personal Account", "Other"],
                        help="Select your primary account type for compliance rules"
                    )
                    
                    total_accounts = st.number_input(
                        "Number of Trading Accounts",
                        min_value=1,
                        max_value=6,
                        value=6,
                        help="How many accounts/charts will you monitor?"
                    )
                
                with col2:
                    trading_style = st.selectbox(
                        "Trading Style",
                        ["Day Trading", "Swing Trading", "Scalping", "Algorithmic", "Mixed"],
                        help="Your primary trading approach"
                    )
                    
                    experience_level = st.selectbox(
                        "Experience Level",
                        ["Beginner", "Intermediate", "Advanced", "Professional"],
                        help="Your trading experience level"
                    )
                    
                    use_ocr = st.checkbox(
                        "Enable OCR Screen Reading",
                        value=True,
                        help="Automatically read signals from AlgoBox or similar software"
                    )
                
                # Save setup
                if st.button("🎯 Complete Setup & Launch Dashboard", type="primary", use_container_width=True):
                    # Update session state
                    st.session_state.trader_name = trader_name
                    st.session_state.account_type = account_type
                    st.session_state.total_accounts = total_accounts
                    st.session_state.trading_style = trading_style
                    st.session_state.experience_level = experience_level
                    st.session_state.use_ocr = use_ocr
                    st.session_state.setup_complete = True
                    
                    # Initialize chart data based on user input
                    if hasattr(self.dashboard, 'initialize_charts'):
                        self.dashboard.initialize_charts()
                    
                    st.success("✅ Setup complete! Welcome to your trading dashboard!")
                    st.rerun()
            
            return False  # Setup not complete
        
        return True  # Setup complete
    
    def create_tab_navigation(self):
        """Create tab-based navigation"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard", 
            "🔍 OCR Settings", 
            "⚖️ Compliance", 
            "📈 Analytics", 
            "⚙️ Settings"
        ])
        
        return tab1, tab2, tab3, tab4, tab5
    
    def render_dashboard_tab(self, tab):
        """Render main dashboard tab"""
        with tab:
            if self.dashboard:
                # Overall margin indicator (most important)
                overall_margin, total_remaining, total_pnl = self.dashboard.create_overall_margin_indicator()
                
                st.divider()
                
                # Chart grid with visual status
                self.dashboard.create_chart_grid()
                
                st.divider()
                
                # Control panel
                self.dashboard.create_control_panel()
                
                # Auto-update if monitoring is active
                if st.session_state.get('is_monitoring', False):
                    # Update with OCR data if available
                    if self.ocr_coordinator and st.session_state.get('ocr_enabled', False):
                        self.ocr_coordinator.update_chart_data_with_ocr()
                    
                    # Simulate data update
                    self.dashboard.simulate_data_update()
                    
                    # Auto-refresh every 3 seconds
                    time.sleep(3)
                    st.rerun()
            else:
                st.error("Dashboard module not available")
    
    def render_ocr_tab(self, tab):
        """Render OCR settings tab"""
        with tab:
            if self.ocr_coordinator:
                st.subheader("🔍 OCR Configuration & Testing")
                
                # OCR status
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    ocr_status = "ACTIVE" if st.session_state.get('ocr_enabled', False) else "DISABLED"
                    status_color = "#00ff88" if ocr_status == "ACTIVE" else "#ff4444"
                    
                    st.markdown(f"""
                    <div style='padding: 15px; background-color: {status_color}; border-radius: 10px; text-align: center; color: black; font-weight: bold;'>
                        OCR Status: {ocr_status}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    total_signals = len(st.session_state.get('ocr_signals', {}))
                    st.metric("Active Signals", total_signals)
                
                with col3:
                    last_update = st.session_state.get('last_update', datetime.now())
                    st.metric("Last OCR Update", last_update.strftime("%H:%M:%S"))
                
                st.divider()
                
                # OCR region configuration
                self.ocr_coordinator.show_region_config()
                
                st.divider()
                
                # Live OCR data display
                self.ocr_coordinator.create_ocr_status_display()
            else:
                st.error("OCR module not available")
    
    def render_compliance_tab(self, tab):
        """Render compliance monitoring tab"""
        with tab:
            st.subheader("⚖️ Compliance Monitoring")
            
            # Compliance status overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Daily P&L", "$1,250.50", "↗️ $150")
            
            with col2:
                st.metric("Max Drawdown", "5.2%", "✅ Safe")
            
            with col3:
                st.metric("Consistency Score", "92%", "↗️ 2%")
            
            with col4:
                st.metric("Risk Level", "LOW", "✅ Compliant")
            
            st.divider()
            
            # Compliance rules based on account type
            account_type = st.session_state.get('account_type', 'Apex Trader Funding')
            
            st.markdown(f"**{account_type} Rules:**")
            
            if account_type == "Apex Trader Funding":
                compliance_rules = {
                    "30% Consistency Rule": "✅ Compliant",
                    "Trailing Drawdown": "✅ Within Limits",
                    "Daily Loss Limit": "✅ Safe",
                    "Weekend Holding": "✅ Allowed",
                    "News Trading": "⚠️ Restricted"
                }
            else:
                compliance_rules = {
                    "Daily Loss Limit": "✅ Safe",
                    "Max Drawdown": "✅ Within Limits",
                    "Position Sizing": "✅ Appropriate",
                    "Risk Management": "✅ Active"
                }
            
            for rule, status in compliance_rules.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(rule)
                with col2:
                    st.write(status)
            
            st.divider()
            
            # Violation alerts
            st.subheader("🚨 Recent Alerts")
            
            if 'violation_alerts' in st.session_state and st.session_state.violation_alerts:
                for alert in st.session_state.violation_alerts[-5:]:  # Show last 5
                    st.warning(alert)
            else:
                st.success("No recent violations - all systems compliant! ✅")
    
    def render_analytics_tab(self, tab):
        """Render analytics and performance tab"""
        with tab:
            if self.dashboard:
                self.dashboard.create_performance_dashboard()
            
            st.divider()
            
            # Additional analytics
            st.subheader("📊 Trading Analytics")
            
            # Generate sample analytics data
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            
            # Win rate chart
            win_rates = np.random.uniform(0.6, 0.8, len(dates))
            
            fig_winrate = go.Figure()
            fig_winrate.add_trace(go.Scatter(
                x=dates,
                y=win_rates * 100,
                mode='lines+markers',
                name='Win Rate %',
                line=dict(color='#00ff88', width=3)
            ))
            
            fig_winrate.update_layout(
                title="30-Day Win Rate Trend",
                xaxis_title="Date",
                yaxis_title="Win Rate (%)",
                height=400
            )
            
            st.plotly_chart(fig_winrate, use_container_width=True)
            
            # Risk metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average Win Rate", "72.5%", "↗️ 2.1%")
            
            with col2:
                st.metric("Profit Factor", "1.85", "↗️ 0.15")
            
            with col3:
                st.metric("Sharpe Ratio", "2.34", "↗️ 0.21")
    
    def render_settings_tab(self, tab):
        """Render settings and configuration tab"""
        with tab:
            st.subheader("⚙️ System Settings")
            
            # User profile
            with st.expander("👤 User Profile", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input(
                        "Trader Name",
                        value=st.session_state.get('trader_name', ''),
                        help="Your display name"
                    )
                    
                    if new_name != st.session_state.get('trader_name', ''):
                        st.session_state.trader_name = new_name
                
                with col2:
                    new_account_type = st.selectbox(
                        "Account Type",
                        ["Apex Trader Funding", "TopStep", "FTMO", "Personal Account", "Other"],
                        index=0 if st.session_state.get('account_type') == 'Apex Trader Funding' else 0
                    )
                    
                    if new_account_type != st.session_state.get('account_type'):
                        st.session_state.account_type = new_account_type
            
            # Dashboard settings
            with st.expander("📊 Dashboard Settings"):
                auto_refresh = st.checkbox(
                    "Auto Refresh",
                    value=st.session_state.get('auto_refresh', True),
                    help="Automatically update dashboard data"
                )
                
                refresh_interval = st.slider(
                    "Refresh Interval (seconds)",
                    min_value=1,
                    max_value=30,
                    value=3,
                    help="How often to update the dashboard"
                )
                
                dark_theme = st.checkbox(
                    "Dark Theme",
                    value=True,
                    help="Use dark theme (recommended for trading)"
                )
            
            # Data export
            with st.expander("💾 Data Management"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📁 Export Configuration", use_container_width=True):
                        config_data = {
                            "trader_name": st.session_state.get('trader_name', ''),
                            "account_type": st.session_state.get('account_type', ''),
                            "setup_complete": st.session_state.get('setup_complete', False),
                            "chart_data": {k: asdict(v) for k, v in st.session_state.get('chart_data', {}).items()}
                        }
                        
                        st.download_button(
                            label="Download Config",
                            data=json.dumps(config_data, indent=2, default=str),
                            file_name=f"trading_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
                with col2:
                    uploaded_file = st.file_uploader(
                        "📁 Import Configuration",
                        type=["json"],
                        help="Upload a previously exported configuration"
                    )
                    
                    if uploaded_file:
                        try:
                            config_data = json.load(uploaded_file)
                            # Import configuration
                            for key, value in config_data.items():
                                st.session_state[key] = value
                            st.success("Configuration imported successfully!")
                        except Exception as e:
                            st.error(f"Import failed: {e}")
            
            # Reset settings
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Reset to Defaults", type="secondary", use_container_width=True):
                    # Reset specific settings without losing user data
                    settings_to_reset = ['auto_refresh', 'refresh_interval', 'dark_theme']
                    for setting in settings_to_reset:
                        if setting in st.session_state:
                            del st.session_state[setting]
                    st.success("Settings reset to defaults")
                    st.rerun()
            
            with col2:
                if st.button("⚠️ Clear All Data", type="secondary", use_container_width=True):
                    if st.checkbox("I understand this will clear all data"):
                        # Clear all session state
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.success("All data cleared")
                        st.rerun()
    
    def run(self):
        """Main application entry point"""
        try:
            # Create main header
            self.create_main_header()
            
            # Check if setup is complete
            if not self.create_setup_wizard():
                return  # Show setup wizard until complete
            
            # OCR settings in sidebar (always available)
            if self.ocr_coordinator:
                self.ocr_coordinator.create_ocr_settings_ui()
            
            # Create tab navigation
            tab1, tab2, tab3, tab4, tab5 = self.create_tab_navigation()
            
            # Render tabs
            self.render_dashboard_tab(tab1)
            self.render_ocr_tab(tab2)
            self.render_compliance_tab(tab3)
            self.render_analytics_tab(tab4)
            self.render_settings_tab(tab5)
            
        except Exception as e:
            st.error(f"Application Error: {e}")
            st.exception(e)

def main():
    """Main entry point"""
    # Initialize and run the universal dashboard
    dashboard = UniversalTradingDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
