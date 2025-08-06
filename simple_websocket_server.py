#!/usr/bin/env python3
"""
🌐 SIMPLE WEBSOCKET SERVER FOR APEX COMPLIANCE GUARDIAN
Basic WebSocket server for real-time communication with NinjaTrader and other clients
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set
import signal
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleWebSocketServer:
    """Simple WebSocket server for Apex Compliance Guardian"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients: Set = set()
        self.server = None
        
    async def register_client(self, websocket, path):
        """Register a new client"""
        self.clients.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"📱 Client connected: {client_info} (Total: {len(self.clients)})")
        
        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "message": "Connected to Apex Compliance Guardian WebSocket Server",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "host": self.host,
                "port": self.port,
                "version": "1.0.0"
            }
        }
        
        try:
            await websocket.send(json.dumps(welcome_message))
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
        
    async def unregister_client(self, websocket):
        """Unregister a client"""
        if websocket in self.clients:
            self.clients.remove(websocket)
            logger.info(f"📱 Client disconnected (Total: {len(self.clients)})")
    
    async def handle_message(self, websocket, path):
        """Handle WebSocket messages"""
        await self.register_client(websocket, path)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(websocket, data)
                except json.JSONDecodeError:
                    error_response = {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(error_response))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def process_message(self, websocket, data):
        """Process incoming messages"""
        message_type = data.get('type', 'unknown')
        timestamp = datetime.now().isoformat()
        
        logger.info(f"📨 Received {message_type} from {websocket.remote_address}")
        
        # Handle different message types
        if message_type == 'ping':
            response = {
                "type": "pong",
                "timestamp": timestamp,
                "original_message": data
            }
            await websocket.send(json.dumps(response))
            
        elif message_type == 'enigma_signal':
            # Handle Enigma signal from OCR or manual input
            await self.broadcast_message({
                "type": "enigma_signal_received",
                "signal_data": data.get('signal', {}),
                "timestamp": timestamp,
                "source": "enigma_reader"
            })
            
        elif message_type == 'compliance_alert':
            # Handle compliance alerts
            await self.broadcast_message({
                "type": "compliance_alert",
                "alert_data": data.get('alert', {}),
                "timestamp": timestamp,
                "source": "compliance_guardian"
            })
            
        elif message_type == 'trade_update':
            # Handle trade updates from NinjaTrader
            await self.broadcast_message({
                "type": "trade_update_received",
                "trade_data": data.get('trade', {}),
                "timestamp": timestamp,
                "source": "ninjatrader"
            })
            
        elif message_type == 'emergency_stop':
            # Handle emergency stop signals
            await self.broadcast_message({
                "type": "emergency_stop_activated",
                "reason": data.get('reason', 'Manual trigger'),
                "timestamp": timestamp,
                "source": "emergency_system"
            })
            
        elif message_type == 'status_request':
            # Provide server status
            status_response = {
                "type": "status_response",
                "server_status": "running",
                "connected_clients": len(self.clients),
                "uptime": timestamp,
                "timestamp": timestamp
            }
            await websocket.send(json.dumps(status_response))
            
        else:
            # Echo unknown messages
            echo_response = {
                "type": "echo",
                "original_message": data,
                "timestamp": timestamp,
                "note": f"Unknown message type: {message_type}"
            }
            await websocket.send(json.dumps(echo_response))
    
    async def broadcast_message(self, message):
        """Broadcast message to all connected clients"""
        if not self.clients:
            logger.info("📢 No clients to broadcast to")
            return
            
        logger.info(f"📢 Broadcasting {message.get('type')} to {len(self.clients)} clients")
        
        # Send to all clients
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.unregister_client(client)
    
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            # Try to import websockets
            import websockets
        except ImportError:
            logger.error("❌ websockets library not installed. Run: pip install websockets")
            return False
        
        logger.info(f"🚀 Starting WebSocket server on {self.host}:{self.port}")
        
        try:
            self.server = await websockets.serve(
                self.handle_message,
                self.host,
                self.port
            )
            
            logger.info(f"✅ WebSocket server running on ws://{self.host}:{self.port}")
            logger.info("🔗 Ready for connections from:")
            logger.info("   - NinjaTrader strategies")
            logger.info("   - Apex Compliance Guardian")
            logger.info("   - Mobile applications")
            logger.info("   - OCR Enigma Reader")
            
            # Send periodic heartbeat
            asyncio.create_task(self.heartbeat_loop())
            
            return True
            
        except OSError as e:
            if e.errno == 10048:  # Port already in use
                logger.error(f"❌ Port {self.port} already in use")
                logger.info(f"💡 Try a different port: python {sys.argv[0]} --port 8766")
            else:
                logger.error(f"❌ Failed to start server: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error starting server: {e}")
            return False
    
    async def heartbeat_loop(self):
        """Send periodic heartbeat to all clients"""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                if self.clients:
                    heartbeat_message = {
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat(),
                        "connected_clients": len(self.clients),
                        "server_status": "running"
                    }
                    
                    await self.broadcast_message(heartbeat_message)
                    
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        if self.server:
            logger.info("🛑 Stopping WebSocket server...")
            self.server.close()
            await self.server.wait_closed()
            logger.info("✅ WebSocket server stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"📡 Received signal {signum}, shutting down...")
    sys.exit(0)

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Apex Compliance Guardian WebSocket Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8765, help='Port to bind to')
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start server
    server = SimpleWebSocketServer(args.host, args.port)
    
    if await server.start_server():
        try:
            # Keep server running
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("📡 Received shutdown signal")
        finally:
            await server.stop_server()
    else:
        logger.error("❌ Failed to start WebSocket server")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 WebSocket server shutdown complete")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
