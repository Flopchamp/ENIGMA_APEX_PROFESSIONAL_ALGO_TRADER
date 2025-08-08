"""
NinjaTrader Configuration Module
Handles ATI port configuration and connection settings
"""

import json
import os

CONFIG_FILE = "ninjatrader_settings.json"

def get_default_config():
    """Default NinjaTrader configuration"""
    return {
        "ati_port": 36973,  # Default ATI port from user's NinjaTrader
        "host": "localhost",
        "enabled": True,
        "charts": ["ES", "NQ", "YM", "RTY", "GC", "CL"],
        "layout": "3x2"
    }

def save_config(config):
    """Save NinjaTrader configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_config():
    """Load NinjaTrader configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return get_default_config()

# Initialize with default settings
config = load_config()

def get_ati_port():
    """Get current ATI port"""
    return config.get("ati_port", 36973)

def set_ati_port(port):
    """Set new ATI port"""
    config["ati_port"] = port
    save_config(config)

def get_connection_settings():
    """Get all connection settings"""
    return {
        "ati_port": get_ati_port(),
        "host": config.get("host", "localhost"),
        "enabled": config.get("enabled", True)
    }
