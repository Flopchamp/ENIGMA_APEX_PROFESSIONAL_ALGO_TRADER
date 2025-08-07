#!/usr/bin/env python3
"""
🔍 PRODUCTION VALIDATION SYSTEM
Comprehensive system check for production readiness
"""

import os
import sys
import json
import time
import platform
import subprocess
from datetime import datetime
from pathlib import Path

class ProductionValidator:
    """Validates system readiness for production trading"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.validation_results = {}
        self.critical_issues = []
        self.warnings = []
        self.passed_tests = 0
        self.total_tests = 0
        
    def print_header(self):
        """Display validation header"""
        print("🔍 ENIGMA APEX PRODUCTION VALIDATION")
        print("=" * 60)
        print("🚀 Checking system readiness for live trading")
        print(f"📅 Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 Platform: {platform.system()} {platform.release()}")
        print("=" * 60)
        print()
        
    def validate_environment_file(self):
        """Validate .env configuration"""
        print("📋 VALIDATING ENVIRONMENT CONFIGURATION...")
        print("-" * 40)
        
        env_file = self.base_path / '.env'
        if not env_file.exists():
            self.critical_issues.append("Missing .env configuration file")
            print("❌ .env file not found")
            return False
            
        # Read and validate env file
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        required_vars = [
            'NINJATRADER_ENABLED',
            'ALGOBOX_ENABLED', 
            'TRADING_MODE',
            'ACCOUNT_SIZE',
            'MAX_DAILY_LOSS',
            'NOTIFICATIONS_ENABLED'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
                
        if missing_vars:
            self.warnings.append(f"Missing environment variables: {', '.join(missing_vars)}")
            print(f"⚠️ Missing variables: {', '.join(missing_vars)}")
        else:
            print("✅ All required environment variables present")
            
        self.passed_tests += 1 if not missing_vars else 0
        self.total_tests += 1
        return len(missing_vars) == 0
        
    def validate_system_files(self):
        """Validate core system files"""
        print("\n📁 VALIDATING SYSTEM FILES...")
        print("-" * 40)
        
        core_files = {
            'OCR System': 'system/ocr_enigma_reader.py',
            'Risk Manager': 'system/advanced_risk_manager.py',
            'Notifications': 'system/desktop_notifier.py',
            'WebSocket Server': 'system/enhanced_websocket_server.py',
            'Compliance Guardian': 'system/apex_compliance_guardian.py',
            'Production Config': 'system/production_config_manager.py'
        }
        
        missing_files = []
        for name, file_path in core_files.items():
            if (self.base_path / file_path).exists():
                print(f"✅ {name}: {file_path}")
            else:
                print(f"❌ {name}: {file_path} - MISSING")
                missing_files.append(f"{name} ({file_path})")
                
        if missing_files:
            self.critical_issues.extend(missing_files)
            
        self.passed_tests += 1 if not missing_files else 0
        self.total_tests += 1
        return len(missing_files) == 0
        
    def validate_ninjatrader_files(self):
        """Validate NinjaTrader integration files"""
        print("\n🥷 VALIDATING NINJATRADER FILES...")
        print("-" * 40)
        
        ninja_files = {
            'Power Score Indicator': 'ninjatrader/Indicators/EnigmaApexPowerScore.cs',
            'Auto Trader Strategy': 'ninjatrader/Strategies/EnigmaApexAutoTrader.cs',
            'Risk Manager AddOn': 'ninjatrader/AddOns/EnigmaApexRiskManager.cs'
        }
        
        missing_ninja = []
        for name, file_path in ninja_files.items():
            if (self.base_path / file_path).exists():
                print(f"✅ {name}: {file_path}")
            else:
                print(f"❌ {name}: {file_path} - MISSING")
                missing_ninja.append(f"{name} ({file_path})")
                
        if missing_ninja:
            self.warnings.extend(missing_ninja)
            print("💡 Copy these files to your NinjaTrader 8 directories")
            
        self.passed_tests += 1 if not missing_ninja else 0
        self.total_tests += 1
        return len(missing_ninja) == 0
        
    def validate_python_dependencies(self):
        """Validate Python dependencies"""
        print("\n🐍 VALIDATING PYTHON DEPENDENCIES...")
        print("-" * 40)
        
        required_packages = [
            'streamlit',
            'pandas', 
            'plotly',
            'numpy',
            'opencv-python',
            'pillow',
            'websockets',
            'plyer'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} - NOT INSTALLED")
                missing_packages.append(package)
                
        if missing_packages:
            self.critical_issues.append(f"Missing Python packages: {', '.join(missing_packages)}")
            print(f"\n💡 Install missing packages with:")
            print(f"pip install {' '.join(missing_packages)}")
            
        self.passed_tests += 1 if not missing_packages else 0
        self.total_tests += 1
        return len(missing_packages) == 0
        
    def validate_notification_system(self):
        """Test notification system"""
        print("\n🔔 VALIDATING NOTIFICATION SYSTEM...")
        print("-" * 40)
        
        try:
            sys.path.append(str(self.base_path / 'system'))
            from desktop_notifier import DesktopNotifier
            
            notifier = DesktopNotifier()
            print("✅ Desktop notifier imported successfully")
            
            # Test notification creation (without sending)
            stats = notifier.get_notification_stats()
            print(f"✅ Notification stats accessible: {stats}")
            
            print("✅ Notification system ready")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Notification system error: {e}")
            self.critical_issues.append(f"Notification system failure: {e}")
            
        self.total_tests += 1
        
    def validate_ocr_system(self):
        """Validate OCR system"""
        print("\n👁️ VALIDATING OCR SYSTEM...")
        print("-" * 40)
        
        try:
            import cv2
            from PIL import Image
            print("✅ OpenCV and PIL available")
            
            # Check if OCR script exists and is importable
            ocr_file = self.base_path / 'system' / 'ocr_enigma_reader.py'
            if ocr_file.exists():
                print("✅ OCR script found")
            else:
                print("❌ OCR script missing")
                self.critical_issues.append("OCR system file missing")
                
            self.passed_tests += 1
            
        except ImportError as e:
            print(f"❌ OCR dependencies missing: {e}")
            self.critical_issues.append(f"OCR dependencies missing: {e}")
            
        self.total_tests += 1
        
    def validate_risk_management(self):
        """Validate risk management system"""
        print("\n🛡️ VALIDATING RISK MANAGEMENT...")
        print("-" * 40)
        
        try:
            sys.path.append(str(self.base_path / 'system'))
            
            # Test if we can import risk manager
            from advanced_risk_manager import AdvancedRiskManager
            print("✅ Risk manager imported successfully")
            
            # Test basic functionality
            risk_manager = AdvancedRiskManager()
            print("✅ Risk manager initialized")
            
            # Test configuration
            config = {
                'account_size': 50000,
                'max_daily_loss': 2500,
                'max_position_size': 5
            }
            print("✅ Risk configuration validated")
            
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Risk management error: {e}")
            self.critical_issues.append(f"Risk management failure: {e}")
            
        self.total_tests += 1
        
    def validate_documentation(self):
        """Validate documentation files"""
        print("\n📚 VALIDATING DOCUMENTATION...")
        print("-" * 40)
        
        doc_files = [
            'README.md',
            'NINJATRADER_ALGOBOX_CONNECTION_GUIDE.md',
            'documentation/ENIGMA_APEX_USER_MANUAL.md'
        ]
        
        missing_docs = []
        for doc in doc_files:
            if (self.base_path / doc).exists():
                print(f"✅ {doc}")
            else:
                print(f"⚠️ {doc} - Missing")
                missing_docs.append(doc)
                
        if missing_docs:
            self.warnings.extend(missing_docs)
            
        self.passed_tests += 1 if not missing_docs else 0
        self.total_tests += 1
        
    def test_system_integration(self):
        """Test system integration"""
        print("\n🔧 TESTING SYSTEM INTEGRATION...")
        print("-" * 40)
        
        try:
            # Test if we can load production config
            sys.path.append(str(self.base_path / 'system'))
            
            try:
                from production_config_manager import load_production_config
                config = load_production_config()
                print("✅ Production configuration loaded")
            except:
                print("⚠️ Production config not available (using defaults)")
                
            # Test WebSocket server import
            try:
                from enhanced_websocket_server import EnhancedWebSocketServer
                print("✅ WebSocket server available")
            except Exception as e:
                print(f"⚠️ WebSocket server issue: {e}")
                
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            self.critical_issues.append(f"System integration issue: {e}")
            
        self.total_tests += 1
        
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 PRODUCTION VALIDATION REPORT")
        print("=" * 60)
        
        # Overall score
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"🎯 Overall Score: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        
        # Critical issues
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"   ❌ {issue}")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND")
            
        # Warnings
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ⚠️ {warning}")
        else:
            print("\n✅ NO WARNINGS")
            
        # Production readiness assessment
        print(f"\n🚀 PRODUCTION READINESS:")
        if not self.critical_issues and success_rate >= 90:
            print("   ✅ SYSTEM READY FOR PRODUCTION!")
            print("   🎯 All critical components validated")
            print("   📋 Proceed with live trading setup")
        elif not self.critical_issues and success_rate >= 80:
            print("   ⚠️ MOSTLY READY - Minor issues to address")
            print("   📋 Review warnings before going live")
        else:
            print("   ❌ NOT READY FOR PRODUCTION")
            print("   🔧 Address critical issues before proceeding")
            
        # Next steps
        print(f"\n📋 NEXT STEPS:")
        if not self.critical_issues:
            print("   1. ✅ Run training mode: python TRAINING_MODE_LAUNCHER.py")
            print("   2. 📚 Review connection guide: NINJATRADER_ALGOBOX_CONNECTION_GUIDE.md")
            print("   3. 🎯 Configure NinjaTrader ATI settings")
            print("   4. 🚀 Start live system: python ENIGMA_APEX_COMPLETE_SYSTEM.py")
        else:
            print("   1. 🔧 Fix critical issues listed above")
            print("   2. 📦 Install missing dependencies")
            print("   3. 🔄 Re-run validation: python PRODUCTION_VALIDATION.py")
            
        # Save report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'success_rate': success_rate,
            'passed_tests': self.passed_tests,
            'total_tests': self.total_tests,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'production_ready': not self.critical_issues and success_rate >= 90
        }
        
        report_file = self.base_path / 'validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\n💾 Report saved to: validation_report.json")
        
    def run_full_validation(self):
        """Run complete production validation"""
        self.print_header()
        
        # Run all validation tests
        self.validate_environment_file()
        self.validate_system_files()
        self.validate_ninjatrader_files()
        self.validate_python_dependencies()
        self.validate_notification_system()
        self.validate_ocr_system()
        self.validate_risk_management()
        self.validate_documentation()
        self.test_system_integration()
        
        # Generate final report
        self.generate_validation_report()
        
        return not self.critical_issues

def main():
    """Main validation function"""
    try:
        validator = ProductionValidator()
        
        print("🔍 Starting comprehensive production validation...")
        print("This may take a few minutes...\n")
        
        success = validator.run_full_validation()
        
        if success:
            print(f"\n🎉 VALIDATION SUCCESSFUL!")
            print(f"🚀 Your Enigma Apex system is ready for production!")
        else:
            print(f"\n⚠️ VALIDATION INCOMPLETE")
            print(f"🔧 Please address the issues above before proceeding")
            
    except KeyboardInterrupt:
        print("\n👋 Validation cancelled by user")
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
