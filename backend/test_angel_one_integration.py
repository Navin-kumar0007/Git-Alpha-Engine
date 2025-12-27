"""
Angel One API Integration Diagnostic Script
This script helps diagnose issues with Angel One API integration
"""

import os
import sys
from dotenv import load_dotenv

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    print("=" * 60)
    print("STEP 1: Checking Environment Variables")
    print("=" * 60)
    
    required_vars = {
        'ANGEL_API_KEY': 'Angel One API Key',
        'ANGEL_CLIENT_ID': 'Angel One Client ID',
        'ANGEL_PASSWORD': 'Angel One Password',
        'ANGEL_TOTP_KEY': 'Angel One TOTP Secret Key'
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask the value for security
            masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
            print(f"[OK] {var}: {masked_value}")
        else:
            print(f"[MISSING] {var}")
            missing.append(var)
    
    if missing:
        print("\n[ERROR] Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease add these to your .env file")
        return False
    else:
        print("\n[OK] All environment variables are set!")
        return True

def test_authentication():
    """Test Angel One authentication"""
    print("\n" + "=" * 60)
    print("STEP 2: Testing Angel One Authentication")
    print("=" * 60)
    
    try:
        from smart_auth import SmartAuth
        
        print("Attempting to login to Angel One...")
        auth = SmartAuth()
        result = auth.login()
        
        if result['status']:
            print(f"[OK] Login Successful!")
            print(f"  Auth Token: {result['auth_token'][:20]}...")
            print(f"  Feed Token: {result['feed_token']}")
            return True, result
        else:
            print(f"[ERROR] Login Failed: {result['message']}")
            return False, result
            
    except Exception as e:
        print(f"[ERROR] Exception during authentication: {str(e)}")
        return False, None

def test_websocket_connection(auth_data):
    """Test WebSocket connection"""
    print("\n" + "=" * 60)
    print("STEP 3: Testing WebSocket Connection")
    print("=" * 60)
    
    try:
        from websocket_manager import WebSocketManager
        import time
        
        ws_manager = WebSocketManager()
        
        # Add a simple callback to test data reception
        received_data = []
        def test_callback(data):
            received_data.append(data)
            print(f"[OK] Received tick data: {data.get('token', 'unknown')}")
        
        ws_manager.add_callback(test_callback)
        
        # Test with NIFTY 50
        test_tokens = [{"exchangeType": 1, "tokens": ["26000"]}]
        
        print(f"Starting WebSocket with tokens: {test_tokens}")
        ws_manager.start(tokens=test_tokens)
        
        # Wait for connection
        print("Waiting for connection (5 seconds)...")
        time.sleep(5)
        
        if ws_manager.is_connected:
            print("[OK] WebSocket connected successfully!")
            print(f"  Subscribed tokens: {ws_manager.subscribed_tokens}")
            
            # Wait for some data
            print("Waiting for market data (10 seconds)...")
            time.sleep(10)
            
            if received_data:
                print(f"[OK] Received {len(received_data)} data packets")
                print(f"  Sample data: {received_data[0]}")
            else:
                print("[WARNING] No data received (market might be closed)")
            
            ws_manager.stop()
            return True
        else:
            print("[ERROR] WebSocket failed to connect")
            return False
            
    except Exception as e:
        print(f"[ERROR] WebSocket test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n" + "=" * 60)
    print("STEP 0: Checking Dependencies")
    print("=" * 60)
    
    required_packages = [
        ('SmartApi', 'smartapi-python'),
        ('pyotp', 'pyotp'),
        ('websocket', 'websocket-client')
    ]
    
    missing = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"[OK] {package_name}")
        except ImportError:
            print(f"[MISSING] {package_name}")
            missing.append(package_name)
    
    if missing:
        print("\n[ERROR] Missing packages. Install with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("\n[OK] All required packages installed!")
    return True

def main():
    print("""
===============================================================
   Angel One API Integration Diagnostic Tool
   Testing authentication and data connectivity
===============================================================
""")
    
    # Step 0: Check dependencies
    if not check_dependencies():
        print("\n[ERROR] Please install missing dependencies first")
        return
    
    # Step 1: Check environment variables
    if not check_environment():
        print("\n[ERROR] Please configure environment variables first")
        return
    
    # Step 2: Test authentication
    success, auth_data = test_authentication()
    if not success:
        print("\n[ERROR] Authentication failed. Please check your credentials")
        return
    
    # Step 3: Test WebSocket (optional, can be slow)
    print("\n" + "=" * 60)
    response = input("Do you want to test WebSocket connection? (y/n): ")
    if response.lower() == 'y':
        test_websocket_connection(auth_data)
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print("""
Summary:
1. If authentication works but no data: Market might be closed
2. If WebSocket fails: Check firewall/network settings
3. For frontend integration: You need to call /api/angel-one/start from frontend
    """)

if __name__ == "__main__":
    main()

