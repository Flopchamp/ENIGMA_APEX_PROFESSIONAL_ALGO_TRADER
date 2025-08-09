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
    last_update: datetime

class MultiChartControlPanel:
    """Michael's 6-Chart Visual Control Panel"""
    
    def __init__(self):
        self.chart_data: Dict[int, ChartStatus] = {}
        self.total_margin_remaining = 0.0
        self.total_margin_percentage = 100.0
        self.is_monitoring = False
        
        # Initialize 6 charts with demo data
        self.initialize_charts()
        
        # Setup GUI
        self.setup_gui()
        
        # Start monitoring thread
        self.start_monitoring()
        
    def initialize_charts(self):
        """Initialize 6 trading charts with sample data"""
        chart_configs = [
            {"id": 1, "name": "ES-Account-1", "balance": 25000},
            {"id": 2, "name": "ES-Account-2", "balance": 50000},
            {"id": 3, "name": "NQ-Account-1", "balance": 25000},
            {"id": 4, "name": "NQ-Account-2", "balance": 50000},
            {"id": 5, "name": "YM-Account-1", "balance": 25000},
            {"id": 6, "name": "RTY-Account-1", "balance": 25000}
        ]
        
        for config in chart_configs:
            self.chart_data[config["id"]] = ChartStatus(
                chart_id=config["id"],
                account_name=config["name"],
                account_balance=config["balance"],
                daily_pnl=0.0,
                margin_used=0.0,
                margin_remaining=config["balance"] * 0.8,  # 80% available
                margin_percentage=80.0,
                open_positions=0,
                is_active=True,
                risk_level="SAFE",
                last_signal="NONE",
                last_update=datetime.now()
            )
    
    def setup_gui(self):
        """Create Michael's visual control panel"""
        self.root = tk.Tk()
        self.root.title("🎯 MICHAEL'S 6-CHART APEX CONTROL PANEL")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Main header
        self.create_header()
        
        # Most important indicator - Overall margin remaining
        self.create_overall_margin_indicator()
        
        # 6-chart grid (2 rows x 3 columns)
        self.create_chart_grid()
        
        # Control buttons
        self.create_control_buttons()
        
    def create_header(self):
        """Create main header"""
        header_frame = tk.Frame(self.root, bg='#1a1a1a', pady=10)
        header_frame.pack(fill='x')
        
        title = tk.Label(header_frame, text="🎯 MICHAEL'S 6-CHART APEX CONTROL PANEL", 
                        bg='#1a1a1a', fg='#00ff88', font=('Arial', 18, 'bold'))
        title.pack()
        
        subtitle = tk.Label(header_frame, text="Training Wheels for Multi-Account Prop Trading", 
                           bg='#1a1a1a', fg='white', font=('Arial', 12))
        subtitle.pack()
        
    def create_overall_margin_indicator(self):
        """Create the MOST IMPORTANT indicator - Overall margin remaining"""
        margin_frame = tk.Frame(self.root, bg='#2d2d2d', relief='raised', bd=3)
        margin_frame.pack(fill='x', padx=20, pady=10)
        
        # Title
        title_label = tk.Label(margin_frame, text="📊 OVERALL MARGIN REMAINING (MOST IMPORTANT)", 
                              bg='#2d2d2d', fg='#ffaa00', font=('Arial', 14, 'bold'))
        title_label.pack(pady=5)
        
        # Margin display frame
        display_frame = tk.Frame(margin_frame, bg='#2d2d2d')
        display_frame.pack(pady=10)
        
        # Percentage display
        self.margin_percentage_label = tk.Label(display_frame, text="85.2%", 
                                               bg='#2d2d2d', fg='#00ff88', 
                                               font=('Arial', 36, 'bold'))
        self.margin_percentage_label.pack(side='left', padx=20)
        
        # Dollar amount display
        self.margin_amount_label = tk.Label(display_frame, text="$127,500", 
                                           bg='#2d2d2d', fg='#00ff88', 
                                           font=('Arial', 24, 'bold'))
        self.margin_amount_label.pack(side='left', padx=20)
        
        # Status indicator
        self.overall_status_label = tk.Label(display_frame, text="SAFE TRADING", 
                                            bg='#00ff88', fg='black', 
                                            font=('Arial', 16, 'bold'), padx=20, pady=5)
        self.overall_status_label.pack(side='left', padx=20)
        
    def create_chart_grid(self):
        """Create 6-chart grid with Red/Green/Yellow boxes"""
        grid_frame = tk.Frame(self.root, bg='#1a1a1a')
        grid_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.chart_frames = {}
        self.chart_labels = {}
        self.chart_switches = {}
        
        # Create 2 rows x 3 columns
        for row in range(2):
            for col in range(3):
                chart_id = row * 3 + col + 1
                self.create_chart_box(grid_frame, chart_id, row, col)
                
    def create_chart_box(self, parent, chart_id: int, row: int, col: int):
        """Create individual chart control box"""
        chart_data = self.chart_data[chart_id]
        
        # Main chart frame
        chart_frame = tk.Frame(parent, bg='#2d2d2d', relief='raised', bd=2)
        chart_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Configure grid weights
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        self.chart_frames[chart_id] = chart_frame
        
        # Chart header with on/off switch
        header_frame = tk.Frame(chart_frame, bg='#2d2d2d')
        header_frame.pack(fill='x', pady=5)
        
        # Chart name
        name_label = tk.Label(header_frame, text=chart_data.account_name, 
                             bg='#2d2d2d', fg='white', font=('Arial', 12, 'bold'))
        name_label.pack(side='left', padx=10)
        
        # On/off switch
        switch_var = tk.BooleanVar(value=chart_data.is_active)
        switch = tk.Checkbutton(header_frame, text="ON", variable=switch_var,
                               bg='#2d2d2d', fg='#00ff88', selectcolor='#4a4a4a',
                               font=('Arial', 10, 'bold'),
                               command=lambda cid=chart_id: self.toggle_chart(cid))
        switch.pack(side='right', padx=10)
        self.chart_switches[chart_id] = switch_var
        
        # Status display (Red/Green/Yellow box)
        status_frame = tk.Frame(chart_frame, height=100, bg='#00ff88')  # Default green
        status_frame.pack(fill='x', padx=10, pady=5)
        status_frame.pack_propagate(False)
        
        # Risk level text
        risk_label = tk.Label(status_frame, text="SAFE TRADING", 
                             bg='#00ff88', fg='black', font=('Arial', 14, 'bold'))
        risk_label.pack(expand=True)
        
        # Margin info
        margin_info = tk.Label(status_frame, text=f"{chart_data.margin_percentage:.1f}% | ${chart_data.margin_remaining:,.0f}", 
                              bg='#00ff88', fg='black', font=('Arial', 12))
        margin_info.pack()
        
        self.chart_labels[chart_id] = {
            'status_frame': status_frame,
            'risk_label': risk_label,
            'margin_info': margin_info
        }
        
        # Account details
        details_frame = tk.Frame(chart_frame, bg='#2d2d2d')
        details_frame.pack(fill='x', padx=10, pady=5)
        
        # Balance
        balance_label = tk.Label(details_frame, text=f"Balance: ${chart_data.account_balance:,.0f}", 
                                bg='#2d2d2d', fg='white', font=('Arial', 10))
        balance_label.pack(anchor='w')
        
        # Daily P&L
        pnl_color = '#00ff88' if chart_data.daily_pnl >= 0 else '#ff4444'
        pnl_label = tk.Label(details_frame, text=f"Daily P&L: ${chart_data.daily_pnl:,.2f}", 
                            bg='#2d2d2d', fg=pnl_color, font=('Arial', 10))
        pnl_label.pack(anchor='w')
        
        # Open positions
        positions_label = tk.Label(details_frame, text=f"Positions: {chart_data.open_positions}", 
                                  bg='#2d2d2d', fg='white', font=('Arial', 10))
        positions_label.pack(anchor='w')
        
        # Last signal
        signal_label = tk.Label(details_frame, text=f"Signal: {chart_data.last_signal}", 
                               bg='#2d2d2d', fg='#ffaa00', font=('Arial', 10))
        signal_label.pack(anchor='w')
        
    def create_control_buttons(self):
        """Create main control buttons"""
        control_frame = tk.Frame(self.root, bg='#1a1a1a', pady=20)
        control_frame.pack(fill='x')
        
        # Emergency stop all
        emergency_btn = tk.Button(control_frame, text="🛑 EMERGENCY STOP ALL", 
                                 bg='#ff4444', fg='white', font=('Arial', 14, 'bold'),
                                 command=self.emergency_stop_all, width=20, height=2)
        emergency_btn.pack(side='left', padx=20)
        
        # Pause all monitoring
        pause_btn = tk.Button(control_frame, text="⏸️ PAUSE ALL", 
                             bg='#ffaa00', fg='black', font=('Arial', 14, 'bold'),
                             command=self.pause_all_monitoring, width=15, height=2)
        pause_btn.pack(side='left', padx=20)
        
        # Resume all monitoring
        resume_btn = tk.Button(control_frame, text="▶️ RESUME ALL", 
                              bg='#00ff88', fg='black', font=('Arial', 14, 'bold'),
                              command=self.resume_all_monitoring, width=15, height=2)
        resume_btn.pack(side='left', padx=20)
        
        # Settings
        settings_btn = tk.Button(control_frame, text="⚙️ SETTINGS", 
                                bg='#4444ff', fg='white', font=('Arial', 14, 'bold'),
                                command=self.open_settings, width=15, height=2)
        settings_btn.pack(side='left', padx=20)
        
    def toggle_chart(self, chart_id: int):
        """Toggle individual chart on/off"""
        is_active = self.chart_switches[chart_id].get()
        self.chart_data[chart_id].is_active = is_active
        
        # Update visual state
        if is_active:
            self.chart_frames[chart_id].configure(bg='#2d2d2d')
            print(f"✅ Chart {chart_id} ({self.chart_data[chart_id].account_name}) ACTIVATED")
        else:
            self.chart_frames[chart_id].configure(bg='#4a4a4a')
            print(f"❌ Chart {chart_id} ({self.chart_data[chart_id].account_name}) DEACTIVATED")
    
    def update_chart_status(self, chart_id: int, margin_percentage: float, daily_pnl: float, 
                           open_positions: int = 0, last_signal: str = "NONE"):
        """Update individual chart status and color"""
        chart_data = self.chart_data[chart_id]
        chart_data.margin_percentage = margin_percentage
        chart_data.daily_pnl = daily_pnl
        chart_data.open_positions = open_positions
        chart_data.last_signal = last_signal
        chart_data.margin_remaining = chart_data.account_balance * (margin_percentage / 100)
        chart_data.last_update = datetime.now()
        
        # Determine risk level and color
        if margin_percentage >= 70:
            risk_level = "SAFE TRADING"
            color = '#00ff88'  # Green
            text_color = 'black'
        elif margin_percentage >= 40:
            risk_level = "MARGINAL CALL"
            color = '#ffaa00'  # Yellow
            text_color = 'black'
        else:
            risk_level = "NO TRADE"
            color = '#ff4444'  # Red
            text_color = 'white'
            
        chart_data.risk_level = risk_level
        
        # Update GUI
        labels = self.chart_labels[chart_id]
        labels['status_frame'].configure(bg=color)
        labels['risk_label'].configure(text=risk_level, bg=color, fg=text_color)
        labels['margin_info'].configure(text=f"{margin_percentage:.1f}% | ${chart_data.margin_remaining:,.0f}", 
                                       bg=color, fg=text_color)
        
    def calculate_overall_margin(self):
        """Calculate overall margin remaining across all charts"""
        total_balance = sum(chart.account_balance for chart in self.chart_data.values() if chart.is_active)
        total_remaining = sum(chart.margin_remaining for chart in self.chart_data.values() if chart.is_active)
        
        if total_balance > 0:
            overall_percentage = (total_remaining / total_balance) * 100
        else:
            overall_percentage = 0
            
        self.total_margin_remaining = total_remaining
        self.total_margin_percentage = overall_percentage
        
        # Update overall display
        self.margin_percentage_label.configure(text=f"{overall_percentage:.1f}%")
        self.margin_amount_label.configure(text=f"${total_remaining:,.0f}")
        
        # Update overall status color
        if overall_percentage >= 70:
            status_text = "SAFE TRADING"
            status_color = '#00ff88'
            text_color = 'black'
        elif overall_percentage >= 40:
            status_text = "CAUTION"
            status_color = '#ffaa00'
            text_color = 'black'
        else:
            status_text = "DANGER"
            status_color = '#ff4444'
            text_color = 'white'
            
        self.overall_status_label.configure(text=status_text, bg=status_color, fg=text_color)
        
        # Update margin percentage and amount colors
        if overall_percentage >= 70:
            color = '#00ff88'
        elif overall_percentage >= 40:
            color = '#ffaa00'
        else:
            color = '#ff4444'
            
        self.margin_percentage_label.configure(fg=color)
        self.margin_amount_label.configure(fg=color)
        
    def emergency_stop_all(self):
        """Emergency stop all trading activities"""
        print("🛑 EMERGENCY STOP ALL CHARTS TRIGGERED")
        
        for chart_id, chart_data in self.chart_data.items():
            if chart_data.is_active:
                # In real implementation, send stop commands to trading platforms
                print(f"   🛑 Stopping all trades on Chart {chart_id} ({chart_data.account_name})")
                
                # Update chart to show stopped state
                self.update_chart_status(chart_id, chart_data.margin_percentage, 
                                       chart_data.daily_pnl, 0, "STOPPED")
                
        # Show emergency dialog
        import tkinter.messagebox as mb
        mb.showwarning("Emergency Stop", 
                      "🛑 ALL TRADING ACTIVITIES STOPPED\n\n"
                      "All open positions have been closed.\n"
                      "All pending orders have been cancelled.\n"
                      "Trading is paused on all charts.")
        
    def pause_all_monitoring(self):
        """Pause monitoring on all charts"""
        print("⏸️ PAUSING ALL CHART MONITORING")
        self.is_monitoring = False
        
        for chart_id in self.chart_data.keys():
            self.chart_switches[chart_id].set(False)
            self.toggle_chart(chart_id)
            
    def resume_all_monitoring(self):
        """Resume monitoring on all charts"""
        print("▶️ RESUMING ALL CHART MONITORING")
        self.is_monitoring = True
        
        for chart_id in self.chart_data.keys():
            self.chart_switches[chart_id].set(True)
            self.toggle_chart(chart_id)
            
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Multi-Chart Settings")
        settings_window.geometry("600x400")
        settings_window.configure(bg='#1a1a1a')
        
        title = tk.Label(settings_window, text="⚙️ Multi-Chart Configuration", 
                        bg='#1a1a1a', fg='white', font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # Add configuration options here
        info_label = tk.Label(settings_window, 
                             text="Configure individual chart settings, risk thresholds,\n"
                                  "and Apex compliance parameters here.", 
                             bg='#1a1a1a', fg='white', font=('Arial', 12))
        info_label.pack(pady=20)
        
    def start_monitoring(self):
        """Start monitoring thread"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
    def monitoring_loop(self):
        """Main monitoring loop with simulated data"""
        import random
        
        while True:
            if self.is_monitoring:
                # Simulate margin changes for each active chart
                for chart_id, chart_data in self.chart_data.items():
                    if chart_data.is_active:
                        # Simulate margin percentage changes
                        change = random.uniform(-2, 2)
                        new_margin = max(10, min(95, chart_data.margin_percentage + change))
                        
                        # Simulate P&L changes
                        pnl_change = random.uniform(-100, 100)
                        new_pnl = chart_data.daily_pnl + pnl_change
                        
                        # Simulate positions
                        positions = random.randint(0, 3)
                        
                        # Simulate signals
                        signals = ["BULLISH", "BEARISH", "NONE", "CONFLUENCE L2", "CONFLUENCE L3"]
                        signal = random.choice(signals)
                        
                        # Update chart
                        self.update_chart_status(chart_id, new_margin, new_pnl, positions, signal)
                
                # Update overall margin
                self.calculate_overall_margin()
                
            time.sleep(2)  # Update every 2 seconds
            
    def run(self):
        """Start the control panel"""
        print("🎯 Starting Michael's 6-Chart Control Panel...")
        print("📊 Most Important Indicator: Overall Margin Remaining")
        print("🎨 Visual System: Red (No Trade) | Yellow (Marginal) | Green (Trade On)")
        print("🔧 Individual Controls: Each chart has on/off switch")
        print()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Control panel stopped by user")

def main():
    """Main entry point"""
    control_panel = MultiChartControlPanel()
    control_panel.run()

if __name__ == "__main__":
    main()
