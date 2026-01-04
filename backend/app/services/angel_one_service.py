"""
Angel One Service - Centralized service for managing live market data
"""

import asyncio
from datetime import datetime
from typing import Dict, List
from websocket_manager import WebSocketManager

class AngelOneService:
    """Singleton service to manage Angel One WebSocket connection and data broadcasting"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.ws_manager = WebSocketManager()
            self.is_running = False
            self.last_ticks: Dict[str, dict] = {}  # Cache latest tick for each token
            self.frontend_broadcast_callback = None
            self.initialized = True
    
    def set_broadcast_callback(self, callback):
        """Set the callback function to broadcast data to frontend WebSocket clients"""
        self.frontend_broadcast_callback = callback
    
    def start(self, tokens=None):
        """Start the Angel One WebSocket connection"""
        if self.is_running:
            print("Angel One service already running")
            return
        
        # Register our data handler as a callback
        self.ws_manager.add_callback(self._handle_tick_data)
        
        # Start WebSocket connection
        self.ws_manager.start(tokens=tokens)
        self.is_running = True
        print("Angel One service started")
    
    def stop(self):
        """Stop the Angel One WebSocket connection"""
        self.ws_manager.stop()
        self.is_running = False
        print("Angel One service stopped")
    
    def subscribe(self, tokens, mode=1):
        """Subscribe to additional tokens"""
        self.ws_manager.subscribe(tokens, mode)
    
    def unsubscribe(self, tokens, mode=1):
        """Unsubscribe from tokens"""
        self.ws_manager.unsubscribe(tokens, mode)
    
    def get_status(self):
        """Get current status of the service"""
        return {
            "is_running": self.is_running,
            "is_connected": self.ws_manager.is_connected,
            "subscribed_tokens": self.ws_manager.subscribed_tokens,
            "last_update": datetime.now().isoformat()
        }
    
    def get_last_tick(self, token: str):
        """Get the last received tick for a specific token"""
        return self.last_ticks.get(token)
    
    def _handle_tick_data(self, tick_data: dict):
        """
        Internal handler for tick data
        - Caches latest tick
        - Broadcasts to frontend
        - Triggers alerts (future)
        """
        token = tick_data.get('token')
        
        # Cache the latest tick
        if token:
            self.last_ticks[token] = tick_data
        
        # Broadcast to frontend WebSocket clients
        if self.frontend_broadcast_callback:
            try:
                # Create message format for frontend
                message = {
                    "type": "MARKET_DATA",
                    "data": tick_data,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Call the async broadcast function
                # Note: This runs in a WebSocket thread context, not FastAPI's event loop
                # We'll need to handle this differently - for now, skip broadcasting
                # TODO: Implement proper async WebSocket broadcasting
                # asyncio.create_task(self.frontend_broadcast_callback(message))
            except Exception as e:
                # Silently ignore broadcast errors - not critical
                pass

# Global instance
angel_one_service = AngelOneService()
