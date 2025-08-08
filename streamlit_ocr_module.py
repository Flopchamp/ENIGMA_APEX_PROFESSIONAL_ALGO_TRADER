"""
👁️ STREAMLIT OCR INTEGRATION MODULE
Real-time OCR signal reading for Streamlit trading dashboard
Configurable for any number of charts and any screen layout
"""

import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageGrab
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import base64
import io

# Configure OCR path - this should be auto-detected or configurable
try:
    import pytesseract
    # Try to auto-detect tesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    st.error("❌ pytesseract not installed. Please install: pip install pytesseract")

@dataclass
class OCRRegion:
    """OCR region configuration for screen capture"""
    name: str
    x1: int
    y1: int
    x2: int
    y2: int
    data_type: str  # "number", "text", "color"
    chart_id: int

@dataclass
class OCRReading:
    """Reading result from OCR"""
    region_name: str
    value: str
    confidence: float
    timestamp: datetime
    chart_id: int

class StreamlitOCRManager:
    """
    OCR Manager integrated with Streamlit
    Handles screen capture, region configuration, and real-time reading
    """
    
    def __init__(self):
        self.regions: Dict[str, OCRRegion] = {}
        self.latest_readings: Dict[str, OCRReading] = {}
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Initialize session state for OCR
        if 'ocr_regions' not in st.session_state:
            st.session_state.ocr_regions = {}
        
        if 'ocr_readings' not in st.session_state:
            st.session_state.ocr_readings = {}
        
        if 'ocr_monitoring' not in st.session_state:
            st.session_state.ocr_monitoring = False
    
    def render_ocr_configuration(self):
        """Render OCR configuration interface in Streamlit"""
        st.subheader("👁️ OCR Configuration")
        
        # Check if user config exists
        if 'user_config' not in st.session_state or not st.session_state.user_config:
            st.warning("⚠️ Please configure user settings first")
            return
        
        config = st.session_state.user_config
        
        # OCR enable/disable
        ocr_enabled = st.checkbox("Enable OCR Monitoring", value=st.session_state.ocr_monitoring)
        
        if ocr_enabled != st.session_state.ocr_monitoring:
            st.session_state.ocr_monitoring = ocr_enabled
            if ocr_enabled:
                self.start_monitoring()
            else:
                self.stop_monitoring()
        
        st.divider()
        
        # Region configuration for each chart
        st.subheader("📊 Chart Region Setup")
        
        for i in range(config.max_charts):
            chart_id = i + 1
            chart_name = config.chart_names[i] if i < len(config.chart_names) else f"Chart-{chart_id}"
            
            with st.expander(f"Chart {chart_id}: {chart_name}", expanded=False):
                self.render_chart_ocr_config(chart_id, chart_name)
        
        # Global OCR settings
        st.divider()
        st.subheader("⚙️ OCR Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reading_interval = st.slider("Reading Interval (seconds)", 0.5, 5.0, 1.0, 0.5)
            confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.7, 0.1)
        
        with col2:
            ocr_language = st.selectbox("OCR Language", ["eng", "eng+fra", "eng+spa"], index=0)
            preprocessing = st.selectbox("Image Preprocessing", ["auto", "threshold", "blur", "sharpen"], index=0)
        
        # Screen capture test
        st.divider()
        st.subheader("📸 Screen Capture Test")
        
        if st.button("🖥️ Capture Full Screen"):
            self.capture_and_display_screen()
        
        # Save/Load OCR configuration
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save OCR Config"):
                self.save_ocr_config()
                st.success("OCR configuration saved!")
        
        with col2:
            if st.button("📥 Load OCR Config"):
                self.load_ocr_config()
                st.success("OCR configuration loaded!")
    
    def render_chart_ocr_config(self, chart_id: int, chart_name: str):
        """Render OCR configuration for individual chart"""
        
        # Power Score region
        st.write("🔢 Power Score Region")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            power_x1 = st.number_input("X1", value=100, key=f"power_x1_{chart_id}")
        with col2:
            power_y1 = st.number_input("Y1", value=100, key=f"power_y1_{chart_id}")
        with col3:
            power_x2 = st.number_input("X2", value=200, key=f"power_x2_{chart_id}")
        with col4:
            power_y2 = st.number_input("Y2", value=130, key=f"power_y2_{chart_id}")
        
        # Signal Color region
        st.write("🎨 Signal Color Region")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            signal_x1 = st.number_input("X1", value=210, key=f"signal_x1_{chart_id}")
        with col2:
            signal_y1 = st.number_input("Y1", value=100, key=f"signal_y1_{chart_id}")
        with col3:
            signal_x2 = st.number_input("X2", value=280, key=f"signal_x2_{chart_id}")
        with col4:
            signal_y2 = st.number_input("Y2", value=130, key=f"signal_y2_{chart_id}")
        
        # Confluence Level regions
        st.write("📊 Confluence Levels")
        confluence_regions = {}
        
        for level in ["L1", "L2", "L3", "L4"]:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if level == "L1":
                    st.write(f"{level}")
                confluence_regions[level] = {
                    'x1': col1.number_input("", value=300 + (ord(level[1]) - ord('1')) * 30, key=f"conf_{level}_x1_{chart_id}", label_visibility="collapsed"),
                    'y1': col2.number_input("", value=100, key=f"conf_{level}_y1_{chart_id}", label_visibility="collapsed"),
                    'x2': col3.number_input("", value=330 + (ord(level[1]) - ord('1')) * 30, key=f"conf_{level}_x2_{chart_id}", label_visibility="collapsed"),
                    'y2': col4.number_input("", value=120, key=f"conf_{level}_y2_{chart_id}", label_visibility="collapsed")
                }
        
        # Store regions in session state
        chart_regions = {
            'power_score': {'x1': power_x1, 'y1': power_y1, 'x2': power_x2, 'y2': power_y2},
            'signal_color': {'x1': signal_x1, 'y1': signal_y1, 'x2': signal_x2, 'y2': signal_y2},
            'confluence': confluence_regions
        }
        
        st.session_state.ocr_regions[chart_id] = chart_regions
        
        # Test capture for this chart
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"📸 Test Power Score", key=f"test_power_{chart_id}"):
                self.test_region_capture(chart_id, "power_score")
        
        with col2:
            if st.button(f"🎨 Test Signal Color", key=f"test_signal_{chart_id}"):
                self.test_region_capture(chart_id, "signal_color")
    
    def capture_and_display_screen(self):
        """Capture and display full screen for region setup"""
        try:
            # Capture full screen
            screenshot = ImageGrab.grab()
            
            # Convert to bytes for streamlit display
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            st.image(img_byte_arr, caption="Full Screen Capture", use_column_width=True)
            
            # Display screen dimensions
            st.info(f"Screen Size: {screenshot.width} x {screenshot.height} pixels")
            
        except Exception as e:
            st.error(f"Error capturing screen: {e}")
    
    def test_region_capture(self, chart_id: int, region_type: str):
        """Test capture of specific region"""
        try:
            if chart_id not in st.session_state.ocr_regions:
                st.error(f"No regions configured for Chart {chart_id}")
                return
            
            regions = st.session_state.ocr_regions[chart_id]
            
            if region_type not in regions:
                st.error(f"Region '{region_type}' not found")
                return
            
            region = regions[region_type]
            bbox = (region['x1'], region['y1'], region['x2'], region['y2'])
            
            # Capture region
            screenshot = ImageGrab.grab(bbox=bbox)
            
            # Convert to bytes for display
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            st.image(img_byte_arr, caption=f"Chart {chart_id} - {region_type}", width=200)
            
            # Try OCR on the region
            if region_type == "power_score":
                ocr_result = self.read_power_score_from_image(screenshot)
                st.write(f"OCR Result: {ocr_result}")
            elif region_type == "signal_color":
                color_result = self.detect_color_from_image(screenshot)
                st.write(f"Color Detection: {color_result}")
            
        except Exception as e:
            st.error(f"Error testing region capture: {e}")
    
    def read_power_score_from_image(self, image: Image.Image) -> str:
        """Read power score from image using OCR"""
        try:
            # Convert to numpy array
            image_np = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            
            # Apply threshold for better OCR
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR configuration for numbers
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(thresh, config=custom_config).strip()
            
            return text if text.isdigit() else "0"
            
        except Exception as e:
            return f"Error: {e}"
    
    def detect_color_from_image(self, image: Image.Image) -> str:
        """Detect dominant color from image"""
        try:
            image_np = np.array(image)
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            
            # Define color ranges
            color_ranges = {
                "GREEN": ([40, 50, 50], [80, 255, 255]),
                "RED": ([0, 50, 50], [10, 255, 255]),
                "BLUE": ([100, 50, 50], [130, 255, 255]),
                "YELLOW": ([20, 50, 50], [40, 255, 255])
            }
            
            max_pixels = 0
            detected_color = "NONE"
            
            for color_name, (lower, upper) in color_ranges.items():
                lower_np = np.array(lower)
                upper_np = np.array(upper)
                mask = cv2.inRange(hsv, lower_np, upper_np)
                pixel_count = np.sum(mask)
                
                if pixel_count > max_pixels:
                    max_pixels = pixel_count
                    detected_color = color_name
            
            return detected_color if max_pixels > 100 else "NONE"
            
        except Exception as e:
            return f"Error: {e}"
    
    def start_monitoring(self):
        """Start OCR monitoring in background thread"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        st.success("🚀 OCR monitoring started")
    
    def stop_monitoring(self):
        """Stop OCR monitoring"""
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        
        st.info("🛑 OCR monitoring stopped")
    
    def monitoring_loop(self):
        """Main OCR monitoring loop"""
        while self.is_monitoring:
            try:
                # Read all configured charts
                for chart_id, regions in st.session_state.ocr_regions.items():
                    if chart_id in st.session_state.charts:
                        chart = st.session_state.charts[chart_id]
                        
                        if chart.is_enabled:
                            # Read power score
                            power_score = self.read_chart_power_score(chart_id, regions)
                            chart.power_score = power_score
                            
                            # Read signal color
                            signal_color = self.read_chart_signal_color(chart_id, regions)
                            
                            # Update chart status based on readings
                            if power_score >= 70:
                                chart.status_color = "green"
                                chart.signal_strength = "Strong"
                            elif power_score >= 40:
                                chart.status_color = "yellow"
                                chart.signal_strength = "Medium"
                            else:
                                chart.status_color = "red"
                                chart.signal_strength = "Weak"
                            
                            chart.last_update = datetime.now()
                
                time.sleep(1.0)  # Read every second
                
            except Exception as e:
                print(f"OCR monitoring error: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def read_chart_power_score(self, chart_id: int, regions: Dict) -> int:
        """Read power score for specific chart"""
        try:
            if 'power_score' not in regions:
                return 0
            
            region = regions['power_score']
            bbox = (region['x1'], region['y1'], region['x2'], region['y2'])
            
            screenshot = ImageGrab.grab(bbox=bbox)
            power_text = self.read_power_score_from_image(screenshot)
            
            return int(power_text) if power_text.isdigit() else 0
            
        except Exception as e:
            return 0
    
    def read_chart_signal_color(self, chart_id: int, regions: Dict) -> str:
        """Read signal color for specific chart"""
        try:
            if 'signal_color' not in regions:
                return "NONE"
            
            region = regions['signal_color']
            bbox = (region['x1'], region['y1'], region['x2'], region['y2'])
            
            screenshot = ImageGrab.grab(bbox=bbox)
            color = self.detect_color_from_image(screenshot)
            
            return color
            
        except Exception as e:
            return "NONE"
    
    def save_ocr_config(self):
        """Save OCR configuration to file"""
        try:
            config_data = {
                'regions': st.session_state.ocr_regions,
                'settings': {
                    'monitoring_enabled': st.session_state.ocr_monitoring
                }
            }
            
            import os
            os.makedirs("config", exist_ok=True)
            
            with open("config/ocr_config.json", 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            st.error(f"Error saving OCR config: {e}")
    
    def load_ocr_config(self):
        """Load OCR configuration from file"""
        try:
            with open("config/ocr_config.json", 'r') as f:
                config_data = json.load(f)
            
            st.session_state.ocr_regions = config_data.get('regions', {})
            settings = config_data.get('settings', {})
            
            if settings.get('monitoring_enabled', False):
                st.session_state.ocr_monitoring = True
                self.start_monitoring()
                
        except FileNotFoundError:
            st.warning("No OCR configuration file found")
        except Exception as e:
            st.error(f"Error loading OCR config: {e}")
    
    def render_ocr_status(self):
        """Render OCR status in main dashboard"""
        if not st.session_state.ocr_monitoring:
            st.warning("👁️ OCR Monitoring: DISABLED")
            return
        
        st.success("👁️ OCR Monitoring: ACTIVE")
        
        # Show latest readings
        if st.session_state.ocr_readings:
            st.subheader("📊 Latest OCR Readings")
            
            readings_data = []
            for reading in st.session_state.ocr_readings.values():
                readings_data.append({
                    "Chart": reading.chart_id,
                    "Region": reading.region_name,
                    "Value": reading.value,
                    "Confidence": f"{reading.confidence:.2f}",
                    "Time": reading.timestamp.strftime("%H:%M:%S")
                })
            
            if readings_data:
                import pandas as pd
                df = pd.DataFrame(readings_data)
                st.dataframe(df, hide_index=True)

def main():
    """Standalone OCR configuration interface"""
    st.set_page_config(
        page_title="OCR Configuration",
        page_icon="👁️",
        layout="wide"
    )
    
    st.title("👁️ OCR Configuration Interface")
    
    ocr_manager = StreamlitOCRManager()
    ocr_manager.render_ocr_configuration()

if __name__ == "__main__":
    main()
