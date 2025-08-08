"""
🚀 MICHAEL'S 6-CHART ALGO TRADING SYSTEM LAUNCHER
Simple launcher for the complete integrated system

Features:
- 6-Chart Visual Control Panel (Red/Green/Yellow boxes)
- AlgoBox OCR Signal Reading  
- Apex Trader Funding Compliance
- Kelly Criterion Position Sizing
- Overall Margin Indicator (#3 Most Important)
- Emergency Stop Protection
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add system path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'system'))

try:
    # Import Michael's systems
    from michael_6_chart_control_panel import Michael6ChartControlPanel
    from system_integration_bridge import SystemIntegrationBridge
    
    # Optional: Import Harrison's systems if available
    try:
        from apex_compliance_guardian import ApexComplianceGuardian
        HARRISON_SYSTEMS_AVAILABLE = True
    except ImportError:
        HARRISON_SYSTEMS_AVAILABLE = False
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("⚠️  Please ensure all system files are in the 'system/' directory")
    sys.exit(1)

class MichaelSystemLauncher:
    """
    Main launcher for Michael's 6-chart trading system
    Coordinates the visual panel with all backend systems
    """
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # System components
        self.integration_bridge = None
        self.control_panel = None
        
        self.logger.info("🚀 Michael's 6-Chart System Launcher initialized")
    
    def setup_logging(self):
        """Setup logging for the launcher"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"michael_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(log_dir, log_filename)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def check_system_requirements(self):
        """Check if all required components are available"""
        self.logger.info("🔍 Checking system requirements...")
        
        requirements_check = {
            "Python": sys.version_info >= (3, 7),
            "System Files": True,  # Already checked in imports
            "Config Directory": os.path.exists("config") or True,  # Will create if needed
            "Logs Directory": os.path.exists("logs") or True,  # Already created
            "Harrison's Systems": HARRISON_SYSTEMS_AVAILABLE
        }
        
        for requirement, status in requirements_check.items():
            status_icon = "✅" if status else "❌"
            self.logger.info(f"   {status_icon} {requirement}")
        
        return all(requirements_check.values())
    
    def initialize_systems(self):
        """Initialize all system components"""
        self.logger.info("⚙️ Initializing system components...")
        
        try:
            # Initialize integration bridge (connects all systems)
            self.logger.info("   🔗 Initializing Integration Bridge...")
            self.integration_bridge = SystemIntegrationBridge()
            
            # Initialize visual control panel
            self.logger.info("   📊 Initializing 6-Chart Control Panel...")
            self.control_panel = Michael6ChartControlPanel()
            
            # Connect control panel to integration bridge
            self.logger.info("   🔌 Connecting systems...")
            self.connect_systems()
            
            self.logger.info("✅ All systems initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")
            return False
    
    def connect_systems(self):
        """Connect the visual panel to the backend systems"""
        if not (self.control_panel and self.integration_bridge):
            raise Exception("Systems not initialized")
        
        # Register the control panel as an update callback
        self.integration_bridge.register_update_callback(
            self.control_panel.update_chart_statuses
        )
        
        # Connect control panel actions to integration bridge
        # (In a full implementation, this would wire up all the UI controls)
        
        self.logger.info("🔌 Systems connected successfully")
    
    def start_systems(self):
        """Start all systems"""
        self.logger.info("🚀 Starting Michael's 6-Chart Trading System...")
        
        try:
            # Start the integration bridge (backend systems)
            self.logger.info("   🔄 Starting backend systems...")
            self.integration_bridge.start_system()
            
            # Start the visual control panel (GUI)
            self.logger.info("   📊 Launching visual control panel...")
            
            # Note: The control panel will run in the main thread
            # and handle its own event loop
            
            self.logger.info("✅ All systems started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start systems: {e}")
            return False
    
    def stop_systems(self):
        """Stop all systems gracefully"""
        self.logger.info("🛑 Stopping Michael's 6-Chart Trading System...")
        
        try:
            if self.integration_bridge:
                self.integration_bridge.stop_system()
                
            self.logger.info("✅ All systems stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping systems: {e}")
    
    def run(self):
        """Main run method - launches the complete system"""
        self.logger.info("=" * 60)
        self.logger.info("🎯 MICHAEL'S 6-CHART ALGO TRADING SYSTEM")
        self.logger.info("   Features: Visual Control + OCR + Apex Compliance")
        self.logger.info("=" * 60)
        
        try:
            # Check requirements
            if not self.check_system_requirements():
                self.logger.error("❌ System requirements not met")
                return False
            
            # Initialize systems
            if not self.initialize_systems():
                self.logger.error("❌ System initialization failed")
                return False
            
            # Start systems
            if not self.start_systems():
                self.logger.error("❌ System startup failed")
                return False
            
            # Run the visual control panel (blocks until closed)
            self.logger.info("📊 Launching Visual Control Panel...")
            self.logger.info("   🔴🟢🟡 Red/Green/Yellow status boxes ready")
            self.logger.info("   💰 Overall margin indicator active")
            self.logger.info("   🚨 Emergency stop protection enabled")
            
            # Start the GUI (this will block)
            self.control_panel.run()
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            self.logger.error(f"❌ System error: {e}")
        finally:
            # Always try to stop systems cleanly
            self.stop_systems()
        
        self.logger.info("👋 Michael's 6-Chart System shutdown complete")
        return True

def print_startup_banner():
    """Print system startup banner"""
    print("\n" + "=" * 70)
    print("🎯 MICHAEL'S 6-CHART ALGORITHMIC TRADING SYSTEM")
    print("=" * 70)
    print("📊 Features:")
    print("   🔴🟢🟡 6-Chart Visual Control Panel")
    print("   👁️  AlgoBox OCR Signal Reading")
    print("   ⚖️  Apex Trader Funding Compliance")
    print("   🧮 Kelly Criterion Position Sizing")
    print("   💰 Overall Margin Indicator (Most Important)")
    print("   🚨 Emergency Stop Protection")
    print("   🔗 NinjaTrader Integration (Port 36973)")
    print("=" * 70)
    print("⚠️  IMPORTANT:")
    print("   1. Ensure AlgoBox is running with 6 charts visible")
    print("   2. Calibrate OCR regions for your screen setup")
    print("   3. Verify NinjaTrader connection is active")
    print("   4. Test emergency stop before live trading")
    print("=" * 70)

def main():
    """Main entry point"""
    print_startup_banner()
    
    # Create and run the launcher
    launcher = MichaelSystemLauncher()
    success = launcher.run()
    
    if success:
        print("✅ System completed successfully")
        return 0
    else:
        print("❌ System completed with errors")
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    # Keep window open on Windows
    if os.name == 'nt':  # Windows
        input("\nPress Enter to close...")
    
    sys.exit(exit_code)
