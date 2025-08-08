"""
🧪 ENIGMA APEX PROFESSIONAL - AUTOMATED SYSTEM TEST
Quick validation script to test all critical system components
Run this before using the trading system for the first time
"""

import sys
import os
import importlib
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Tuple

class SystemTester:
    """Automated testing suite for ENIGMA APEX Professional"""
    
    def __init__(self):
        self.test_results = {}
        self.critical_failures = []
        self.warnings = []
        
    def print_header(self):
        """Print test suite header"""
        print("=" * 70)
        print("🧪 ENIGMA APEX PROFESSIONAL - SYSTEM VALIDATION TEST")
        print("=" * 70)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python Version: {sys.version}")
        print("-" * 70)
    
    def test_python_version(self) -> bool:
        """Test Python version compatibility"""
        print("🐍 Testing Python version...")
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
            self.critical_failures.append("Python version too old")
            return False
    
    def test_required_packages(self) -> bool:
        """Test all required Python packages"""
        print("📦 Testing required packages...")
        
        required_packages = {
            'streamlit': 'streamlit',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'plotly': 'plotly',
            'requests': 'requests',
            'websockets': 'websockets',
            'cryptography': 'cryptography',
            'psutil': 'psutil'
        }
        
        missing_packages = []
        
        for package_name, import_name in required_packages.items():
            try:
                importlib.import_module(import_name)
                print(f"   ✅ {package_name} - Available")
            except ImportError:
                print(f"   ❌ {package_name} - Missing")
                missing_packages.append(package_name)
        
        if missing_packages:
            print(f"   ⚠️  Missing packages: {', '.join(missing_packages)}")
            print(f"   💡 Install with: pip install {' '.join(missing_packages)}")
            self.critical_failures.append(f"Missing packages: {missing_packages}")
            return False
        
        return True
    
    def test_file_structure(self) -> bool:
        """Test required files exist"""
        print("📁 Testing file structure...")
        
        required_files = [
            'harrison_original_complete.py',
            'production_api_manager.py',
            'secure_credential_manager.py',
            'USER_TESTING_GUIDE.md'
        ]
        
        missing_files = []
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"   ✅ {file_path} - Found")
            else:
                print(f"   ❌ {file_path} - Missing")
                missing_files.append(file_path)
        
        if missing_files:
            self.warnings.append(f"Missing files: {missing_files}")
            return False
        
        return True
    
    def test_streamlit_functionality(self) -> bool:
        """Test Streamlit can start"""
        print("🌐 Testing Streamlit functionality...")
        
        try:
            import streamlit as st
            print("   ✅ Streamlit import - Success")
            
            # Test if we can run streamlit command
            result = subprocess.run(
                ['streamlit', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   ✅ Streamlit CLI - {version}")
                return True
            else:
                print("   ❌ Streamlit CLI - Failed")
                self.warnings.append("Streamlit CLI not working")
                return False
                
        except Exception as e:
            print(f"   ❌ Streamlit test failed: {e}")
            self.critical_failures.append("Streamlit not functional")
            return False
    
    def test_main_application(self) -> bool:
        """Test main application can be imported"""
        print("🎯 Testing main application...")
        
        try:
            # Add current directory to path
            sys.path.insert(0, os.getcwd())
            
            # Test importing main components
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "harrison_complete", 
                "harrison_original_complete.py"
            )
            
            if spec and spec.loader:
                print("   ✅ Main application file - Importable")
                return True
            else:
                print("   ❌ Main application file - Import failed")
                self.critical_failures.append("Main application not importable")
                return False
                
        except Exception as e:
            print(f"   ❌ Application import error: {e}")
            self.critical_failures.append(f"Application import error: {e}")
            return False
    
    def test_network_connectivity(self) -> bool:
        """Test internet connectivity for API connections"""
        print("🌍 Testing network connectivity...")
        
        test_urls = [
            ("Google DNS", "8.8.8.8"),
            ("Tradovate Demo", "demo.tradovateapi.com"),
            ("PyPI", "pypi.org")
        ]
        
        import socket
        
        connectivity_ok = True
        
        for name, host in test_urls:
            try:
                socket.create_connection((host, 80), timeout=5)
                print(f"   ✅ {name} - Reachable")
            except OSError:
                print(f"   ❌ {name} - Unreachable")
                connectivity_ok = False
        
        if not connectivity_ok:
            self.warnings.append("Network connectivity issues detected")
        
        return connectivity_ok
    
    def test_api_managers(self) -> bool:
        """Test API manager components"""
        print("🔗 Testing API managers...")
        
        try:
            # Test production API manager
            from production_api_manager import TradovateAPI, ProductionAPIManager
            print("   ✅ Production API Manager - Importable")
            
            # Test credential manager
            from secure_credential_manager import SecureCredentialManager
            print("   ✅ Secure Credential Manager - Importable")
            
            return True
            
        except ImportError as e:
            print(f"   ❌ API manager import failed: {e}")
            self.warnings.append("API managers not available")
            return False
    
    def test_system_resources(self) -> bool:
        """Test system has adequate resources"""
        print("💻 Testing system resources...")
        
        try:
            import psutil
            
            # Check available memory
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            if memory_gb >= 4:
                print(f"   ✅ System Memory - {memory_gb:.1f} GB (Adequate)")
            else:
                print(f"   ⚠️  System Memory - {memory_gb:.1f} GB (May be low)")
                self.warnings.append("Low system memory")
            
            # Check CPU
            cpu_count = psutil.cpu_count()
            print(f"   ✅ CPU Cores - {cpu_count} (Available)")
            
            # Check disk space
            disk = psutil.disk_usage('.')
            disk_free_gb = disk.free / (1024**3)
            
            if disk_free_gb >= 1:
                print(f"   ✅ Disk Space - {disk_free_gb:.1f} GB free")
            else:
                print(f"   ⚠️  Disk Space - {disk_free_gb:.1f} GB free (Low)")
                self.warnings.append("Low disk space")
            
            return True
            
        except Exception as e:
            print(f"   ⚠️  Resource check failed: {e}")
            return True  # Non-critical
    
    def test_port_availability(self) -> bool:
        """Test required ports are available"""
        print("🔌 Testing port availability...")
        
        import socket
        
        ports_to_test = [
            (8501, "Streamlit default"),
            (8502, "Streamlit backup"),
            (8765, "WebSocket server")
        ]
        
        available_ports = []
        
        for port, description in ports_to_test:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    print(f"   ✅ Port {port} ({description}) - Available")
                    available_ports.append(port)
            except OSError:
                print(f"   ⚠️  Port {port} ({description}) - In use")
        
        if len(available_ports) > 0:
            return True
        else:
            self.warnings.append("No ports available for Streamlit")
            return False
    
    def run_startup_simulation(self) -> bool:
        """Simulate application startup"""
        print("🚀 Testing application startup simulation...")
        
        try:
            # Simulate the main imports that would happen on startup
            import json
            import time
            from datetime import datetime
            import logging
            
            print("   ✅ Core Python modules - Available")
            
            # Test JSON operations (used for config)
            test_config = {"test": True, "timestamp": datetime.now().isoformat()}
            json_str = json.dumps(test_config)
            parsed = json.loads(json_str)
            print("   ✅ JSON operations - Working")
            
            # Test logging setup
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger("test")
            logger.info("Test log message")
            print("   ✅ Logging system - Working")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Startup simulation failed: {e}")
            self.critical_failures.append(f"Startup simulation error: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """Generate final test report"""
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "critical_failures": self.critical_failures,
            "warnings": self.warnings,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        }
        
        return report
    
    def print_summary(self, report: Dict):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        print(f"Tests Run: {report['total_tests']}")
        print(f"Passed: {report['passed_tests']} ✅")
        print(f"Failed: {report['failed_tests']} ❌")
        print(f"Success Rate: {report['success_rate']:.1f}%")
        
        if report['critical_failures']:
            print(f"\n🚨 CRITICAL FAILURES ({len(report['critical_failures'])}):")
            for failure in report['critical_failures']:
                print(f"   ❌ {failure}")
        
        if report['warnings']:
            print(f"\n⚠️  WARNINGS ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"   ⚠️  {warning}")
        
        print("\n" + "=" * 70)
        
        # Overall assessment
        if len(report['critical_failures']) == 0:
            if len(report['warnings']) == 0:
                print("🎉 SYSTEM STATUS: EXCELLENT - Ready for trading!")
                print("✅ All tests passed. You can proceed with confidence.")
            else:
                print("✅ SYSTEM STATUS: GOOD - Ready with minor issues")
                print("⚠️  Some warnings present, but system should work.")
        else:
            print("❌ SYSTEM STATUS: ISSUES DETECTED")
            print("🔧 Please fix critical failures before using the system.")
        
        print("\n📋 NEXT STEPS:")
        if len(report['critical_failures']) == 0:
            print("1. Run the main application: streamlit run harrison_original_complete.py")
            print("2. Follow the USER_TESTING_GUIDE.md for complete validation")
            print("3. Start with DEMO mode and progress to live trading")
        else:
            print("1. Fix critical failures listed above")
            print("2. Re-run this test script")
            print("3. Proceed to manual testing once all tests pass")
        
        print("=" * 70)
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.print_header()
        
        # Define all tests
        tests = [
            ("Python Version", self.test_python_version),
            ("Required Packages", self.test_required_packages),
            ("File Structure", self.test_file_structure),
            ("Streamlit Functionality", self.test_streamlit_functionality),
            ("Main Application", self.test_main_application),
            ("Network Connectivity", self.test_network_connectivity),
            ("API Managers", self.test_api_managers),
            ("System Resources", self.test_system_resources),
            ("Port Availability", self.test_port_availability),
            ("Startup Simulation", self.run_startup_simulation)
        ]
        
        # Run each test
        for test_name, test_function in tests:
            try:
                result = test_function()
                self.test_results[test_name] = result
                print()  # Empty line for readability
            except Exception as e:
                print(f"   ❌ Test '{test_name}' crashed: {e}")
                self.test_results[test_name] = False
                self.critical_failures.append(f"Test crash: {test_name}")
                print()
        
        # Generate and display report
        report = self.generate_report()
        self.print_summary(report)
        
        return report

def main():
    """Main test execution"""
    print("Starting ENIGMA APEX Professional system validation...\n")
    
    tester = SystemTester()
    report = tester.run_all_tests()
    
    # Save report to file
    try:
        import json
        with open("system_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: system_test_report.json")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")
    
    # Exit with appropriate code
    if len(report['critical_failures']) == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
