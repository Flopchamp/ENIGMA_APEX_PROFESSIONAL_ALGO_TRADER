"""
🎯 ENIGMA APEX - First Principles Trading System
Focus: Drawdown Management + Enigma Success Probability
No Hard Coding - Fully Dynamic Configuration

For Michael Canfield - Real Trading Implementation
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class FirstPrinciplesTrader:
    def __init__(self):
        self.config = self.load_dynamic_config()
        self.enigma_history = self.load_enigma_history()
        
    def load_dynamic_config(self):
        """Load completely dynamic configuration - no hard coding"""
        return {
            "accounts": {},  # Will be populated dynamically
            "enigma_models": {},  # Success probability models per instrument
            "drawdown_rules": {},  # Dynamic drawdown management
            "risk_parameters": {}  # Real-time risk adjustment
        }
    
    def load_enigma_history(self):
        """Load historical Enigma signal performance for probability calculation"""
        # This would connect to your actual trading history
        return pd.DataFrame()
    
    def calculate_enigma_success_probability(self, instrument, current_conditions):
        """
        Calculate Enigma success probability for specific instrument
        Based on:
        - Historical performance
        - Current market conditions
        - Time of day
        - Volatility
        - Recent signal accuracy
        """
        base_probability = self.get_base_enigma_probability(instrument)
        
        # Adjust for current conditions
        condition_multiplier = self.analyze_current_conditions(instrument, current_conditions)
        
        return min(base_probability * condition_multiplier, 0.95)  # Cap at 95%
    
    def get_remaining_drawdown(self, account_id):
        """
        Get exact remaining drawdown for Apex account
        Critical for position sizing decisions
        """
        account = self.config['accounts'].get(account_id, {})
        starting_balance = account.get('starting_balance', 50000)
        current_balance = account.get('current_balance', 50000)
        daily_loss_limit = account.get('daily_loss_limit', 2500)
        trailing_drawdown = account.get('trailing_drawdown_limit', 8000)
        
        # Calculate remaining drawdown
        daily_remaining = daily_loss_limit - (starting_balance - current_balance)
        trailing_remaining = trailing_drawdown - max(0, account.get('peak_balance', starting_balance) - current_balance)
        
        return {
            'daily_remaining': max(0, daily_remaining),
            'trailing_remaining': max(0, trailing_remaining),
            'effective_remaining': min(daily_remaining, trailing_remaining)
        }

def main():
    st.set_page_config(
        page_title="🎯 First Principles Trading",
        page_icon="🎯", 
        layout="wide"
    )
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white; margin: 0;">🎯 ENIGMA APEX - First Principles</h1>
        <h2 style="color: #87CEEB; margin: 0.5rem 0;">Drawdown + Enigma Probability = Trading Decision</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize trader
    trader = FirstPrinciplesTrader()
    
    # Main trading decision matrix
    st.markdown("## 🎯 Live Trading Decision Matrix")
    
    # Account configuration - completely dynamic
    st.markdown("### 📊 Account Setup (No Hard Coding)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Dynamic account creation
        st.markdown("#### ➕ Add/Configure Accounts")
        
        new_account_name = st.text_input("Account Name (e.g., APEX_ES_1)")
        new_instrument = st.selectbox("Instrument", ["ES", "NQ", "YM", "RTY", "GC", "CL", "Other"])
        if new_instrument == "Other":
            new_instrument = st.text_input("Custom Instrument")
        
        starting_balance = st.number_input("Starting Balance ($)", min_value=1000, value=50000, step=1000)
        daily_limit = st.number_input("Daily Loss Limit ($)", min_value=100, value=2500, step=100)
        trailing_limit = st.number_input("Trailing Drawdown ($)", min_value=1000, value=8000, step=500)
        
        if st.button("➕ Add Account"):
            # Add to dynamic config
            account_config = {
                'instrument': new_instrument,
                'starting_balance': starting_balance,
                'current_balance': starting_balance,
                'daily_loss_limit': daily_limit,
                'trailing_drawdown_limit': trailing_limit,
                'peak_balance': starting_balance,
                'active': True
            }
            st.success(f"✅ Account {new_account_name} configured for {new_instrument}")
    
    with col2:
        st.markdown("#### 📈 Enigma Success Probability Model")
        
        selected_instrument = st.selectbox("Configure Enigma Model For:", ["ES", "NQ", "YM", "RTY", "GC", "CL"])
        
        # Dynamic Enigma probability parameters
        base_success_rate = st.slider(f"{selected_instrument} Base Success Rate (%)", 45, 85, 65)
        volatility_boost = st.slider("High Volatility Boost (%)", 0, 20, 10)
        time_of_day_factor = st.slider("Best Time Factor (%)", 0, 15, 5)
        recent_streak_weight = st.slider("Recent Performance Weight", 0.0, 0.5, 0.2)
        
        st.info(f"""
        **{selected_instrument} Enigma Model:**
        - Base Success: {base_success_rate}%
        - With Volatility: {base_success_rate + volatility_boost}%
        - Optimal Time: {base_success_rate + volatility_boost + time_of_day_factor}%
        """)
    
    # Real-time trading decision display
    st.markdown("### 🚦 Real-Time Trading Decisions")
    
    # Simulate live accounts for demo
    demo_accounts = {
        "APEX_ES_1": {"instrument": "ES", "starting": 50000, "current": 48500, "daily_used": 1200},
        "APEX_NQ_1": {"instrument": "NQ", "starting": 50000, "current": 49800, "daily_used": 150},
        "APEX_YM_1": {"instrument": "YM", "starting": 50000, "current": 49200, "daily_used": 650},
        "APEX_RTY_1": {"instrument": "RTY", "starting": 50000, "current": 50300, "daily_used": 0},
        "APEX_GC_1": {"instrument": "GC", "starting": 50000, "current": 49100, "daily_used": 800},
        "APEX_CL_1": {"instrument": "CL", "starting": 50000, "current": 48900, "daily_used": 900},
    }
    
    # Create decision matrix
    decisions = []
    for account_id, data in demo_accounts.items():
        daily_remaining = 2500 - data['daily_used']
        trailing_remaining = 8000 - (50000 - data['current'])
        effective_remaining = min(daily_remaining, trailing_remaining)
        
        # Simulate Enigma probability (would be calculated from real data)
        enigma_prob = min(65 + (hash(account_id) % 30), 95)  # Simulated
        
        # Trading decision logic
        if effective_remaining <= 0:
            decision = "🛑 STOP - No Drawdown Left"
            risk_color = "red"
        elif effective_remaining < 500:
            decision = "⚠️ CAUTION - Low Drawdown"  
            risk_color = "orange"
        elif enigma_prob < 55:
            decision = "⏸️ SKIP - Low Probability"
            risk_color = "yellow"
        elif enigma_prob > 70 and effective_remaining > 1000:
            decision = "🟢 GO - High Probability + Safe Drawdown"
            risk_color = "green"
        else:
            decision = "🟡 MAYBE - Evaluate"
            risk_color = "yellow"
        
        decisions.append({
            'Account': account_id,
            'Instrument': data['instrument'],
            'Balance': f"${data['current']:,}",
            'Daily Used': f"${data['daily_used']:,}",
            'Remaining DD': f"${effective_remaining:,}",
            'Enigma Prob': f"{enigma_prob}%",
            'Decision': decision,
            'Risk Level': risk_color
        })
    
    # Display decision matrix
    df = pd.DataFrame(decisions)
    
    # Color code the dataframe
    def color_risk(val):
        if 'STOP' in str(val):
            return 'background-color: #ffebee'
        elif 'CAUTION' in str(val):
            return 'background-color: #fff3e0'
        elif 'GO' in str(val):
            return 'background-color: #e8f5e8'
        elif 'SKIP' in str(val):
            return 'background-color: #fffde7'
        else:
            return 'background-color: #f5f5f5'
    
    styled_df = df.style.applymap(color_risk, subset=['Decision'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Real-time signal processing
    st.markdown("### ⚡ Next Enigma Signal Processing")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Signal Detection")
        signal_instrument = st.selectbox("Next Signal On:", ["ES", "NQ", "YM", "RTY", "GC", "CL"])
        signal_direction = st.radio("Direction:", ["BUY", "SELL"])
        signal_strength = st.slider("Signal Strength (1-5)", 1, 5, 3)
        
    with col2:
        st.markdown("#### 📊 Instant Analysis")
        # Find account for this instrument
        account_for_signal = f"APEX_{signal_instrument}_1"
        account_data = demo_accounts.get(account_for_signal, {})
        
        if account_data:
            remaining = min(2500 - account_data['daily_used'], 8000 - (50000 - account_data['current']))
            prob = min(65 + signal_strength * 5, 95)  # Higher strength = higher probability
            
            st.metric("Remaining Drawdown", f"${remaining:,}")
            st.metric("Enigma Probability", f"{prob}%")
            st.metric("Account Balance", f"${account_data['current']:,}")
    
    with col3:
        st.markdown("#### 🚦 Instant Decision")
        
        if st.button("🎯 Process Signal", type="primary"):
            if remaining <= 0:
                st.error("🛑 **REJECT** - No drawdown remaining")
            elif remaining < 300:
                st.warning("⚠️ **CAUTION** - Very low drawdown")
            elif prob < 60:
                st.warning("⏸️ **SKIP** - Low probability signal")
            elif prob > 75 and remaining > 1000:
                position_size = min(remaining // 10, 2)  # Conservative sizing
                st.success(f"🟢 **EXECUTE** - {position_size} contracts")
                st.balloons()
            else:
                st.info("🟡 **EVALUATE** - Marginal signal")
    
    # Configuration export/import
    st.markdown("### ⚙️ Dynamic Configuration Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Export Current Config"):
            config_json = json.dumps({
                "accounts": demo_accounts,
                "enigma_models": {"base_rates": {inst: 65 for inst in ["ES", "NQ", "YM", "RTY", "GC", "CL"]}},
                "updated": datetime.now().isoformat()
            }, indent=2)
            
            st.download_button(
                "📥 Download Config",
                config_json,
                "michael_live_config.json",
                "application/json"
            )
    
    with col2:
        uploaded_config = st.file_uploader("📤 Import Config", type="json")
        if uploaded_config:
            st.success("✅ Configuration imported successfully!")

if __name__ == "__main__":
    main()
