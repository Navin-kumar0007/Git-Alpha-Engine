"""
Test Angel One API Connection
Run this to diagnose authentication and API issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from smart_auth import SmartAuth

# Load environment variables
load_dotenv()

print("=" * 60)
print("ANGEL ONE API DIAGNOSTIC TEST")
print("=" * 60)

# Check if credentials exist
print("\n1. Checking Environment Variables...")
angel_api_key = os.getenv("ANGEL_API_KEY")
angel_client_id = os.getenv("ANGEL_CLIENT_ID")
angel_password = os.getenv("ANGEL_PASSWORD")
angel_totp_key = os.getenv("ANGEL_TOTP_KEY")

if not all([angel_api_key, angel_client_id, angel_password, angel_totp_key]):
    print("❌ Missing credentials in .env file!")
    print(f"   API Key: {'✓' if angel_api_key else '✗'}")
    print(f"   Client ID: {'✓' if angel_client_id else '✗'}")
    print(f"   Password: {'✓' if angel_password else '✗'}")
    print(f"   TOTP Key: {'✓' if angel_totp_key else '✗'}")
    sys.exit(1)

print("✓ All credentials found")
print(f"   API Key: {angel_api_key[:10]}...")
print(f"   Client ID: {angel_client_id}")

# Test authentication
print("\n2. Testing Angel One Authentication...")
try:
    auth = SmartAuth()
    login_result = auth.login()
    
    if login_result['status']:
        print("✓ Authentication SUCCESSFUL!")
        print(f"   Auth Token: {login_result['auth_token'][:20]}...")
        print(f"   Feed Token: {login_result['feed_token'][:20]}...")
    else:
        print(f"❌ Authentication FAILED!")
        print(f"   Error: {login_result['message']}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Exception during authentication:")
    print(f"   {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test API calls
print("\n3. Testing Angel One API Calls...")
try:
    smart_api = auth.get_instance()
    
    # Test holdings
    print("\n   Testing holdings() API...")
    holdings_response = smart_api.holding()
    print(f"   Response: {holdings_response}")
    
    if holdings_response and holdings_response.get('status'):
        holdings_data = holdings_response.get('data', [])
        print(f"   ✓ Holdings API works! Found {len(holdings_data)} holdings")
        if holdings_data:
            print(f"   First holding: {holdings_data[0].get('tradingsymbol', 'N/A')}")
    else:
        print(f"   ❌ Holdings API failed: {holdings_response.get('message', 'Unknown error')}")
    
    # Test positions
    print("\n   Testing position() API...")
    positions_response = smart_api.position()
    print(f"   Response: {positions_response}")
    
    if positions_response and positions_response.get('status'):
        positions_data = positions_response.get('data')
        # Handle None response (no positions)
        if positions_data is None:
            positions_data = []
        print(f"   ✓ Positions API works! Found {len(positions_data)} positions")
    else:
        print(f"   ❌ Positions API failed: {positions_response.get('message', 'Unknown error')}")
    
    # Test funds
    print("\n   Testing rmsLimit() API...")
    funds_response = smart_api.rmsLimit()
    print(f"   Response: {funds_response}")
    
    if funds_response and funds_response.get('status'):
        print(f"   ✓ Funds API works!")
        funds_data = funds_response.get('data', {})
        print(f"   Available cash: ₹{funds_data.get('availablecash', 0)}")
    else:
        print(f"   ❌ Funds API failed: {funds_response.get('message', 'Unknown error')}")
        
except Exception as e:
    print(f"\n❌ Exception during API calls:")
    print(f"   {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print("\nIf all tests passed, the integration should work!")
print("If tests failed, check the error messages above.")
