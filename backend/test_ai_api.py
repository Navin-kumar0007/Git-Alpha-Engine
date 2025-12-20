"""Simple script to test the AI Agent API endpoint"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
AI_AGENT_URL = f"{BASE_URL}/api/ai-agent/query"

# Login credentials
USERNAME = "jhon"
PASSWORD = "jhon123"

def test_ai_agent():
    print("🔐 Logging in...")
    
    # Step 1: Login to get token
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    login_response = requests.post(LOGIN_URL, data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    # Step 2: Test AI Agent
    print("\n🤖 Testing AI Agent API...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query_data = {
        "message": "What is the current price of AAPL?",
        "stream": False
    }
    
    print(f"📤 Sending query: {query_data['message']}")
    
    ai_response = requests.post(AI_AGENT_URL, headers=headers, json=query_data)
    
    print(f"\n📊 Status Code: {ai_response.status_code}")
    
    if ai_response.status_code == 200:
        print("✅ Success!")
        response_data = ai_response.json()
        print(f"\n🤖 AI Response:\n{response_data.get('response', 'No response')}")
    else:
        print(f"❌ Error!")
        print(f"Response: {ai_response.text}")

if __name__ == "__main__":
    test_ai_agent()
