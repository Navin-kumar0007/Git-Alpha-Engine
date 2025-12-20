from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from smart_auth import SmartAuth
import threading
import time
from datetime import datetime

class WebSocketManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.auth = SmartAuth()
            self.sws = None
            self.is_connected = False
            self.subscribed_tokens = []
            self.data_callbacks = []  # List of callback functions
            self.initialized = True
    
    def add_callback(self, callback):
        """Add a callback function to receive tick data"""
        if callback not in self.data_callbacks:
            self.data_callbacks.append(callback)
    
    def remove_callback(self, callback):
        """Remove a callback function"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
            
    def start(self, tokens=None):
        """
        Start the WebSocket connection.
        tokens: List of tokens to subscribe to. 
                Example: [{"exchangeType": 1, "tokens": ["26000", "26009"]}] (Nifty & BankNifty)
        """
        if self.is_connected:
            print("WebSocket already connected")
            return
            
        login_data = self.auth.login()
        if not login_data['status']:
            print(f"WS Login Failed: {login_data['message']}")
            return

        auth_token = login_data['auth_token']
        feed_token = login_data['feed_token']
        api_key = self.auth.api_key
        client_id = self.auth.client_id

        self.sws = SmartWebSocketV2(auth_token, api_key, client_id, feed_token)

        def on_data(wsapp, message):
            # Process and normalize tick data
            tick_data = self._normalize_tick(message)
            
            # Call all registered callbacks
            for callback in self.data_callbacks:
                try:
                    callback(tick_data)
                except Exception as e:
                    print(f"Callback error: {e}")

        def on_open(wsapp):
            print("WebSocket Connected")
            self.is_connected = True
            if tokens:
                self.subscribe(tokens)

        def on_error(wsapp, error):
            print(f"WebSocket Error: {error}")
            self.is_connected = False
            
        def on_close(wsapp):
            print("WebSocket Closed")
            self.is_connected = False

        self.sws.on_open = on_open
        self.sws.on_data = on_data
        self.sws.on_error = on_error
        self.sws.on_close = on_close

        # Run in a separate thread to not block main thread
        ws_thread = threading.Thread(target=self.sws.connect)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Wait a bit for connection
        time.sleep(2)

    def subscribe(self, tokens, mode=1):
        """Subscribe to tokens. Mode 1=LTP, Mode 3=Full Quote"""
        if self.sws and self.is_connected:
            self.sws.subscribe("correlation_id", mode, tokens)
            self.subscribed_tokens.extend(tokens)
            print(f"Subscribed to: {tokens}")
        else:
            print("WebSocket not connected. Cannot subscribe.")
    
    def unsubscribe(self, tokens, mode=1):
        """Unsubscribe from tokens"""
        if self.sws and self.is_connected:
            self.sws.unsubscribe("correlation_id", mode, tokens)
            # Remove from subscribed list
            for token_group in tokens:
                if token_group in self.subscribed_tokens:
                    self.subscribed_tokens.remove(token_group)
            print(f"Unsubscribed from: {tokens}")
        else:
            print("WebSocket not connected. Cannot unsubscribe.")
    
    def stop(self):
        """Stop the WebSocket connection"""
        if self.sws:
            self.is_connected = False
            self.sws.close()
            print("WebSocket stopped")
    
    def _normalize_tick(self, raw_tick):
        """Normalize tick data (convert paise to rupees, format timestamps)"""
        normalized = raw_tick.copy()
        
        # Convert price from paise to rupees
        if 'last_traded_price' in normalized:
            normalized['last_traded_price_rupees'] = normalized['last_traded_price'] / 100
        
        # Add timestamp
        normalized['received_at'] = datetime.now().isoformat()
        
        return normalized
