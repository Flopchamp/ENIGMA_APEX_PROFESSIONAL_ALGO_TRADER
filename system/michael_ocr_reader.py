#!/usr/bin/env python3
"""
MICHAEL'S 6-CHART OCR ENIGMA READER
===================================
Real-time screen reading for Michael's exact AlgoBox setup
- Monitors 6 charts: ES, NQ, YM, RTY, GC, CL
- Color detection for Enigma signals (Green=BUY, Red=SELL, Yellow=CAUTION)
- Sub-second response time using pixel color detection
- Sends signals to Kelly engine and control panel

SCREEN SETUP: 3x2 grid layout as seen in Michael's screenshot
"""

import cv2
import numpy as np
import json
import time
import threading
from datetime import datetime
import mss
import websocket
import logging
from pathlib import Path

class MichaelScreenReader:
    def __init__(self):
        self.config_path = Path(__file__).parent / "michael_screen_config.json"
        self.load_config()
        self.running = False
        self.signals = {}
        self.last_signals = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # WebSocket connection for sending signals
        self.ws_url = "ws://localhost:8765"
        self.ws = None
        
    def load_config(self):
        """Load Michael's screen configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info("✅ Loaded Michael's 6-chart screen configuration")
        except Exception as e:
            self.logger.error(f"❌ Failed to load config: {e}")
            # Create default config if missing
            self.create_default_config()
            
    def create_default_config(self):
        """Create default configuration for Michael's setup"""
        self.config = {
            "chart_regions": {
                "ES": {
                    "screen_region": {"x": 640, "y": 140, "width": 640, "height": 360},
                    "enigma_signal_region": {"x": 1200, "y": 280, "width": 60, "height": 60},
                    "success_probability": 68
                },
                "NQ": {
                    "screen_region": {"x": 1280, "y": 140, "width": 640, "height": 360},
                    "enigma_signal_region": {"x": 1840, "y": 280, "width": 60, "height": 60},
                    "success_probability": 72
                },
                "YM": {
                    "screen_region": {"x": 1920, "y": 140, "width": 640, "height": 360},
                    "enigma_signal_region": {"x": 2480, "y": 280, "width": 60, "height": 60},
                    "success_probability": 65
                },
                "RTY": {
                    "screen_region": {"x": 640, "y": 500, "width": 640, "height": 360},
                    "enigma_signal_region": {"x": 1200, "y": 640, "width": 60, "height": 60},
                    "success_probability": 63
                },
                "GC": {
                    "screen_region": {"x": 1280, "y": 500, "width": 640, "height": 360},
                    "enigma_signal_region": {"x": 1840, "y": 640, "width": 60, "height": 60},
                    "success_probability": 60
                },
                "CL": {
                    "screen_region": {"x": 1920, "y": 500, "width": 640, "height": 360},
                    "enigma_signal_region": {"x": 2480, "y": 640, "width": 60, "height": 60},
                    "success_probability": 58
                }
            },
            "signal_detection": {
                "colors": {
                    "BUY_SIGNAL": [0, 255, 0],
                    "SELL_SIGNAL": [255, 0, 0],
                    "CAUTION": [255, 255, 0],
                    "NEUTRAL": [128, 128, 128]
                },
                "tolerance": 30
            }
        }
        
    def connect_websocket(self):
        """Connect to WebSocket server for signal broadcasting"""
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(self.ws_url)
            self.logger.info("✅ Connected to WebSocket server")
        except Exception as e:
            self.logger.warning(f"⚠️ WebSocket connection failed: {e}")
            self.ws = None
            
    def capture_screen(self):
        """Capture the entire screen"""
        try:
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                
                return img
        except Exception as e:
            self.logger.error(f"❌ Screen capture failed: {e}")
            return None
            
    def detect_color_in_region(self, image, region, target_color, tolerance=30):
        """Detect if target color is present in specified region"""
        try:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            roi = image[y:y+h, x:x+w]
            
            # Convert target color to numpy array
            target = np.array(target_color)
            
            # Calculate color distance for each pixel
            distances = np.sqrt(np.sum((roi - target) ** 2, axis=2))
            
            # Check if any pixel is within tolerance
            matches = distances < tolerance
            match_percentage = np.sum(matches) / matches.size
            
            return match_percentage > 0.1  # At least 10% of pixels match
            
        except Exception as e:
            self.logger.error(f"❌ Color detection failed: {e}")
            return False
            
    def analyze_enigma_signal(self, image, chart_name):
        """Analyze Enigma signal for specific chart"""
        try:
            chart_config = self.config['chart_regions'][chart_name]
            signal_region = chart_config['enigma_signal_region']
            colors = self.config['signal_detection']['colors']
            tolerance = self.config['signal_detection']['tolerance']
            
            # Check for each signal color
            signals_detected = []
            
            if self.detect_color_in_region(image, signal_region, colors['BUY_SIGNAL'], tolerance):
                signals_detected.append('BUY')
                
            if self.detect_color_in_region(image, signal_region, colors['SELL_SIGNAL'], tolerance):
                signals_detected.append('SELL')
                
            if self.detect_color_in_region(image, signal_region, colors['CAUTION'], tolerance):
                signals_detected.append('CAUTION')
                
            # Return strongest signal (prioritize BUY/SELL over CAUTION)
            if 'BUY' in signals_detected:
                return 'BUY'
            elif 'SELL' in signals_detected:
                return 'SELL'
            elif 'CAUTION' in signals_detected:
                return 'CAUTION'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            self.logger.error(f"❌ Signal analysis failed for {chart_name}: {e}")
            return 'NEUTRAL'
            
    def process_all_charts(self):
        """Process all 6 charts in Michael's setup"""
        screenshot = self.capture_screen()
        if screenshot is None:
            return
            
        current_signals = {}
        
        # Analyze each chart
        for chart_name in ['ES', 'NQ', 'YM', 'RTY', 'GC', 'CL']:
            signal = self.analyze_enigma_signal(screenshot, chart_name)
            current_signals[chart_name] = {
                'signal': signal,
                'timestamp': datetime.now().isoformat(),
                'success_probability': self.config['chart_regions'][chart_name]['success_probability']
            }
            
        # Check for signal changes
        self.check_signal_changes(current_signals)
        self.signals = current_signals
        
    def check_signal_changes(self, new_signals):
        """Check for signal changes and broadcast them"""
        for chart_name, signal_data in new_signals.items():
            current_signal = signal_data['signal']
            last_signal = self.last_signals.get(chart_name, {}).get('signal', 'NEUTRAL')
            
            if current_signal != last_signal:
                self.logger.info(f"🔔 {chart_name}: {last_signal} → {current_signal}")
                
                # Broadcast signal change
                self.broadcast_signal(chart_name, signal_data)
                
        self.last_signals = new_signals.copy()
        
    def broadcast_signal(self, chart_name, signal_data):
        """Broadcast signal to WebSocket and other systems"""
        message = {
            'type': 'enigma_signal',
            'chart': chart_name,
            'signal': signal_data['signal'],
            'timestamp': signal_data['timestamp'],
            'success_probability': signal_data['success_probability']
        }
        
        # Send via WebSocket
        if self.ws:
            try:
                self.ws.send(json.dumps(message))
            except Exception as e:
                self.logger.warning(f"⚠️ WebSocket send failed: {e}")
                
        # Log to console for immediate feedback
        print(f"📊 {chart_name}: {signal_data['signal']} ({signal_data['success_probability']}%)")
        
    def run_monitoring(self):
        """Main monitoring loop"""
        self.logger.info("🚀 Starting Michael's 6-chart monitoring...")
        self.running = True
        
        # Connect to WebSocket
        self.connect_websocket()
        
        while self.running:
            try:
                start_time = time.time()
                
                # Process all charts
                self.process_all_charts()
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Log status every 10 seconds
                if int(time.time()) % 10 == 0:
                    active_signals = [f"{k}:{v['signal']}" for k, v in self.signals.items() if v['signal'] != 'NEUTRAL']
                    if active_signals:
                        self.logger.info(f"📊 Active: {', '.join(active_signals)} | Processing: {processing_time:.2f}s")
                    
                # Sleep to maintain ~1fps scanning
                time.sleep(max(0.5, 1.0 - processing_time))
                
            except KeyboardInterrupt:
                self.logger.info("👋 Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                time.sleep(5)  # Wait before retrying
                
        self.running = False
        
        # Close WebSocket
        if self.ws:
            self.ws.close()
            
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False

def main():
    """Main execution function"""
    print("👁️ MICHAEL'S 6-CHART ENIGMA READER")
    print("=" * 50)
    print("📊 Monitoring: ES, NQ, YM, RTY, GC, CL")
    print("🔍 Detection: Green=BUY, Red=SELL, Yellow=CAUTION")
    print("⚡ Speed: Sub-second color detection")
    print("=" * 50)
    
    reader = MichaelScreenReader()
    
    try:
        reader.run_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Reader stopped")
    finally:
        reader.stop_monitoring()

if __name__ == "__main__":
    main()
