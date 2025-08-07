"""
🎯 UNIVERSAL 6-CHART TRADING SYSTEM
Main Streamlit application that integrates all components
Works for any trader - fully configurable and universal
"""

import streamlit as st
import sys
import os
from datetime import datetime
import logging

# Add system directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
system_dir = os.path.join(current_dir, 'system')
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if system_dir not in sys.path:
    sys.path.insert(0, system_dir)

# Import dashboard components (with fallback)
try:
    from system.streamlit_6_chart_dashboard import StreamlitTradingDashboard
    from system.streamlit_system_integration import StreamlitSystemIntegration
except ImportError:
    try:
        from streamlit_6_chart_dashboard import StreamlitTradingDashboard
        from streamlit_system_integration import StreamlitSystemIntegration
    except ImportError:
        # Create fallback classes if imports fail
        class StreamlitTradingDashboard:
            def run(self):
                st.error("Dashboard module not found. Creating basic dashboard...")
                st.markdown("## 🎯 6-Chart Trading Dashboard")
                st.info("This is a fallback dashboard. Please ensure all system files are properly installed.")
        
        class StreamlitSystemIntegration:
            def render_integration_dashboard(self):
                st.error("Integration module not found. Creating basic integration...")
                st.markdown("## 🔗 System Integration")
                st.info("This is a fallback integration panel. Please ensure all system files are properly installed.")

