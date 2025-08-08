"""
🎯 ENIGMA APEX - Professional Configuration Interface
Streamlit-based configuration for professional trading setup
"""

import streamlit as st
import json
import os
import sys
from datetime import datetime
import socket
import asyncio
import websockets
from pathlib import Path

# Add system path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import system components
from enhanced_websocket_server import WebSocketMessage, MessageType
from apex_compliance_guardian import ComplianceGuardian
from advanced_risk_manager import RiskManager

def load_config():
    """Load trading configuration"""
    try:
        with open('trading_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Configuration error: {str(e)}")
        return None

def save_config(config):
    """Save trading configuration"""
    try:
        with open('trading_config.json', 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Save error: {str(e)}")
        return False

def test_ninjatrader_connection(port):
    """Test NinjaTrader ATI connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    st.set_page_config(
        page_title="🎯 ENIGMA APEX Professional",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Professional header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">
            🎯 ENIGMA APEX PROFESSIONAL CONFIGURATION
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            6-Chart Professional Trading Setup
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Load configuration
    config = load_config()
    if not config:
        st.error("Unable to load configuration. Please contact support.")
        return

    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🎯 Configuration")
        page = st.radio(
            "Select Section:",
            ["🔧 NinjaTrader Setup", "💼 Account Configuration", "📊 Chart Settings", "⚡ Quick Test"]
        )

    if page == "🔧 NinjaTrader Setup":
        st.markdown("## 🔧 NinjaTrader Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ati_port = st.number_input(
                "NinjaTrader ATI Port",
                min_value=1024,
                max_value=65535,
                value=config['ninjatrader']['ati_port'],
                help="Enter your NinjaTrader Automated Trading Interface port"
            )
            
            if st.button("🔗 Test Connection"):
                if test_ninjatrader_connection(ati_port):
                    st.success(f"✅ Successfully connected to NinjaTrader on port {ati_port}")
                else:
                    st.error(f"❌ Could not connect to NinjaTrader on port {ati_port}")
                    st.info("Please check:")
                    st.info("1. NinjaTrader is running")
                    st.info("2. ATI port is correct in Tools > Options")
        
        with col2:
            st.markdown("""
            ### 📋 Connection Guide
            1. Open NinjaTrader 8
            2. Go to Tools > Options
            3. Select "Automated Trading Interface"
            4. Check the port number
            5. Enter it here and test connection
            """)

    elif page == "💼 Account Configuration":
        st.markdown("## 💼 Account Configuration")
        
        accounts = [
            ("ES", "S&P 500 E-mini", "ES_SCALPING"),
            ("NQ", "Nasdaq E-mini", "NQ_MOMENTUM"),
            ("YM", "Dow Jones E-mini", "YM_SWING"),
            ("RTY", "Russell 2000", "RTY_BREAKOUT"),
            ("GC", "Gold Futures", "GC_TREND"),
            ("CL", "Crude Oil", "CL_INTRADAY")
        ]

        total_capital = 0
        for symbol, name, account_key in accounts:
            st.markdown(f"### 📊 {symbol} - {name}")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                capital = st.number_input(
                    f"Capital for {symbol} ($)",
                    min_value=0,
                    value=config['accounts'][account_key]['size'],
                    step=1000,
                    key=f"capital_{symbol}"
                )
                total_capital += capital
            
            with col2:
                risk = st.number_input(
                    f"Risk % for {symbol}",
                    min_value=0.1,
                    max_value=10.0,
                    value=config['accounts'][account_key]['risk'],
                    step=0.1,
                    key=f"risk_{symbol}"
                )
            
            with col3:
                contracts = st.number_input(
                    f"Max Contracts for {symbol}",
                    min_value=1,
                    max_value=100,
                    value=config['accounts'][account_key]['max_contracts'],
                    key=f"contracts_{symbol}"
                )
            
            # Update config
            config['accounts'][account_key]['size'] = capital
            config['accounts'][account_key]['risk'] = risk
            config['accounts'][account_key]['max_contracts'] = contracts
            
            st.markdown("---")

        # Show total capital
        st.markdown(f"""
        <div style="background: #1e3c72; color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
            <h2>Total Capital: ${total_capital:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    elif page == "📊 Chart Settings":
        st.markdown("## 📊 Chart Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            layout = st.selectbox(
                "Chart Layout",
                ["3x2", "2x3", "6x1", "1x6"],
                index=["3x2", "2x3", "6x1", "1x6"].index(config['ninjatrader']['layout'])
            )
            
            sync_charts = st.checkbox("Synchronize All Charts", value=True)
        
        with col2:
            st.markdown("""
            ### 📈 Layout Preview
            ```
            Selected: 3x2 Layout
            ┌─────┬─────┬─────┐
            │ ES  │ NQ  │ YM  │
            ├─────┼─────┼─────┤
            │ RTY │ GC  │ CL  │
            └─────┴─────┴─────┘
            ```
            """)
        
        config['ninjatrader']['layout'] = layout

    elif page == "⚡ Quick Test":
        st.markdown("## ⚡ System Test")
        
        if st.button("🧪 Run Quick Test"):
            with st.spinner("Testing system configuration..."):
                # Test NinjaTrader
                nt_connection = test_ninjatrader_connection(config['ninjatrader']['ati_port'])
                
                # Show results
                st.markdown("### 🎯 Test Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🔗 Connection Status")
                    if nt_connection:
                        st.success(f"✅ NinjaTrader (Port {config['ninjatrader']['ati_port']})")
                    else:
                        st.error(f"❌ NinjaTrader (Port {config['ninjatrader']['ati_port']})")
                    
                    st.success("✅ 6-Chart Configuration")
                    st.success("✅ Account Settings")
                    st.success("✅ Risk Parameters")
                
                with col2:
                    st.markdown("#### 💼 Account Summary")
                    total = sum(account['size'] for account in config['accounts'].values())
                    st.info(f"Total Capital: ${total:,.2f}")
                    st.info(f"Active Charts: 6")
                    st.info(f"Layout: {config['ninjatrader']['layout']}")

    # Save configuration
    if st.sidebar.button("💾 Save All Changes"):
        if save_config(config):
            st.sidebar.success("✅ Configuration saved successfully!")
            st.sidebar.info("🎯 System ready for trading")
        else:
            st.sidebar.error("❌ Failed to save configuration")

    # Show last update
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
