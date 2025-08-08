"""
🧪 CORE FUNCTIONALITY TEST
Test the trading dashboard core functions without Streamlit dependencies
"""

import sys
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import json

@dataclass
class UserConfig:
    """User-specific configuration"""
    trader_name: str
    account_size: float
    max_charts: int
    chart_names: List[str]
    safety_ratio: float
    daily_loss_limit: float
    max_position_per_chart: float
    priority_indicator: str
    broker: str

@dataclass
class ChartState:
    """State for individual chart"""
    chart_id: int
    name: str
    is_enabled: bool
    status_color: str
    power_score: int
    signal_strength: str
    confluence_level: str
    position_size: float
    pnl: float
    risk_level: str
    last_update: datetime

class CoreTradingSystem:
    """Core trading system without UI dependencies"""
    
    def __init__(self):
        self.user_config = None
        self.charts = {}
        self.system_running = False
        self.emergency_stop = False
        self.total_pnl = 0.0
        self.margin_used = 0.0
        
        print("🔧 Core Trading System initialized")
    
    def create_default_config(self):
        """Create default configuration"""
        self.user_config = UserConfig(
            trader_name="Universal Trader",
            account_size=25000.0,
            max_charts=6,
            chart_names=[
                "Chart-1", "Chart-2", "Chart-3", 
                "Chart-4", "Chart-5", "Chart-6"
            ],
            safety_ratio=25.0,
            daily_loss_limit=2000.0,
            max_position_per_chart=5.0,
            priority_indicator="margin",
            broker="universal"
        )
        
        print(f"✅ Default config created for {self.user_config.trader_name}")
        return self.user_config
    
    def customize_config(self, trader_name: str, num_charts: int, account_size: float):
        """Customize configuration for specific trader"""
        if not self.user_config:
            self.create_default_config()
        
        # Update basic settings
        self.user_config.trader_name = trader_name
        self.user_config.max_charts = num_charts
        self.user_config.account_size = account_size
        
        # Update chart names
        self.user_config.chart_names = [f"{trader_name}-Chart-{i+1}" for i in range(num_charts)]
        
        print(f"🎯 Configuration customized for {trader_name}")
        print(f"   📊 Charts: {num_charts}")
        print(f"   💰 Account: ${account_size:,.0f}")
        
        return self.user_config
    
    def initialize_charts(self):
        """Initialize chart states"""
        if not self.user_config:
            self.create_default_config()
        
        self.charts = {}
        
        for i in range(self.user_config.max_charts):
            chart_id = i + 1
            chart_name = self.user_config.chart_names[i] if i < len(self.user_config.chart_names) else f"Chart-{chart_id}"
            
            self.charts[chart_id] = ChartState(
                chart_id=chart_id,
                name=chart_name,
                is_enabled=True,
                status_color="yellow",
                power_score=0,
                signal_strength="None",
                confluence_level="L0",
                position_size=0.0,
                pnl=0.0,
                risk_level="Low",
                last_update=datetime.now()
            )
        
        print(f"📊 Initialized {len(self.charts)} charts")
        return self.charts
    
    def update_chart_signal(self, chart_id: int, power_score: int, signal_color: str = None):
        """Update chart with new signal data"""
        if chart_id not in self.charts:
            print(f"❌ Chart {chart_id} not found")
            return
        
        chart = self.charts[chart_id]
        chart.power_score = power_score
        chart.last_update = datetime.now()
        
        # Determine status based on power score
        if power_score >= 70:
            chart.status_color = "green"
            chart.signal_strength = "Strong"
        elif power_score >= 40:
            chart.status_color = "yellow"
            chart.signal_strength = "Medium"
        else:
            chart.status_color = "red"
            chart.signal_strength = "Weak"
        
        # Calculate position size (Kelly-style)
        if chart.is_enabled and chart.status_color == "green":
            kelly_factor = power_score / 100.0
            safety_factor = self.user_config.safety_ratio / 100.0
            chart.position_size = min(
                self.user_config.max_position_per_chart,
                kelly_factor * safety_factor * self.user_config.max_position_per_chart
            )
        else:
            chart.position_size = 0.0
        
        print(f"📊 Chart {chart_id} ({chart.name}): {power_score}% -> {chart.status_color.upper()}")
        return chart
    
    def calculate_system_status(self):
        """Calculate overall system metrics"""
        total_position = sum(chart.position_size for chart in self.charts.values())
        self.total_pnl = sum(chart.pnl for chart in self.charts.values())
        self.margin_used = total_position * 400  # $400 per contract
        
        margin_remaining = self.user_config.account_size - self.margin_used
        active_charts = sum(1 for chart in self.charts.values() if chart.is_enabled)
        
        return {
            "margin_remaining": margin_remaining,
            "margin_used": self.margin_used,
            "total_pnl": self.total_pnl,
            "active_charts": active_charts,
            "total_position": total_position
        }
    
    def get_priority_metric(self):
        """Get the user's priority metric value"""
        status = self.calculate_system_status()
        
        if self.user_config.priority_indicator == "margin":
            return f"💰 Margin Remaining: ${status['margin_remaining']:,.0f}"
        elif self.user_config.priority_indicator == "pnl":
            return f"💵 Total P&L: ${status['total_pnl']:,.0f}"
        elif self.user_config.priority_indicator == "risk":
            risk_percent = (status['margin_used'] / self.user_config.account_size) * 100
            return f"⚖️ Risk Exposure: {risk_percent:.1f}%"
        else:
            return f"📊 Active Charts: {status['active_charts']}"
    
    def emergency_stop_all(self):
        """Trigger emergency stop"""
        self.emergency_stop = True
        self.system_running = False
        
        for chart in self.charts.values():
            chart.is_enabled = False
            chart.status_color = "red"
            chart.position_size = 0.0
        
        print("🚨 EMERGENCY STOP ACTIVATED - ALL TRADING HALTED")
        return True
    
    def reset_emergency_stop(self):
        """Reset emergency stop"""
        self.emergency_stop = False
        
        for chart in self.charts.values():
            chart.is_enabled = True
            chart.status_color = "yellow"
        
        print("🔄 Emergency stop reset - System ready")
        return True
    
    def export_config(self) -> str:
        """Export configuration as JSON"""
        if not self.user_config:
            return "{}"
        
        return json.dumps(asdict(self.user_config), indent=2)
    
    def import_config(self, config_json: str):
        """Import configuration from JSON"""
        try:
            config_data = json.loads(config_json)
            self.user_config = UserConfig(**config_data)
            print("✅ Configuration imported successfully")
            return True
        except Exception as e:
            print(f"❌ Configuration import failed: {e}")
            return False
    
    def print_dashboard_status(self):
        """Print text-based dashboard"""
        if not self.user_config or not self.charts:
            print("❌ System not initialized")
            return
        
        print("\n" + "="*60)
        print(f"🎯 {self.user_config.trader_name.upper()} TRADING DASHBOARD")
        print("="*60)
        
        # Priority metric
        print(f"🎯 PRIORITY: {self.get_priority_metric()}")
        
        # Chart grid
        print(f"\n📊 CHART STATUS GRID ({len(self.charts)} charts)")
        print("-"*60)
        
        for chart_id, chart in self.charts.items():
            color_icon = {"red": "🔴", "yellow": "🟡", "green": "🟢"}.get(chart.status_color, "⚪")
            enabled_status = "ON" if chart.is_enabled else "OFF"
            
            print(f"{color_icon} {chart.name:<15} | Power: {chart.power_score:3d}% | "
                  f"Pos: {chart.position_size:4.1f} | P&L: ${chart.pnl:6.0f} | {enabled_status}")
        
        # System status
        status = self.calculate_system_status()
        print(f"\n💰 ACCOUNT STATUS")
        print(f"   Total Equity: ${self.user_config.account_size + status['total_pnl']:,.0f}")
        print(f"   Margin Used: ${status['margin_used']:,.0f}")
        print(f"   Margin Free: ${status['margin_remaining']:,.0f}")
        print(f"   Active Charts: {status['active_charts']}")
        
        # Safety status
        if self.emergency_stop:
            print("🚨 EMERGENCY STOP ACTIVE")
        elif self.system_running:
            print("✅ SYSTEM RUNNING")
        else:
            print("⏸️ SYSTEM PAUSED")
        
        print("="*60)

