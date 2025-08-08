"""
🔍 STREAMLIT OCR INTEGRATION
OCR coordinator integrated with Streamlit dashboard for real-time chart reading
Universal system for any trading setup with AlgoBox or similar OCR sources
"""

import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageGrab
import json
import time
import asyncio
import threading
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging
import base64
from io import BytesIO

@dataclass
class OCRSignal:
    """OCR signal data from individual chart"""
    chart_id: int
    chart_name: str
    power_score: int
    confluence_level: str
    signal_color: str
    macvu_status: str
    atr_value: float
    timestamp: datetime
    is_valid: bool
    raw_image_data: Optional[str] = None  # Base64 encoded image

@dataclass
class OCRRegion:
    """Screen region configuration for OCR"""
    chart_id: int
    region_name: str
    x1: int
    y1: int
    x2: int
    y2: int
    is_active: bool = True

class StreamlitOCRCoordinator:
    """
    OCR Coordinator integrated with Streamlit
    Handles screen reading from multiple trading charts
    """
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_logging()
        
        # OCR settings
        self.ocr_config = {
            "tesseract_cmd": r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            "confidence_threshold": 60,
            "power_score_config": r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
            "text_config": r'--oem 3 --psm 6'
        }
        
        # Try to set tesseract path
        try:
            pytesseract.pytesseract.tesseract_cmd = self.ocr_config["tesseract_cmd"]
        except:
            pass  # Will handle missing tesseract gracefully
    
    def initialize_session_state(self):
        """Initialize Streamlit session state for OCR"""
        if 'ocr_regions' not in st.session_state:
            st.session_state.ocr_regions = {}
            self.create_default_regions()
        
        if 'ocr_signals' not in st.session_state:
            st.session_state.ocr_signals = {}
        
        if 'ocr_enabled' not in st.session_state:
            st.session_state.ocr_enabled = False
        
        if 'ocr_auto_refresh' not in st.session_state:
            st.session_state.ocr_auto_refresh = False
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def create_default_regions(self):
        """Create default OCR regions for 6 charts"""
        # Default 2x3 grid layout assumptions
        chart_layouts = [
            {"id": 1, "pos": "top-left", "base_x": 50, "base_y": 50},
            {"id": 2, "pos": "top-center", "base_x": 500, "base_y": 50},
            {"id": 3, "pos": "top-right", "base_x": 950, "base_y": 50},
            {"id": 4, "pos": "bottom-left", "base_x": 50, "base_y": 400},
            {"id": 5, "pos": "bottom-center", "base_x": 500, "base_y": 400},
            {"id": 6, "pos": "bottom-right", "base_x": 950, "base_y": 400}
        ]
        
        for layout in chart_layouts:
            chart_id = layout["id"]
            base_x = layout["base_x"]
            base_y = layout["base_y"]
            
            # Create regions for each chart
            regions = [
                OCRRegion(chart_id, "power_score", base_x + 10, base_y + 10, base_x + 80, base_y + 40),
                OCRRegion(chart_id, "confluence", base_x + 100, base_y + 10, base_x + 150, base_y + 40),
                OCRRegion(chart_id, "signal_color", base_x + 160, base_y + 10, base_x + 220, base_y + 40),
                OCRRegion(chart_id, "macvu", base_x + 230, base_y + 10, base_x + 300, base_y + 40),
                OCRRegion(chart_id, "full_chart", base_x, base_y, base_x + 400, base_y + 300)
            ]
            
            if chart_id not in st.session_state.ocr_regions:
                st.session_state.ocr_regions[chart_id] = {}
            
            for region in regions:
                st.session_state.ocr_regions[chart_id][region.region_name] = region
    
    def capture_screen_region(self, region: OCRRegion) -> Optional[Image.Image]:
        """Capture screen region and return PIL Image"""
        try:
            bbox = (region.x1, region.y1, region.x2, region.y2)
            screenshot = ImageGrab.grab(bbox=bbox)
            return screenshot
        except Exception as e:
            self.logger.error(f"Failed to capture region {region.region_name}: {e}")
            return None
    
    def image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def preprocess_image_for_ocr(self, image: Image.Image, region_type: str = "text") -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert to numpy array
        img_np = np.array(image)
        
        # Convert to grayscale
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np
        
        if region_type == "power_score":
            # For numbers, use stronger thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = np.ones((2,2), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return thresh
        
        elif region_type == "signal_color":
            # For color detection, return original
            return img_np
        
        else:
            # General text preprocessing
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return thresh
    
    def read_power_score(self, chart_id: int) -> int:
        """Read power score from chart"""
        try:
            if chart_id not in st.session_state.ocr_regions:
                return 0
            
            if "power_score" not in st.session_state.ocr_regions[chart_id]:
                return 0
            
            region = st.session_state.ocr_regions[chart_id]["power_score"]
            image = self.capture_screen_region(region)
            
            if image is None:
                return 0
            
            # Preprocess for OCR
            processed_img = self.preprocess_image_for_ocr(image, "power_score")
            
            # OCR with number-specific config
            text = pytesseract.image_to_string(
                processed_img, 
                config=self.ocr_config["power_score_config"]
            ).strip()
            
            # Parse and validate
            if text.isdigit():
                power_score = int(text)
                if 0 <= power_score <= 100:
                    return power_score
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error reading power score from chart {chart_id}: {e}")
            return 0
    
    def detect_signal_color(self, chart_id: int) -> str:
        """Detect signal color from chart"""
        try:
            if chart_id not in st.session_state.ocr_regions:
                return "NONE"
            
            if "signal_color" not in st.session_state.ocr_regions[chart_id]:
                return "NONE"
            
            region = st.session_state.ocr_regions[chart_id]["signal_color"]
            image = self.capture_screen_region(region)
            
            if image is None:
                return "NONE"
            
            # Convert to HSV for color detection
            img_np = np.array(image)
            hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
            
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
                
                if pixel_count > max_pixels and pixel_count > 100:  # Minimum threshold
                    max_pixels = pixel_count
                    detected_color = color_name
            
            return detected_color
            
        except Exception as e:
            self.logger.error(f"Error detecting signal color from chart {chart_id}: {e}")
            return "NONE"
    
    def read_confluence_level(self, chart_id: int) -> str:
        """Read confluence level from chart"""
        try:
            if chart_id not in st.session_state.ocr_regions:
                return "L0"
            
            if "confluence" not in st.session_state.ocr_regions[chart_id]:
                return "L0"
            
            region = st.session_state.ocr_regions[chart_id]["confluence"]
            image = self.capture_screen_region(region)
            
            if image is None:
                return "L0"
            
            # Preprocess for OCR
            processed_img = self.preprocess_image_for_ocr(image, "text")
            
            # OCR
            text = pytesseract.image_to_string(
                processed_img, 
                config=self.ocr_config["text_config"]
            ).strip().upper()
            
            # Parse confluence level
            for level in ["L4", "L3", "L2", "L1"]:  # Check highest first
                if level in text:
                    return level
            
            return "L0"
            
        except Exception as e:
            self.logger.error(f"Error reading confluence level from chart {chart_id}: {e}")
            return "L0"
    
    def read_chart_signals(self, chart_id: int) -> OCRSignal:
        """Read all signals from specific chart"""
        try:
            chart_name = f"Chart-{chart_id}"
            
            # Get chart name from session state if available
            if 'chart_data' in st.session_state and chart_id in st.session_state.chart_data:
                chart_name = st.session_state.chart_data[chart_id].account_name
            
            # Read individual components
            power_score = self.read_power_score(chart_id)
            signal_color = self.detect_signal_color(chart_id)
            confluence_level = self.read_confluence_level(chart_id)
            
            # Simulate other values for now
            macvu_status = "GREEN" if power_score > 50 else "RED"
            atr_value = 2.5  # Simulated
            
            # Validate signal
            is_valid = (
                power_score > 0 and
                signal_color != "NONE" and
                confluence_level != "L0"
            )
            
            # Capture screenshot for display
            raw_image_data = None
            if chart_id in st.session_state.ocr_regions and "full_chart" in st.session_state.ocr_regions[chart_id]:
                full_region = st.session_state.ocr_regions[chart_id]["full_chart"]
                full_image = self.capture_screen_region(full_region)
                if full_image:
                    raw_image_data = self.image_to_base64(full_image)
            
            signal = OCRSignal(
                chart_id=chart_id,
                chart_name=chart_name,
                power_score=power_score,
                confluence_level=confluence_level,
                signal_color=signal_color,
                macvu_status=macvu_status,
                atr_value=atr_value,
                timestamp=datetime.now(),
                is_valid=is_valid,
                raw_image_data=raw_image_data
            )
            
            # Store in session state
            st.session_state.ocr_signals[chart_id] = signal
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error reading signals from chart {chart_id}: {e}")
            return OCRSignal(
                chart_id, f"Chart-{chart_id}", 0, "L0", "NONE", 
                "ERROR", 0.0, datetime.now(), False
            )
    
    def read_all_charts(self) -> Dict[int, OCRSignal]:
        """Read signals from all configured charts"""
        signals = {}
        
        if not st.session_state.ocr_enabled:
            return signals
        
        for chart_id in range(1, 7):  # Always check 6 charts
            signal = self.read_chart_signals(chart_id)
            signals[chart_id] = signal
        
        return signals
    
    def update_chart_data_with_ocr(self):
        """Update chart data in session state with OCR results"""
        if not st.session_state.ocr_enabled:
            return
        
        signals = self.read_all_charts()
        
        for chart_id, signal in signals.items():
            if 'chart_data' in st.session_state and chart_id in st.session_state.chart_data:
                # Update chart data with OCR results
                chart_data = st.session_state.chart_data[chart_id]
                
                chart_data.last_signal = signal.signal_color
                chart_data.signal_strength = signal.power_score
                chart_data.confluence_level = signal.confluence_level
                chart_data.last_update = signal.timestamp
                
                # Update margin percentage based on signal strength
                if signal.is_valid and signal.power_score > 70:
                    # Strong signal - higher margin usage allowed
                    new_margin = min(90, chart_data.margin_percentage + 5)
                elif signal.is_valid and signal.power_score > 40:
                    # Medium signal - moderate margin
                    new_margin = max(40, min(70, chart_data.margin_percentage))
                else:
                    # Weak/no signal - conservative margin
                    new_margin = max(20, chart_data.margin_percentage - 5)
                
                chart_data.margin_percentage = new_margin
                chart_data.margin_remaining = chart_data.account_balance * (new_margin / 100)
    
    def create_ocr_settings_ui(self):
        """Create OCR settings UI in sidebar"""
        with st.sidebar:
            st.header("🔍 OCR Settings")
            
            # Enable/disable OCR
            ocr_enabled = st.checkbox(
                "Enable OCR Reading",
                value=st.session_state.ocr_enabled,
                help="Enable automatic screen reading from trading charts"
            )
            
            if ocr_enabled != st.session_state.ocr_enabled:
                st.session_state.ocr_enabled = ocr_enabled
            
            # Auto-refresh
            auto_refresh = st.checkbox(
                "Auto Refresh",
                value=st.session_state.ocr_auto_refresh,
                help="Automatically refresh OCR data every few seconds"
            )
            
            if auto_refresh != st.session_state.ocr_auto_refresh:
                st.session_state.ocr_auto_refresh = auto_refresh
            
            if st.session_state.ocr_enabled:
                # Manual refresh button
                if st.button("🔄 Read All Charts", use_container_width=True):
                    self.update_chart_data_with_ocr()
                    st.success("OCR data updated!")
                
                # Region calibration
                st.subheader("📐 Region Calibration")
                
                if st.button("Configure Regions", use_container_width=True):
                    self.show_region_config()
    
    def show_region_config(self):
        """Show region configuration interface"""
        st.subheader("📐 OCR Region Configuration")
        
        st.info("""
        **Setup Instructions:**
        1. Position your trading charts in a 2x3 grid
        2. Adjust the coordinates below to match your screen
        3. Test each region to verify OCR accuracy
        4. Save configuration when satisfied
        """)
        
        # Chart selection
        selected_chart = st.selectbox(
            "Select Chart to Configure",
            options=list(range(1, 7)),
            format_func=lambda x: f"Chart {x}"
        )
        
        if selected_chart in st.session_state.ocr_regions:
            chart_regions = st.session_state.ocr_regions[selected_chart]
            
            for region_name, region in chart_regions.items():
                st.markdown(f"**{region_name.replace('_', ' ').title()}**")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    new_x1 = st.number_input(f"X1", value=region.x1, key=f"{selected_chart}_{region_name}_x1")
                
                with col2:
                    new_y1 = st.number_input(f"Y1", value=region.y1, key=f"{selected_chart}_{region_name}_y1")
                
                with col3:
                    new_x2 = st.number_input(f"X2", value=region.x2, key=f"{selected_chart}_{region_name}_x2")
                
                with col4:
                    new_y2 = st.number_input(f"Y2", value=region.y2, key=f"{selected_chart}_{region_name}_y2")
                
                # Update region if values changed
                if (new_x1, new_y1, new_x2, new_y2) != (region.x1, region.y1, region.x2, region.y2):
                    region.x1, region.y1, region.x2, region.y2 = new_x1, new_y1, new_x2, new_y2
                
                # Test region
                if st.button(f"Test {region_name}", key=f"test_{selected_chart}_{region_name}"):
                    self.test_region(selected_chart, region_name)
    
    def test_region(self, chart_id: int, region_name: str):
        """Test specific OCR region"""
        try:
            region = st.session_state.ocr_regions[chart_id][region_name]
            image = self.capture_screen_region(region)
            
            if image:
                # Display captured image
                st.image(image, caption=f"Captured: {region_name}", width=200)
                
                # Perform OCR based on region type
                if region_name == "power_score":
                    result = self.read_power_score(chart_id)
                    st.success(f"Power Score: {result}")
                elif region_name == "signal_color":
                    result = self.detect_signal_color(chart_id)
                    st.success(f"Signal Color: {result}")
                elif region_name == "confluence":
                    result = self.read_confluence_level(chart_id)
                    st.success(f"Confluence Level: {result}")
                else:
                    st.info("Image captured successfully")
            else:
                st.error("Failed to capture image")
                
        except Exception as e:
            st.error(f"Test failed: {e}")
    
    def create_ocr_status_display(self):
        """Create OCR status display"""
        if st.session_state.ocr_enabled and st.session_state.ocr_signals:
            st.subheader("🔍 Live OCR Data")
            
            # Create columns for OCR data
            cols = st.columns(3)
            
            for idx, (chart_id, signal) in enumerate(st.session_state.ocr_signals.items()):
                col_idx = idx % 3
                
                with cols[col_idx]:
                    # Status color based on signal validity
                    status_color = "#00ff88" if signal.is_valid else "#ff4444"
                    
                    st.markdown(f"""
                    <div style='
                        padding: 10px; 
                        background-color: {status_color}; 
                        border-radius: 5px; 
                        margin: 5px 0;
                        color: black;
                    '>
                        <strong>{signal.chart_name}</strong><br>
                        Power: {signal.power_score}%<br>
                        Color: {signal.signal_color}<br>
                        Level: {signal.confluence_level}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show captured image if available
                    if signal.raw_image_data:
                        try:
                            img_data = base64.b64decode(signal.raw_image_data)
                            img = Image.open(BytesIO(img_data))
                            st.image(img, caption=f"Chart {chart_id}", width=150)
                        except:
                            pass

def main():
    """Main function for testing OCR coordinator"""
    st.title("🔍 OCR Coordinator Test")
    
    ocr = StreamlitOCRCoordinator()
    ocr.create_ocr_settings_ui()
    ocr.create_ocr_status_display()
    
    if st.session_state.ocr_enabled:
        if st.button("Test All Charts"):
            signals = ocr.read_all_charts()
            st.json({k: v.__dict__ for k, v in signals.items()})

if __name__ == "__main__":
    main()
