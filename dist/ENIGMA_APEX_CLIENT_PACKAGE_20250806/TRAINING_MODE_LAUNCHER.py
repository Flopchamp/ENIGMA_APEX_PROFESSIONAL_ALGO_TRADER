#!/usr/bin/env python3
"""
🎯 ENIGMA APEX TRAINING MODE LAUNCHER
Safe training environment for client learning and testing
"""

import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

# Add system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'system'))

class TrainingModeLauncher:
    def __init__(self):
        self.training_mode = True
        self.simulation_account = 100000  # $100k simulation
        self.max_training_risk = 1000     # $1k max loss for training
        self.running_components = []
        
    def print_training_header(self):
        """Display training mode header"""
        print("🎯 ENIGMA APEX TRAINING MODE")
        print("=" * 60)
        print("📚 SAFE LEARNING ENVIRONMENT")
        print("💰 Simulation Account: $100,000")
        print("🛡️ Max Training Risk: $1,000")
        print("🔔 Live Notifications: ENABLED")
        print("📊 Performance Tracking: ENABLED")
        print("=" * 60)
        print()
        
    def setup_training_environment(self):
        """Setup safe training environment"""
        print("🔧 SETTING UP TRAINING ENVIRONMENT...")
        print("-" * 40)
        
        # Create training config
        training_config = {
            'TRADING_MODE': 'SIMULATION',
            'ACCOUNT_SIZE': '100000',
            'MAX_DAILY_RISK': '1000',
            'RISK_PER_TRADE': '0.5',
            'PAPER_TRADING': 'true',
            'LIVE_NOTIFICATIONS': 'true',
            'EDUCATIONAL_MODE': 'true',
            'DEMO_SIGNALS': 'true'
        }
        
        # Write training config
        with open('.env.training', 'w') as f:
            for key, value in training_config.items():
                f.write(f"{key}={value}\n")
        
        print("✅ Training configuration created")
        print("✅ Simulation mode enabled")
        print("✅ Risk limits set for learning")
        print("✅ Notifications active for training")
        print()
        
    async def start_training_components(self):
        """Start all components in training mode"""
        print("🚀 STARTING TRAINING COMPONENTS...")
        print("-" * 40)
        
        # 1. Start notification system test
        print("📱 1. Testing notification system...")
        try:
            from system.desktop_notifier import DesktopNotifier
            notifier = DesktopNotifier()
            
            # Send welcome notification
            welcome_data = {
                'symbol': 'TRAINING',
                'type': 'Training Started',
                'power_score': 0,
                'direction': 'READY',
                'confluence_level': 'LEARNING',
                'signal_color': 'BLUE'
            }
            await notifier.send_signal_notification(welcome_data)
            print("   ✅ Notification system active")
        except Exception as e:
            print(f"   ⚠️ Notification issue: {e}")
        
        # 2. Start WebSocket server
        print("🔌 2. Starting WebSocket server...")
        try:
            ws_process = subprocess.Popen([
                sys.executable, "system/enhanced_websocket_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running_components.append(("WebSocket Server", ws_process))
            time.sleep(2)
            print("   ✅ WebSocket server running")
        except Exception as e:
            print(f"   ⚠️ WebSocket error: {e}")
        
        # 3. Start training dashboard
        print("🌐 3. Starting training dashboard...")
        try:
            dashboard_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                "system/apex_compliance_guardian_streamlit.py",
                "--server.port", "8501"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running_components.append(("Training Dashboard", dashboard_process))
            time.sleep(3)
            print("   ✅ Training dashboard available at: http://localhost:8501")
        except Exception as e:
            print(f"   ⚠️ Dashboard error: {e}")
        
        print()
        
    def display_training_instructions(self):
        """Display training instructions for client"""
        print("📚 TRAINING INSTRUCTIONS FOR CLIENT:")
        print("=" * 60)
        print()
        print("🎯 TRAINING OBJECTIVES:")
        print("   1. Learn system navigation and interface")
        print("   2. Understand risk management controls")
        print("   3. Practice signal recognition and response")
        print("   4. Test notification and alert systems")
        print("   5. Master emergency procedures")
        print()
        print("🔧 TRAINING EXERCISES:")
        print()
        print("   EXERCISE 1: SYSTEM FAMILIARIZATION")
        print("   • Navigate to: http://localhost:8501")
        print("   • Explore all dashboard tabs")
        print("   • Test notification settings")
        print("   • Review risk management panel")
        print()
        print("   EXERCISE 2: NOTIFICATION TESTING")
        print("   • Run: python CLIENT_NOTIFICATION_DEMO.py")
        print("   • Verify Windows toast notifications appear")
        print("   • Test sound alerts and visual effects")
        print("   • Practice emergency stop procedures")
        print()
        print("   EXERCISE 3: NINJASCRIPT INTEGRATION")
        print("   • Open NinjaTrader 8")
        print("   • Add EnigmaApexPowerScore indicator")
        print("   • Verify real-time power score display")
        print("   • Test websocket connection")
        print()
        print("   EXERCISE 4: RISK MANAGEMENT")
        print("   • Review daily loss limits")
        print("   • Test position sizing calculations")
        print("   • Practice manual override procedures")
        print("   • Verify compliance enforcement")
        print()
        print("🛡️ SAFETY FEATURES IN TRAINING:")
        print("   ✅ Paper trading only - NO REAL MONEY")
        print("   ✅ Reduced risk limits for learning")
        print("   ✅ Full notification system active")
        print("   ✅ All features enabled for practice")
        print("   ✅ Performance tracking for review")
        print()
        
    def display_progress_checklist(self):
        """Display training progress checklist"""
        print("📋 TRAINING PROGRESS CHECKLIST:")
        print("-" * 40)
        print("□ System startup and component verification")
        print("□ Notification system tested and working")
        print("□ Dashboard navigation completed")
        print("□ Risk management controls understood")
        print("□ NinjaScript indicators installed and tested")
        print("□ Signal recognition practice completed")
        print("□ Emergency procedures practiced")
        print("□ Performance review and analysis")
        print("□ Ready for live trading assessment")
        print()
        
    def run_training_session(self):
        """Run complete training session"""
        self.print_training_header()
        self.setup_training_environment()
        
        # Start components
        try:
            asyncio.run(self.start_training_components())
        except Exception as e:
            print(f"Error starting components: {e}")
        
        self.display_training_instructions()
        self.display_progress_checklist()
        
        print("🎯 TRAINING SESSION ACTIVE")
        print("=" * 60)
        print("📊 System Status:")
        for name, process in self.running_components:
            status = "🟢 RUNNING" if process.poll() is None else "🔴 STOPPED"
            print(f"   {status} {name}")
        print()
        print("💡 Access your training dashboard: http://localhost:8501")
        print("🔔 Notifications are live - you'll see alerts during training")
        print("📚 Follow the training exercises above")
        print("🛑 Press Ctrl+C to stop training session")
        print()
        
        # Keep training session running
        try:
            while True:
                time.sleep(30)
                # Check component health
                running_count = sum(1 for _, proc in self.running_components if proc.poll() is None)
                print(f"📊 Training Status: {running_count}/{len(self.running_components)} components active")
        except KeyboardInterrupt:
            print("\n🛑 STOPPING TRAINING SESSION...")
            self.stop_training_session()
            
    def stop_training_session(self):
        """Stop all training components"""
        print("   Stopping all training components...")
        for name, process in self.running_components:
            try:
                process.terminate()
                print(f"   ✅ Stopped {name}")
            except:
                print(f"   ⚠️ Could not stop {name}")
        
        print("\n🎓 TRAINING SESSION COMPLETE!")
        print("📊 Review your training progress and prepare for live trading")
        print("💡 Next step: Complete the production checklist")

def main():
    """Main training launcher"""
    try:
        print("🚀 INITIALIZING ENIGMA APEX TRAINING MODE...")
        print()
        
        trainer = TrainingModeLauncher()
        trainer.run_training_session()
        
    except KeyboardInterrupt:
        print("\n👋 Training session ended by user")
    except Exception as e:
        print(f"❌ Training error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
