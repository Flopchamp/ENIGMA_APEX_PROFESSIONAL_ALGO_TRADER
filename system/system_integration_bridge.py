"""
🔗 SYSTEM INTEGRATION BRIDGE
Connects Michael's 6-chart control panel to Harrison's existing systems
Bridges: Visual Panel ↔ OCR ↔ Risk Manager ↔ Apex Compliance
"""

import asyncio
import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
import logging
from dataclasses import dataclass, asdict

# Import existing system components
from apex_compliance_guardian import ApexComplianceGuardian
from advanced_risk_manager import AdvancedRiskManager
from multi_chart_ocr_coordinator import MultiChartOCRCoordinator, ChartSignal
from kelly_criterion_engine import KellyCriterionEngine

@dataclass
class ChartStatus:
    """Status for individual chart"""
    chart_id: int
    chart_name: str
    is_enabled: bool
    status_color: str  # RED, GREEN, YELLOW
    signal_strength: int
    risk_level: str
    last_signal: Optional[ChartSignal]
    violation_count: int
    is_locked_out: bool
    position_size: float
    margin_used: float
    profit_loss: float

@dataclass
class SystemStatus:
    """Overall system status"""
    overall_margin_remaining: float
    total_equity: float
    daily_profit_loss: float
    active_charts: int
    violation_alerts: List[str]
    emergency_stop_active: bool
    safety_ratio: float
    system_health: str

