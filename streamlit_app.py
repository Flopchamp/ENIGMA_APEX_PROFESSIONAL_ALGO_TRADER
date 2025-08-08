"""
🛡️ APEX COMPLIANCE GUARDIAN - STREAMLIT CLOUD EDITION
Streamlit Cloud optimized version for prop trader compliance monitoring
Training Wheels for Apex Trader Funding Rules
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import json
import time
import random
import logging
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import base64

# Page configuration
st.set_page_config(
    page_title="🛡️ Apex Compliance Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class ApexRules:
    """Apex Trader Funding rule configurations - OFFICIAL APEX 3.0 RULES"""
    
    # EVALUATION PHASE RULES (Official Apex 3.0)
    evaluation_target: float = 8.0  # 8% profit target
    evaluation_max_daily_loss: float = 5.0  # 5% max daily loss
    evaluation_trailing_threshold: float = 5.0  # 5% trailing threshold (from high water mark)
    evaluation_minimum_days: int = 5  # Minimum 5 trading days
    evaluation_max_days: int = 30  # Maximum 30 calendar days
    
    # PERFORMANCE ACCOUNT (PA) RULES (Official Apex 3.0)
    pa_target: float = 5.0  # 5% profit target
    pa_max_daily_loss: float = 5.0  # 5% max daily loss
    pa_trailing_threshold: float = 5.0  # 5% trailing threshold
    pa_minimum_days: int = 5  # Minimum 5 trading days
    
    # LIVE ACCOUNT RULES (Official Apex 3.0)
    live_max_daily_loss: float = 5.0  # 5% max daily loss
    live_trailing_threshold: float = 5.0  # 5% trailing threshold
    live_scaling_enabled: bool = True  # Live account scaling available
    
    # CONSISTENCY RULE (Official Apex 3.0 - CRITICAL)
    consistency_rule: float = 30.0  # 30% max single day profit of total profit
    consistency_applies_to: str = "all_phases"  # Applies to Evaluation, PA, and Live
    
    # NEWS/HIGH IMPACT EVENTS
    news_restricted_trading: bool = True  # No trading during high impact news
    news_buffer_minutes: int = 15  # 15 min before/after news events
    
    # WEEKEND/HOLIDAY RULES
    weekend_holding_allowed: bool = False  # No weekend position holding
    
    # MAXIMUM POSITION SIZES
    max_contracts_per_trade: int = 10  # Maximum contracts per single trade
    max_total_contracts: int = 20  # Maximum total contracts across all positions
    
    # Platform Settings
    platform: str = "Tradovate"  # Default platform
    safety_ratio: float = 80.0  # 80% safety margin (configurable 5-90%)

@dataclass
class TradeData:
    """Current trade and account data"""
    account_balance: float = 25000.0
    daily_pnl: float = 0.0
    total_pnl: float = 0.0
    current_equity: float = 25000.0
    high_water_mark: float = 25000.0
    max_daily_loss_amount: float = 1250.0
    trailing_threshold_amount: float = 1250.0
    current_positions: int = 0
    contracts_held: int = 0
    phase: str = "Evaluation"  # Evaluation, Performance Account, Live

class ApexComplianceGuardian:
    def __init__(self):
        self.rules = ApexRules()
        self.trade_data = TradeData()
        self.violation_alerts = []
        self.daily_trade_log = []
        
    def check_compliance(self) -> Dict[str, any]:
        """Check all Apex compliance rules"""
        violations = []
        warnings = []
        
        # Daily Loss Check
        daily_loss_pct = abs(self.trade_data.daily_pnl / self.trade_data.account_balance * 100)
        if daily_loss_pct >= self.rules.evaluation_max_daily_loss:
            violations.append(f"🚨 DAILY LOSS VIOLATION: {daily_loss_pct:.1f}% (Max: {self.rules.evaluation_max_daily_loss}%)")
        elif daily_loss_pct >= self.rules.evaluation_max_daily_loss * 0.8:
            warnings.append(f"⚠️ Daily Loss Warning: {daily_loss_pct:.1f}% (Max: {self.rules.evaluation_max_daily_loss}%)")
        
        # Trailing Threshold Check
        drawdown_from_hwm = (self.trade_data.high_water_mark - self.trade_data.current_equity) / self.trade_data.account_balance * 100
        if drawdown_from_hwm >= self.rules.evaluation_trailing_threshold:
            violations.append(f"🚨 TRAILING THRESHOLD VIOLATION: {drawdown_from_hwm:.1f}% (Max: {self.rules.evaluation_trailing_threshold}%)")
        elif drawdown_from_hwm >= self.rules.evaluation_trailing_threshold * 0.8:
            warnings.append(f"⚠️ Trailing Threshold Warning: {drawdown_from_hwm:.1f}% (Max: {self.rules.evaluation_trailing_threshold}%)")
        
        # Consistency Rule Check
        if self.trade_data.total_pnl > 0:
            consistency_limit = self.trade_data.total_pnl * (self.rules.consistency_rule / 100)
            if abs(self.trade_data.daily_pnl) > consistency_limit:
                violations.append(f"🚨 CONSISTENCY RULE VIOLATION: Daily P&L ${self.trade_data.daily_pnl:.0f} exceeds 30% of total profit")
        
        return {
            "violations": violations,
            "warnings": warnings,
            "compliant": len(violations) == 0,
            "daily_loss_pct": daily_loss_pct,
            "trailing_drawdown": drawdown_from_hwm
        }

# Initialize session state
if 'guardian' not in st.session_state:
    st.session_state.guardian = ApexComplianceGuardian()
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

def main():
    st.title("🛡️ Apex Compliance Guardian")
    st.markdown("**Training Wheels for Prop Firm Traders - Apex Trader Funding Edition**")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # Account Settings
    st.sidebar.subheader("📊 Account Settings")
    account_balance = st.sidebar.number_input("Account Balance ($)", value=25000, min_value=1000, max_value=1000000, step=1000)
    phase = st.sidebar.selectbox("Account Phase", ["Evaluation", "Performance Account", "Live"])
    
    # Current Trade Data
    st.sidebar.subheader("💰 Current Trade Data")
    daily_pnl = st.sidebar.number_input("Daily P&L ($)", value=0.0, step=50.0, format="%.2f")
    total_pnl = st.sidebar.number_input("Total P&L ($)", value=0.0, step=50.0, format="%.2f")
    current_positions = st.sidebar.number_input("Current Positions", value=0, min_value=0, max_value=20)
    
    # Update trade data
    guardian = st.session_state.guardian
    guardian.trade_data.account_balance = account_balance
    guardian.trade_data.daily_pnl = daily_pnl
    guardian.trade_data.total_pnl = total_pnl
    guardian.trade_data.current_equity = account_balance + total_pnl
    guardian.trade_data.current_positions = current_positions
    guardian.trade_data.phase = phase
    
    # Update high water mark
    if guardian.trade_data.current_equity > guardian.trade_data.high_water_mark:
        guardian.trade_data.high_water_mark = guardian.trade_data.current_equity
    
    # Main Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Account Balance", f"${account_balance:,.0f}", f"{total_pnl:+.0f}")
    
    with col2:
        st.metric("Daily P&L", f"${daily_pnl:+.0f}", f"{daily_pnl/account_balance*100:+.2f}%")
    
    with col3:
        st.metric("Total P&L", f"${total_pnl:+.0f}", f"{total_pnl/account_balance*100:+.2f}%")
    
    with col4:
        st.metric("Current Equity", f"${guardian.trade_data.current_equity:,.0f}", f"{current_positions} positions")
    
    # Compliance Check
    compliance_result = guardian.check_compliance()
    
    # Status Panel
    st.subheader("🛡️ Compliance Status")
    
    if compliance_result["compliant"]:
        st.success("✅ ALL RULES COMPLIANT - Safe to Trade")
    else:
        st.error("🚨 RULE VIOLATIONS DETECTED - STOP TRADING IMMEDIATELY")
        for violation in compliance_result["violations"]:
            st.error(violation)
    
    # Warnings
    if compliance_result["warnings"]:
        st.warning("⚠️ Compliance Warnings:")
        for warning in compliance_result["warnings"]:
            st.warning(warning)
    
    # Risk Meters
    st.subheader("📊 Risk Meters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily Loss Meter
        daily_loss_pct = compliance_result["daily_loss_pct"]
        max_daily_loss = guardian.rules.evaluation_max_daily_loss
        
        fig_daily = go.Figure(go.Indicator(
            mode="gauge+number",
            value=daily_loss_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Daily Loss %"},
            gauge={
                'axis': {'range': [None, max_daily_loss * 1.2]},
                'bar': {'color': "red" if daily_loss_pct >= max_daily_loss else "orange" if daily_loss_pct >= max_daily_loss * 0.8 else "green"},
                'steps': [
                    {'range': [0, max_daily_loss * 0.6], 'color': "lightgray"},
                    {'range': [max_daily_loss * 0.6, max_daily_loss * 0.8], 'color': "yellow"},
                    {'range': [max_daily_loss * 0.8, max_daily_loss], 'color': "orange"},
                    {'range': [max_daily_loss, max_daily_loss * 1.2], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_daily_loss
                }
            }
        ))
        st.plotly_chart(fig_daily, use_container_width=True)
    
    with col2:
        # Trailing Threshold Meter
        trailing_drawdown = compliance_result["trailing_drawdown"]
        max_trailing = guardian.rules.evaluation_trailing_threshold
        
        fig_trailing = go.Figure(go.Indicator(
            mode="gauge+number",
            value=trailing_drawdown,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Trailing Drawdown %"},
            gauge={
                'axis': {'range': [None, max_trailing * 1.2]},
                'bar': {'color': "red" if trailing_drawdown >= max_trailing else "orange" if trailing_drawdown >= max_trailing * 0.8 else "green"},
                'steps': [
                    {'range': [0, max_trailing * 0.6], 'color': "lightgray"},
                    {'range': [max_trailing * 0.6, max_trailing * 0.8], 'color': "yellow"},
                    {'range': [max_trailing * 0.8, max_trailing], 'color': "orange"},
                    {'range': [max_trailing, max_trailing * 1.2], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_trailing
                }
            }
        ))
        st.plotly_chart(fig_trailing, use_container_width=True)
    
    # Rules Summary
    st.subheader("📋 Apex Rules Summary")
    
    rules_col1, rules_col2 = st.columns(2)
    
    with rules_col1:
        st.info(f"""
        **{phase} Phase Rules:**
        - Daily Loss Limit: {guardian.rules.evaluation_max_daily_loss}%
        - Trailing Threshold: {guardian.rules.evaluation_trailing_threshold}%
        - Profit Target: {guardian.rules.evaluation_target if phase == 'Evaluation' else guardian.rules.pa_target}%
        - Consistency Rule: {guardian.rules.consistency_rule}% max single day
        """)
    
    with rules_col2:
        st.info(f"""
        **Position Limits:**
        - Max Contracts/Trade: {guardian.rules.max_contracts_per_trade}
        - Max Total Contracts: {guardian.rules.max_total_contracts}
        - Current Positions: {current_positions}
        - Weekend Holding: {'❌ Not Allowed' if not guardian.rules.weekend_holding_allowed else '✅ Allowed'}
        """)
    
    # P&L Chart
    st.subheader("📈 P&L Tracking")
    
    # Generate sample data for demonstration
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    np.random.seed(42)
    daily_changes = np.random.normal(0, account_balance * 0.02, len(dates))
    cumulative_pnl = np.cumsum(daily_changes)
    
    # Adjust to match current total P&L
    if len(cumulative_pnl) > 0:
        adjustment = total_pnl - cumulative_pnl[-1]
        cumulative_pnl += adjustment
    
    df_pnl = pd.DataFrame({
        'Date': dates,
        'Daily_PnL': daily_changes,
        'Cumulative_PnL': cumulative_pnl,
        'Equity_Curve': account_balance + cumulative_pnl
    })
    
    fig_pnl = go.Figure()
    
    fig_pnl.add_trace(go.Scatter(
        x=df_pnl['Date'],
        y=df_pnl['Cumulative_PnL'],
        mode='lines',
        name='Cumulative P&L',
        line=dict(color='blue', width=2)
    ))
    
    # Add profit target line
    target_amount = account_balance * (guardian.rules.evaluation_target / 100)
    fig_pnl.add_hline(y=target_amount, line_dash="dash", line_color="green", 
                     annotation_text=f"Target: ${target_amount:,.0f}")
    
    # Add max loss line
    max_loss = -account_balance * (guardian.rules.evaluation_max_daily_loss / 100)
    fig_pnl.add_hline(y=max_loss, line_dash="dash", line_color="red", 
                     annotation_text=f"Max Loss: ${max_loss:,.0f}")
    
    fig_pnl.update_layout(
        title="P&L Progress",
        xaxis_title="Date",
        yaxis_title="P&L ($)",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig_pnl, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**🛡️ Training Wheels for Prop Firm Traders** | Apex Trader Funding Compliance Edition")
    st.markdown("Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