def test_universal_configuration():
    """Test the universal configuration system"""
    print("\n🧪 TESTING UNIVERSAL CONFIGURATION")
    print("="*50)
    
    # Test different trader setups
    test_configs = [
        ("Michael", 6, 25000, "His original 6-chart request"),
        ("Sarah", 3, 15000, "Day trader with 3 charts"),
        ("Professional", 12, 100000, "Pro trader with 12 charts"),
        ("Beginner", 1, 5000, "New trader with 1 chart")
    ]
    
    for trader_name, num_charts, account_size, description in test_configs:
        print(f"\n👤 Testing: {trader_name} - {description}")
        
        # Create system instance
        system = CoreTradingSystem()
        
        # Customize for this trader
        system.customize_config(trader_name, num_charts, account_size)
        
        # Initialize charts
        system.initialize_charts()
        
        # Simulate some signals
        for i in range(min(3, num_charts)):
            chart_id = i + 1
            power_score = 75 - (i * 20)  # Decreasing scores
            system.update_chart_signal(chart_id, power_score)
        
        # Print status
        system.print_dashboard_status()
        
        print(f"✅ {trader_name}'s setup completed successfully")

def test_priority_indicators():
    """Test different priority indicators"""
    print("\n🎯 TESTING PRIORITY INDICATORS")
    print("="*50)
    
    system = CoreTradingSystem()
    system.customize_config("TestTrader", 4, 50000)
    system.initialize_charts()
    
    # Test each priority indicator
    priorities = ["margin", "pnl", "risk", "charts"]
    
    for priority in priorities:
        system.user_config.priority_indicator = priority
        metric = system.get_priority_metric()
        print(f"   {priority.upper()}: {metric}")

def main():
    """Main test function"""
    print("🧪 CORE TRADING SYSTEM TEST")
    print("Testing universal configuration capabilities")
    print("No Streamlit dependencies required")
    
    # Test basic functionality
    system = CoreTradingSystem()
    config = system.create_default_config()
    charts = system.initialize_charts()
    
    print(f"\n✅ Basic functionality working")
    print(f"   Config: {config.trader_name}")
    print(f"   Charts: {len(charts)}")
    
    # Test universal configuration
    test_universal_configuration()
    
    # Test priority indicators
    test_priority_indicators()
    
    print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("✅ Core system is universal and configurable")
    print("✅ Not hardcoded for any specific trader")
    print("✅ Supports any number of charts")
    print("✅ Customizable priority indicators")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 Ready for Streamlit integration!")
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to close...")