class SystemIntegrationBridge:
    """
    Integration bridge connecting all Michael's systems:
    - 6-Chart Visual Control Panel (Frontend)
    - Multi-Chart OCR Coordinator (Data Collection)
    - Apex Compliance Guardian (Rule Enforcement)
    - Advanced Risk Manager (Position Sizing)
    - Kelly Criterion Engine (Math)
    """
    
    def __init__(self):
        # Initialize core systems
        self.ocr_coordinator = MultiChartOCRCoordinator()
        self.apex_guardian = ApexComplianceGuardian()
        self.risk_manager = AdvancedRiskManager()
        self.kelly_engine = KellyCriterionEngine()
        
        # System state
        self.chart_statuses: Dict[int, ChartStatus] = {}
        self.system_status = SystemStatus(
            overall_margin_remaining=0.0,
            total_equity=0.0,
            daily_profit_loss=0.0,
            active_charts=0,
            violation_alerts=[],
            emergency_stop_active=False,
            safety_ratio=25.0,  # Default 25%
            system_health="INITIALIZING"
        )
        
        # Control state
        self.is_running = False
        self.monitoring_thread = None
        self.update_callbacks: List[Callable] = []
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize chart statuses
        self.initialize_chart_statuses()
        
        self.logger.info("🔗 System Integration Bridge initialized")
    
    def initialize_chart_statuses(self):
        """Initialize status tracking for all 6 charts"""
        for chart_id in range(1, 7):
            chart_name = f"Chart-{chart_id}"
            if chart_id in self.ocr_coordinator.chart_regions:
                chart_name = self.ocr_coordinator.chart_regions[chart_id].chart_name
            
            self.chart_statuses[chart_id] = ChartStatus(
                chart_id=chart_id,
                chart_name=chart_name,
                is_enabled=True,  # Default enabled
                status_color="YELLOW",  # Starting state
                signal_strength=0,
                risk_level="LOW",
                last_signal=None,
                violation_count=0,
                is_locked_out=False,
                position_size=0.0,
                margin_used=0.0,
                profit_loss=0.0
            )
    
    def register_update_callback(self, callback: Callable):
        """Register callback for status updates (for GUI)"""
        self.update_callbacks.append(callback)
    
    def notify_update_callbacks(self):
        """Notify all registered callbacks of status update"""
        for callback in self.update_callbacks:
            try:
                callback(self.chart_statuses, self.system_status)
            except Exception as e:
                self.logger.error(f"❌ Callback error: {e}")
    
    def enable_chart(self, chart_id: int, enabled: bool):
        """Enable/disable specific chart"""
        if chart_id in self.chart_statuses:
            self.chart_statuses[chart_id].is_enabled = enabled
            status = "ENABLED" if enabled else "DISABLED"
            self.logger.info(f"📊 Chart {chart_id} {status}")
            
            if not enabled:
                # Clear signals and set to yellow when disabled
                self.chart_statuses[chart_id].status_color = "YELLOW"
                self.chart_statuses[chart_id].signal_strength = 0
                
            self.notify_update_callbacks()
    
    def set_safety_ratio(self, ratio: float):
        """Set overall safety ratio (5-90%)"""
        if 5.0 <= ratio <= 90.0:
            self.system_status.safety_ratio = ratio
            # Update Apex Guardian
            if hasattr(self.apex_guardian, 'set_safety_ratio'):
                self.apex_guardian.set_safety_ratio(ratio)
            self.logger.info(f"⚙️ Safety ratio set to {ratio}%")
            self.notify_update_callbacks()
    
    def emergency_stop(self):
        """Trigger emergency stop"""
        self.system_status.emergency_stop_active = True
        
        # Stop all charts
        for chart_id in self.chart_statuses:
            self.chart_statuses[chart_id].is_enabled = False
            self.chart_statuses[chart_id].status_color = "RED"
        
        # Stop OCR monitoring
        if self.ocr_coordinator.is_monitoring:
            self.ocr_coordinator.stop_monitoring_all_charts()
        
        self.logger.critical("🚨 EMERGENCY STOP ACTIVATED - ALL TRADING HALTED")
        self.notify_update_callbacks()
    
    def reset_emergency_stop(self):
        """Reset emergency stop (requires manual action)"""
        self.system_status.emergency_stop_active = False
        
        # Reset all charts to enabled/yellow
        for chart_id in self.chart_statuses:
            self.chart_statuses[chart_id].is_enabled = True
            self.chart_statuses[chart_id].status_color = "YELLOW"
            self.chart_statuses[chart_id].violation_count = 0
            self.chart_statuses[chart_id].is_locked_out = False
        
        self.system_status.violation_alerts.clear()
        
        self.logger.info("🔄 Emergency stop reset - System ready")
        self.notify_update_callbacks()
    
    def process_chart_signal(self, chart_id: int, signal: ChartSignal):
        """Process new signal from specific chart"""
        if chart_id not in self.chart_statuses:
            return
        
        chart_status = self.chart_statuses[chart_id]
        
        # Skip if chart disabled or emergency stop active
        if not chart_status.is_enabled or self.system_status.emergency_stop_active:
            return
        
        # Update last signal
        chart_status.last_signal = signal
        chart_status.signal_strength = signal.power_score
        
        # Determine status color based on signal validity and strength
        if signal.is_valid and signal.power_score >= 70:
            chart_status.status_color = "GREEN"
            chart_status.risk_level = "HIGH" if signal.power_score >= 85 else "MEDIUM"
        elif signal.is_valid and signal.power_score >= 40:
            chart_status.status_color = "YELLOW"
            chart_status.risk_level = "MEDIUM"
        else:
            chart_status.status_color = "RED"
            chart_status.risk_level = "LOW"
        
        # Check Apex compliance
        self.check_apex_compliance(chart_id, signal)
        
        # Calculate position sizing if signal is valid
        if signal.is_valid and chart_status.status_color == "GREEN":
            self.calculate_position_size(chart_id, signal)
    
    def check_apex_compliance(self, chart_id: int, signal: ChartSignal):
        """Check Apex Trader Funding compliance rules"""
        chart_status = self.chart_statuses[chart_id]
        
        try:
            # Simulate Apex compliance check
            # In real implementation, this would use apex_guardian
            
            # Check trailing drawdown (example)
            if chart_status.profit_loss < -1000:  # $1000 drawdown limit
                self.add_violation(chart_id, "Trailing drawdown exceeded")
                chart_status.status_color = "RED"
                chart_status.is_locked_out = True
            
            # Check consistency rule (30% rule simulation)
            if chart_status.violation_count >= 3:
                self.add_violation(chart_id, "Consistency rule violation")
                chart_status.is_locked_out = True
            
            # Check daily loss limit
            if self.system_status.daily_profit_loss < -2000:  # $2000 daily limit
                self.emergency_stop()
                self.add_violation(0, "Daily loss limit exceeded - Emergency stop triggered")
                
        except Exception as e:
            self.logger.error(f"❌ Compliance check error for Chart {chart_id}: {e}")
    
    def add_violation(self, chart_id: int, message: str):
        """Add violation alert"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        violation_msg = f"[{timestamp}] Chart {chart_id}: {message}"
        
        self.system_status.violation_alerts.append(violation_msg)
        
        # Keep only last 10 violations
        if len(self.system_status.violation_alerts) > 10:
            self.system_status.violation_alerts = self.system_status.violation_alerts[-10:]
        
        if chart_id > 0:
            self.chart_statuses[chart_id].violation_count += 1
        
        self.logger.warning(f"⚠️ VIOLATION: {violation_msg}")
    
    def calculate_position_size(self, chart_id: int, signal: ChartSignal):
        """Calculate position size using Kelly Criterion"""
        try:
            # Simulate Kelly calculation
            # In real implementation, this would use kelly_engine
            
            base_size = 1.0  # 1 contract base
            kelly_multiplier = signal.power_score / 100.0  # Use power score as multiplier
            safety_multiplier = self.system_status.safety_ratio / 100.0
            
            position_size = base_size * kelly_multiplier * safety_multiplier
            
            # Apply maximum position limits
            max_position = 5.0  # Maximum 5 contracts
            position_size = min(position_size, max_position)
            
            self.chart_statuses[chart_id].position_size = position_size
            
            # Simulate margin calculation
            margin_per_contract = 400.0  # $400 per ES contract
            self.chart_statuses[chart_id].margin_used = position_size * margin_per_contract
            
        except Exception as e:
            self.logger.error(f"❌ Position sizing error for Chart {chart_id}: {e}")
    
    def update_system_financials(self):
        """Update overall system financial status"""
        try:
            # Calculate totals from all charts
            total_margin_used = sum(status.margin_used for status in self.chart_statuses.values())
            total_pnl = sum(status.profit_loss for status in self.chart_statuses.values())
            
            # Simulate account values
            self.system_status.total_equity = 25000.0  # $25k account
            self.system_status.overall_margin_remaining = self.system_status.total_equity - total_margin_used
            self.system_status.daily_profit_loss = total_pnl
            
            # Calculate active charts
            self.system_status.active_charts = sum(
                1 for status in self.chart_statuses.values() 
                if status.is_enabled and not status.is_locked_out
            )
            
            # Determine system health
            margin_ratio = total_margin_used / self.system_status.total_equity if self.system_status.total_equity > 0 else 0
            
            if self.system_status.emergency_stop_active:
                self.system_status.system_health = "EMERGENCY_STOP"
            elif margin_ratio > 0.8:
                self.system_status.system_health = "HIGH_RISK"
            elif margin_ratio > 0.6:
                self.system_status.system_health = "MEDIUM_RISK"
            elif self.system_status.active_charts > 0:
                self.system_status.system_health = "HEALTHY"
            else:
                self.system_status.system_health = "IDLE"
                
        except Exception as e:
            self.logger.error(f"❌ Financial update error: {e}")
            self.system_status.system_health = "ERROR"
    
    def monitoring_loop(self):
        """Main monitoring loop running in separate thread"""
        self.logger.info("🔄 Starting monitoring loop")
        
        while self.is_running:
            try:
                # Read signals from all charts
                if self.ocr_coordinator.is_monitoring:
                    latest_signals = self.ocr_coordinator.get_latest_signals()
                    
                    # Process each chart's signal
                    for chart_id, signal in latest_signals.items():
                        self.process_chart_signal(chart_id, signal)
                
                # Update system financials
                self.update_system_financials()
                
                # Notify GUI updates
                self.notify_update_callbacks()
                
                # Sleep between updates
                time.sleep(1)  # Update every second
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(5)  # Wait longer on error
        
        self.logger.info("🛑 Monitoring loop stopped")
    
    def start_system(self):
        """Start the integrated system"""
        if self.is_running:
            self.logger.warning("⚠️ System already running")
            return
        
        try:
            # Start OCR monitoring
            self.ocr_coordinator.start_monitoring_all_charts()
            
            # Start monitoring thread
            self.is_running = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            self.logger.info("🚀 Integrated system started")
            self.notify_update_callbacks()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start system: {e}")
            self.is_running = False
    
    def stop_system(self):
        """Stop the integrated system"""
        if not self.is_running:
            self.logger.warning("⚠️ System not running")
            return
        
        try:
            # Stop monitoring
            self.is_running = False
            
            # Stop OCR monitoring
            self.ocr_coordinator.stop_monitoring_all_charts()
            
            # Wait for monitoring thread
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            self.logger.info("🛑 Integrated system stopped")
            self.notify_update_callbacks()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop system: {e}")
    
    def get_chart_status(self, chart_id: int) -> Optional[ChartStatus]:
        """Get status for specific chart"""
        return self.chart_statuses.get(chart_id)
    
    def get_all_chart_statuses(self) -> Dict[int, ChartStatus]:
        """Get all chart statuses"""
        return self.chart_statuses.copy()
    
    def get_system_status(self) -> SystemStatus:
        """Get overall system status"""
        return self.system_status
    
    def export_status_json(self) -> str:
        """Export current status as JSON (for external monitoring)"""
        status_data = {
            "timestamp": datetime.now().isoformat(),
            "system_status": asdict(self.system_status),
            "chart_statuses": {
                str(chart_id): asdict(status) 
                for chart_id, status in self.chart_statuses.items()
            }
        }
        
        return json.dumps(status_data, indent=2, default=str)
    
    def import_settings(self, settings: Dict):
        """Import system settings"""
        try:
            if "safety_ratio" in settings:
                self.set_safety_ratio(settings["safety_ratio"])
            
            if "enabled_charts" in settings:
                for chart_id, enabled in settings["enabled_charts"].items():
                    self.enable_chart(int(chart_id), enabled)
            
            self.logger.info("✅ Settings imported successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to import settings: {e}")

def main():
    """Test the integration bridge"""
    bridge = SystemIntegrationBridge()
    
    print("🔗 System Integration Bridge Test")
    print(f"📊 Charts configured: {len(bridge.chart_statuses)}")
    
    # Test status updates
    print("\n📊 Initial chart statuses:")
    for chart_id, status in bridge.get_all_chart_statuses().items():
        print(f"   Chart {chart_id} ({status.chart_name}): {status.status_color}, Enabled: {status.is_enabled}")
    
    print(f"\n💰 System Status:")
    sys_status = bridge.get_system_status()
    print(f"   Health: {sys_status.system_health}")
    print(f"   Active Charts: {sys_status.active_charts}")
    print(f"   Safety Ratio: {sys_status.safety_ratio}%")
    
    # Test system start/stop
    print("\n🚀 Testing system start...")
    bridge.start_system()
    
    time.sleep(5)  # Run for 5 seconds
    
    print("🛑 Testing system stop...")
    bridge.stop_system()
    
    print("✅ Integration bridge test completed")

if __name__ == "__main__":
    main()
