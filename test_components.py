"""
🧪 Quick Test Script for Universal 6-Chart Trading System
Tests the Streamlit application components
"""

import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
system_dir = os.path.join(current_dir, 'system')
sys.path.insert(0, current_dir)
sys.path.insert(0, system_dir)

def test_imports():
    """Test all imports"""
    print("🧪 Testing Universal 6-Chart Trading System Components...")
    
    # Test main app
    try:
        import app
        print("✅ Main app imported successfully")
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        return False
    
    # Test dashboard
    try:
        from system.streamlit_6_chart_dashboard import StreamlitTradingDashboard
        print("✅ Dashboard imported successfully")
    except Exception as e:
        print(f"❌ Dashboard import failed: {e}")
        return False
    
    # Test integration
    try:
        from system.streamlit_system_integration import StreamlitSystemIntegration
        print("✅ Integration imported successfully")
    except Exception as e:
        print(f"❌ Integration import failed: {e}")
        return False
    
    # Test OCR coordinator
    try:
        from system.multi_chart_ocr_coordinator import MultiChartOCRCoordinator
        print("✅ OCR coordinator imported successfully")
    except Exception as e:
        print(f"⚠️  OCR coordinator import failed (optional): {e}")
    
    return True

def test_instantiation():
    """Test component instantiation"""
    print("\n🔧 Testing component instantiation...")
    
    try:
        from system.streamlit_6_chart_dashboard import StreamlitTradingDashboard
        dashboard = StreamlitTradingDashboard()
        print("✅ Dashboard instantiated successfully")
    except Exception as e:
        print(f"❌ Dashboard instantiation failed: {e}")
        return False
    
    try:
        from system.streamlit_system_integration import StreamlitSystemIntegration
        integration = StreamlitSystemIntegration()
        print("✅ Integration instantiated successfully")
    except Exception as e:
        print(f"❌ Integration instantiation failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("=" * 60)
    print("🎯 UNIVERSAL 6-CHART TRADING SYSTEM - COMPONENT TEST")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return 1
    
    # Test instantiation
    if not test_instantiation():
        print("\n❌ Instantiation tests failed")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("🚀 Ready to launch Streamlit application:")
    print("   python -m streamlit run app.py")
    print("   OR")
    print("   python launch_streamlit.py")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to close...")
    
    sys.exit(exit_code)
