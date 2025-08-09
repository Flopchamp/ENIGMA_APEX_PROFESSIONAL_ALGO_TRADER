"""
🏛️ PROP FIRM COMPLIANCE ENGINE
Advanced real-time compliance monitoring for all major prop trading firms
Prevents account violations before they happen - the #1 feature prop firms need
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json
from abc import ABC, abstractmethod

class ViolationType(Enum):
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    MAX_LOSS_LIMIT = "max_loss_limit"
    POSITION_SIZE = "position_size"
    FORBIDDEN_INSTRUMENT = "forbidden_instrument"
    TIME_RESTRICTION = "time_restriction"
    NEWS_BLACKOUT = "news_blackout"
    CONSISTENCY_RULE = "consistency_rule"
    MAXIMUM_CONTRACTS = "maximum_contracts"
    SCALING_VIOLATION = "scaling_violation"
    WEEKEND_HOLDING = "weekend_holding"

class ViolationSeverity(Enum):
    WARNING = "warning"      # Minor violation, can continue
    STOP = "stop"           # Must close positions immediately
    BREACH = "breach"       # Account terminated

@dataclass
class ComplianceViolation:
    """Represents a compliance rule violation"""
    violation_type: ViolationType
    severity: ViolationSeverity
    message: str
    current_value: float
    limit_value: float
    timestamp: datetime
    suggested_action: str
    auto_action_taken: bool = False

@dataclass
class PropFirmRules:
    """Base class for prop firm trading rules"""
    firm_name: str
    account_size: float
    daily_loss_limit: float
    max_loss_limit: float
    profit_target: float
    max_position_size: float
    forbidden_instruments: List[str]
    trading_hours: Dict[str, Any]
    news_blackout_minutes: int
    consistency_rule: bool
    max_contracts_per_side: int
    weekend_holding_allowed: bool
    scaling_plan: Dict[str, float]

class PropFirmComplianceRules(ABC):
    """Abstract base class for prop firm compliance rules"""
    
    @abstractmethod
    def get_rules(self, account_size: float) -> PropFirmRules:
        """Get compliance rules for given account size"""
        pass
    
    @abstractmethod
    def check_compliance(self, trade_data: Dict, account_data: Dict) -> List[ComplianceViolation]:
        """Check if proposed trade violates any rules"""
        pass

class ApexTraderFundingRules(PropFirmComplianceRules):
    """Apex Trader Funding compliance rules implementation"""
    
    def get_rules(self, account_size: float) -> PropFirmRules:
        """Get Apex-specific rules based on account size"""
        
        # Apex Trader Funding 3.0 Rules
        if account_size <= 25000:
            return PropFirmRules(
                firm_name="Apex Trader Funding",
                account_size=account_size,
                daily_loss_limit=1000,  # $1,000 daily loss limit
                max_loss_limit=2000,    # $2,000 max loss limit
                profit_target=3000,     # $3,000 profit target
                max_position_size=5,    # 5 contracts max per position
                forbidden_instruments=["CRYPTO", "PENNY_STOCKS", "OPTIONS"],
                trading_hours={
                    "start": time(9, 30),   # 9:30 AM EST
                    "end": time(16, 0),     # 4:00 PM EST
                    "timezone": "EST"
                },
                news_blackout_minutes=2,    # 2 minutes before/after major news
                consistency_rule=True,      # Cannot make more than 30% of profits in a single day
                max_contracts_per_side=10,  # Max 10 contracts per side
                weekend_holding_allowed=False,
                scaling_plan={
                    "phase1": 25000,    # Evaluation
                    "phase2": 50000,    # Funded
                    "phase3": 100000    # Scaled
                }
            )
        elif account_size <= 50000:
            return PropFirmRules(
                firm_name="Apex Trader Funding",
                account_size=account_size,
                daily_loss_limit=2000,
                max_loss_limit=3000,
                profit_target=4000,
                max_position_size=7,
                forbidden_instruments=["CRYPTO", "PENNY_STOCKS"],
                trading_hours={
                    "start": time(9, 30),
                    "end": time(16, 0),
                    "timezone": "EST"
                },
                news_blackout_minutes=2,
                consistency_rule=True,
                max_contracts_per_side=15,
                weekend_holding_allowed=False,
                scaling_plan={
                    "current": 50000,
                    "next": 100000
                }
            )
        else:  # $100K+ accounts
            return PropFirmRules(
                firm_name="Apex Trader Funding",
                account_size=account_size,
                daily_loss_limit=3000,
                max_loss_limit=5000,
                profit_target=6000,
                max_position_size=10,
                forbidden_instruments=["CRYPTO"],
                trading_hours={
                    "start": time(9, 30),
                    "end": time(16, 0),
                    "timezone": "EST"
                },
                news_blackout_minutes=2,
                consistency_rule=True,
                max_contracts_per_side=20,
                weekend_holding_allowed=True,
                scaling_plan={
                    "current": 100000,
                    "next": 200000
                }
            )
    
    def check_compliance(self, trade_data: Dict, account_data: Dict) -> List[ComplianceViolation]:
        """Check Apex-specific compliance rules"""
        violations = []
        rules = self.get_rules(account_data["account_size"])
        
        # Check daily loss limit
        if account_data["daily_pnl"] <= -rules.daily_loss_limit:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.DAILY_LOSS_LIMIT,
                severity=ViolationSeverity.BREACH,
                message=f"Daily loss limit of ${rules.daily_loss_limit:,.0f} exceeded",
                current_value=account_data["daily_pnl"],
                limit_value=-rules.daily_loss_limit,
                timestamp=datetime.now(),
                suggested_action="STOP ALL TRADING - Account may be terminated"
            ))
        
        # Check max loss limit (trailing)
        if account_data["max_drawdown"] <= -rules.max_loss_limit:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.MAX_LOSS_LIMIT,
                severity=ViolationSeverity.BREACH,
                message=f"Maximum loss limit of ${rules.max_loss_limit:,.0f} exceeded",
                current_value=account_data["max_drawdown"],
                limit_value=-rules.max_loss_limit,
                timestamp=datetime.now(),
                suggested_action="STOP ALL TRADING - Account terminated"
            ))
        
        # Check position size
        if trade_data.get("quantity", 0) > rules.max_position_size:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.POSITION_SIZE,
                severity=ViolationSeverity.STOP,
                message=f"Position size {trade_data['quantity']} exceeds limit of {rules.max_position_size}",
                current_value=trade_data["quantity"],
                limit_value=rules.max_position_size,
                timestamp=datetime.now(),
                suggested_action="Reduce position size to comply with rules"
            ))
        
        # Check forbidden instruments
        if trade_data.get("symbol", "").upper() in rules.forbidden_instruments:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.FORBIDDEN_INSTRUMENT,
                severity=ViolationSeverity.STOP,
                message=f"Trading {trade_data['symbol']} is forbidden",
                current_value=0,
                limit_value=0,
                timestamp=datetime.now(),
                suggested_action="Select a different instrument to trade"
            ))
        
        # Check trading hours
        current_time = datetime.now().time()
        if not (rules.trading_hours["start"] <= current_time <= rules.trading_hours["end"]):
            violations.append(ComplianceViolation(
                violation_type=ViolationType.TIME_RESTRICTION,
                severity=ViolationSeverity.STOP,
                message="Trading outside allowed hours",
                current_value=0,
                limit_value=0,
                timestamp=datetime.now(),
                suggested_action="Wait for market open or close existing positions"
            ))
        
        # Check consistency rule (30% rule)
        if rules.consistency_rule and account_data.get("daily_pnl", 0) > 0:
            total_profits = account_data.get("total_profits", 1)
            daily_percentage = (account_data["daily_pnl"] / total_profits) * 100
            if daily_percentage > 30:
                violations.append(ComplianceViolation(
                    violation_type=ViolationType.CONSISTENCY_RULE,
                    severity=ViolationSeverity.WARNING,
                    message=f"Daily profits ({daily_percentage:.1f}%) exceed 30% of total profits",
                    current_value=daily_percentage,
                    limit_value=30,
                    timestamp=datetime.now(),
                    suggested_action="Consider reducing position sizes for consistency"
                ))
        
        return violations

class FTMORules(PropFirmComplianceRules):
    """FTMO compliance rules implementation"""
    
    def get_rules(self, account_size: float) -> PropFirmRules:
        """Get FTMO-specific rules"""
        
        if account_size <= 10000:
            daily_loss = 500
            max_loss = 1000
            profit_target = 1000
        elif account_size <= 25000:
            daily_loss = 1250
            max_loss = 2500
            profit_target = 2500
        elif account_size <= 50000:
            daily_loss = 2500
            max_loss = 5000
            profit_target = 5000
        else:  # $100K+
            daily_loss = 5000
            max_loss = 10000
            profit_target = 10000
        
        return PropFirmRules(
            firm_name="FTMO",
            account_size=account_size,
            daily_loss_limit=daily_loss,
            max_loss_limit=max_loss,
            profit_target=profit_target,
            max_position_size=2.0,  # 2% risk per trade
            forbidden_instruments=["CRYPTO", "EXOTIC_PAIRS"],
            trading_hours={
                "start": time(0, 0),    # 24/5 trading
                "end": time(23, 59),
                "timezone": "GMT"
            },
            news_blackout_minutes=2,
            consistency_rule=False,  # FTMO doesn't have consistency rule
            max_contracts_per_side=999,  # Based on 2% risk rule
            weekend_holding_allowed=True,
            scaling_plan={
                "challenge": account_size,
                "verification": account_size,
                "funded": account_size
            }
        )
    
    def check_compliance(self, trade_data: Dict, account_data: Dict) -> List[ComplianceViolation]:
        """Check FTMO-specific compliance rules"""
        violations = []
        rules = self.get_rules(account_data["account_size"])
        
        # Similar to Apex but with FTMO-specific rules
        # Daily loss check
        if account_data["daily_pnl"] <= -rules.daily_loss_limit:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.DAILY_LOSS_LIMIT,
                severity=ViolationSeverity.BREACH,
                message=f"FTMO daily loss limit of ${rules.daily_loss_limit:,.0f} exceeded",
                current_value=account_data["daily_pnl"],
                limit_value=-rules.daily_loss_limit,
                timestamp=datetime.now(),
                suggested_action="STOP TRADING - FTMO account terminated"
            ))
        
        # Max loss check (from high-water mark)
        if account_data["drawdown_from_high"] <= -rules.max_loss_limit:
            violations.append(ComplianceViolation(
                violation_type=ViolationType.MAX_LOSS_LIMIT,
                severity=ViolationSeverity.BREACH,
                message=f"FTMO maximum loss of ${rules.max_loss_limit:,.0f} exceeded",
                current_value=account_data["drawdown_from_high"],
                limit_value=-rules.max_loss_limit,
                timestamp=datetime.now(),
                suggested_action="STOP TRADING - Account terminated"
            ))
        
        # Risk per trade (2% rule)
        if trade_data.get("risk_amount", 0) > (account_data["account_size"] * 0.02):
            violations.append(ComplianceViolation(
                violation_type=ViolationType.POSITION_SIZE,
                severity=ViolationSeverity.STOP,
                message="Risk per trade exceeds 2% of account",
                current_value=trade_data["risk_amount"],
                limit_value=account_data["account_size"] * 0.02,
                timestamp=datetime.now(),
                suggested_action="Reduce position size to limit risk to 2%"
            ))
        
        return violations

class PropFirmComplianceEngine:
    """Main compliance engine for all prop firms"""
    
    def __init__(self):
        self.rules_engines = {
            "apex": ApexTraderFundingRules(),
            "ftmo": FTMORules(),
            # Add more prop firms as needed
            "the5ers": None,  # Placeholder for future implementation
            "topstep": None,
            "leeloo": None
        }
        self.logger = logging.getLogger(__name__)
        self.violation_history = []
        
    def get_firm_rules(self, firm_name: str, account_size: float) -> Optional[PropFirmRules]:
        """Get rules for specific prop firm"""
        engine = self.rules_engines.get(firm_name.lower())
        if engine:
            return engine.get_rules(account_size)
        return None
    
    def check_trade_compliance(self, 
                             firm_name: str,
                             trade_data: Dict,
                             account_data: Dict) -> List[ComplianceViolation]:
        """Check if a proposed trade violates any rules"""
        
        engine = self.rules_engines.get(firm_name.lower())
        if not engine:
            self.logger.warning(f"No compliance engine found for {firm_name}")
            return []
        
        violations = engine.check_compliance(trade_data, account_data)
        
        # Log violations
        for violation in violations:
            self.violation_history.append(violation)
            self.logger.warning(f"Compliance violation: {violation.message}")
        
        return violations
    
    def get_real_time_compliance_status(self, 
                                      firm_name: str,
                                      account_data: Dict) -> Dict[str, Any]:
        """Get real-time compliance status"""
        
        rules = self.get_firm_rules(firm_name, account_data["account_size"])
        if not rules:
            return {"status": "error", "message": "Unknown firm"}
        
        # Calculate compliance metrics
        daily_loss_usage = abs(account_data.get("daily_pnl", 0)) / rules.daily_loss_limit * 100
        max_loss_usage = abs(account_data.get("max_drawdown", 0)) / rules.max_loss_limit * 100
        
        # Determine overall status
        if daily_loss_usage >= 100 or max_loss_usage >= 100:
            status = "BREACH"
            color = "red"
        elif daily_loss_usage >= 80 or max_loss_usage >= 80:
            status = "DANGER"
            color = "orange"
        elif daily_loss_usage >= 60 or max_loss_usage >= 60:
            status = "WARNING"
            color = "yellow"
        else:
            status = "SAFE"
            color = "green"
        
        return {
            "status": status,
            "color": color,
            "daily_loss_usage": daily_loss_usage,
            "max_loss_usage": max_loss_usage,
            "rules": rules,
            "profit_target_progress": (account_data.get("total_pnl", 0) / rules.profit_target) * 100
        }
    
    def get_maximum_position_size(self,
                                 firm_name: str,
                                 symbol: str,
                                 account_data: Dict,
                                 price: float) -> Dict[str, Any]:
        """Calculate maximum allowed position size for compliance"""
        
        rules = self.get_firm_rules(firm_name, account_data["account_size"])
        if not rules:
            return {"max_contracts": 0, "reason": "Unknown firm"}
        
        # Check multiple constraints
        constraints = []
        
        # 1. Position size limit
        max_by_position_limit = rules.max_position_size
        constraints.append(("position_limit", max_by_position_limit))
        
        # 2. Daily loss remaining
        daily_loss_remaining = rules.daily_loss_limit - abs(account_data.get("daily_pnl", 0))
        if daily_loss_remaining > 0:
            # Assume $50 risk per contract (adjust based on symbol)
            risk_per_contract = 50  # This should be calculated based on actual stop loss
            max_by_daily_loss = daily_loss_remaining / risk_per_contract
            constraints.append(("daily_loss", max_by_daily_loss))
        else:
            max_by_daily_loss = 0
            constraints.append(("daily_loss", 0))
        
        # 3. Max loss remaining
        max_loss_remaining = rules.max_loss_limit - abs(account_data.get("max_drawdown", 0))
        if max_loss_remaining > 0:
            max_by_max_loss = max_loss_remaining / 50  # Same assumption
            constraints.append(("max_loss", max_by_max_loss))
        else:
            max_by_max_loss = 0
            constraints.append(("max_loss", 0))
        
        # 4. Contract limit per side
        max_by_contract_limit = rules.max_contracts_per_side
        constraints.append(("contract_limit", max_by_contract_limit))
        
        # Take the minimum constraint
        limiting_constraint = min(constraints, key=lambda x: x[1])
        max_contracts = int(limiting_constraint[1])
        
        return {
            "max_contracts": max_contracts,
            "limiting_factor": limiting_constraint[0],
            "constraints": dict(constraints),
            "rules": rules
        }

# Streamlit Integration Functions
def integrate_compliance_with_streamlit():
    """Initialize compliance engine in Streamlit session state"""
    if 'compliance_engine' not in st.session_state:
        st.session_state.compliance_engine = PropFirmComplianceEngine()
    return st.session_state.compliance_engine

def render_compliance_dashboard():
    """Render comprehensive compliance dashboard"""
    st.header("🏛️ Prop Firm Compliance Monitor")
    st.markdown("**Real-time compliance monitoring for prop trading firms**")
    
    compliance_engine = integrate_compliance_with_streamlit()
    
    # Firm selection
    col1, col2 = st.columns(2)
    with col1:
        selected_firm = st.selectbox(
            "Select Prop Firm",
            ["Apex", "FTMO", "The5ers", "TopStep", "Leeloo"],
            key="compliance_firm"
        )
    
    with col2:
        account_size = st.selectbox(
            "Account Size",
            [10000, 25000, 50000, 100000, 200000],
            index=1,
            key="compliance_account_size"
        )
    
    # Mock account data for demonstration
    account_data = {
        "account_size": account_size,
        "daily_pnl": st.slider("Current Daily P&L", -3000, 3000, 150, key="daily_pnl"),
        "total_pnl": st.slider("Total P&L", -5000, 10000, 2500, key="total_pnl"),
        "max_drawdown": st.slider("Max Drawdown", -5000, 0, -500, key="max_drawdown"),
        "drawdown_from_high": st.slider("Drawdown from High", -5000, 0, -300, key="drawdown_high")
    }
    
    # Get compliance status
    compliance_status = compliance_engine.get_real_time_compliance_status(
        selected_firm.lower(), account_data
    )
    
    if compliance_status.get("status") != "error":
        # Status display
        st.markdown("---")
        st.subheader("📊 Real-Time Compliance Status")
        
        status_col1, status_col2, status_col3, status_col4 = st.columns(4)
        
        with status_col1:
            status_color = compliance_status["color"]
            st.markdown(f"""
            <div style="
                padding: 1rem;
                background-color: {status_color};
                color: white;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
            ">
                STATUS: {compliance_status["status"]}
            </div>
            """, unsafe_allow_html=True)
        
        with status_col2:
            daily_usage = compliance_status["daily_loss_usage"]
            st.metric(
                "Daily Loss Usage",
                f"{daily_usage:.1f}%",
                delta=f"{daily_usage-50:.1f}% from safe zone"
            )
        
        with status_col3:
            max_usage = compliance_status["max_loss_usage"]
            st.metric(
                "Max Loss Usage", 
                f"{max_usage:.1f}%",
                delta=f"{max_usage-50:.1f}% from safe zone"
            )
        
        with status_col4:
            profit_progress = compliance_status["profit_target_progress"]
            st.metric(
                "Profit Target",
                f"{profit_progress:.1f}%",
                delta=f"{profit_progress:.1f}% complete"
            )
        
        # Rules display
        st.markdown("---")
        st.subheader("📋 Current Rules")
        
        rules = compliance_status["rules"]
        rule_col1, rule_col2 = st.columns(2)
        
        with rule_col1:
            st.markdown("**Loss Limits:**")
            st.write(f"• Daily Loss Limit: ${rules.daily_loss_limit:,.0f}")
            st.write(f"• Max Loss Limit: ${rules.max_loss_limit:,.0f}")
            st.write(f"• Profit Target: ${rules.profit_target:,.0f}")
            
            st.markdown("**Position Limits:**")
            st.write(f"• Max Position Size: {rules.max_position_size}")
            st.write(f"• Max Contracts/Side: {rules.max_contracts_per_side}")
        
        with rule_col2:
            st.markdown("**Restrictions:**")
            st.write(f"• Forbidden: {', '.join(rules.forbidden_instruments)}")
            st.write(f"• News Blackout: {rules.news_blackout_minutes} minutes")
            st.write(f"• Consistency Rule: {'Yes' if rules.consistency_rule else 'No'}")
            st.write(f"• Weekend Holding: {'Allowed' if rules.weekend_holding_allowed else 'Forbidden'}")
        
        # Position sizing calculator
        st.markdown("---")
        st.subheader("🎯 Position Size Calculator")
        
        symbol = st.text_input("Symbol", value="ES", key="calc_symbol")
        price = st.number_input("Current Price", value=4500.0, key="calc_price")
        
        if st.button("Calculate Max Position Size", key="calc_position"):
            max_position = compliance_engine.get_maximum_position_size(
                selected_firm.lower(), symbol, account_data, price
            )
            
            if max_position["max_contracts"] > 0:
                st.success(f"✅ Maximum Position Size: **{max_position['max_contracts']} contracts**")
                st.info(f"Limited by: {max_position['limiting_factor'].replace('_', ' ').title()}")
                
                # Show all constraints
                with st.expander("View All Constraints"):
                    for constraint, value in max_position["constraints"].items():
                        st.write(f"• {constraint.replace('_', ' ').title()}: {value:.1f} contracts")
            else:
                st.error("❌ No trading allowed - compliance limits exceeded")
        
        # Compliance test
        st.markdown("---")
        st.subheader("🧪 Test Trade Compliance")
        
        test_col1, test_col2 = st.columns(2)
        
        with test_col1:
            test_symbol = st.text_input("Test Symbol", value="ES", key="test_symbol")
            test_quantity = st.number_input("Test Quantity", value=2, key="test_quantity")
        
        with test_col2:
            test_side = st.selectbox("Side", ["BUY", "SELL"], key="test_side")
            test_risk = st.number_input("Risk Amount ($)", value=100.0, key="test_risk")
        
        if st.button("Check Trade Compliance", key="test_compliance"):
            trade_data = {
                "symbol": test_symbol,
                "quantity": test_quantity,
                "side": test_side,
                "risk_amount": test_risk
            }
            
            violations = compliance_engine.check_trade_compliance(
                selected_firm.lower(), trade_data, account_data
            )
            
            if violations:
                st.error(f"❌ **{len(violations)} Compliance Violation(s) Found:**")
                for violation in violations:
                    severity_color = {
                        ViolationSeverity.WARNING: "yellow",
                        ViolationSeverity.STOP: "orange", 
                        ViolationSeverity.BREACH: "red"
                    }[violation.severity]
                    
                    st.markdown(f"""
                    <div style="
                        padding: 0.5rem;
                        background-color: {severity_color};
                        color: white;
                        border-radius: 4px;
                        margin: 0.25rem 0;
                    ">
                        <strong>{violation.severity.value.upper()}:</strong> {violation.message}
                        <br><em>Action: {violation.suggested_action}</em>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ **Trade passes all compliance checks!**")
                st.balloons()

# Example usage for integration
if __name__ == "__main__":
    # Test the compliance engine
    engine = PropFirmComplianceEngine()
    
    # Test Apex rules
    test_account = {
        "account_size": 25000,
        "daily_pnl": -800,
        "max_drawdown": -1500,
        "total_pnl": 2000
    }
    
    test_trade = {
        "symbol": "ES",
        "quantity": 3,
        "side": "BUY",
        "risk_amount": 150
    }
    
    violations = engine.check_trade_compliance("apex", test_trade, test_account)
    print(f"Found {len(violations)} violations")
    
    for violation in violations:
        print(f"- {violation.severity.value}: {violation.message}")
        
    status = engine.get_real_time_compliance_status("apex", test_account)
    print(f"Compliance status: {status['status']}")
    print(f"Daily loss usage: {status['daily_loss_usage']:.1f}%")
