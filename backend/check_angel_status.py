"""
Quick test script to verify Angel One service is running
Run this after starting the server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Angel One Service Status Check")
print("=" * 60)

# Note: This endpoint requires authentication
# For a quick test without auth, we'll check if the server is running
# and the endpoint exists

try:
    # Try to access the status endpoint (will require auth)
    response = requests.get(f"{BASE_URL}/api/angel-one/status")
    
    if response.status_code == 401:
        print("\n✓ Server is running!")
        print("✓ Angel One endpoints are registered!")
        print("\nℹ Status endpoint requires authentication.")
        print("  Please login first to get your token, then call:")
        print("  GET /api/angel-one/status")
        print("  with header: Authorization: Bearer YOUR_TOKEN")
    elif response.status_code == 200:
        data = response.json()
        print("\n✓ Successfully retrieved status!")
        print(json.dumps(data, indent=2))
        
        if data.get('is_running') and data.get('is_connected'):
            print("\n✓✓✓ Angel One service is RUNNING and CONNECTED!")
            print(f"Subscribed tokens: {data.get('subscribed_tokens', [])}")
        elif data.get('is_running'):
            print("\n⚠ Service is running but not connected to Angel One WebSocket")
        else:
            print("\n⚠ Service is not running")
    else:
        print(f"\nUnexpected response: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n✗ Could not connect to server!")
    print("  Make sure the backend server is running:")
    print("  cd backend && uvicorn main:app --reload")
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)
print("1. Start the backend server: cd backend && uvicorn main:app --reload")
print("2. Check the console output for Angel One auto-start messages")
print("3. Login to get an auth token")
print("4. Use the token to call /api/angel-one/status")
print("\nIf auto-start succeeded, you should see:")
print("  '✓ Angel One service auto-started with NIFTY & BANKNIFTY'")
print("in the server console output")
