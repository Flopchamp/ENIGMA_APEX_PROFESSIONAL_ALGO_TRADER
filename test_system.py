"""
🧪 SYSTEM TEST - Michael's 6-Chart Trading System
Quick test to verify all components work together
"""

import sys
import os

# Add system directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
system_dir = os.path.join(current_dir, 'system')
sys.path.insert(0, system_dir)

def test_imports():
    """Test if all system components can be imported"""
    print("🧪 Testing System Component Imports...")
    
    tests = []
    
    # Test Michael's 6-chart control panel
    try:
        from michael_6_chart_control_panel import Michael6ChartControlPanel
        tests.append(("6-Chart Control Panel", True))
        print("   ✅ 6-Chart Control Panel imported successfully")
    except Exception as e:
        tests.append(("6-Chart Control Panel", False))
        print(f"   ❌ 6-Chart Control Panel error: {e}")
    
    # Test multi-chart OCR coordinator  
    try:
        from multi_chart_ocr_coordinator import MultiChartOCRCoordinator
        tests.append(("Multi-Chart OCR", True))
        print("   ✅ Multi-Chart OCR imported successfully")
    except Exception as e:
        tests.append(("Multi-Chart OCR", False))
        print(f"   ❌ Multi-Chart OCR error: {e}")
    
    # Test system integration bridge
    try:
        from system_integration_bridge import SystemIntegrationBridge
        tests.append(("Integration Bridge", True))
        print("   ✅ Integration Bridge imported successfully")
    except Exception as e:
        tests.append(("Integration Bridge", False))
        print(f"   ❌ Integration Bridge error: {e}")
    
    # Test Harrison's systems (if available)
    try:
        from apex_compliance_guardian import ApexComplianceGuardian
        tests.append(("Apex Compliance (Harrison)", True))
        print("   ✅ Apex Compliance Guardian imported successfully")
    except Exception as e:
        tests.append(("Apex Compliance (Harrison)", False))
        print(f"   ⚠️  Apex Compliance Guardian not available: {e}")
    
    return tests

def test_system_initialization():
    """Test system initialization"""
    print("\n🔧 Testing System Initialization...")
    
    try:
        from multi_chart_ocr_coordinator import MultiChartOCRCoordinator
        ocr = MultiChartOCRCoordinator()
        print(f"   ✅ OCR Coordinator: {len(ocr.chart_regions)} charts configured")
        
        from system_integration_bridge import SystemIntegrationBridge  
        bridge = SystemIntegrationBridge()
        print(f"   ✅ Integration Bridge: {len(bridge.chart_statuses)} charts ready")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Initialization error: {e}")
        return False

def test_configuration_files():
    """Test configuration file creation"""
    print("\n📁 Testing Configuration Files...")
    
    config_tests = []
    
    # Check if config directory exists or can be created
    config_dir = "config"
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
            config_tests.append(("Config Directory", True))
            print("   ✅ Config directory created")
        except Exception as e:
            config_tests.append(("Config Directory", False))
            print(f"   ❌ Config directory error: {e}")
    else:
        config_tests.append(("Config Directory", True))
        print("   ✅ Config directory exists")
    
    # Test OCR config creation
    try:
        from multi_chart_ocr_coordinator import MultiChartOCRCoordinator
        ocr = MultiChartOCRCoordinator()
        ocr_config = "config/multi_chart_ocr_config.json"
        config_tests.append(("OCR Config", os.path.exists(ocr_config)))
        if os.path.exists(ocr_config):
            print("   ✅ OCR configuration file ready")
        else:
            print("   ⚠️  OCR configuration will be created on first run")
    except Exception as e:
        config_tests.append(("OCR Config", False))
        print(f"   ❌ OCR config error: {e}")
    
    return config_tests

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 MICHAEL'S 6-CHART SYSTEM - COMPONENT TEST")
    print("=" * 60)
    
    # Test imports
    import_tests = test_imports()
    
    # Test initialization
    init_success = test_system_initialization()
    
    # Test configuration
    config_tests = test_configuration_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print("🔧 Component Imports:")
    for component, success in import_tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {component}")
    
    print(f"\n⚙️ System Initialization: {'✅ PASS' if init_success else '❌ FAIL'}")
    
    print("\n📁 Configuration Files:")
    for config, success in config_tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {config}")
    
    # Overall result
    all_imports_passed = all(success for _, success in import_tests)
    all_configs_ok = all(success for _, success in config_tests)
    overall_success = all_imports_passed and init_success and all_configs_ok
    
    print(f"\n🎯 OVERALL RESULT: {'✅ SYSTEM READY' if overall_success else '❌ SYSTEM NEEDS ATTENTION'}")
    
    if overall_success:
        print("\n🚀 Ready to launch Michael's 6-Chart Trading System!")
        print("   Next step: Run 'python launch_michael_system.py'")
    else:
        print("\n🔧 Please address the failed components before launching.")
    
    print("=" * 60)
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    
    # Keep window open on Windows for review
    if os.name == 'nt':
        input("\nPress Enter to close...")
    
    sys.exit(exit_code)
