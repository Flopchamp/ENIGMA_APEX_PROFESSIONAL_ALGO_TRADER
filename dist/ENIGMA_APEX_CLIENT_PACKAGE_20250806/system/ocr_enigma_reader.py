"""
🎯 ENIGMA-APEX OCR SIGNAL READER
Real-time AlgoBox Enigma panel reading with first principles analysis
Designed specifically for Michael Canfield's ChatGPT Agent vision
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageGrab
import json
import time
import asyncio
import websockets
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging

# Configure OCR path (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@dataclass
class EnigmaSignal:
    """Enigma signal data structure"""
    timestamp: datetime
    power_score: int
    confluence_level: str
    signal_color: str
    macvu_status: str
    atr_value: float
    session: str
    cadence_failures: int
    
class OCRSignalReader:
    """
    Advanced OCR system for reading AlgoBox Enigma signals
    Implements Michael's hybrid approach: OCR + Computer Vision + AI Enhancement
    """
    
    def __init__(self, config_path: str = "config/ocr_regions.json"):
        self.config_path = config_path
        self.regions = {}
        self.last_signal = None
        self.cadence_failures = 0
        self.session = "AM"  # AM or PM
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load or create OCR regions configuration
        self.load_or_create_config()
        
        # Signal validation thresholds
        self.validation_thresholds = {
            "power_score_min": 10,
            "power_score_max": 100,
            "confluence_levels": ["L1", "L2", "L3", "L4"],
            "signal_colors": ["GREEN", "RED", "BLUE", "PINK"],
            "macvu_states": ["GREEN", "RED", "NEUTRAL", "YELLOW"]
        }
        
        self.logger.info("🔍 OCR Signal Reader initialized")
    
    def load_or_create_config(self):
        """Load OCR regions config or create template"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Extract regions from config structure
            if "regions" in config_data:
                # Convert from new format to expected format
                self.regions = {}
                for region_name, region_data in config_data["regions"].items():
                    if "coordinates" in region_data:
                        self.regions[region_name] = region_data["coordinates"]
                    else:
                        # Fallback for different format
                        self.regions[region_name] = region_data
            else:
                # Assume old format where regions are at root level
                self.regions = config_data
                
            self.logger.info(f"✅ Loaded OCR config from {self.config_path}")
        except FileNotFoundError:
            # Create default configuration template
            self.regions = {
                "power_score": [100, 100, 200, 150],      # [x1, y1, x2, y2]
                "confluence_l1": [300, 100, 350, 130],
                "confluence_l2": [300, 130, 350, 160],
                "confluence_l3": [300, 160, 350, 190],
                "confluence_l4": [300, 190, 350, 220],
                "signal_color": [500, 100, 600, 200],
                "macvu_status": [700, 100, 800, 150],
                "atr_value": [900, 100, 1000, 150],
                "enigma_panel": [50, 50, 1200, 800]       # Full panel area
            }
            
            # Save template
            import os
            os.makedirs("config", exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.regions, f, indent=2)
            
            self.logger.warning(f"📝 Created OCR config template at {self.config_path}")
            self.logger.warning("⚠️  Please calibrate screen regions before using!")
    
    def capture_region(self, region_name: str) -> Optional[Image.Image]:
        """Capture specific screen region"""
        if region_name not in self.regions:
            self.logger.error(f"❌ Region '{region_name}' not found in config")
            return None
        
        try:
            bbox = tuple(self.regions[region_name])
            screenshot = ImageGrab.grab(bbox=bbox)
            return screenshot
        except Exception as e:
            self.logger.error(f"❌ Failed to capture region '{region_name}': {e}")
            return None
    
    def read_power_score(self) -> int:
        """Read Enigma Power Score using OCR"""
        try:
            image = self.capture_region("power_score")
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
            self.logger.error(f"❌ Failed to read power score: {e}")
            return 0
    
    def detect_confluence_level(self) -> str:
        """Detect active confluence level using color detection"""
        try:
            confluence_levels = ["L1", "L2", "L3", "L4"]
            active_level = "L0"  # Default
            
            for level in confluence_levels:
                region_name = f"confluence_{level.lower()}"
                image = self.capture_region(region_name)
                
                if image is None:
                    continue
                
                # Convert to numpy array for color analysis
                image_np = np.array(image)
                
                # Check for green color (active state)
                # Adjust these HSV ranges based on your AlgoBox theme
                hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
                green_lower = np.array([40, 50, 50])
                green_upper = np.array([80, 255, 255])
                green_mask = cv2.inRange(hsv, green_lower, green_upper)
                
                # If green pixels found, this level is active
                if np.sum(green_mask) > 100:  # Threshold for activation
                    active_level = level
            
            return active_level
            
        except Exception as e:
            self.logger.error(f"❌ Failed to detect confluence level: {e}")
            return "L0"
    
    def detect_signal_color(self) -> str:
        """Detect Enigma signal color using computer vision"""
        try:
            image = self.capture_region("signal_color")
            if image is None:
                return "NONE"
            
            image_np = np.array(image)
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            
            # Define color ranges (adjust based on your AlgoBox theme)
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
                
                if pixel_count > max_pixels:
                    max_pixels = pixel_count
                    detected_color = color_name
            
            # Require minimum pixel count for valid detection
            if max_pixels < 50:
                return "NONE"
            
            return detected_color
            
        except Exception as e:
            self.logger.error(f"❌ Failed to detect signal color: {e}")
            return "NONE"
    
    def read_macvu_status(self) -> str:
        """Read MACVU filter status"""
        try:
            image = self.capture_region("macvu_status")
            if image is None:
                return "NEUTRAL"
            
            image_np = np.array(image)
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            
            # Color detection for MACVU states
            color_ranges = {
                "GREEN": ([40, 50, 50], [80, 255, 255]),
                "RED": ([0, 50, 50], [10, 255, 255]),
                "YELLOW": ([20, 50, 50], [30, 255, 255])
            }
            
            for status, (lower, upper) in color_ranges.items():
                lower_np = np.array(lower)
                upper_np = np.array(upper)
                mask = cv2.inRange(hsv, lower_np, upper_np)
                
                if np.sum(mask) > 100:  # Threshold
                    return status
            
            return "NEUTRAL"
            
        except Exception as e:
            self.logger.error(f"❌ Failed to read MACVU status: {e}")
            return "NEUTRAL"
    
    def read_atr_value(self) -> float:
        """Read ATR value from chart"""
        try:
            image = self.capture_region("atr_value")
            if image is None:
                return 0.0
            
            # Preprocess for OCR
            image_np = np.array(image)
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR for decimal numbers
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789.'
            text = pytesseract.image_to_string(thresh, config=custom_config).strip()
            
            # Parse as float
            try:
                atr_value = float(text)
                if 0 < atr_value < 1000:  # Reasonable range
                    return atr_value
            except ValueError:
                pass
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"❌ Failed to read ATR value: {e}")
            return 0.0
    
    def read_full_panel(self) -> EnigmaSignal:
        """Read complete Enigma panel state"""
        try:
            timestamp = datetime.now()
            
            # Read all components
            power_score = self.read_power_score()
            confluence_level = self.detect_confluence_level()
            signal_color = self.detect_signal_color()
            macvu_status = self.read_macvu_status()
            atr_value = self.read_atr_value()
            
            # Determine session based on time
            current_hour = timestamp.hour
            session = "AM" if 6 <= current_hour < 12 else "PM"
            
            # Create signal object
            signal = EnigmaSignal(
                timestamp=timestamp,
                power_score=power_score,
                confluence_level=confluence_level,
                signal_color=signal_color,
                macvu_status=macvu_status,
                atr_value=atr_value,
                session=session,
                cadence_failures=self.cadence_failures
            )
            
            self.last_signal = signal
            return signal
            
        except Exception as e:
            self.logger.error(f"❌ Failed to read full panel: {e}")
            return None
    
    def validate_signal_quality(self, signal: EnigmaSignal) -> Dict:
        """Validate signal quality for trading decisions"""
        quality_score = 0.0
        issues = []
        
        # Power score validation
        if signal.power_score >= 20:
            quality_score += 0.3
        elif signal.power_score >= 15:
            quality_score += 0.2
        elif signal.power_score >= 10:
            quality_score += 0.1
        else:
            issues.append("Low power score")
        
        # Confluence validation
        if signal.confluence_level == "L4":
            quality_score += 0.3
        elif signal.confluence_level == "L3":
            quality_score += 0.2
        elif signal.confluence_level == "L2":
            quality_score += 0.1
        else:
            issues.append("Low confluence level")
        
        # MACVU filter validation
        if signal.macvu_status == "GREEN":
            quality_score += 0.2
        elif signal.macvu_status == "NEUTRAL":
            quality_score += 0.1
        else:
            issues.append("MACVU not aligned")
        
        # Signal color validation
        if signal.signal_color in ["GREEN", "BLUE"]:
            quality_score += 0.2
        elif signal.signal_color in ["RED", "PINK"]:
            quality_score += 0.2
        else:
            issues.append("No clear signal color")
        
        return {
            "quality_score": min(1.0, quality_score),
            "is_tradeable": quality_score >= 0.6,
            "issues": issues
        }
    
    def update_cadence_tracking(self, trade_outcome: str):
        """Update cadence failure tracking"""
        if trade_outcome == "WIN":
            self.cadence_failures = 0
            self.logger.info("✅ Cadence reset - winning trade")
        elif trade_outcome == "LOSS":
            self.cadence_failures += 1
            self.logger.info(f"❌ Cadence failure count: {self.cadence_failures}")
    
    def check_cadence_threshold(self) -> bool:
        """Check if cadence threshold is met for high-probability setup"""
        threshold = 2 if self.session == "AM" else 3
        return self.cadence_failures >= threshold
    
    async def start_continuous_monitoring(self, websocket_url: str = "ws://localhost:8765"):
        """Start continuous signal monitoring and transmission"""
        self.logger.info("🚀 Starting continuous Enigma signal monitoring")
        
        while True:
            try:
                # Read current panel state
                signal = self.read_full_panel()
                
                if signal is None:
                    await asyncio.sleep(1)
                    continue
                
                # Validate signal quality
                validation = self.validate_signal_quality(signal)
                
                # Check cadence for high-probability setup
                cadence_met = self.check_cadence_threshold()
                
                # Prepare signal data for transmission
                signal_data = {
                    "type": "enigma_signal",
                    "timestamp": signal.timestamp.isoformat(),
                    "power_score": signal.power_score,
                    "confluence_level": signal.confluence_level,
                    "signal_color": signal.signal_color,
                    "macvu_status": signal.macvu_status,
                    "atr_value": signal.atr_value,
                    "session": signal.session,
                    "cadence_failures": signal.cadence_failures,
                    "cadence_threshold_met": cadence_met,
                    "quality_score": validation["quality_score"],
                    "is_tradeable": validation["is_tradeable"],
                    "validation_issues": validation["issues"]
                }
                
                # Transmit to WebSocket server
                try:
                    async with websockets.connect(websocket_url) as websocket:
                        await websocket.send(json.dumps(signal_data))
                        
                        # Log significant signals
                        if validation["is_tradeable"] and cadence_met:
                            self.logger.info(f"🎯 HIGH-PROBABILITY SIGNAL: Power={signal.power_score}, "
                                           f"Confluence={signal.confluence_level}, Cadence={signal.cadence_failures}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Failed to transmit signal: {e}")
                
                # Wait before next reading (adjust frequency as needed)
                await asyncio.sleep(2)  # 2-second intervals
                
            except Exception as e:
                self.logger.error(f"❌ Error in continuous monitoring: {e}")
                await asyncio.sleep(5)
    
    def calibrate_screen_regions(self):
        """Interactive calibration tool for screen regions"""
        print("🎯 ENIGMA PANEL CALIBRATION TOOL")
        print("=" * 40)
        print("Please position your AlgoBox Enigma panel and follow instructions:")
        print()
        
        # Take screenshot for calibration
        full_screen = ImageGrab.grab()
        full_screen.save("calibration_screenshot.png")
        print("📸 Screenshot saved as 'calibration_screenshot.png'")
        print("Use this image to determine coordinates for each region.")
        print()
        
        # Guide user through calibration
        regions_to_calibrate = [
            ("power_score", "Enigma Power Score number"),
            ("confluence_l3", "L3 confluence button"),
            ("confluence_l4", "L4 confluence button"),
            ("signal_color", "Enigma signal color area"),
            ("macvu_status", "MACVU filter status"),
            ("atr_value", "ATR value display")
        ]
        
        for region_name, description in regions_to_calibrate:
            print(f"📍 Calibrating: {description}")
            print("Enter coordinates as: x1,y1,x2,y2 (top-left to bottom-right)")
            
            while True:
                try:
                    coords_input = input(f"{region_name}: ").strip()
                    coords = [int(x.strip()) for x in coords_input.split(',')]
                    
                    if len(coords) == 4:
                        self.regions[region_name] = coords
                        print(f"✅ Set {region_name}: {coords}")
                        break
                    else:
                        print("❌ Please enter exactly 4 coordinates")
                        
                except ValueError:
                    print("❌ Please enter valid numbers")
        
        # Save calibrated configuration
        with open(self.config_path, 'w') as f:
            json.dump(self.regions, f, indent=2)
        
        print(f"✅ Calibration saved to {self.config_path}")
        print("🚀 Ready for signal reading!")

def main():
    """Main function for standalone OCR testing"""
    ocr_reader = OCRSignalReader()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        # Run calibration tool
        ocr_reader.calibrate_screen_regions()
        return
    
    # Test signal reading
    print("🔍 Testing Enigma signal reading...")
    signal = ocr_reader.read_full_panel()
    
    if signal:
        print(f"📊 Power Score: {signal.power_score}")
        print(f"🎯 Confluence: {signal.confluence_level}")
        print(f"🎨 Signal Color: {signal.signal_color}")
        print(f"📈 MACVU: {signal.macvu_status}")
        print(f"📏 ATR: {signal.atr_value}")
        print(f"⏰ Session: {signal.session}")
        print(f"❌ Cadence Failures: {signal.cadence_failures}")
        
        validation = ocr_reader.validate_signal_quality(signal)
        print(f"✅ Quality Score: {validation['quality_score']:.2f}")
        print(f"📈 Tradeable: {validation['is_tradeable']}")
        
        if validation['issues']:
            print(f"⚠️  Issues: {', '.join(validation['issues'])}")
    else:
        print("❌ Failed to read signal")

if __name__ == "__main__":
    main()
