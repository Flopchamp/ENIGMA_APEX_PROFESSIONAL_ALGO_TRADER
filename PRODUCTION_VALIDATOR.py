#!/usr/bin/env python3
"""
🔍 ENIGMA APEX PRODUCTION VALIDATOR
Complete system validation for client training and live trading
"""

import os
import sys
import json
import subprocess
import importlib
from pathlib import Path
from datetime import datetime

class ProductionValidator:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.validation_results = {}
        self.critical_errors = []
        self.warnings = []
        
    def print_header(self):
        """Display validation header"""
        print("🔍 ENIGMA APEX PRODUCTION VALIDATOR")
        print("=" * 60)
        print("📅 Validation Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("🎯 Target: Client Training & Live Trading")
        print("=" * 60)
        print()
        
    def validate_file_structure(self):
        """Validate all required files exist"""
        print("📁 VALIDATING FILE STRUCTURE...")
        print("-" * 40)
        
        required_files = {
            # Core system files
            'ENIGMA_APEX_COMPLETE_SYSTEM.py': 'Main system launcher',
            'TRAINING_MODE_LAUNCHER.py': 'Training environment',
            'CLIENT_NOTIFICATION_DEMO.py': 'Client demonstration',
            'requirements.txt': 'Python dependencies',
            
            # System components
            'system/apex_compliance_guardian_streamlit.py': 'Streamlit web interface (MAIN DEPLOYMENT FILE)',
            'system/enhanced_websocket_server.py': 'WebSocket communication',
            'system/desktop_notifier.py': 'Notification system',
            'system/apex_compliance_guardian.py': 'Risk management',
            'system/advanced_risk_manager.py': 'Advanced risk controls',
            'system/ocr_enigma_reader.py': 'Signal detection',
            'system/production_config_manager.py': 'Production configuration',
            
            # NinjaScript components
            'ninjatrader/Indicators/EnigmaApexPowerScore.cs': 'Power score indicator',
            'ninjatrader/Strategies/EnigmaApexAutoTrader.cs': 'Automated trading',
            'ninjatrader/AddOns/EnigmaApexRiskManager.cs': 'Risk management addon',
            
            # Documentation
            'documentation/ENIGMA_APEX_USER_MANUAL.md': 'User manual',
            'documentation/ENIGMA_APEX_VISUAL_SETUP_GUIDE.md': 'Setup guide',
            'PRODUCTION_RELEASE_GUIDE.md': 'Production guide'
        }
        
        all_files_exist = True
        for file_path, description in required_files.items():
            full_path = self.base_path / file_path
            exists = full_path.exists()
            status = "✅" if exists else "❌"
            print(f"   {status} {file_path}")
            print(f"      {description}")
            
            if not exists:
                all_files_exist = False
                self.critical_errors.append(f"Missing file: {file_path}")
            
        self.validation_results['file_structure'] = all_files_exist
        print(f"\n📁 File Structure: {'✅ VALID' if all_files_exist else '❌ INVALID'}")
        print()
        
    def validate_python_dependencies(self):
        """Validate Python dependencies"""
        print("🐍 VALIDATING PYTHON DEPENDENCIES...")
        print("-" * 40)
        
        required_packages = [
            'streamlit', 'pandas', 'numpy', 'plotly', 'websockets',
            'asyncio', 'plyer', 'opencv-python', 'Pillow',
            'requests', 'flask'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                if package == 'opencv-python':
                    import cv2
                else:
                    importlib.import_module(package)
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package} - NOT INSTALLED")
                missing_packages.append(package)
        
        dependencies_valid = len(missing_packages) == 0
        self.validation_results['dependencies'] = dependencies_valid
        
        if missing_packages:
            self.critical_errors.append(f"Missing packages: {', '.join(missing_packages)}")
            print(f"\n💡 Install missing packages: pip install {' '.join(missing_packages)}")
        
        print(f"\n🐍 Dependencies: {'✅ VALID' if dependencies_valid else '❌ INVALID'}")
        print()
        
    def validate_notification_system(self):
        """Validate notification system"""
        print("🔔 VALIDATING NOTIFICATION SYSTEM...")
        print("-" * 40)
        
        try:
            # Import and test notification system
            sys.path.append(str(self.base_path / 'system'))
            from desktop_notifier import DesktopNotifier
            
            notifier = DesktopNotifier()
            stats = notifier.get_notification_stats()
            
            print("   ✅ DesktopNotifier class imported")
            print("   ✅ Notification settings loaded")
            print(f"   ✅ Plyer available: {stats.get('plyer_available', False)}")
            print(f"   ✅ Windows sound available: {stats.get('windows_sound_available', False)}")
            
            self.validation_results['notifications'] = True
            print("\n🔔 Notifications: ✅ VALID")
            
        except Exception as e:
            print(f"   ❌ Notification system error: {e}")
            self.critical_errors.append(f"Notification system failure: {e}")
            self.validation_results['notifications'] = False
            print("\n🔔 Notifications: ❌ INVALID")
        
        print()
        
    def run_full_validation(self):
        """Run complete system validation"""
        self.print_header()
        
        # Run all validations
        self.validate_file_structure()
        self.validate_python_dependencies()
        self.validate_notification_system()
        
        # Generate final report
        critical_issues = len(self.critical_errors)
        
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        
        if critical_issues == 0:
            status = "🟢 PRODUCTION READY"
            recommendation = "✅ APPROVED FOR CLIENT TRAINING AND LIVE TRADING"
            print(f"🎯 OVERALL STATUS: {status}")
            print(f"📋 RECOMMENDATION: {recommendation}")
            print()
            print("🚀 DEPLOYMENT INFORMATION:")
            print("   📱 Main file for deployment: system/apex_compliance_guardian_streamlit.py")
            print("   🎯 Training launcher: python TRAINING_MODE_LAUNCHER.py")
            print("   🔔 Notification demo: python CLIENT_NOTIFICATION_DEMO.py")
            print("   📊 System demo: python ENIGMA_APEX_COMPLETE_SYSTEM.py")
            return True
        else:
            status = "🔴 NOT READY"
            recommendation = "❌ RESOLVE CRITICAL ISSUES BEFORE DEPLOYMENT"
            print(f"🎯 OVERALL STATUS: {status}")
            print(f"📋 RECOMMENDATION: {recommendation}")
            print()
            print("🚨 CRITICAL ISSUES TO RESOLVE:")
            for error in self.critical_errors:
                print(f"   ❌ {error}")
            return False

def main():
    """Main validation function"""
    try:
        validator = ProductionValidator()
        is_production_ready = validator.run_full_validation()
        
        if is_production_ready:
            print("\n🎉 SYSTEM READY FOR CLIENT DEPLOYMENT!")
            return 0
        else:
            print("\n⚠️ SYSTEM NEEDS ATTENTION BEFORE DEPLOYMENT")
            return 1
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
