"""
🔍 MULTI-CHART OCR COORDINATOR
Handles OCR reading from 6 AlgoBox charts simultaneously
Designed for Michael's 6-chart trading setup
"""

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

# Configure OCR path (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@dataclass
class ChartSignal:
    """Signal data from individual chart"""
    chart_id: int
    chart_name: str
    power_score: int
    confluence_level: str
    signal_color: str
    macvu_status: str
    atr_value: float
    timestamp: datetime
    is_valid: bool

@dataclass
class ChartRegions:
    """Screen regions for individual chart"""
    chart_id: int
    chart_name: str
    power_score_region: List[int]  # [x1, y1, x2, y2]
    confluence_regions: Dict[str, List[int]]  # L1, L2, L3, L4 regions
    signal_color_region: List[int]
    macvu_region: List[int]
    atr_region: List[int]
    full_panel_region: List[int]

class MultiChartOCRCoordinator:
    """
    Coordinates OCR reading across 6 AlgoBox charts
    Each chart runs independently with its own screen regions
    """
    
    def __init__(self, config_path: str = "config/multi_chart_ocr_config.json"):
        self.config_path = config_path
        self.chart_regions: Dict[int, ChartRegions] = {}
        self.last_signals: Dict[int, ChartSignal] = {}
        self.is_monitoring = False
        self.monitoring_threads: Dict[int, threading.Thread] = {}
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load or create configuration
        self.load_or_create_config()
        
        # Signal validation thresholds
        self.validation_thresholds = {
            "power_score_min": 10,
            "power_score_max": 100,
            "confluence_levels": ["L1", "L2", "L3", "L4"],
            "signal_colors": ["GREEN", "RED", "BLUE", "PINK"],
            "macvu_states": ["GREEN", "RED", "NEUTRAL", "YELLOW"]
        }
        
        self.logger.info("🔍 Multi-Chart OCR Coordinator initialized for 6 charts")
    
    def load_or_create_config(self):
        """Load multi-chart OCR configuration or create template"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Load chart regions
            for chart_id_str, chart_config in config_data.get("charts", {}).items():
                chart_id = int(chart_id_str)
                self.chart_regions[chart_id] = ChartRegions(
                    chart_id=chart_id,
                    chart_name=chart_config["chart_name"],
                    power_score_region=chart_config["power_score_region"],
                    confluence_regions=chart_config["confluence_regions"],
                    signal_color_region=chart_config["signal_color_region"],
                    macvu_region=chart_config["macvu_region"],
                    atr_region=chart_config["atr_region"],
                    full_panel_region=chart_config["full_panel_region"]
                )
                
            self.logger.info(f"✅ Loaded OCR config for {len(self.chart_regions)} charts from {self.config_path}")
            
        except FileNotFoundError:
            # Create default configuration template for 6 charts
            self.create_default_config()
            
    def create_default_config(self):
        """Create default 6-chart configuration template"""
        # Michael's 6-chart layout assumptions:
        # Assume 3 charts on top row, 3 on bottom row
        # Each chart approximately 400x300 pixels
        
        chart_templates = {
            "1": {
                "chart_name": "ES-Account-1",
                "chart_position": "top-left",
                "base_x": 50, "base_y": 50,
                "width": 400, "height": 300
            },
            "2": {
                "chart_name": "ES-Account-2", 
                "chart_position": "top-center",
                "base_x": 500, "base_y": 50,
                "width": 400, "height": 300
            },
            "3": {
                "chart_name": "NQ-Account-1",
                "chart_position": "top-right", 
                "base_x": 950, "base_y": 50,
                "width": 400, "height": 300
            },
            "4": {
                "chart_name": "NQ-Account-2",
                "chart_position": "bottom-left",
                "base_x": 50, "base_y": 400,
                "width": 400, "height": 300
            },
            "5": {
                "chart_name": "YM-Account-1",
                "chart_position": "bottom-center",
                "base_x": 500, "base_y": 400,
                "width": 400, "height": 300
            },
            "6": {
                "chart_name": "RTY-Account-1",
                "chart_position": "bottom-right",
                "base_x": 950, "base_y": 400,
                "width": 400, "height": 300
            }
        }
        
        config = {"charts": {}}
        
        for chart_id, template in chart_templates.items():
            base_x = template["base_x"]
            base_y = template["base_y"]
            
            # Define relative positions within each chart
            chart_config = {
                "chart_name": template["chart_name"],
                "chart_position": template["chart_position"],
                "power_score_region": [base_x + 10, base_y + 10, base_x + 80, base_y + 40],
                "confluence_regions": {
                    "L1": [base_x + 100, base_y + 10, base_x + 130, base_y + 30],
                    "L2": [base_x + 100, base_y + 35, base_x + 130, base_y + 55],
                    "L3": [base_x + 100, base_y + 60, base_x + 130, base_y + 80],
                    "L4": [base_x + 100, base_y + 85, base_x + 130, base_y + 105]
                },
                "signal_color_region": [base_x + 150, base_y + 10, base_x + 220, base_y + 60],
                "macvu_region": [base_x + 240, base_y + 10, base_x + 310, base_y + 40],
                "atr_region": [base_x + 320, base_y + 10, base_x + 390, base_y + 40],
                "full_panel_region": [base_x, base_y, base_x + template["width"], base_y + template["height"]]
            }
            
            config["charts"][chart_id] = chart_config
            
            # Create ChartRegions object
            self.chart_regions[int(chart_id)] = ChartRegions(
                chart_id=int(chart_id),
                chart_name=chart_config["chart_name"],
                power_score_region=chart_config["power_score_region"],
                confluence_regions=chart_config["confluence_regions"],
                signal_color_region=chart_config["signal_color_region"],
                macvu_region=chart_config["macvu_region"],
                atr_region=chart_config["atr_region"],
                full_panel_region=chart_config["full_panel_region"]
            )
        
        # Save template
        import os
        os.makedirs("config", exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.warning(f"📝 Created multi-chart OCR config template at {self.config_path}")
        self.logger.warning("⚠️  Please calibrate screen regions for each of your 6 charts!")
        
    def capture_chart_region(self, chart_id: int, region_name: str) -> Optional[Image.Image]:
        """Capture specific region from specific chart"""
        if chart_id not in self.chart_regions:
            self.logger.error(f"❌ Chart {chart_id} not found in configuration")
            return None
            
        chart_regions = self.chart_regions[chart_id]
        
        try:
            if region_name == "power_score":
                bbox = tuple(chart_regions.power_score_region)
            elif region_name.startswith("confluence_"):
                level = region_name.split("_")[1].upper()
                if level in chart_regions.confluence_regions:
                    bbox = tuple(chart_regions.confluence_regions[level])
                else:
                    return None
            elif region_name == "signal_color":
                bbox = tuple(chart_regions.signal_color_region)
            elif region_name == "macvu":
                bbox = tuple(chart_regions.macvu_region)
            elif region_name == "atr":
                bbox = tuple(chart_regions.atr_region)
            elif region_name == "full_panel":
                bbox = tuple(chart_regions.full_panel_region)
            else:
                self.logger.error(f"❌ Unknown region '{region_name}'")
                return None
                
            screenshot = ImageGrab.grab(bbox=bbox)
            return screenshot
            
        except Exception as e:
            self.logger.error(f"❌ Failed to capture region '{region_name}' from chart {chart_id}: {e}")
            return None
    
    def read_chart_power_score(self, chart_id: int) -> int:
        """Read power score from specific chart"""
        try:
            image = self.capture_chart_region(chart_id, "power_score")
            if image is None:
                return 0
            
            # Preprocess image for better OCR
            image_np = np.array(image)
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            
            # Apply thresholding for better text recognition
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR configuration for numbers
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(thresh, config=custom_config).strip()
            
            # Parse and validate
            if text.isdigit():
                power_score = int(text)
                if self.validation_thresholds["power_score_min"] <= power_score <= self.validation_thresholds["power_score_max"]:
                    return power_score
            
            return 0
            
        except Exception as e:
            self.logger.error(f"❌ Failed to read power score from chart {chart_id}: {e}")
            return 0
    
    def detect_chart_confluence_level(self, chart_id: int) -> str:
        """Detect active confluence level for specific chart"""
        try:
            confluence_levels = ["L1", "L2", "L3", "L4"]
            active_level = "L0"  # Default
            
            for level in confluence_levels:
                image = self.capture_chart_region(chart_id, f"confluence_{level.lower()}")
                
                if image is None:
                    continue
                
                # Convert to numpy array for color analysis
                image_np = np.array(image)
                
                # Check for green color (active state)
                hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
                green_lower = np.array([40, 50, 50])
                green_upper = np.array([80, 255, 255])
                green_mask = cv2.inRange(hsv, green_lower, green_upper)
                
                # If green pixels found, this level is active
                if np.sum(green_mask) > 100:  # Threshold for activation
                    active_level = level
            
            return active_level
            
        except Exception as e:
            self.logger.error(f"❌ Failed to detect confluence level for chart {chart_id}: {e}")
            return "L0"
    
    def detect_chart_signal_color(self, chart_id: int) -> str:
        """Detect signal color for specific chart"""
        try:
            image = self.capture_chart_region(chart_id, "signal_color")
            if image is None:
                return "NONE"
            
            image_np = np.array(image)
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            
            # Define color ranges
            color_ranges = {
                "GREEN": ([40, 50, 50], [80, 255, 255]),
                "RED": ([0, 50, 50], [10, 255, 255]),
                "BLUE": ([100, 50, 50], [130, 255, 255]),
                "PINK": ([140, 50, 50], [170, 255, 255])
            }
            
            max_pixels = 0
            detected_color = "NONE"
            
            for color_name, (lower, upper) in color_ranges.items():
                lower_np = np.array(lower)
                upper_np = np.array(upper)
                mask = cv2.inRange(hsv, lower_np, upper_np)
                pixel_count = np.sum(mask)
                
                if pixel_count > max_pixels and pixel_count > 200:  # Minimum threshold
                    max_pixels = pixel_count
                    detected_color = color_name
            
            return detected_color
            
        except Exception as e:
            self.logger.error(f"❌ Failed to detect signal color for chart {chart_id}: {e}")
            return "NONE"
    
    def read_chart_signals(self, chart_id: int) -> ChartSignal:
        """Read all signals from specific chart"""
        try:
            chart_regions = self.chart_regions[chart_id]
            
            # Read individual components
            power_score = self.read_chart_power_score(chart_id)
            confluence_level = self.detect_chart_confluence_level(chart_id)
            signal_color = self.detect_chart_signal_color(chart_id)
            
            # For now, simulate MACVU and ATR (can be implemented later)
            macvu_status = "GREEN"  # Simulated
            atr_value = 2.5  # Simulated
            
            # Validate signal
            is_valid = (
                power_score > 0 and
                confluence_level in ["L1", "L2", "L3", "L4"] and
                signal_color in self.validation_thresholds["signal_colors"]
            )
            
            signal = ChartSignal(
                chart_id=chart_id,
                chart_name=chart_regions.chart_name,
                power_score=power_score,
                confluence_level=confluence_level,
                signal_color=signal_color,
                macvu_status=macvu_status,
                atr_value=atr_value,
                timestamp=datetime.now(),
                is_valid=is_valid
            )
            
            self.last_signals[chart_id] = signal
            return signal
            
        except Exception as e:
            self.logger.error(f"❌ Failed to read signals from chart {chart_id}: {e}")
            return ChartSignal(chart_id, f"Chart-{chart_id}", 0, "L0", "NONE", "NONE", 0.0, datetime.now(), False)
    
    def read_all_charts(self) -> Dict[int, ChartSignal]:
        """Read signals from all 6 charts simultaneously"""
        signals = {}
        
        for chart_id in self.chart_regions.keys():
            signal = self.read_chart_signals(chart_id)
            signals[chart_id] = signal
            
        return signals
    
    def start_monitoring_chart(self, chart_id: int):
        """Start monitoring specific chart in separate thread"""
        def monitor_loop():
            self.logger.info(f"🔍 Started monitoring Chart {chart_id} ({self.chart_regions[chart_id].chart_name})")
            
            while self.is_monitoring:
                try:
                    signal = self.read_chart_signals(chart_id)
                    
                    if signal.is_valid:
                        self.logger.info(f"📊 Chart {chart_id}: Power={signal.power_score}%, "
                                       f"Level={signal.confluence_level}, Color={signal.signal_color}")
                    
                    time.sleep(1)  # Read every second
                    
                except Exception as e:
                    self.logger.error(f"❌ Monitoring error for Chart {chart_id}: {e}")
                    time.sleep(5)  # Wait longer on error
                    
            self.logger.info(f"🛑 Stopped monitoring Chart {chart_id}")
        
        thread = threading.Thread(target=monitor_loop)
        thread.daemon = True
        thread.start()
        self.monitoring_threads[chart_id] = thread
    
    def start_monitoring_all_charts(self):
        """Start monitoring all 6 charts simultaneously"""
        self.is_monitoring = True
        
        for chart_id in self.chart_regions.keys():
            self.start_monitoring_chart(chart_id)
            
        self.logger.info(f"🚀 Started monitoring all {len(self.chart_regions)} charts")
    
    def stop_monitoring_all_charts(self):
        """Stop monitoring all charts"""
        self.is_monitoring = False
        
        # Wait for threads to finish
        for chart_id, thread in self.monitoring_threads.items():
            if thread.is_alive():
                thread.join(timeout=2)
                
        self.monitoring_threads.clear()
        self.logger.info("🛑 Stopped monitoring all charts")
    
    def get_latest_signals(self) -> Dict[int, ChartSignal]:
        """Get latest signals from all charts"""
        return self.last_signals.copy()
    
    def calibrate_chart_regions(self, chart_id: int):
        """Interactive calibration for chart regions (placeholder)"""
        self.logger.info(f"🔧 Calibrating regions for Chart {chart_id}")
        self.logger.info("Implementation: Use screenshot tool to set coordinates for each region")
        # Future: Implement interactive region selection tool
    
    def test_chart_regions(self, chart_id: int) -> Dict[str, bool]:
        """Test if chart regions are correctly configured"""
        results = {}
        
        try:
            # Test each region
            regions_to_test = ["power_score", "signal_color", "macvu", "atr", "full_panel"]
            
            for region in regions_to_test:
                image = self.capture_chart_region(chart_id, region)
                results[region] = image is not None
                
            # Test confluence regions
            for level in ["L1", "L2", "L3", "L4"]:
                image = self.capture_chart_region(chart_id, f"confluence_{level.lower()}")
                results[f"confluence_{level}"] = image is not None
                
            self.logger.info(f"📋 Chart {chart_id} region test results: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to test chart {chart_id} regions: {e}")
            return {}
    
    def get_monitoring_status(self) -> Dict[str, any]:
        """Get current monitoring status"""
        return {
            "is_monitoring": self.is_monitoring,
            "charts_configured": len(self.chart_regions),
            "active_threads": len([t for t in self.monitoring_threads.values() if t.is_alive()]),
            "last_signals_count": len(self.last_signals),
            "chart_names": [regions.chart_name for regions in self.chart_regions.values()]
        }

def main():
    """Test the multi-chart OCR coordinator"""
    coordinator = MultiChartOCRCoordinator()
    
    print("🔍 Multi-Chart OCR Coordinator Test")
    print(f"📊 Configured charts: {len(coordinator.chart_regions)}")
    
    for chart_id, regions in coordinator.chart_regions.items():
        print(f"   Chart {chart_id}: {regions.chart_name}")
    
    # Test reading from all charts
    print("\n📖 Testing signal reading from all charts...")
    signals = coordinator.read_all_charts()
    
    for chart_id, signal in signals.items():
        print(f"Chart {chart_id} ({signal.chart_name}): "
              f"Power={signal.power_score}%, Level={signal.confluence_level}, "
              f"Color={signal.signal_color}, Valid={signal.is_valid}")
    
    # Start monitoring for a short time
    print("\n🚀 Starting 10-second monitoring test...")
    coordinator.start_monitoring_all_charts()
    time.sleep(10)
    coordinator.stop_monitoring_all_charts()
    
    print("✅ Multi-chart OCR test completed")

if __name__ == "__main__":
    main()