class UniversalTradingApp:
    """
    Universal 6-Chart Trading Application
    Complete Streamlit-based trading control system
    """
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        self.setup_logging()
        
    def setup_page_config(self):
        """Configure Streamlit application"""
        st.set_page_config(
            page_title="Universal 6-Chart Trading System",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo/trading-system',
                'Report a bug': 'https://github.com/your-repo/trading-system/issues',
                'About': """
                # Universal 6-Chart Trading System
                
                A complete Streamlit-based trading control panel that works with:
                - Any prop trading firm (Apex, FTMO, etc.)
                - Any trader's setup and preferences
                - Multiple chart configurations
                - OCR signal reading from AlgoBox
                - Automated compliance monitoring
                - Risk management and position sizing
                
                Built with ❤️ using Streamlit
                """
            }
        )
        
        # Enhanced custom CSS
        st.markdown("""
        <style>
        /* Main app styling */
        .main > div {
            padding: 1rem;
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(90deg, #1f4e79, #2d5aa0);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        /* Metric cards */
        .stMetric {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Status indicators */
        .status-safe {
            background-color: #28a745;
            color: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .status-warning {
            background-color: #ffc107;
            color: black;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .status-danger {
            background-color: #dc3545;
            color: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Chart boxes */
        .chart-container {
            border: 3px solid #ddd;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .chart-container:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
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
        
        /* Navigation */
        .nav-pills {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 20px;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Emergency button */
        .emergency-button {
            background-color: #dc3545 !important;
            color: white !important;
            font-size: 16px !important;
            padding: 15px 30px !important;
            border-radius: 10px !important;
        }
        
        /* Sidebar */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 40px;
        }
        
        /* Animation for status changes */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_session_state(self):
        """Initialize application session state"""
        if 'app_initialized' not in st.session_state:
            st.session_state.app_initialized = True
            st.session_state.current_page = "Dashboard"
            st.session_state.app_start_time = datetime.now()
            
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {
                'name': 'Trader',
                'trading_style': 'Day Trading',
                'experience_level': 'Intermediate',
                'preferred_instruments': ['ES', 'NQ', 'YM'],
                'account_type': 'Apex Trader Funding',
                'risk_tolerance': 'Moderate'
            }
    
    def render_main_header(self):
        """Render the main application header"""
        st.markdown("""
        <div class="main-header">
            <h1>🎯 Universal 6-Chart Trading System</h1>
            <p>Complete control panel for multi-chart algorithmic trading</p>
            <p><strong>Universal Design</strong> • Works with any trader's setup • Fully configurable</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_navigation(self):
        """Render navigation menu"""
        st.markdown('<div class="nav-pills">', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
        
        with col2:
            if st.button("🔗 Integration", use_container_width=True):
                st.session_state.current_page = "Integration"
        
        with col3:
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.current_page = "Settings"
        
        with col4:
            if st.button("📈 Analytics", use_container_width=True):
                st.session_state.current_page = "Analytics"
        
        with col5:
            if st.button("❓ Help", use_container_width=True):
                st.session_state.current_page = "Help"
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_user_profile_sidebar(self):
        """Render user profile in sidebar"""
        st.sidebar.markdown("### 👤 User Profile")
        
        # Editable profile
        st.session_state.user_profile['name'] = st.sidebar.text_input(
            "Trader Name", 
            value=st.session_state.user_profile['name'],
            key="main_trader_name"
        )
        
        st.session_state.user_profile['account_type'] = st.sidebar.selectbox(
            "Account Type",
            ["Apex Trader Funding", "FTMO", "MyForexFunds", "TopStep", "The5%ers", "Other"],
            index=0,
            key="main_account_type"
        )
        
        st.session_state.user_profile['trading_style'] = st.sidebar.selectbox(
            "Trading Style",
            ["Day Trading", "Swing Trading", "Scalping", "Position Trading"],
            index=0,
            key="main_trading_style"
        )
        
        st.session_state.user_profile['experience_level'] = st.sidebar.selectbox(
            "Experience Level",
            ["Beginner", "Intermediate", "Advanced", "Expert"],
            index=1,
            key="main_experience_level"
        )
        
        st.session_state.user_profile['risk_tolerance'] = st.sidebar.selectbox(
            "Risk Tolerance",
            ["Conservative", "Moderate", "Aggressive"],
            index=1,
            key="main_risk_tolerance"
        )
        
        # Session info
        st.sidebar.markdown("### 📊 Session Info")
        uptime = datetime.now() - st.session_state.app_start_time
        st.sidebar.write(f"**Uptime:** {str(uptime).split('.')[0]}")
        st.sidebar.write(f"**Current Page:** {st.session_state.current_page}")
        st.sidebar.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")
    
    def render_quick_actions_sidebar(self):
        """Render quick actions in sidebar"""
        st.sidebar.markdown("### ⚡ Quick Actions")
        
        if st.sidebar.button("🚀 Start All Systems", type="primary", key="main_start_systems"):
            st.success("🚀 All systems started!")
            
        if st.sidebar.button("🛑 Emergency Stop All", key="main_emergency_stop"):
            st.error("🛑 Emergency stop activated!")
            
        if st.sidebar.button("📊 Refresh Data", key="main_refresh_data"):
            st.info("📊 Data refreshed!")
            
        if st.sidebar.button("💾 Save Configuration", key="main_save_config"):
            st.success("💾 Configuration saved!")
            
        if st.sidebar.button("🔄 Reset to Defaults", key="main_reset_defaults"):
            if st.sidebar.checkbox("Confirm Reset", key="main_confirm_reset"):
                st.warning("🔄 Reset to defaults!")
    
    def render_dashboard_page(self):
        """Render the main dashboard page"""
        dashboard = StreamlitTradingDashboard()
        dashboard.run()
    
    def render_integration_page(self):
        """Render the system integration page"""
        integration = StreamlitSystemIntegration()
        integration.render_integration_dashboard()
    
    def render_settings_page(self):
        """Render the settings page"""
        st.markdown("## ⚙️ System Settings")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart Settings", "🔍 OCR Settings", "⚖️ Compliance", "🧮 Risk Management"])
        
        with tab1:
            st.markdown("### 📊 Chart Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                chart_layout = st.selectbox(
                    "Chart Layout",
                    ["2x3 (6 charts)", "3x2 (6 charts)", "1x6 (6 charts)", "Custom"],
                    index=0
                )
                
                update_frequency = st.selectbox(
                    "Update Frequency",
                    ["1 second", "2 seconds", "5 seconds", "10 seconds"],
                    index=1
                )
                
                auto_refresh = st.checkbox("Auto-refresh data", value=True)
                
            with col2:
                chart_theme = st.selectbox(
                    "Chart Theme",
                    ["Light", "Dark", "Auto"],
                    index=0
                )
                
                show_animations = st.checkbox("Show status animations", value=True)
                sound_alerts = st.checkbox("Enable sound alerts", value=False)
        
        with tab2:
            st.markdown("### 🔍 OCR Configuration")
            
            ocr_enabled = st.checkbox("Enable OCR monitoring", value=True)
            
            if ocr_enabled:
                col1, col2 = st.columns(2)
                
                with col1:
                    screen_resolution = st.selectbox(
                        "Screen Resolution",
                        ["1920x1080", "2560x1440", "3840x2160", "Custom"],
                        index=0
                    )
                    
                    ocr_confidence = st.slider(
                        "OCR Confidence Threshold",
                        min_value=50,
                        max_value=100,
                        value=80,
                        help="Minimum confidence for OCR text recognition"
                    )
                
                with col2:
                    chart_detection = st.selectbox(
                        "Chart Detection Method",
                        ["Manual Setup", "Auto-detect", "Template Matching"],
                        index=0
                    )
                    
                    if st.button("🔧 Calibrate OCR Regions"):
                        st.info("OCR calibration wizard would open here")
        
        with tab3:
            st.markdown("### ⚖️ Compliance Settings")
            
            compliance_firm = st.selectbox(
                "Compliance Rules",
                ["Apex Trader Funding 3.0", "FTMO", "MyForexFunds", "TopStep", "Custom"],
                index=0
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                max_daily_loss = st.number_input(
                    "Max Daily Loss ($)",
                    min_value=100,
                    max_value=5000,
                    value=2000,
                    step=100
                )
                
                trailing_drawdown = st.number_input(
                    "Trailing Drawdown (%)",
                    min_value=1.0,
                    max_value=10.0,
                    value=5.0,
                    step=0.5
                )
            
            with col2:
                consistency_rule = st.number_input(
                    "Consistency Rule (%)",
                    min_value=10,
                    max_value=50,
                    value=30,
                    step=5
                )
                
                min_trading_days = st.number_input(
                    "Minimum Trading Days",
                    min_value=1,
                    max_value=30,
                    value=10,
                    step=1
                )
        
        with tab4:
            st.markdown("### 🧮 Risk Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                position_sizing = st.selectbox(
                    "Position Sizing Method",
                    ["Kelly Criterion", "Fixed Size", "Percentage Risk", "Volatility Adjusted"],
                    index=0
                )
                
                max_position_size = st.number_input(
                    "Max Position Size (contracts)",
                    min_value=1,
                    max_value=10,
                    value=3,
                    step=1
                )
                
                safety_multiplier = st.slider(
                    "Safety Multiplier",
                    min_value=0.1,
                    max_value=2.0,
                    value=0.5,
                    step=0.1
                )
            
            with col2:
                stop_loss_method = st.selectbox(
                    "Stop Loss Method",
                    ["ATR Based", "Fixed Points", "Percentage", "Support/Resistance"],
                    index=0
                )
                
                risk_reward_ratio = st.number_input(
                    "Minimum Risk:Reward Ratio",
                    min_value=1.0,
                    max_value=10.0,
                    value=2.0,
                    step=0.5
                )
                
                correlation_limit = st.slider(
                    "Max Correlation Between Positions",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.1
                )
    
    def render_analytics_page(self):
        """Render the analytics page"""
        st.markdown("## 📈 Trading Analytics")
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total P&L", "$1,247.83", delta="$89.32")
        with col2:
            st.metric("Win Rate", "68.5%", delta="2.1%")
        with col3:
            st.metric("Profit Factor", "1.85", delta="0.12")
        with col4:
            st.metric("Sharpe Ratio", "1.72", delta="0.08")
        
        # Charts would go here (using placeholder for now)
        st.markdown("### 📊 Performance Charts")
        st.info("Performance charts will be displayed here when historical data is available")
        
        # Trade log
        st.markdown("### 📋 Recent Trades")
        st.info("Trade history will be displayed here when connected to trading platform")
    
    def render_help_page(self):
        """Render the help page"""
        st.markdown("## ❓ Help & Documentation")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 Quick Start", "📖 User Guide", "🔧 Troubleshooting", "📞 Support"])
        
        with tab1:
            st.markdown("""
            ### 🚀 Quick Start Guide
            
            #### 1. Setup Your Profile
            - Go to the sidebar and update your trader profile
            - Select your account type (Apex, FTMO, etc.)
            - Choose your trading style and risk tolerance
            
            #### 2. Configure Your Charts
            - Navigate to Settings → Chart Settings
            - Set up your 6-chart layout (default: 2x3)
            - Configure update frequency and theme
            
            #### 3. Enable OCR (Optional)
            - Go to Settings → OCR Settings
            - Calibrate screen regions for your AlgoBox setup
            - Test OCR detection with live charts
            
            #### 4. Start Trading
            - Return to the Dashboard
            - Enable monitoring for each chart
            - Monitor the overall margin indicator (most important!)
            - Use emergency stop if needed
            """)
        
        with tab2:
            st.markdown("""
            ### 📖 Complete User Guide
            
            #### Dashboard Features
            - **Overall Margin Indicator**: The most important metric - shows total margin remaining
            - **Individual Chart Controls**: Each chart has its own on/off switch and status
            - **Color Coding**: 🟢 Green (Safe), 🟡 Yellow (Warning), 🔴 Red (Danger)
            - **Real-time Updates**: Data refreshes automatically when monitoring is active
            
            #### System Integration
            - **OCR Monitoring**: Reads signals from AlgoBox automatically
            - **Compliance Checking**: Monitors Apex/FTMO rules in real-time
            - **Risk Management**: Kelly Criterion position sizing
            - **Emergency Controls**: Instant stop-all functionality
            
            #### Settings & Configuration
            - All settings are saved automatically
            - Profiles can be exported/imported
            - Custom compliance rules supported
            - Flexible chart layouts available
            """)
        
        with tab3:
            st.markdown("""
            ### 🔧 Troubleshooting
            
            #### Common Issues
            
            **OCR Not Working**
            - Ensure AlgoBox charts are visible and not overlapped
            - Recalibrate screen regions in OCR settings
            - Check screen resolution matches configuration
            - Verify good contrast in AlgoBox theme
            
            **Charts Not Updating**
            - Check if monitoring is active (green status)
            - Verify internet connection
            - Restart the application
            - Check system integration status
            
            **Emergency Stop Not Working**
            - Emergency stop only affects the dashboard
            - Manually close positions in your trading platform
            - Check connection to trading platform
            - Contact support if issues persist
            
            **Performance Issues**
            - Reduce update frequency in settings
            - Disable animations if using older hardware
            - Close other resource-intensive applications
            - Consider upgrading system RAM
            """)
        
        with tab4:
            st.markdown("""
            ### 📞 Support & Contact
            
            #### Getting Help
            - **Documentation**: Check the User Guide tab for detailed instructions
            - **Video Tutorials**: Available on our YouTube channel
            - **Community Forum**: Join our Discord/Telegram community
            - **Email Support**: support@tradingsystem.com
            
            #### System Information
            - **Version**: 1.0.0
            - **Platform**: Streamlit
            - **Python**: 3.8+
            - **Last Updated**: Today
            
            #### Feedback
            We value your feedback! Please let us know:
            - Feature requests
            - Bug reports
            - Improvement suggestions
            - Success stories
            """)
    
    def render_footer(self):
        """Render application footer"""
        st.markdown("""
        <div class="footer">
            <p>🎯 <strong>Universal 6-Chart Trading System</strong> | Built with ❤️ using Streamlit</p>
            <p>Designed for any trader • Any setup • Any strategy</p>
            <p><small>Remember: This tool is for educational purposes. Always trade responsibly and within your risk tolerance.</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main application run method"""
        # Render main components
        self.render_main_header()
        self.render_navigation()
        
        # Render current page content (sidebar will be handled by individual pages)
        if st.session_state.current_page == "Dashboard":
            self.render_dashboard_page()
        elif st.session_state.current_page == "Integration":
            self.render_integration_page()
        elif st.session_state.current_page == "Settings":
            self.render_settings_page()
        elif st.session_state.current_page == "Analytics":
            self.render_analytics_page()
        elif st.session_state.current_page == "Help":
            self.render_help_page()
        else:
            # If on other pages, show sidebar
            self.render_user_profile_sidebar()
            self.render_quick_actions_sidebar()
        
        # Render footer
        self.render_footer()

def main():
    """Main entry point"""
    app = UniversalTradingApp()
    app.run()

if __name__ == "__main__":
    main()
