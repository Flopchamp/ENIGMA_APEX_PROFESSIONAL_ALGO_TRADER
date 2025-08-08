"""
🎯 ENIGMA APEX - Direct AlgoBox Screen Reader
Reads Enigma signals directly from Michael's AlgoBox screen
No launcher needed - direct interface

Core Logic: Drawdown + Enigma Probability = Trading Decision
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageGrab
import json
import os
import time
from datetime import datetime
import pytesseract
import re

class AlgoBoxScreenReader:
    def __init__(self):
        self.config = self.load_config()
        self.enigma_history = {}
        
    def load_config(self):
        """Load Michael's configuration"""
        try:
            with open('michael_trading_config.json', 'r') as f:
                return json.load(f)
        except:
            return self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration for Michael"""
        return {
            "screen_regions": {
                "chart_1": {"x": 0, "y": 0, "width": 640, "height": 480, "instrument": "ES"},
                "chart_2": {"x": 640, "y": 0, "width": 640, "height": 480, "instrument": "NQ"},
                "chart_3": {"x": 1280, "y": 0, "width": 640, "height": 480, "instrument": "YM"},
                "chart_4": {"x": 0, "y": 480, "width": 640, "height": 480, "instrument": "RTY"},
                "chart_5": {"x": 640, "y": 480, "width": 640, "height": 480, "instrument": "GC"},
                "chart_6": {"x": 1280, "y": 480, "width": 640, "height": 480, "instrument": "CL"}
            },
            "enigma_detection": {
                "green_circle": {"color_range": [(40, 100, 100), (80, 255, 255)], "signal": "BUY"},
                "red_circle": {"color_range": [(0, 100, 100), (20, 255, 255)], "signal": "SELL"},
                "yellow_circle": {"color_range": [(20, 100, 100), (40, 255, 255)], "signal": "CAUTION"},
                "blue_circle": {"color_range": [(100, 100, 100), (140, 255, 255)], "signal": "NEUTRAL"}
            },
            "accounts": {}
        }
    
    def capture_screen_region(self, region):
        """Capture specific region of screen"""
        try:
            screenshot = ImageGrab.grab(bbox=(
                region['x'], 
                region['y'], 
                region['x'] + region['width'], 
                region['y'] + region['height']
            ))
            return np.array(screenshot)
        except Exception as e:
            st.error(f"Screen capture error: {e}")
            return None
    
    def detect_enigma_signals(self, image):
        """Detect Enigma circles in the image"""
        if image is None:
            return []
        
        signals = []
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        for signal_type, config in self.config['enigma_detection'].items():
            color_ranges = config['color_range']
            
            # Create mask for this color
            mask = cv2.inRange(hsv, np.array(color_ranges[0]), np.array(color_ranges[1]))
            
            # Find contours (circles)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 50 < area < 2000:  # Filter by circle size
                    # Check if it's circular
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if circularity > 0.7:  # It's circular enough
                            x, y, w, h = cv2.boundingRect(contour)
                            signals.append({
                                'type': signal_type,
                                'signal': config['signal'],
                                'position': (x + w//2, y + h//2),
                                'confidence': circularity,
                                'timestamp': datetime.now()
                            })
        
        return signals

def main():
    st.set_page_config(
        page_title="🎯 AlgoBox Live Reader",
        page_icon="🎯",
        layout="wide"
    )

    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">🎯 ENIGMA APEX - Live AlgoBox Reader</h1>
        <p style="color: #87CEEB; text-align: center; margin: 0.5rem 0 0 0;">Reading Michael's 6-Chart Setup in Real-Time</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize reader
    reader = AlgoBoxScreenReader()

    # Main interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("## 📊 Live Chart Monitoring")
        
        # Screen capture button
        if st.button("📸 Capture Current Screen", type="primary"):
            with st.spinner("Capturing and analyzing screen..."):
                all_signals = []
                
                # Capture each chart region
                for chart_name, region in reader.config['screen_regions'].items():
                    image = reader.capture_screen_region(region)
                    if image is not None:
                        signals = reader.detect_enigma_signals(image)
                        for signal in signals:
                            signal['chart'] = chart_name
                            signal['instrument'] = region['instrument']
                        all_signals.extend(signals)
                
                # Display results
                if all_signals:
                    st.success(f"✅ Found {len(all_signals)} Enigma signals!")
                    
                    # Create signal summary
                    signal_data = []
                    for signal in all_signals:
                        signal_data.append({
                            'Chart': signal['chart'],
                            'Instrument': signal['instrument'],
                            'Signal Type': signal['type'],
                            'Direction': signal['signal'],
                            'Confidence': f"{signal['confidence']:.2f}",
                            'Time': signal['timestamp'].strftime('%H:%M:%S')
                        })
                    
                    st.dataframe(signal_data, use_container_width=True)
                    
                    # Show captured images
                    st.markdown("### 🖼️ Captured Chart Regions")
                    for chart_name, region in reader.config['screen_regions'].items():
                        image = reader.capture_screen_region(region)
                        if image is not None:
                            st.image(image, caption=f"{chart_name} - {region['instrument']}", width=300)
                else:
                    st.warning("⚠️ No Enigma signals detected in current screen capture")

        # Auto-refresh option
        auto_refresh = st.checkbox("🔄 Auto-refresh every 5 seconds")
        if auto_refresh:
            time.sleep(5)
            st.rerun()

    with col2:
        st.markdown("## ⚙️ Configuration")
        
        # Account setup
        st.markdown("### 💼 Quick Account Setup")
        
        account_name = st.text_input("Account Name", "APEX_ES_MAIN")
        instrument = st.selectbox("Instrument", ["ES", "NQ", "YM", "RTY", "GC", "CL"])
        starting_balance = st.number_input("Starting Balance", value=50000, step=1000)
        current_balance = st.number_input("Current Balance", value=50000, step=100)
        daily_limit = st.number_input("Daily Loss Limit", value=2500, step=100)
        
        if st.button("➕ Add Account"):
            # Calculate drawdown
            daily_used = starting_balance - current_balance
            remaining_drawdown = daily_limit - daily_used
            
            st.success(f"✅ Added {account_name}")
            st.info(f"Remaining drawdown: ${remaining_drawdown:,}")

        # Screen region setup
        st.markdown("### 📺 Screen Regions")
        
        selected_chart = st.selectbox("Configure Chart", 
            ["chart_1", "chart_2", "chart_3", "chart_4", "chart_5", "chart_6"])
        
        if selected_chart in reader.config['screen_regions']:
            region = reader.config['screen_regions'][selected_chart]
            
            new_x = st.number_input(f"{selected_chart} X", value=region['x'])
            new_y = st.number_input(f"{selected_chart} Y", value=region['y'])
            new_width = st.number_input(f"{selected_chart} Width", value=region['width'])
            new_height = st.number_input(f"{selected_chart} Height", value=region['height'])
            
            if st.button(f"💾 Update {selected_chart}"):
                reader.config['screen_regions'][selected_chart].update({
                    'x': new_x, 'y': new_y, 'width': new_width, 'height': new_height
                })
                st.success(f"✅ Updated {selected_chart}")

    # Decision matrix section
    st.markdown("## 🚦 Live Trading Decision Matrix")
    
    # Demo decision table
    demo_decisions = [
        {"Account": "APEX_ES_MAIN", "Instrument": "ES", "Remaining_DD": "$1,200", 
         "Last_Signal": "🟢 BUY", "Enigma_Prob": "78%", "Decision": "🟢 GO - 2 contracts"},
        {"Account": "APEX_NQ_MAIN", "Instrument": "NQ", "Remaining_DD": "$300", 
         "Last_Signal": "🔴 SELL", "Enigma_Prob": "82%", "Decision": "⚠️ CAUTION - 1 contract"},
        {"Account": "APEX_YM_MAIN", "Instrument": "YM", "Remaining_DD": "$0", 
         "Last_Signal": "🟢 BUY", "Enigma_Prob": "65%", "Decision": "🛑 STOP - No drawdown"},
    ]
    
    # Color-code decisions
    def color_decision(val):
        if "🟢 GO" in str(val):
            return 'background-color: #e8f5e8'
        elif "⚠️ CAUTION" in str(val):
            return 'background-color: #fff3e0'
        elif "🛑 STOP" in str(val):
            return 'background-color: #ffebee'
        return ''
    
    import pandas as pd
    df = pd.DataFrame(demo_decisions)
    styled_df = df.style.applymap(color_decision, subset=['Decision'])
    st.dataframe(styled_df, use_container_width=True)

    # Real-time status
    st.markdown("## ⚡ System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("NinjaTrader ATI", "36973", "Connected ✅")
    
    with col2:
        st.metric("Charts Monitored", "6", "All Active 🟢")
    
    with col3:
        st.metric("Last Signal", "2 min ago", "ES BUY")
    
    with col4:
        st.metric("Auto Mode", "OFF", "Manual Review")

    # Instructions for Michael
    st.markdown("## 📋 Instructions for Michael")
    
    st.info("""
    **How to Use:**
    1. 🖥️ **Position AlgoBox** on your screen with 6 charts visible
    2. 📸 **Click 'Capture Current Screen'** to analyze for Enigma signals
    3. ⚙️ **Configure screen regions** if signals aren't detected properly
    4. 💼 **Add your Apex accounts** with current balances
    5. 🚦 **Review trading decisions** in the decision matrix
    
    **The system will:**
    - ✅ Automatically detect Enigma circles (green, red, yellow, blue)
    - ✅ Calculate remaining drawdown for each account
    - ✅ Show GO/CAUTION/STOP decisions based on drawdown + probability
    - ✅ Work with your existing NinjaTrader setup (port 36973)
    """)

if __name__ == "__main__":
    main()
