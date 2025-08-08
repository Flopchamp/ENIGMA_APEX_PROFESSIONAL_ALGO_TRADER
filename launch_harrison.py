"""
🎯 HARRISON'S ENHANCED DASHBOARD LAUNCHER
Direct launcher for Harrison's original design enhanced with NinjaTrader + Tradovate features
Keeps the clean interface but adds real connection capabilities
"""

import streamlit as st
import sys
import os
import subprocess
import time

def install_required_packages():
    """Install required packages if not already installed"""
    required_packages = [
        "streamlit>=1.48.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "plotly>=5.11.0",
        "psutil>=5.9.0"  # For NinjaTrader process detection
    ]
    
    st.info("🔄 Checking and installing required packages...")
    
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            st.warning(f"Could not install {package}: {e}")
    
    st.success("✅ Package installation complete!")

def main():
    """Main launcher function"""
    st.set_page_config(
        page_title="Harrison's Enhanced Dashboard",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Harrison's Enhanced Dashboard Launcher")
    st.markdown("**Enhanced with NinjaTrader + Tradovate real connection capabilities**")
    
    # Installation option
    if st.button("📦 Install/Update Required Packages"):
        install_required_packages()
        time.sleep(2)
        st.rerun()
    
    st.markdown("---")
    
    # Add current directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    system_dir = os.path.join(current_dir, 'system')
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if system_dir not in sys.path:
        sys.path.insert(0, system_dir)
    
    # Try to import and run Harrison's enhanced dashboard
    try:
        from system.harrison_enhanced_dashboard import HarrisonEnhancedDashboard
        
        st.success("✅ Harrison's Enhanced Dashboard loaded successfully!")
        st.markdown("### Features:")
        st.markdown("""
        - **Harrison's Original Clean Interface** - Simple and elegant design
        - **Enhanced with Real NinjaTrader Connection** - Actual process detection
        - **Tradovate Multi-Account Support** - Real account integration
        - **Three Connection Modes**: Demo → Test → Live progression
        - **6-Chart Layout** - Classic 2x3 grid design
        - **Professional Margin Monitoring** - Real-time safety calculations
        """)
        
        st.markdown("---")
        
        # Run the dashboard
        dashboard = HarrisonEnhancedDashboard()
        dashboard.run()
        
    except ImportError as e:
        st.error(f"❌ Error importing Harrison's Enhanced Dashboard: {e}")
        st.markdown("### 🔧 Troubleshooting:")
        st.markdown("""
        1. Make sure you're in the correct directory
        2. Check that `system/harrison_enhanced_dashboard.py` exists
        3. Install required packages using the button above
        4. Try running: `python launch_harrison.py`
        """)
        
        # Show file structure for debugging
        if st.checkbox("🔍 Show current directory structure"):
            st.markdown("**Current Directory:**")
            for root, dirs, files in os.walk(current_dir):
                level = root.replace(current_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                st.text(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    if file.endswith(('.py', '.md', '.txt')):
                        st.text(f"{subindent}{file}")
                if level >= 2:  # Limit depth
                    break

if __name__ == "__main__":
    main()
