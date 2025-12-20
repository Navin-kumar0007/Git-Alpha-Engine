from smart_auth import SmartAuth
import sys
import os

# Add parent directory to path to import backend modules if needed, 
# though running from root as `python backend/test_auth.py` handles imports relative to cwd if we are careful.
# However, inside backend/test_auth.py, importing smart_auth (which is in the same dir) works if we run as script from that dir or module.
# Let's handle it simply.

def test_login():
    print("Testing Angel One Login...")
    auth = SmartAuth()
    
    # Check if credentials loaded (basic check)
    if not auth.api_key or not auth.client_id:
        print("FAIL: Credentials not found in .env")
        return

    result = auth.login()
    
    if result['status']:
        print("SUCCESS: Login Successful!")
        print(f"Auth Token: {result['auth_token'][:10]}... (truncated)")
    else:
        print(f"FAIL: Login Failed - {result['message']}")

if __name__ == "__main__":
    test_login()
