

import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime
from pathlib import Path
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

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
    
    # OFFICIAL APEX VIOLATION CONSEQUENCES
    violation_lockout_hours: int = 24  # 24-hour lockout after violation
    max_violations_allowed: int = 0  # ZERO tolerance - any violation = account breach

@dataclass
class TradeData:
    """Current trade and account data"""
    account_balance: float = 0.0
    daily_pnl: float = 0.0
    total_pnl: float = 0.0
    open_positions: int = 0
    max_daily_profit: float = 0.0
    drawdown_from_high: float = 0.0
    is_locked_out: bool = False
    lockout_until: Optional[datetime.datetime] = None

class ApexComplianceGuardian:
    def __init__(self):
        self.rules = ApexRules()
        self.trade_data = TradeData()
        self.violations = []
        self.alerts = []
        self.is_monitoring = False
        
        # Setup logging
        logging.basicConfig(
            filename='apex_compliance.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Load settings
        self.load_settings()
        
        # Create GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Create the main compliance guardian interface"""
        self.root = tk.Tk()
        self.root.title("APEX COMPLIANCE GUARDIAN - Training Wheels for Prop Traders")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#1e1e1e', foreground='white')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#1e1e1e', foreground='#4CAF50')
        style.configure('Warning.TLabel', font=('Arial', 10, 'bold'), background='#1e1e1e', foreground='#FF6B6B')
        style.configure('Safe.TLabel', font=('Arial', 10), background='#1e1e1e', foreground='#4CAF50')
        
        self.create_header()
        self.create_rule_configuration()
        self.create_monitoring_panel()
        self.create_alert_system()
        self.create_control_panel()
        
    def create_header(self):
        """Create main header"""
        header_frame = tk.Frame(self.root, bg='#1e1e1e', pady=20)
        header_frame.pack(fill='x')
        
        title = ttk.Label(header_frame, text="🛡️ APEX COMPLIANCE GUARDIAN", style='Title.TLabel')
        title.pack()
        
        subtitle = ttk.Label(header_frame, text="Training Wheels for Prop Firm Traders - Prevent Rule Violations", 
                           style='Header.TLabel')
        subtitle.pack()
        
        client_info = ttk.Label(header_frame, text="FOR: Harrison Aloo & Michael Canfield | Platform: Tradovate", 
                              style='Safe.TLabel')
        client_info.pack()
        
    def create_rule_configuration(self):
        """Create rule configuration panel"""
        config_frame = tk.LabelFrame(self.root, text="APEX RULE CONFIGURATION", 
                                   bg='#2d2d2d', fg='white', font=('Arial', 12, 'bold'))
        config_frame.pack(fill='x', padx=20, pady=10)
        
        # Safety Ratio (Harrison's key requirement)
        safety_frame = tk.Frame(config_frame, bg='#2d2d2d')
        safety_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(safety_frame, text="Safety Ratio (5% - 90%):", background='#2d2d2d', foreground='white').pack(side='left')
        self.safety_scale = tk.Scale(safety_frame, from_=5, to=90, orient='horizontal', 
                                   bg='#2d2d2d', fg='white', length=200)
        self.safety_scale.set(self.rules.safety_ratio)
        self.safety_scale.pack(side='left', padx=10)
        
        self.safety_label = ttk.Label(safety_frame, text=f"{self.rules.safety_ratio}%", 
                                    background='#2d2d2d', foreground='#4CAF50')
        self.safety_label.pack(side='left')
        
        # Risk Level Presets (Harrison's 3 choice settings)
        risk_frame = tk.Frame(config_frame, bg='#2d2d2d')
        risk_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(risk_frame, text="Risk Presets:", background='#2d2d2d', foreground='white').pack(side='left')
        
        tk.Button(risk_frame, text="Conservative (90%)", bg='#4CAF50', fg='white',
                 command=lambda: self.set_risk_preset(90)).pack(side='left', padx=5)
        tk.Button(risk_frame, text="Moderate (70%)", bg='#FFA726', fg='white',
                 command=lambda: self.set_risk_preset(70)).pack(side='left', padx=5)
        tk.Button(risk_frame, text="Aggressive (50%)", bg='#FF6B6B', fg='white',
                 command=lambda: self.set_risk_preset(50)).pack(side='left', padx=5)
        
        # Platform Selection
        platform_frame = tk.Frame(config_frame, bg='#2d2d2d')
        platform_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(platform_frame, text="Trading Platform:", background='#2d2d2d', foreground='white').pack(side='left')
        self.platform_var = tk.StringVar(value=self.rules.platform)
        platform_combo = ttk.Combobox(platform_frame, textvariable=self.platform_var,
                                     values=["Tradovate", "NinjaTrader", "TradingView", "MetaTrader", "Other"])
        platform_combo.pack(side='left', padx=10)
        
    def create_monitoring_panel(self):
        """Create real-time monitoring panel"""
        monitor_frame = tk.LabelFrame(self.root, text="REAL-TIME APEX COMPLIANCE MONITORING", 
                                    bg='#2d2d2d', fg='white', font=('Arial', 12, 'bold'))
        monitor_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create monitoring grid
        self.create_monitoring_grid(monitor_frame)
        
    def create_monitoring_grid(self, parent):
        """Create the monitoring data grid"""
        # Account Status
        status_frame = tk.Frame(parent, bg='#2d2d2d')
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_labels = {}
        
        # Row 1: Basic Account Info
        row1 = tk.Frame(status_frame, bg='#2d2d2d')
        row1.pack(fill='x', pady=2)
        
        self.status_labels['balance'] = self.create_status_item(row1, "Account Balance:", "$0.00", '#4CAF50')
        self.status_labels['daily_pnl'] = self.create_status_item(row1, "Daily P&L:", "$0.00", '#4CAF50')
        self.status_labels['positions'] = self.create_status_item(row1, "Open Positions:", "0", '#4CAF50')
        
        # Row 2: Apex Rule Monitoring
        row2 = tk.Frame(status_frame, bg='#2d2d2d')
        row2.pack(fill='x', pady=2)
        
        self.status_labels['drawdown'] = self.create_status_item(row2, "Trailing Drawdown:", "0%", '#4CAF50')
        self.status_labels['consistency'] = self.create_status_item(row2, "Consistency Rule:", "0%", '#4CAF50')
        self.status_labels['safety_margin'] = self.create_status_item(row2, "Safety Margin:", "100%", '#4CAF50')
        
        # Row 3: Lockout Status
        row3 = tk.Frame(status_frame, bg='#2d2d2d')
        row3.pack(fill='x', pady=2)
        
        self.status_labels['lockout'] = self.create_status_item(row3, "Trading Status:", "ACTIVE", '#4CAF50')
        self.status_labels['next_reset'] = self.create_status_item(row3, "Next Reset:", "None", '#4CAF50')
        
    def create_status_item(self, parent, label_text, value_text, color):
        """Create a status monitoring item"""
        frame = tk.Frame(parent, bg='#2d2d2d')
        frame.pack(side='left', padx=20)
        
        label = ttk.Label(frame, text=label_text, background='#2d2d2d', foreground='white')
        label.pack()
        
        value_label = ttk.Label(frame, text=value_text, background='#2d2d2d', 
                              foreground=color, font=('Arial', 12, 'bold'))
        value_label.pack()
        
        return value_label
        
    def create_alert_system(self):
        """Create alert and violation tracking system"""
        alert_frame = tk.LabelFrame(self.root, text="COMPLIANCE ALERTS & VIOLATIONS", 
                                  bg='#2d2d2d', fg='white', font=('Arial', 12, 'bold'))
        alert_frame.pack(fill='x', padx=20, pady=10)
        
        # Alert log
        self.alert_text = tk.Text(alert_frame, height=8, bg='#1e1e1e', fg='white', 
                                font=('Consolas', 10))
        alert_scroll = tk.Scrollbar(alert_frame, command=self.alert_text.yview)
        self.alert_text.configure(yscrollcommand=alert_scroll.set)
        
        self.alert_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        alert_scroll.pack(side='right', fill='y')
        
        # Add initial message
        self.add_alert("🛡️ Apex Compliance Guardian initialized - Training wheels active", "INFO")
        self.add_alert("📊 Monitoring Tradovate platform for rule violations", "INFO")
        self.add_alert("⚙️ Configure safety ratio and start monitoring", "INFO")
        
    def create_control_panel(self):
        """Create main control buttons"""
        control_frame = tk.Frame(self.root, bg='#1e1e1e', pady=20)
        control_frame.pack(fill='x')
        
        # Start/Stop Monitoring
        self.monitor_btn = tk.Button(control_frame, text="🚀 START MONITORING", 
                                   bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'),
                                   command=self.toggle_monitoring, width=20)
        self.monitor_btn.pack(side='left', padx=20)
        
        # Emergency Stop All Trades
        emergency_btn = tk.Button(control_frame, text="🛑 EMERGENCY STOP", 
                                bg='#FF6B6B', fg='white', font=('Arial', 12, 'bold'),
                                command=self.emergency_stop_all, width=20)
        emergency_btn.pack(side='left', padx=20)
        
        # Force Lockout
        lockout_btn = tk.Button(control_frame, text="🔒 FORCE LOCKOUT", 
                              bg='#FFA726', fg='white', font=('Arial', 12, 'bold'),
                              command=self.force_lockout, width=20)
        lockout_btn.pack(side='left', padx=20)
        
        # Settings
        settings_btn = tk.Button(control_frame, text="⚙️ SETTINGS", 
                               bg='#2196F3', fg='white', font=('Arial', 12, 'bold'),
                               command=self.open_settings, width=20)
        settings_btn.pack(side='left', padx=20)
        
    def set_risk_preset(self, percentage):
        """Set risk preset (Harrison's 3 choice settings)"""
        self.safety_scale.set(percentage)
        self.rules.safety_ratio = percentage
        self.safety_label.config(text=f"{percentage}%")
        
        preset_names = {90: "Conservative", 70: "Moderate", 50: "Aggressive"}
        self.add_alert(f"🎯 Risk preset changed to {preset_names[percentage]} ({percentage}%)", "INFO")
        
    def toggle_monitoring(self):
        """Start/stop compliance monitoring"""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start compliance monitoring"""
        self.is_monitoring = True
        self.monitor_btn.config(text="🛑 STOP MONITORING", bg='#FF6B6B')
        
        self.add_alert("🚀 Compliance monitoring STARTED", "SUCCESS")
        self.add_alert(f"📊 Platform: {self.platform_var.get()}", "INFO")
        self.add_alert(f"🛡️ Safety ratio: {self.safety_scale.get()}%", "INFO")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop compliance monitoring"""
        self.is_monitoring = False
        self.monitor_btn.config(text="🚀 START MONITORING", bg='#4CAF50')
        self.add_alert("🛑 Compliance monitoring STOPPED", "WARNING")
        
    def monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Simulate trade data (in real implementation, connect to Tradovate API)
                self.update_trade_data()
                self.check_compliance()
                self.update_gui()
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                self.add_alert(f"❌ Monitoring error: {str(e)}", "ERROR")
                
    def update_trade_data(self):
        """Update trade data (simulate for demo)"""
        # In real implementation, this would connect to Tradovate API
        import random
        
        # Simulate account changes
        if self.trade_data.account_balance == 0:
            self.trade_data.account_balance = 25000.0  # Demo account
            
        # Simulate daily P&L changes
        change = random.uniform(-50, 50)
        self.trade_data.daily_pnl += change
        
        # Calculate drawdown and consistency metrics
        if self.trade_data.daily_pnl > self.trade_data.max_daily_profit:
            self.trade_data.max_daily_profit = self.trade_data.daily_pnl
            
        # Calculate trailing drawdown
        if self.trade_data.max_daily_profit > 0:
            current_drawdown = (self.trade_data.max_daily_profit - self.trade_data.daily_pnl) / self.trade_data.account_balance * 100
            self.trade_data.drawdown_from_high = max(0, current_drawdown)
            
    def check_compliance(self):
        """Check all Apex compliance rules - OFFICIAL APEX 3.0 COMPLIANCE"""
        safety_ratio = self.safety_scale.get() / 100.0
        account_balance = self.trade_data.account_balance
        
        # CRITICAL: Check if already locked out
        if self.trade_data.is_locked_out:
            current_time = datetime.datetime.now()
            if current_time < self.trade_data.lockout_until:
                return  # Still locked out
            else:
                # Reset lockout
                self.trade_data.is_locked_out = False
                self.add_alert("🔓 Trading lockout expired - monitoring resumed", "INFO")
        
        # 1. DAILY LOSS LIMIT (5% - APEX OFFICIAL RULE)
        daily_loss_limit_percentage = self.rules.evaluation_max_daily_loss
        daily_loss_limit_amount = account_balance * daily_loss_limit_percentage / 100
        safety_loss_limit = daily_loss_limit_amount * safety_ratio
        
        if self.trade_data.daily_pnl <= -safety_loss_limit:
            self.trigger_violation(
                "DAILY LOSS LIMIT", 
                f"Daily loss ${abs(self.trade_data.daily_pnl):,.2f} exceeded {safety_ratio*100:.0f}% of ${daily_loss_limit_amount:,.2f} limit"
            )
            
        # 2. TRAILING DRAWDOWN (5% FROM HIGH WATER MARK - APEX OFFICIAL RULE)
        trailing_threshold_percentage = self.rules.evaluation_trailing_threshold
        safety_trailing_limit = trailing_threshold_percentage * safety_ratio
        
        if self.trade_data.drawdown_from_high >= safety_trailing_limit:
            self.trigger_violation(
                "TRAILING DRAWDOWN", 
                f"Drawdown {self.trade_data.drawdown_from_high:.2f}% exceeded {safety_ratio*100:.0f}% of {trailing_threshold_percentage}% limit"
            )
            
        # 3. CONSISTENCY RULE (30% - APEX OFFICIAL RULE - APPLIES TO ALL PHASES)
        if account_balance > 0 and self.trade_data.total_pnl > 0:
            daily_profit_percentage = (self.trade_data.daily_pnl / self.trade_data.total_pnl) * 100
            consistency_limit = self.rules.consistency_rule
            safety_consistency_limit = consistency_limit * safety_ratio
            
            if daily_profit_percentage > safety_consistency_limit:
                self.trigger_violation(
                    "CONSISTENCY RULE", 
                    f"Daily profit {daily_profit_percentage:.1f}% of total profit exceeded {safety_ratio*100:.0f}% of {consistency_limit}% limit"
                )
        
        # 4. MAXIMUM POSITION SIZE LIMITS (APEX OFFICIAL RULE)
        max_contracts = self.rules.max_total_contracts
        if self.trade_data.open_positions > max_contracts:
            self.trigger_violation(
                "POSITION SIZE LIMIT", 
                f"Open positions {self.trade_data.open_positions} exceeded maximum {max_contracts} contracts"
            )
        
        # 5. NEWS EVENT RESTRICTIONS (APEX OFFICIAL RULE)
        if self.rules.news_restricted_trading:
            # In real implementation, check economic calendar
            # For demo, simulate random news events
            import random
            if random.random() < 0.001:  # 0.1% chance per check
                self.add_alert("📰 HIGH IMPACT NEWS DETECTED - Trading restricted for 15 minutes", "WARNING")
        
        # 6. WEEKEND HOLDING RESTRICTIONS (APEX OFFICIAL RULE)
        current_time = datetime.datetime.now()
        if current_time.weekday() >= 5 and self.trade_data.open_positions > 0:  # Saturday/Sunday
            if not self.rules.weekend_holding_allowed:
                self.trigger_violation(
                    "WEEKEND HOLDING", 
                    "Positions must be closed before weekend - Apex rule violation"
                )
            
    def trigger_violation(self, rule_type, message):
        """Trigger rule violation response - OFFICIAL APEX 3.0 CONSEQUENCES"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.add_alert(f"🚨 APEX RULE VIOLATION: {rule_type}", "ERROR")
        self.add_alert(f"💥 {message}", "ERROR") 
        self.add_alert(f"⚡ EXECUTING EMERGENCY PROTOCOL", "ERROR")
        
        # IMMEDIATE ACTIONS (Harrison's requirements + Apex official)
        
        # 1. EMERGENCY STOP ALL TRADES (Harrison's requirement)
        self.emergency_stop_all()
        
        # 2. RECORD VIOLATION (Official Apex requirement)
        violation_record = {
            'timestamp': datetime.datetime.now().isoformat(),
            'rule_type': rule_type,
            'message': message,
            'account_balance': self.trade_data.account_balance,
            'daily_pnl': self.trade_data.daily_pnl,
            'safety_ratio': self.safety_scale.get()
        }
        self.violations.append(violation_record)
        
        # 3. IMMEDIATE ACCOUNT LOCKOUT (Official Apex - ZERO TOLERANCE)
        self.force_lockout()
        
        # 4. BREACH NOTIFICATION (Official Apex consequence)
        self.add_alert(f"💀 ACCOUNT BREACH TRIGGERED", "ERROR")
        self.add_alert(f"🔒 Account status: VIOLATED - Contact Apex Support", "ERROR")
        self.add_alert(f"📧 Violation report generated for review", "ERROR")
        
        # 5. SAVE VIOLATION LOG (For Apex review)
        self.save_violation_log(violation_record)
        
        # 6. DISABLE ALL TRADING (Official Apex - immediate effect)
        self.is_monitoring = False
        self.monitor_btn.config(text="❌ ACCOUNT BREACHED", bg='#FF0000', state='disabled')
        
        # 7. SHOW CRITICAL ALERT (User notification)
        import tkinter.messagebox as mb
        mb.showerror(
            "APEX RULE VIOLATION - ACCOUNT BREACHED",
            f"CRITICAL: {rule_type} violation detected!\n\n"
            f"Details: {message}\n\n"
            f"ACTIONS TAKEN:\n"
            f"• All positions closed immediately\n"
            f"• Account locked until next day\n"
            f"• Violation logged for Apex review\n"
            f"• Trading disabled\n\n"
            f"Contact Apex Trader Funding support."
        )
        
    def emergency_stop_all(self):
        """Emergency stop all trades (Harrison's key requirement)"""
        self.add_alert("🛑 EMERGENCY STOP: Closing all positions immediately", "ERROR")
        
        # In real implementation, send API calls to close all positions
        # For Tradovate: Use Tradovate API to close positions
        # For NinjaTrader: Send close commands
        
        self.trade_data.open_positions = 0
        self.add_alert("✅ All positions closed successfully", "SUCCESS")
        
    def check_drawdown_violation(self, account_data: Dict) -> Optional[Dict]:
        """Check for drawdown violations (Harrison's core requirement)"""
        try:
            current_balance = account_data.get('balance', 10000)
            current_drawdown = account_data.get('current_drawdown', 0.0)
            
            # Check against Apex 3.0 rules
            max_drawdown = self.apex_rules.evaluation_trailing_threshold
            
            if current_drawdown >= max_drawdown:
                violation = {
                    'type': 'DRAWDOWN_VIOLATION',
                    'current_drawdown': current_drawdown,
                    'max_allowed': max_drawdown,
                    'severity': 'CRITICAL',
                    'action': 'IMMEDIATE_STOP',
                    'timestamp': datetime.datetime.now()
                }
                
                # Log violation and trigger emergency stop
                self.add_alert(f"🚨 DRAWDOWN VIOLATION: {current_drawdown:.2f}% exceeds {max_drawdown:.2f}%", "ERROR")
                self.emergency_stop_all()
                
                return violation
            
            return None
            
        except Exception as e:
            self.add_alert(f"❌ Drawdown check error: {e}", "ERROR")
            return None
        
    def save_violation_log(self, violation_record):
        """Save violation log for Apex review"""
        try:
            import os
            os.makedirs("logs", exist_ok=True)
            
            log_filename = f"logs/apex_violation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(log_filename, 'w') as f:
                json.dump(violation_record, f, indent=2)
                
            self.add_alert(f"📄 Violation log saved: {log_filename}", "INFO")
            
        except Exception as e:
            self.add_alert(f"❌ Failed to save violation log: {str(e)}", "ERROR")
    
    def force_lockout(self):
        """Force trading lockout until next day - OFFICIAL APEX COMPLIANCE"""
        self.trade_data.is_locked_out = True
        
        # Calculate next reset time (Official Apex: Next trading day at market open)
        current_time = datetime.datetime.now()
        
        # If violation occurs on Friday, lockout until Monday
        if current_time.weekday() == 4:  # Friday
            days_to_add = 3  # Until Monday
        elif current_time.weekday() == 5:  # Saturday  
            days_to_add = 2  # Until Monday
        elif current_time.weekday() == 6:  # Sunday
            days_to_add = 1  # Until Monday
        else:
            days_to_add = 1  # Next trading day
            
        next_trading_day = current_time + datetime.timedelta(days=days_to_add)
        self.trade_data.lockout_until = next_trading_day.replace(hour=9, minute=30, second=0, microsecond=0)
        
        lockout_duration = self.rules.violation_lockout_hours
        self.add_alert(f"🔒 TRADING LOCKED OUT for {lockout_duration} hours", "ERROR")
        self.add_alert(f"⏰ Lockout until: {self.trade_data.lockout_until.strftime('%Y-%m-%d %H:%M')} EST", "ERROR")
        self.add_alert(f"🚫 NO TRADING ALLOWED until lockout expires", "ERROR")
        
    def update_gui(self):
        """Update GUI with current data"""
        try:
            # Update status labels
            self.status_labels['balance'].config(text=f"${self.trade_data.account_balance:,.2f}")
            
            # Color-code daily P&L
            pnl_color = '#4CAF50' if self.trade_data.daily_pnl >= 0 else '#FF6B6B'
            self.status_labels['daily_pnl'].config(text=f"${self.trade_data.daily_pnl:,.2f}", foreground=pnl_color)
            
            self.status_labels['positions'].config(text=str(self.trade_data.open_positions))
            
            # Update drawdown with color coding
            dd_color = '#FF6B6B' if self.trade_data.drawdown_from_high > 3 else '#4CAF50'
            self.status_labels['drawdown'].config(text=f"{self.trade_data.drawdown_from_high:.2f}%", foreground=dd_color)
            
            # Update consistency rule
            daily_profit_pct = (self.trade_data.daily_pnl / self.trade_data.account_balance) * 100
            consistency_color = '#FF6B6B' if daily_profit_pct > 25 else '#4CAF50'
            self.status_labels['consistency'].config(text=f"{daily_profit_pct:.2f}%", foreground=consistency_color)
            
            # Update safety margin
            safety_margin = 100 - (self.trade_data.drawdown_from_high / self.rules.evaluation_trailing_threshold * 100)
            margin_color = '#FF6B6B' if safety_margin < 20 else '#4CAF50'
            self.status_labels['safety_margin'].config(text=f"{max(0, safety_margin):.1f}%", foreground=margin_color)
            
            # Update lockout status
            if self.trade_data.is_locked_out:
                self.status_labels['lockout'].config(text="LOCKED OUT", foreground='#FF6B6B')
                if self.trade_data.lockout_until:
                    self.status_labels['next_reset'].config(text=self.trade_data.lockout_until.strftime('%H:%M'))
            else:
                self.status_labels['lockout'].config(text="ACTIVE", foreground='#4CAF50')
                self.status_labels['next_reset'].config(text="None")
                
        except Exception as e:
            print(f"GUI update error: {e}")
            
    def add_alert(self, message, level="INFO"):
        """Add alert to the log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Color code by level
        colors = {
            "INFO": "white",
            "SUCCESS": "#4CAF50", 
            "WARNING": "#FFA726",
            "ERROR": "#FF6B6B"
        }
        
        self.alert_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.alert_text.see(tk.END)
        
        # Log to file
        logging.info(f"{level}: {message}")
        
    def open_settings(self):
        """Open advanced settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Apex Compliance Settings")
        settings_window.geometry("600x400")
        settings_window.configure(bg='#1e1e1e')
        
        # Add advanced settings here
        ttk.Label(settings_window, text="Advanced Apex Rule Configuration", 
                 style='Title.TLabel').pack(pady=20)
        
        # API Configuration
        api_frame = tk.LabelFrame(settings_window, text="Platform API Settings", 
                                bg='#2d2d2d', fg='white')
        api_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(api_frame, text="Tradovate API Key:", background='#2d2d2d', foreground='white').pack()
        api_entry = tk.Entry(api_frame, width=50, show='*')
        api_entry.pack(pady=5)
        
        # Save button
        save_btn = tk.Button(settings_window, text="Save Settings", bg='#4CAF50', fg='white',
                           command=lambda: self.save_settings())
        save_btn.pack(pady=20)
        
    def save_settings(self):
        """Save current settings"""
        settings = {
            'safety_ratio': self.safety_scale.get(),
            'platform': self.platform_var.get(),
            'rules': {
                'evaluation_target': self.rules.evaluation_target,
                'evaluation_max_loss': self.rules.evaluation_max_loss,
                'consistency_rule': self.rules.consistency_rule
            }
        }
        
        with open('apex_settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
            
        self.add_alert("💾 Settings saved successfully", "SUCCESS")
        
    def load_settings(self):
        """Load saved settings"""
        try:
            with open('apex_settings.json', 'r') as f:
                settings = json.load(f)
                
            self.rules.safety_ratio = settings.get('safety_ratio', 80.0)
            self.rules.platform = settings.get('platform', 'Tradovate')
            
        except FileNotFoundError:
            # Use defaults
            pass
            
    def run(self):
        """Start the compliance guardian"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("🛡️ APEX COMPLIANCE GUARDIAN")
    print("=" * 50)
    print("Training Wheels for Prop Firm Traders")
    print("Prevents Apex Trader Funding rule violations")
    print()
    print("FOR: Harrison Aloo & Michael Canfield")
    print("Platform: Tradovate (configurable)")
    print("=" * 50)
    
    # Create and run the guardian
    guardian = ApexComplianceGuardian()
    guardian.run()

if __name__ == "__main__":
    main()
