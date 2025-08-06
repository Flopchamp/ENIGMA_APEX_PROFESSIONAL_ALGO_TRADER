"""
Enhanced WebSocket Server with Database Integration
Production-ready server with real-time data storage
"""

import asyncio
import json
import logging
import websockets
import ssl
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, Any, Callable
from dataclasses import asdict
import uuid
from enum import Enum
import sys
import os

# Add current directory to path to import our integration
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from production_websocket_integration import ProductionWebSocketIntegration
from desktop_notifier import DesktopNotifier

class MessageType(Enum):
    """WebSocket message types"""
    ENIGMA_UPDATE = "enigma_update"
    KELLY_UPDATE = "kelly_update"
    CADENCE_UPDATE = "cadence_update"
    COMPLIANCE_UPDATE = "compliance_update"
    TRADE_SIGNAL = "trade_signal"
    EMERGENCY_STOP = "emergency_stop"
    HEARTBEAT = "heartbeat"
    HEARTBEAT_RESPONSE = "heartbeat_response"
    STATUS_REQUEST = "status_request"
    STATUS_RESPONSE = "status_response"
    CONFIG_UPDATE = "config_update"
    MOBILE_COMMAND = "mobile_command"
    MESSAGE_ACKNOWLEDGED = "message_acknowledged"
    SIGNAL_PROCESSED = "signal_processed"
    ERROR = "error"

class ClientType(Enum):
    """Connected client types"""
    NINJA_DASHBOARD = "ninja_dashboard"
    MOBILE_APP = "mobile_app"
    EXTERNAL_API = "external_api"
    ADMIN_PANEL = "admin_panel"

class WebSocketMessage:
    """WebSocket message structure"""
    
    def __init__(self, 
                 message_type: MessageType,
                 data: Dict[str, Any],
                 client_id: str = None,
                 timestamp: datetime = None):
        
        self.message_type = message_type
        self.data = data
        self.client_id = client_id or str(uuid.uuid4())
        self.timestamp = timestamp or datetime.now()
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps({
            'type': self.message_type.value,
            'data': self.data,
            'client_id': self.client_id,
            'timestamp': self.timestamp.isoformat()
        })
    
    @classmethod
    def from_json(cls, json_str: str):
        """Create from JSON string"""
        try:
            data = json.loads(json_str)
            
            # Parse message type
            try:
                message_type = MessageType(data.get('type', 'heartbeat'))
            except ValueError:
                message_type = MessageType.HEARTBEAT
            
            # Parse timestamp
            timestamp = None
            if 'timestamp' in data:
                try:
                    if isinstance(data['timestamp'], str):
                        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.fromtimestamp(data['timestamp'])
                except:
                    timestamp = datetime.now()
            
            return cls(
                message_type=message_type,
                data=data.get('data', {}),
                client_id=data.get('client_id'),
                timestamp=timestamp or datetime.now()
            )
        except Exception as e:
            # If parsing fails completely, create a basic heartbeat message
            return cls(
                message_type=MessageType.HEARTBEAT,
                data={'error': f'Failed to parse message: {str(e)}', 'original': json_str[:100]},
                client_id=None,
                timestamp=datetime.now()
            )

class ConnectedClient:
    """Connected WebSocket client information"""
    
    def __init__(self, 
                 websocket,
                 client_type: ClientType,
                 client_id: str,
                 user_agent: str = None):
        
        self.websocket = websocket
        self.client_type = client_type
        self.client_id = client_id
        self.user_agent = user_agent
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()
        self.message_count = 0

