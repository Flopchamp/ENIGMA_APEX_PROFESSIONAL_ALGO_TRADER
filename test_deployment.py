#!/usr/bin/env python3
"""
🎯 Training Wheels - Local Deployment Test
Test script to verify all components work before deploying to Render
"""

import sys
import subprocess
import importlib
import os
from datetime import datetime

def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_dependencies():
    """Test if all required packages can be imported"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        ('streamlit', 'Streamlit framework'),
        ('pandas', 'Data processing'),
        ('numpy', 'Numerical computing'),
        ('plotly', 'Interactive charts'),
        ('requests', 'HTTP requests'),
        ('PIL', 'Image processing'),
        ('json', 'JSON handling'),
        ('datetime', 'Date/time operations'),
        ('logging', 'Logging system'),
        ('socket', 'Network connections'),
        ('os', 'Operating system interface'),
        ('time', 'Time operations')
    ]
    
    success_count = 0
    for package, description in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {package} - {description} (MISSING)")
    
    print(f"\n📊 Dependencies: {success_count}/{len(required_packages)} available")
    return success_count == len(required_packages)

def test_streamlit_app():
    """Test if the main Streamlit app can be imported"""
    print("\n🎯 Testing main application...")
    
    try:
        # Test if streamlit_app.py exists
        if os.path.exists('streamlit_app.py'):
            print("✅ streamlit_app.py exists")
            
            # Try to import the main components
            sys.path.insert(0, '.')
            import streamlit_app
            print("✅ streamlit_app.py imports successfully")
            
            # Check if main classes exist
            if hasattr(streamlit_app, 'TrainingWheelsDashboard'):
                print("✅ TrainingWheelsDashboard class found")
            else:
                print("⚠️ TrainingWheelsDashboard class not found")
            
            return True
        else:
            print("❌ streamlit_app.py not found")
            return False
            
    except Exception as e:
        print(f"❌ Error importing streamlit_app: {e}")
        return False

def test_deployment_files():
    """Test if all deployment files are present"""
    print("\n📁 Testing deployment files...")
    
    deployment_files = [
        ('requirements.txt', 'Python dependencies'),
        ('Procfile', 'Process configuration'),
        ('render.yaml', 'Render configuration'),
        ('runtime.txt', 'Python runtime version'),
        ('.streamlit/config.toml', 'Streamlit configuration'),
        ('render-build.sh', 'Build script')
    ]
    
    success_count = 0
    for filename, description in deployment_files:
        if os.path.exists(filename):
            print(f"✅ {filename} - {description}")
            success_count += 1
        else:
            print(f"❌ {filename} - {description} (MISSING)")
    
    print(f"\n📊 Deployment files: {success_count}/{len(deployment_files)} present")
    return success_count >= len(deployment_files) - 1  # Allow one missing file

def test_local_streamlit():
    """Test if Streamlit can start locally"""
    print("\n🚀 Testing local Streamlit startup...")
    
    try:
        # Test streamlit command availability
        result = subprocess.run(['streamlit', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Streamlit command available: {result.stdout.strip()}")
            
            print("\n💡 To test locally, run:")
            print("   streamlit run streamlit_app.py")
            print("   Then visit: http://localhost:8501")
            
            return True
        else:
            print("❌ Streamlit command not available")
            return False
            
    except FileNotFoundError:
        print("❌ Streamlit not installed")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Streamlit command timeout")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("🎯 TRAINING WHEELS - DEPLOYMENT TEST REPORT")
    print("="*60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Location: {os.getcwd()}")
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Main Application", test_streamlit_app),
        ("Deployment Files", test_deployment_files),
        ("Local Streamlit", test_local_streamlit)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Ready for Render deployment!")
        print("\n🚀 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Create a new Web Service on Render")
        print("3. Connect your GitHub repository")
        print("4. Use the deployment settings from RENDER_DEPLOYMENT_GUIDE.md")
        
        return True
    else:
        print(f"\n⚠️ {total - passed} tests failed - Fix issues before deploying")
        print("\n🔧 Troubleshooting:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Check that all files are in the correct location")
        print("- Review error messages above")
        
        return False

if __name__ == "__main__":
    print("🎯 Training Wheels - Pre-Deployment Test")
    print("Testing application readiness for Render deployment...\n")
    
    success = generate_test_report()
    sys.exit(0 if success else 1)
