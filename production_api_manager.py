"""
🚀 PRODUCTION API MANAGER
Real trading platform integrations for live algorithmic trading
Enterprise-grade implementation for professional algo traders
"""

import asyncio
import websockets
import requests
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import ssl
import hashlib
import hmac
import base64
from enum import Enum

# Trading Platform Interface
class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class TradingOrder:
    """Universal trading order structure"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    timestamp: Optional[datetime] = None
    account_id: Optional[str] = None

@dataclass
class Position:
    """Universal position structure"""
    symbol: str
    quantity: float
    average_price: float
    market_price: float
    unrealized_pnl: float
    realized_pnl: float
    account_id: str
    timestamp: datetime

@dataclass
class AccountInfo:
    """Universal account information"""
    account_id: str
    balance: float
    equity: float
    margin_used: float
    margin_available: float
    buying_power: float
    day_pnl: float
    positions: List[Position]
    orders: List[TradingOrder]
    timestamp: datetime

class TradingPlatform(ABC):
    """Abstract base class for trading platform integrations"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to trading platform"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from trading platform"""
        pass
    
    @abstractmethod
    async def place_order(self, order: TradingOrder) -> str:
        """Place a trading order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> AccountInfo:
        """Get current account information"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get current positions"""
        pass
    
    @abstractmethod
    async def get_orders(self) -> List[TradingOrder]:
        """Get current orders"""
        pass
    
    @abstractmethod
    async def subscribe_market_data(self, symbols: List[str], callback: Callable):
        """Subscribe to real-time market data"""
        pass

