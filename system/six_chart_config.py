#!/usr/bin/env python3
"""
🎯 ENIGMA APEX - 6-CHART CONFIGURATION SYSTEM
Professional multi-chart trading setup with predefined accounts
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class SixChartManager:
    """Manages 6-chart trading system with predefined accounts"""
    
    def __init__(self):
        self.chart_configs = self.load_default_configs()
        self.account_settings = self.load_account_settings()
        
    def load_default_configs(self) -> Dict[str, Any]:
        """Load default 6-chart configurations"""
        return {
            "layout": {
                "type": "3x2",
                "auto_arrange": True,
                "sync_enabled": True,
                "real_time_updates": True
            },
            "charts": [
                {
                    "id": "chart_1",
                    "symbol": "ES",
                    "name": "S&P 500 E-mini",
                    "timeframe": "5min",
                    "position": (0, 0),
                    "account": "ES_SCALPING",
                    "color_theme": "professional_blue",
                    "indicators": ["PowerScore", "RiskManager", "SignalGen"],
                    "alerts_enabled": True
                },
                {
                    "id": "chart_2", 
                    "symbol": "NQ",
                    "name": "Nasdaq E-mini",
                    "timeframe": "5min",
                    "position": (0, 1),
                    "account": "NQ_MOMENTUM",
                    "color_theme": "professional_blue",
                    "indicators": ["PowerScore", "RiskManager", "SignalGen"],
                    "alerts_enabled": True
                },
                {
                    "id": "chart_3",
                    "symbol": "YM", 
                    "name": "Dow Jones E-mini",
                    "timeframe": "5min",
                    "position": (0, 2),
                    "account": "YM_SWING",
                    "color_theme": "professional_blue",
                    "indicators": ["PowerScore", "RiskManager", "SignalGen"],
                    "alerts_enabled": True
                },
                {
                    "id": "chart_4",
                    "symbol": "RTY",
                    "name": "Russell 2000 E-mini", 
                    "timeframe": "5min",
                    "position": (1, 0),
                    "account": "RTY_BREAKOUT",
                    "color_theme": "professional_blue",
                    "indicators": ["PowerScore", "RiskManager", "SignalGen"],
                    "alerts_enabled": True
                },
                {
                    "id": "chart_5",
                    "symbol": "GC",
                    "name": "Gold Futures",
                    "timeframe": "15min",
                    "position": (1, 1),
                    "account": "GC_TREND", 
                    "color_theme": "professional_gold",
                    "indicators": ["PowerScore", "RiskManager", "TrendFollower"],
                    "alerts_enabled": True
                },
                {
                    "id": "chart_6",
                    "symbol": "CL",
                    "name": "Crude Oil Futures",
                    "timeframe": "15min", 
                    "position": (1, 2),
                    "account": "CL_INTRADAY",
                    "color_theme": "professional_orange",
                    "indicators": ["PowerScore", "RiskManager", "IntradaySignals"],
                    "alerts_enabled": True
                }
            ]
        }
    
    def load_account_settings(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined account configurations"""
        return {
            "ES_SCALPING": {
                "name": "ES_SCALPING",
                "symbol": "ES",
                "account_size": 15000,
                "risk_percent": 2.0,
                "max_contracts": 2,
                "strategy": "scalping",
                "stop_loss_points": 8,
                "take_profit_points": 12,
                "trading_hours": "09:30-16:00",
                "risk_reward_ratio": 1.5
            },
            "NQ_MOMENTUM": {
                "name": "NQ_MOMENTUM", 
                "symbol": "NQ",
                "account_size": 12000,
                "risk_percent": 2.5,
                "max_contracts": 1,
                "strategy": "momentum",
                "stop_loss_points": 25,
                "take_profit_points": 50,
                "trading_hours": "09:30-16:00",
                "risk_reward_ratio": 2.0
            },
            "YM_SWING": {
                "name": "YM_SWING",
                "symbol": "YM", 
                "account_size": 10000,
                "risk_percent": 3.0,
                "max_contracts": 1,
                "strategy": "swing",
                "stop_loss_points": 150,
                "take_profit_points": 300,
                "trading_hours": "09:30-16:00",
                "risk_reward_ratio": 2.0
            },
            "RTY_BREAKOUT": {
                "name": "RTY_BREAKOUT",
                "symbol": "RTY",
                "account_size": 8000,
                "risk_percent": 2.5,
                "max_contracts": 2,
                "strategy": "breakout",
                "stop_loss_points": 15,
                "take_profit_points": 30,
                "trading_hours": "09:30-16:00", 
                "risk_reward_ratio": 2.0
            },
            "GC_TREND": {
                "name": "GC_TREND",
                "symbol": "GC",
                "account_size": 7000,
                "risk_percent": 2.0,
                "max_contracts": 1,
                "strategy": "trend_following",
                "stop_loss_points": 8,
                "take_profit_points": 16,
                "trading_hours": "08:00-17:00",
                "risk_reward_ratio": 2.0
            },
            "CL_INTRADAY": {
                "name": "CL_INTRADAY",
                "symbol": "CL", 
                "account_size": 8000,
                "risk_percent": 2.5,
                "max_contracts": 1,
                "strategy": "intraday",
                "stop_loss_points": 0.5,
                "take_profit_points": 1.0,
                "trading_hours": "09:00-14:30",
                "risk_reward_ratio": 2.0
            }
        }
    
    def get_chart_config(self, chart_id: str) -> Dict[str, Any]:
        """Get configuration for specific chart"""
        for chart in self.chart_configs["charts"]:
            if chart["id"] == chart_id:
                return chart
        return {}
    
    def get_account_config(self, account_name: str) -> Dict[str, Any]:
        """Get configuration for specific account"""
        return self.account_settings.get(account_name, {})
    
    def update_chart_timeframe(self, chart_id: str, timeframe: str) -> bool:
        """Update timeframe for specific chart"""
        for chart in self.chart_configs["charts"]:
            if chart["id"] == chart_id:
                chart["timeframe"] = timeframe
                return True
        return False
    
    def sync_all_charts(self) -> Dict[str, str]:
        """Synchronize all charts to same timeframe"""
        sync_timeframe = "5min"  # Default sync timeframe
        result = {}
        
        for chart in self.chart_configs["charts"]:
            chart["timeframe"] = sync_timeframe
            result[chart["id"]] = f"Synced to {sync_timeframe}"
            
        return result
    
    def get_layout_positions(self) -> List[tuple]:
        """Get chart positions based on layout"""
        layout_type = self.chart_configs["layout"]["type"]
        
        if layout_type == "3x2":
            return [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
        elif layout_type == "2x3":
            return [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)]
        elif layout_type == "6x1":
            return [(0,0), (0,1), (0,2), (0,3), (0,4), (0,5)]
        elif layout_type == "1x6":
            return [(0,0), (1,0), (2,0), (3,0), (4,0), (5,0)]
        else:
            return [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]  # Default 3x2
    
    def calculate_position_sizes(self) -> Dict[str, Dict[str, Any]]:
        """Calculate position sizes for all accounts"""
        position_sizes = {}
        
        for account_name, account_config in self.account_settings.items():
            account_size = account_config["account_size"]
            risk_percent = account_config["risk_percent"]
            max_contracts = account_config["max_contracts"]
            
            risk_amount = account_size * (risk_percent / 100)
            
            # Symbol-specific calculations
            symbol = account_config["symbol"]
            if symbol in ["ES", "NQ", "YM", "RTY"]:
                # E-mini futures
                point_value = 50 if symbol == "ES" else (20 if symbol == "NQ" else (5 if symbol == "YM" else 50))
                stop_loss_points = account_config["stop_loss_points"]
                risk_per_contract = stop_loss_points * point_value
                
            elif symbol == "GC":
                # Gold futures
                point_value = 100
                stop_loss_points = account_config["stop_loss_points"] 
                risk_per_contract = stop_loss_points * point_value
                
            elif symbol == "CL":
                # Crude oil futures
                point_value = 1000
                stop_loss_points = account_config["stop_loss_points"]
                risk_per_contract = stop_loss_points * point_value
            
            else:
                risk_per_contract = 1000  # Default
            
            calculated_contracts = min(int(risk_amount / risk_per_contract), max_contracts)
            
            position_sizes[account_name] = {
                "calculated_contracts": max(1, calculated_contracts),
                "risk_amount": risk_amount,
                "risk_per_contract": risk_per_contract,
                "max_contracts": max_contracts
            }
        
        return position_sizes
    
    def export_config(self, filepath: str) -> bool:
        """Export configuration to JSON file"""
        try:
            config_data = {
                "chart_configs": self.chart_configs,
                "account_settings": self.account_settings,
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def import_config(self, filepath: str) -> bool:
        """Import configuration from JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    config_data = json.load(f)
                
                self.chart_configs = config_data.get("chart_configs", self.chart_configs)
                self.account_settings = config_data.get("account_settings", self.account_settings)
                
                return True
            return False
        except Exception as e:
            print(f"Import error: {e}")
            return False
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system summary"""
        total_account_size = sum([account["account_size"] for account in self.account_settings.values()])
        
        return {
            "total_charts": len(self.chart_configs["charts"]),
            "total_accounts": len(self.account_settings),
            "total_capital": total_account_size,
            "layout_type": self.chart_configs["layout"]["type"],
            "sync_enabled": self.chart_configs["layout"]["sync_enabled"],
            "symbols": [chart["symbol"] for chart in self.chart_configs["charts"]],
            "accounts": list(self.account_settings.keys()),
            "last_updated": datetime.now().isoformat()
        }

# Global instance
six_chart_manager = SixChartManager()

if __name__ == "__main__":
    # Demo usage
    manager = SixChartManager()
    
    print("🎯 ENIGMA APEX - 6-Chart System Configuration")
    print("=" * 50)
    
    summary = manager.get_system_summary()
    print(f"Total Charts: {summary['total_charts']}")
    print(f"Total Accounts: {summary['total_accounts']}")
    print(f"Total Capital: ${summary['total_capital']:,}")
    print(f"Layout: {summary['layout_type']}")
    print(f"Symbols: {', '.join(summary['symbols'])}")
    
    print("\n📊 Position Sizes:")
    positions = manager.calculate_position_sizes()
    for account, pos_data in positions.items():
        print(f"{account}: {pos_data['calculated_contracts']} contracts (Risk: ${pos_data['risk_amount']:,.0f})")
    
    # Export configuration
    manager.export_config("six_chart_config.json")
    print("\n✅ Configuration exported to six_chart_config.json")
