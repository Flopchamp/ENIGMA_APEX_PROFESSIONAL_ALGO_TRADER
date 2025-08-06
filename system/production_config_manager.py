"""
🔧 PRODUCTION CONFIGURATION MANAGER
Production-ready configuration management for Enigma Apex Trading System
Zero hardcoded values, secure environment variable handling
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradingPlatformConfig:
    """Trading platform connection configuration"""
    # NinjaTrader
    ninjatrader_enabled: bool = True
    ninjatrader_host: str = "localhost"
    ninjatrader_port: int = 8080
    ninjatrader_api_key: str = ""
    
    # Tradovate
    tradovate_enabled: bool = True
    tradovate_api_url: str = "https://demo.tradovateapi.com/v1"
    tradovate_username: str = ""
    tradovate_password: str = ""
    tradovate_account_id: str = ""
    
    # Interactive Brokers
    ib_enabled: bool = True
    ib_host: str = "localhost"
    ib_port: int = 7497
    ib_client_id: int = 1
    ib_account: str = ""
    
    # Binance (Demo/Testnet)
    binance_enabled: bool = True
    binance_api_key: str = ""
    binance_secret_key: str = ""
    binance_testnet: bool = True

@dataclass
class AlgoBarConfig:
    """AlgoBox AlgoBar configuration"""
    tide_target: int = 4  # Macro trend points
    wave_target: int = 2  # Intermediate structure points
    ripple_target: int = 1  # Micro entry points
    
    # Chart settings
    show_volume_profile: bool = True
    show_delta_analysis: bool = True
    show_speed_indicators: bool = True
    auto_timeframe_switching: bool = True

@dataclass
class ApexComplianceConfig:
    """Apex Trader Funding compliance settings"""
    # Account limits
    max_daily_loss: float = 100000.0  # Demo account: $100k
    max_total_loss: float = 100000.0  # Demo account: $100k
    profit_target: float = 100000.0   # Demo account: $100k
    
    # Position management
    max_position_size: float = 50000.0  # Max position value
    max_contracts: int = 10  # Max contracts per trade
    max_daily_trades: int = 50  # Conservative limit
    
    # Risk parameters
    max_leverage: float = 10.0  # 10:1 max leverage
    stop_loss_required: bool = True
    trailing_stop_enabled: bool = True

@dataclass
class NotificationConfig:
    """Notification and alerting configuration"""
    # Windows notifications
    windows_notifications: bool = True
    sound_alerts: bool = True
    
    # Email alerts (if configured)
    email_enabled: bool = False
    email_smtp_server: str = ""
    email_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_recipients: List[str] = None
    
    # Discord webhook (optional)
    discord_webhook_url: str = ""
    
    # Telegram bot (optional)
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

class ProductionConfigManager:
    """Manages all production configuration with environment variables"""
    
    def __init__(self, env_file_path: str = None):
        """Initialize configuration manager
        
        Args:
            env_file_path: Path to .env file (optional)
        """
        self.env_file_path = env_file_path or ".env"
        self.user_settings_path = "user_settings.json"
        self._load_environment()
        self._load_user_settings()
    
    def _load_environment(self):
        """Load environment variables from .env file"""
        env_path = Path(self.env_file_path)
        
        if env_path.exists():
            try:
                # Simple .env parser (production systems should use python-dotenv)
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
                            
                logger.info(f"✅ Loaded environment from {env_path}")
            except Exception as e:
                logger.error(f"❌ Error loading .env file: {e}")
        else:
            logger.warning(f"⚠️  .env file not found at {env_path}")
    
    def _load_user_settings(self):
        """Load user settings from JSON file"""
        settings_path = Path(self.user_settings_path)
        
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    self.user_settings = json.load(f)
                logger.info(f"✅ Loaded user settings from {settings_path}")
            except Exception as e:
                logger.error(f"❌ Error loading user settings: {e}")
                self.user_settings = {}
        else:
            self.user_settings = {}
            logger.info("📝 Using default user settings")
    
    def save_user_settings(self, settings: Dict[str, Any]):
        """Save user settings to JSON file"""
        try:
            self.user_settings.update(settings)
            with open(self.user_settings_path, 'w') as f:
                json.dump(self.user_settings, f, indent=2)
            logger.info(f"✅ Saved user settings to {self.user_settings_path}")
        except Exception as e:
            logger.error(f"❌ Error saving user settings: {e}")
    
    def get_trading_platform_config(self) -> TradingPlatformConfig:
        """Get trading platform configuration from environment"""
        return TradingPlatformConfig(
            # NinjaTrader
            ninjatrader_enabled=os.getenv('NINJATRADER_ENABLED', 'true').lower() == 'true',
            ninjatrader_host=os.getenv('NINJATRADER_HOST', 'localhost'),
            ninjatrader_port=int(os.getenv('NINJATRADER_PORT', '8080')),
            ninjatrader_api_key=os.getenv('NINJATRADER_API_KEY', ''),
            
            # Tradovate
            tradovate_enabled=os.getenv('TRADOVATE_ENABLED', 'true').lower() == 'true',
            tradovate_api_url=os.getenv('TRADOVATE_API_URL', 'https://demo.tradovateapi.com/v1'),
            tradovate_username=os.getenv('TRADOVATE_USERNAME', ''),
            tradovate_password=os.getenv('TRADOVATE_PASSWORD', ''),
            tradovate_account_id=os.getenv('TRADOVATE_ACCOUNT_ID', ''),
            
            # Interactive Brokers
            ib_enabled=os.getenv('IB_ENABLED', 'true').lower() == 'true',
            ib_host=os.getenv('IB_HOST', 'localhost'),
            ib_port=int(os.getenv('IB_PORT', '7497')),
            ib_client_id=int(os.getenv('IB_CLIENT_ID', '1')),
            ib_account=os.getenv('IB_ACCOUNT', ''),
            
            # Binance
            binance_enabled=os.getenv('BINANCE_ENABLED', 'true').lower() == 'true',
            binance_api_key=os.getenv('BINANCE_API_KEY', ''),
            binance_secret_key=os.getenv('BINANCE_SECRET_KEY', ''),
            binance_testnet=os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
        )
    
    def get_algobar_config(self) -> AlgoBarConfig:
        """Get AlgoBar configuration from user settings"""
        defaults = asdict(AlgoBarConfig())
        user_algobar = self.user_settings.get('algobar', {})
        
        return AlgoBarConfig(
            tide_target=user_algobar.get('tide_target', defaults['tide_target']),
            wave_target=user_algobar.get('wave_target', defaults['wave_target']),
            ripple_target=user_algobar.get('ripple_target', defaults['ripple_target']),
            show_volume_profile=user_algobar.get('show_volume_profile', defaults['show_volume_profile']),
            show_delta_analysis=user_algobar.get('show_delta_analysis', defaults['show_delta_analysis']),
            show_speed_indicators=user_algobar.get('show_speed_indicators', defaults['show_speed_indicators']),
            auto_timeframe_switching=user_algobar.get('auto_timeframe_switching', defaults['auto_timeframe_switching'])
        )
    
    def get_compliance_config(self) -> ApexComplianceConfig:
        """Get compliance configuration from user settings"""
        defaults = asdict(ApexComplianceConfig())
        user_compliance = self.user_settings.get('compliance', {})
        
        return ApexComplianceConfig(
            max_daily_loss=user_compliance.get('max_daily_loss', defaults['max_daily_loss']),
            max_total_loss=user_compliance.get('max_total_loss', defaults['max_total_loss']),
            profit_target=user_compliance.get('profit_target', defaults['profit_target']),
            max_position_size=user_compliance.get('max_position_size', defaults['max_position_size']),
            max_contracts=user_compliance.get('max_contracts', defaults['max_contracts']),
            max_daily_trades=user_compliance.get('max_daily_trades', defaults['max_daily_trades']),
            max_leverage=user_compliance.get('max_leverage', defaults['max_leverage']),
            stop_loss_required=user_compliance.get('stop_loss_required', defaults['stop_loss_required']),
            trailing_stop_enabled=user_compliance.get('trailing_stop_enabled', defaults['trailing_stop_enabled'])
        )
    
    def get_notification_config(self) -> NotificationConfig:
        """Get notification configuration from user settings"""
        defaults = asdict(NotificationConfig())
        user_notifications = self.user_settings.get('notifications', {})
        
        return NotificationConfig(
            windows_notifications=user_notifications.get('windows_notifications', defaults['windows_notifications']),
            sound_alerts=user_notifications.get('sound_alerts', defaults['sound_alerts']),
            email_enabled=user_notifications.get('email_enabled', defaults['email_enabled']),
            email_smtp_server=user_notifications.get('email_smtp_server', defaults['email_smtp_server']),
            email_port=user_notifications.get('email_port', defaults['email_port']),
            email_username=user_notifications.get('email_username', defaults['email_username']),
            email_password=user_notifications.get('email_password', defaults['email_password']),
            email_recipients=user_notifications.get('email_recipients', defaults['email_recipients'] or []),
            discord_webhook_url=user_notifications.get('discord_webhook_url', defaults['discord_webhook_url']),
            telegram_bot_token=user_notifications.get('telegram_bot_token', defaults['telegram_bot_token']),
            telegram_chat_id=user_notifications.get('telegram_chat_id', defaults['telegram_chat_id'])
        )

def load_production_config(env_file: str = None) -> ProductionConfigManager:
    """Load production configuration
    
    Args:
        env_file: Path to .env file (optional)
        
    Returns:
        ProductionConfigManager instance
    """
    return ProductionConfigManager(env_file)

def get_all_configs(config_manager: ProductionConfigManager = None) -> Dict[str, Any]:
    """Get all configuration objects
    
    Args:
        config_manager: Optional config manager instance
        
    Returns:
        Dictionary with all config objects
    """
    if config_manager is None:
        config_manager = load_production_config()
    
    return {
        'trading_platforms': config_manager.get_trading_platform_config(),
        'algobar': config_manager.get_algobar_config(),
        'compliance': config_manager.get_compliance_config(),
        'notifications': config_manager.get_notification_config()
    }

def create_production_environment():
    """Create production environment setup
    
    Returns:
        Success status and message
    """
    try:
        # Check for .env file
        env_path = Path(".env")
        if not env_path.exists():
            logger.warning("⚠️  .env file not found. Please run SETUP_DEMO.bat first.")
            return False, ".env file not found"
        
        # Load configuration
        config_manager = load_production_config()
        configs = get_all_configs(config_manager)
        
        # Validate essential configurations
        trading_config = configs['trading_platforms']
        
        # Check if at least one platform is enabled and configured
        platforms_ready = []
        
        if trading_config.ninjatrader_enabled and trading_config.ninjatrader_host:
            platforms_ready.append("NinjaTrader")
        
        if trading_config.tradovate_enabled and trading_config.tradovate_username:
            platforms_ready.append("Tradovate")
        
        if trading_config.ib_enabled and trading_config.ib_host:
            platforms_ready.append("Interactive Brokers")
        
        if trading_config.binance_enabled and trading_config.binance_api_key:
            platforms_ready.append("Binance")
        
        if not platforms_ready:
            logger.warning("⚠️  No trading platforms properly configured")
            return False, "No trading platforms configured"
        
        logger.info(f"✅ Production environment ready with platforms: {', '.join(platforms_ready)}")
        return True, f"Ready with {len(platforms_ready)} platforms"
        
    except Exception as e:
        logger.error(f"❌ Error creating production environment: {e}")
        return False, str(e)

if __name__ == "__main__":
    # Test configuration loading
    print("🔧 Testing Production Configuration Manager...")
    
    success, message = create_production_environment()
    print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'} - {message}")
    
    if success:
        config_manager = load_production_config()
        configs = get_all_configs(config_manager)
        
        print("\n📊 Configuration Summary:")
        print(f"  • Trading Platforms: {len([p for p in ['ninjatrader', 'tradovate', 'ib', 'binance'] if getattr(configs['trading_platforms'], f'{p}_enabled')])}")
        print(f"  • AlgoBar Tide Target: {configs['algobar'].tide_target} points")
        print(f"  • Max Daily Loss: ${configs['compliance'].max_daily_loss:,.2f}")
        print(f"  • Windows Notifications: {'✅' if configs['notifications'].windows_notifications else '❌'}")
        
        print("\n🚀 Production configuration ready!")