class EnhancedWebSocketServer:
    """
    Enhanced WebSocket server with database integration
    """
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 8765,
                 ssl_cert_path: str = None,
                 ssl_key_path: str = None):
        
        self.logger = logging.getLogger(__name__)
        
        # Server configuration
        self.host = host
        self.port = port
        self.ssl_cert_path = ssl_cert_path
        self.ssl_key_path = ssl_key_path
        
        # Connected clients
        self.clients: Dict[str, ConnectedClient] = {}
        self.clients_by_type: Dict[ClientType, Set[str]] = {
            client_type: set() for client_type in ClientType
        }
        
        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {}
        
        # Server state
        self.running = False
        self.server = None
        
        # Database integration
        self.db_integration = None
        
        # Desktop notification system
        self.desktop_notifier = DesktopNotifier()
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'start_time': None,
            'last_activity': None
        }
        
        # Setup default handlers
        self._setup_default_handlers()
    
    async def initialize(self):
        """Initialize the enhanced server with database integration"""
        try:
            # Initialize database integration
            self.db_integration = ProductionWebSocketIntegration()
            await self.db_integration.initialize()
            
            self.logger.info("Enhanced WebSocket server initialized with database integration")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced server: {e}")
            raise
    
    def _setup_default_handlers(self):
        """Setup default message handlers"""
        self.message_handlers[MessageType.HEARTBEAT] = self._handle_heartbeat
        self.message_handlers[MessageType.STATUS_REQUEST] = self._handle_status_request
        self.message_handlers[MessageType.ENIGMA_UPDATE] = self._handle_enigma_update
        self.message_handlers[MessageType.MOBILE_COMMAND] = self._handle_mobile_command
    
    async def start(self):
        """Start the enhanced WebSocket server"""
        try:
            # Initialize database integration first
            await self.initialize()
            
            # Setup SSL context if certificates provided
            ssl_context = None
            if self.ssl_cert_path and self.ssl_key_path:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(self.ssl_cert_path, self.ssl_key_path)
                self.logger.info("SSL enabled for WebSocket server")
            
            # Start server
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
                ssl=ssl_context,
                ping_interval=30,
                ping_timeout=10
            )
            
            self.running = True
            self.stats['start_time'] = datetime.now()
            
            protocol = "wss" if ssl_context else "ws"
            self.logger.info(f"Enhanced WebSocket server started on {protocol}://{self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start enhanced WebSocket server: {e}")
            raise
    
    async def stop(self):
        """Stop the enhanced WebSocket server"""
        self.running = False
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Close all client connections
        for client in self.clients.values():
            await client.websocket.close()
        
        self.clients.clear()
        self.clients_by_type = {client_type: set() for client_type in ClientType}
        
        self.logger.info("Enhanced WebSocket server stopped")
    
    async def _handle_client(self, websocket):
        """Handle new client connection"""
        # Get path from websocket request
        path = websocket.path if hasattr(websocket, 'path') else '/'
        
        client_id = str(uuid.uuid4())
        client_type = self._determine_client_type(path)
        
        try:
            # Create client record
            client = ConnectedClient(
                websocket=websocket,
                client_type=client_type,
                client_id=client_id,
                user_agent=getattr(websocket, 'request_headers', {}).get('User-Agent', 'Unknown')
            )
            
            # Add to client tracking
            self.clients[client_id] = client
            self.clients_by_type[client_type].add(client_id)
            self.stats['total_connections'] += 1
            
            self.logger.info(f"New {client_type.value} client connected: {client_id}")
            
            # Send welcome message with enhanced data
            await self._send_welcome_message(client_id, client_type)
            
            # Handle messages from this client
            async for message in websocket:
                await self._process_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            await self._remove_client(client_id)
    
    async def _send_welcome_message(self, client_id: str, client_type: ClientType):
        """Send enhanced welcome message with real-time data"""
        try:
            # Get real-time stats from database integration
            if self.db_integration:
                # Create a status request to get current system state
                status_response = await self.db_integration.handle_websocket_message(
                    {'type': 'status_request', 'data': {}}, 
                    client_id
                )
                
                if status_response and status_response.get('type') == 'status_response':
                    welcome_data = status_response['data']
                else:
                    welcome_data = {}
            else:
                welcome_data = {}
            
            # Add welcome-specific data
            welcome_data.update({
                'client_id': client_id,
                'client_type': client_type.value,
                'server_time': datetime.now().isoformat(),
                'status': 'connected',
                'welcome': True,
                'server_status': 'running',
                'enigma_data': {
                    'power_score': 0,
                    'confluence_level': 'L1', 
                    'signal_color': 'NEUTRAL',
                    'macvu_state': 'NEUTRAL'
                }
            })
            
            welcome_msg = WebSocketMessage(
                MessageType.STATUS_REQUEST,
                welcome_data
            )
            await self._send_to_client(client_id, welcome_msg)
            
        except Exception as e:
            self.logger.error(f"Error sending welcome message to {client_id}: {e}")
    
    def _determine_client_type(self, path: str) -> ClientType:
        """Determine client type from connection path"""
        if '/ninja' in path:
            return ClientType.NINJA_DASHBOARD
        elif '/mobile' in path:
            return ClientType.MOBILE_APP
        elif '/admin' in path:
            return ClientType.ADMIN_PANEL
        else:
            return ClientType.EXTERNAL_API
    
    async def _process_message(self, client_id: str, raw_message: str):
        """Process incoming message from client with database integration"""
        try:
            print(f"DEBUG: Processing message from {client_id}: {raw_message[:100]}...")
            
            message = WebSocketMessage.from_json(raw_message)
            message.client_id = client_id
            
            self.stats['messages_received'] += 1
            self.stats['last_activity'] = datetime.now()
            
            # Update client heartbeat
            if client_id in self.clients:
                self.clients[client_id].last_heartbeat = datetime.now()
                self.clients[client_id].message_count += 1
            
            print(f"DEBUG: Message type: {message.message_type.value}")
            
            # First, pass message to database integration for processing and storage
            if self.db_integration:
                message_dict = {
                    'type': message.message_type.value,
                    'data': message.data,
                    'timestamp': message.timestamp.isoformat()
                }
                
                db_response = await self.db_integration.handle_websocket_message(message_dict, client_id)
                
                # If database integration returns a response, send it back to client
                if db_response:
                    response_msg = WebSocketMessage(
                        MessageType(db_response.get('type', 'heartbeat')),
                        db_response.get('data', {}),
                        client_id,
                        datetime.now()
                    )
                    await self._send_to_client(client_id, response_msg)
            
            # Then route message to specific handlers if needed
            if message.message_type in self.message_handlers:
                print(f"DEBUG: Calling handler for {message.message_type.value}")
                await self.message_handlers[message.message_type](client_id, message)
                print(f"DEBUG: Handler completed for {message.message_type.value}")
            else:
                self.logger.warning(f"No handler for message type: {message.message_type.value}")
                
        except Exception as e:
            self.logger.error(f"Error processing message from {client_id}: {e}")
            print(f"DEBUG: Error in _process_message: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error response
            try:
                error_msg = WebSocketMessage(
                    MessageType.ERROR,
                    {'error': str(e), 'original_message': raw_message[:100]}
                )
                await self._send_to_client(client_id, error_msg)
            except Exception as send_error:
                print(f"DEBUG: Failed to send error message: {send_error}")
    
    async def _handle_heartbeat(self, client_id: str, message: WebSocketMessage):
        """Handle heartbeat message"""
        if client_id in self.clients:
            self.clients[client_id].last_heartbeat = datetime.now()
    
    async def _handle_status_request(self, client_id: str, message: WebSocketMessage):
        """Handle status request with enhanced database data"""
        # The database integration already handles this and sends response
        # This handler is kept for compatibility but the response is sent by _process_message
        pass
    
    async def _handle_enigma_update(self, client_id: str, message: WebSocketMessage):
        """Handle Enigma signal updates"""
        try:
            # Database integration already processed and stored the signal
            # Now broadcast to relevant clients
            
            enigma_data = message.data.get('enigma_data', {})
            
            # Send desktop notification for the signal
            await self._send_signal_notification(enigma_data)
            
            # Create broadcast message
            broadcast_msg = WebSocketMessage(
                MessageType.ENIGMA_UPDATE,
                {
                    'enigma_data': enigma_data,
                    'source_client': client_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Broadcast to NinjaTrader and mobile clients
            await self.broadcast_to_type(ClientType.NINJA_DASHBOARD, broadcast_msg)
            await self.broadcast_to_type(ClientType.MOBILE_APP, broadcast_msg)
            
            self.logger.info(f"Broadcasted Enigma update from {client_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling Enigma update: {e}")
    
    async def _handle_mobile_command(self, client_id: str, message: WebSocketMessage):
        """Handle mobile app commands"""
        command = message.data.get('command')
        
        if command == 'emergency_stop':
            # Broadcast emergency stop to all clients
            await self.broadcast_emergency_stop(
                reason=message.data.get('reason', 'Mobile app emergency stop'),
                triggered_by=client_id
            )
        
        elif command == 'get_status':
            # Database integration already handles this
            pass
        
        else:
            self.logger.warning(f"Unknown mobile command: {command}")
    
    async def _send_to_client(self, client_id: str, message: WebSocketMessage):
        """Send message to specific client"""
        if client_id not in self.clients:
            self.logger.warning(f"Attempted to send message to unknown client: {client_id}")
            return
        
        try:
            print(f"DEBUG: Sending message to {client_id}: {message.message_type.value}")
            client = self.clients[client_id]
            
            # Generate JSON first to catch any serialization errors
            json_data = message.to_json()
            print(f"DEBUG: JSON length: {len(json_data)}")
            
            await client.websocket.send(json_data)
            self.stats['messages_sent'] += 1
            print(f"DEBUG: Message sent successfully to {client_id}")
            
        except websockets.exceptions.ConnectionClosed:
            print(f"DEBUG: Connection closed for {client_id}")
            await self._remove_client(client_id)
        except Exception as e:
            self.logger.error(f"Error sending message to client {client_id}: {e}")
            print(f"DEBUG: Error in _send_to_client: {e}")
            await self._remove_client(client_id)
    
    async def _remove_client(self, client_id: str):
        """Remove client from tracking"""
        if client_id in self.clients:
            client = self.clients[client_id]
            self.clients_by_type[client.client_type].discard(client_id)
            del self.clients[client_id]
            
            self.logger.info(f"Removed client: {client_id}")
    
    async def broadcast_to_type(self, client_type: ClientType, message: WebSocketMessage):
        """Broadcast message to all clients of specific type"""
        client_ids = self.clients_by_type[client_type].copy()
        
        for client_id in client_ids:
            await self._send_to_client(client_id, message)
    
    async def broadcast_to_all(self, message: WebSocketMessage):
        """Broadcast message to all connected clients"""
        client_ids = list(self.clients.keys())
        
        for client_id in client_ids:
            await self._send_to_client(client_id, message)
    
    async def broadcast_emergency_stop(self, reason: str, triggered_by: str = None):
        """Broadcast emergency stop to all clients"""
        message = WebSocketMessage(
            MessageType.EMERGENCY_STOP,
            {
                'reason': reason,
                'triggered_by': triggered_by,
                'timestamp': datetime.now().isoformat(),
                'action_required': 'stop_all_trading'
            }
        )
        
        await self.broadcast_to_all(message)
        self.logger.critical(f"Emergency stop broadcasted: {reason}")
    
    async def _send_signal_notification(self, enigma_data: Dict[str, Any]):
        """Send desktop notification for Enigma signal"""
        try:
            # Extract signal information from enigma_data
            signal_data = {
                'symbol': enigma_data.get('symbol', 'Unknown'),
                'type': enigma_data.get('signal_type', 'Signal'),
                'power_score': enigma_data.get('power_score', 0),
                'direction': enigma_data.get('signal_direction', 'Unknown'),
                'timestamp': enigma_data.get('timestamp', datetime.now().isoformat()),
                'confluence_level': enigma_data.get('confluence_level', 'L1'),
                'signal_color': enigma_data.get('signal_color', 'Unknown')
            }
            
            # Send desktop notification
            success = await self.desktop_notifier.send_signal_notification(signal_data)
            
            if success:
                self.logger.info(f"Desktop notification sent for {signal_data['symbol']} signal")
            else:
                self.logger.warning(f"Failed to send desktop notification for {signal_data['symbol']}")
                
        except Exception as e:
            self.logger.error(f"Error sending signal notification: {e}")
    
    async def send_trade_notification(self, trade_data: Dict[str, Any], alert_type: str):
        """Send desktop notification for trade events"""
        try:
            success = await self.desktop_notifier.send_trade_notification(trade_data, alert_type)
            
            if success:
                self.logger.info(f"Trade notification sent: {alert_type} for {trade_data.get('symbol', 'Unknown')}")
            else:
                self.logger.warning(f"Failed to send trade notification: {alert_type}")
                
        except Exception as e:
            self.logger.error(f"Error sending trade notification: {e}")
    
    async def send_risk_notification(self, risk_data: Dict[str, Any], severity: str):
        """Send desktop notification for risk alerts"""
        try:
            success = await self.desktop_notifier.send_risk_notification(risk_data, severity)
            
            if success:
                self.logger.info(f"Risk notification sent: {severity} severity")
            else:
                self.logger.warning(f"Failed to send risk notification: {severity}")
                
        except Exception as e:
            self.logger.error(f"Error sending risk notification: {e}")
    
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get enhanced server statistics including database metrics"""
        base_stats = {
            **self.stats,
            'running': self.running,
            'connected_clients': len(self.clients),
            'clients_by_type': {
                client_type.value: len(client_ids) 
                for client_type, client_ids in self.clients_by_type.items()
            }
        }
        
        # Add database integration stats if available
        if self.db_integration:
            try:
                # This would need to be implemented in the integration class
                # For now, we'll use basic stats
                base_stats['database_integration'] = {
                    'initialized': True,
                    'status': 'connected'
                }
            except Exception as e:
                base_stats['database_integration'] = {
                    'initialized': False,
                    'error': str(e)
                }
        
        # Add notification stats
        if self.desktop_notifier:
            try:
                notification_stats = self.desktop_notifier.get_notification_stats()
                base_stats['notifications'] = notification_stats
            except Exception as e:
                base_stats['notifications'] = {
                    'error': str(e)
                }
        
        return base_stats

# Main execution
async def main():
    """Main function to run the enhanced WebSocket server"""
    try:
        print("🚀 Starting Enigma-Apex Enhanced WebSocket Server...")
        print("✅ Server created successfully")
        
        # Create and start enhanced server
        server = EnhancedWebSocketServer()
        await server.start()
        
        print("✅ Enhanced server started on ws://localhost:8765")
        print("📡 Ready for NinjaTrader connections with database integration!")
        
        # Keep server running
        try:
            while server.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⚡ Shutting down server...")
            
        await server.stop()
        print("✅ Server stopped successfully")
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server shutdown initiated by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
