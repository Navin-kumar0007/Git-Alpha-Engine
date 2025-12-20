from websocket_manager import WebSocketManager
import time

def test_websocket():
    print("Initializing WebSocket Manager...")
    ws = WebSocketManager()
    
    # NIFTY 50 (Token: 26000), BANK NIFTY (Token: 26009) - NSE Cash (Exchange Type 1)
    tokens_to_subscribe = [{"exchangeType": 1, "tokens": ["26000", "26009"]}]
    
    print("Starting connection and subscribing to NIFTY 50 & BANK NIFTY...")
    ws.start(tokens=tokens_to_subscribe)
    
    # Keep the script running to receive ticks
    try:
        print("Listening for ticks (Press Ctrl+C to stop)...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    test_websocket()