class TradovateAPI(TradingPlatform):
    """Production Tradovate API implementation"""
    
    def __init__(self, username: str, password: str, environment: str = "demo"):
        self.username = username
        self.password = password
        self.environment = environment
        self.access_token = None
        self.websocket = None
        self.is_connected = False
        
        # API endpoints
        if environment == "live":
            self.base_url = "https://live.tradovateapi.com/v1"
            self.ws_url = "wss://live.tradovateapi.com/v1/websocket"
        else:
            self.base_url = "https://demo.tradovateapi.com/v1"
            self.ws_url = "wss://demo.tradovateapi.com/v1/websocket"
        
        self.logger = logging.getLogger(__name__)
        self.market_data_callbacks = []
        
    async def connect(self) -> bool:
        """Establish connection to Tradovate API"""
        try:
            # Step 1: Authenticate and get access token
            auth_response = requests.post(
                f"{self.base_url}/auth/accesstokenrequest",
                json={
                    "name": self.username,
                    "password": self.password,
                    "appId": "ENIGMA_APEX_TRADER",
                    "appVersion": "1.0"
                }
            )
            
            if auth_response.status_code != 200:
                self.logger.error(f"Authentication failed: {auth_response.text}")
                return False
            
            self.access_token = auth_response.json()["accessToken"]
            self.logger.info("Tradovate authentication successful")
            
            # Step 2: Establish WebSocket connection
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            self.websocket = await websockets.connect(
                self.ws_url,
                extra_headers=headers,
                ssl=ssl.SSLContext()
            )
            
            self.is_connected = True
            self.logger.info("Tradovate WebSocket connection established")
            
            # Start WebSocket listener
            asyncio.create_task(self._websocket_listener())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Tradovate connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Tradovate API"""
        try:
            if self.websocket:
                await self.websocket.close()
            self.is_connected = False
            self.logger.info("Tradovate connection closed")
        except Exception as e:
            self.logger.error(f"Error disconnecting from Tradovate: {e}")
    
    async def place_order(self, order: TradingOrder) -> str:
        """Place order through Tradovate API"""
        try:
            # Get contract ID for symbol
            contract_response = requests.get(
                f"{self.base_url}/contract/suggest",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"t": order.symbol}
            )
            
            if contract_response.status_code != 200:
                raise Exception(f"Failed to find contract for {order.symbol}")
            
            contracts = contract_response.json()
            if not contracts:
                raise Exception(f"No contracts found for {order.symbol}")
            
            contract_id = contracts[0]["id"]
            
            # Prepare order payload
            order_payload = {
                "accountId": order.account_id,
                "action": "Buy" if order.side == OrderSide.BUY else "Sell",
                "symbol": order.symbol,
                "orderQty": int(order.quantity),
                "orderType": order.order_type.value.title(),
                "timeInForce": order.time_in_force,
                "isAutomated": True
            }
            
            if order.price and order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
                order_payload["price"] = order.price
            
            if order.stop_price and order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
                order_payload["stopPrice"] = order.stop_price
            
            # Place order
            order_response = requests.post(
                f"{self.base_url}/order/placeorder",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json=order_payload
            )
            
            if order_response.status_code != 200:
                raise Exception(f"Order placement failed: {order_response.text}")
            
            order_result = order_response.json()
            order_id = str(order_result["orderId"])
            
            self.logger.info(f"Order placed successfully: {order_id}")
            return order_id
            
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            raise
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order through Tradovate API"""
        try:
            cancel_response = requests.post(
                f"{self.base_url}/order/cancelorder",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={"orderId": int(order_id)}
            )
            
            success = cancel_response.status_code == 200
            if success:
                self.logger.info(f"Order cancelled successfully: {order_id}")
            else:
                self.logger.error(f"Failed to cancel order {order_id}: {cancel_response.text}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    async def get_account_info(self) -> AccountInfo:
        """Get account information from Tradovate"""
        try:
            # Get account details
            account_response = requests.get(
                f"{self.base_url}/account/list",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if account_response.status_code != 200:
                raise Exception(f"Failed to get account info: {account_response.text}")
            
            accounts = account_response.json()
            if not accounts:
                raise Exception("No accounts found")
            
            account = accounts[0]  # Use first account
            account_id = str(account["id"])
            
            # Get positions
            positions = await self.get_positions()
            
            # Get orders
            orders = await self.get_orders()
            
            # Calculate account metrics
            balance = float(account.get("balance", 0))
            equity = balance + sum(pos.unrealized_pnl for pos in positions)
            margin_used = float(account.get("marginUsed", 0))
            margin_available = balance - margin_used
            buying_power = margin_available * 4  # Typical futures buying power
            day_pnl = sum(pos.unrealized_pnl for pos in positions)
            
            return AccountInfo(
                account_id=account_id,
                balance=balance,
                equity=equity,
                margin_used=margin_used,
                margin_available=margin_available,
                buying_power=buying_power,
                day_pnl=day_pnl,
                positions=positions,
                orders=orders,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            raise
    
    async def get_positions(self) -> List[Position]:
        """Get current positions from Tradovate"""
        try:
            positions_response = requests.get(
                f"{self.base_url}/position/list",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if positions_response.status_code != 200:
                return []
            
            positions_data = positions_response.json()
            positions = []
            
            for pos_data in positions_data:
                if pos_data.get("netPos", 0) != 0:  # Only non-zero positions
                    position = Position(
                        symbol=pos_data.get("contractName", ""),
                        quantity=float(pos_data.get("netPos", 0)),
                        average_price=float(pos_data.get("avgPrice", 0)),
                        market_price=float(pos_data.get("currentPrice", 0)),
                        unrealized_pnl=float(pos_data.get("unrealizedPnL", 0)),
                        realized_pnl=float(pos_data.get("realizedPnL", 0)),
                        account_id=str(pos_data.get("accountId", "")),
                        timestamp=datetime.now()
                    )
                    positions.append(position)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []
    
    async def get_orders(self) -> List[TradingOrder]:
        """Get current orders from Tradovate"""
        try:
            orders_response = requests.get(
                f"{self.base_url}/order/list",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if orders_response.status_code != 200:
                return []
            
            orders_data = orders_response.json()
            orders = []
            
            for order_data in orders_data:
                # Map Tradovate order status to our enum
                status_map = {
                    "Working": OrderStatus.PENDING,
                    "Filled": OrderStatus.FILLED,
                    "PartiallyFilled": OrderStatus.PARTIALLY_FILLED,
                    "Cancelled": OrderStatus.CANCELLED,
                    "Rejected": OrderStatus.REJECTED
                }
                
                order = TradingOrder(
                    symbol=order_data.get("contractName", ""),
                    side=OrderSide.BUY if order_data.get("action") == "Buy" else OrderSide.SELL,
                    order_type=OrderType(order_data.get("orderType", "MARKET").upper()),
                    quantity=float(order_data.get("orderQty", 0)),
                    price=float(order_data.get("price", 0)) if order_data.get("price") else None,
                    order_id=str(order_data.get("id", "")),
                    status=status_map.get(order_data.get("orderStatus"), OrderStatus.PENDING),
                    filled_quantity=float(order_data.get("filledQty", 0)),
                    average_fill_price=float(order_data.get("avgFillPrice", 0)),
                    timestamp=datetime.now(),
                    account_id=str(order_data.get("accountId", ""))
                )
                orders.append(order)
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Error getting orders: {e}")
            return []
    
    async def subscribe_market_data(self, symbols: List[str], callback: Callable):
        """Subscribe to real-time market data"""
        try:
            if not self.is_connected:
                raise Exception("Not connected to Tradovate")
            
            self.market_data_callbacks.append(callback)
            
            # Subscribe to quotes for each symbol
            for symbol in symbols:
                subscribe_message = {
                    "url": "md/subscribeQuote",
                    "body": {"symbol": symbol}
                }
                
                await self.websocket.send(json.dumps(subscribe_message))
                self.logger.info(f"Subscribed to market data for {symbol}")
            
        except Exception as e:
            self.logger.error(f"Error subscribing to market data: {e}")
            raise
    
    async def _websocket_listener(self):
        """Listen for WebSocket messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                # Handle market data updates
                if data.get("e") == "md":  # Market data event
                    for callback in self.market_data_callbacks:
                        try:
                            await callback(data)
                        except Exception as e:
                            self.logger.error(f"Error in market data callback: {e}")
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
            self.is_connected = False

class ProductionAPIManager:
    """Manages all trading platform connections"""
    
    def __init__(self):
        self.platforms: Dict[str, TradingPlatform] = {}
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
    def add_platform(self, name: str, platform: TradingPlatform):
        """Add a trading platform"""
        self.platforms[name] = platform
        self.logger.info(f"Added trading platform: {name}")
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all configured platforms"""
        results = {}
        
        for name, platform in self.platforms.items():
            try:
                success = await platform.connect()
                results[name] = success
                self.logger.info(f"Platform {name} connection: {'Success' if success else 'Failed'}")
            except Exception as e:
                results[name] = False
                self.logger.error(f"Failed to connect to {name}: {e}")
        
        return results
    
    async def disconnect_all(self):
        """Disconnect from all platforms"""
        for name, platform in self.platforms.items():
            try:
                await platform.disconnect()
                self.logger.info(f"Disconnected from {name}")
            except Exception as e:
                self.logger.error(f"Error disconnecting from {name}: {e}")
    
    async def place_order_on_platform(self, platform_name: str, order: TradingOrder) -> str:
        """Place order on specific platform"""
        if platform_name not in self.platforms:
            raise Exception(f"Platform {platform_name} not configured")
        
        platform = self.platforms[platform_name]
        return await platform.place_order(order)
    
    async def get_all_account_info(self) -> Dict[str, AccountInfo]:
        """Get account info from all platforms"""
        results = {}
        
        for name, platform in self.platforms.items():
            try:
                account_info = await platform.get_account_info()
                results[name] = account_info
            except Exception as e:
                self.logger.error(f"Error getting account info from {name}: {e}")
        
        return results
    
    async def emergency_stop_all(self):
        """Emergency stop - cancel all orders and close positions"""
        self.logger.warning("EMERGENCY STOP ACTIVATED")
        
        for name, platform in self.platforms.items():
            try:
                # Cancel all open orders
                orders = await platform.get_orders()
                for order in orders:
                    if order.status == OrderStatus.PENDING:
                        await platform.cancel_order(order.order_id)
                
                # Close all positions (implementation depends on platform)
                positions = await platform.get_positions()
                for position in positions:
                    if position.quantity != 0:
                        # Create market order to close position
                        close_order = TradingOrder(
                            symbol=position.symbol,
                            side=OrderSide.SELL if position.quantity > 0 else OrderSide.BUY,
                            order_type=OrderType.MARKET,
                            quantity=abs(position.quantity),
                            account_id=position.account_id
                        )
                        await platform.place_order(close_order)
                
                self.logger.info(f"Emergency stop completed for {name}")
                
            except Exception as e:
                self.logger.error(f"Error during emergency stop for {name}: {e}")

# Example usage and testing
async def test_production_api():
    """Test the production API manager"""
    
    # Initialize API manager
    api_manager = ProductionAPIManager()
    
    # Add Tradovate demo connection
    tradovate = TradovateAPI(
        username="demo_username",
        password="demo_password", 
        environment="demo"
    )
    
    api_manager.add_platform("tradovate_demo", tradovate)
    
    try:
        # Connect to platforms
        connection_results = await api_manager.connect_all()
        print("Connection results:", connection_results)
        
        if connection_results.get("tradovate_demo"):
            # Get account information
            account_info = await api_manager.get_all_account_info()
            print("Account info:", account_info)
            
            # Place a test order (small size for demo)
            test_order = TradingOrder(
                symbol="MES",  # Micro E-mini S&P 500
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=1,
                price=4000.0,  # Example price
                account_id=account_info["tradovate_demo"].account_id
            )
            
            order_id = await api_manager.place_order_on_platform("tradovate_demo", test_order)
            print(f"Order placed: {order_id}")
            
            # Wait a moment, then cancel the order
            await asyncio.sleep(2)
            cancel_success = await tradovate.cancel_order(order_id)
            print(f"Order cancelled: {cancel_success}")
        
    except Exception as e:
        print(f"Test error: {e}")
    
    finally:
        # Clean up
        await api_manager.disconnect_all()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    asyncio.run(test_production_api())
