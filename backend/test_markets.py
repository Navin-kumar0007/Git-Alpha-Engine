"""Test Multi-Market API Endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:500]}...")
            return True
        else:
            print(f"Error: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Multi-Market API Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", f"{BASE_URL}/api/markets/health"),
        ("List All Markets", f"{BASE_URL}/api/markets/"),
        ("Get US Market", f"{BASE_URL}/api/markets/US"),
        ("Get US Indices", f"{BASE_URL}/api/markets/US/indices"),
        ("Get S&P 500 Live Data", f"{BASE_URL}/api/markets/index/^GSPC/live"),
        ("Get S&P 500 Historical", f"{BASE_URL}/api/markets/index/^GSPC/historical?period=1mo&interval=1d"),
        ("Get S&P 500 Indicators", f"{BASE_URL}/api/markets/index/^GSPC/indicators?indicators=rsi,macd"),
    ]
    
    results = []
    for name, url in tests:
        success = test_endpoint(name, url)
        results.append((name, success))
    
    # Summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")


if __name__ == "__main__":
    main()
