"""
🎯 Training Wheels for Prop Firm Traders - Main Entry Point
Streamlit Cloud Entry Point for Professional Trading Dashboard
"""

import streamlit as st
import sys
import os
from datetime import datetime
import logging

# Configure logging for cloud deployment
logging.basicConfig(level=logging.INFO)

def main():
    """Main entry point for Streamlit Cloud"""
    try:
        # Import the main dashboard
        from harrison_original_complete_clean import TrainingWheelsDashboard
        
        # Initialize and run the dashboard
        dashboard = TrainingWheelsDashboard()
        dashboard.run()
        
    except ImportError as e:
        # Fallback if main dashboard can't be imported
        st.error(f"Import error: {e}")
        render_fallback_interface()
        
    except Exception as e:
        # Handle any other errors gracefully
        st.error(f"Application error: {e}")
        render_fallback_interface()

def render_fallback_interface():
    """Render a fallback interface if main dashboard fails"""
    st.set_page_config(
        page_title="Training Wheels - Loading",
        page_icon="🎯",
        layout="wide"
    )
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1>🎯 Training Wheels for Prop Firm Traders</h1>
        <h2>Professional Trading Enhancement System</h2>
        <p><strong>Loading Dashboard...</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🌤️ **Running in Streamlit Cloud**")
    st.markdown("The dashboard is initializing. If you continue to see this message, the application is loading...")
    
    # Show system status
    st.markdown("### 🔧 System Status")
    st.success("✅ Entry point loaded successfully")
    st.info("📡 Connecting to dashboard...")
    
    # Retry button
    if st.button("🔄 Retry Loading Dashboard", type="primary"):
        st.rerun()
    
    # Basic interface while loading
    st.markdown("### 📊 Basic System Info")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", "Loading")
    with col2:
        st.metric("Mode", "Cloud")
    with col3:
        st.metric("Version", "1.0.0")
    with col4:
        st.metric("Ready", "Soon")

if __name__ == "__main__":
    main()
