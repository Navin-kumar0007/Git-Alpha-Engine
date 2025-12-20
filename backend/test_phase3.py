"""Comprehensive Phase 3 API Test Suite
Run this AFTER restarting the backend server.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text}")
    print(f"{'='*70}")

def test_endpoint(name, method, url, expected_status=200):
    """Test an API endpoint"""
    print(f"\n📍 {name}")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, timeout=10)
        
        print(f"   Status: {response.status_code}", end="")
        
        if response.status_code == expected_status:
            print(" ✅")
            if response.status_code == 200:
                data = response.json()
                # Pretty print first 300 chars
                json_str = json.dumps(data, indent=2)
                if len(json_str) > 300:
                    print(f"   Response: {json_str[:300]}...")
                else:
                    print(f"   Response: {json_str}")
            return True, response
        else:
            print(f" ❌ (Expected {expected_status})")
            print(f"   Error: {response.text[:200]}")
            return False, response
            
    except requests.exceptions.ConnectionError:
        print(" ❌ - Cannot connect to server")
        print("   ⚠️  Is the backend server running?")
        return False, None
    except Exception as e:
        print(f" ❌ - {str(e)[:100]}")
        return False, None


def main():
    """Run all tests"""
    print_header("PHASE 3: MULTI-MARKET API TEST SUITE")
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Health Check
    print_header("1. HEALTH & CONNECTIVITY")
    success, _ = test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/api/markets/health"
    )
    results.append(("Health Check", success))
    
    # Test 2: List Markets
    print_header("2. MARKET INFORMATION")
    success, resp = test_endpoint(
        "List All Markets",
        "GET",
        f"{BASE_URL}/api/markets/"
    )
    results.append(("List All Markets", success))
    
    if success and resp:
        markets = resp.json()
        print(f"   📊 Found {len(markets)} markets:")
        for market in markets:
            print(f"      • {market['name']} ({market['code']}): {market['indices_count']} indices")
    
    # Test 3: Get US Market Detail
    success, resp = test_endpoint(
        "Get US Market Detail",
        "GET",
        f"{BASE_URL}/api/markets/US"
    )
    results.append(("Get US Market Detail", success))
    
    # Test 4: Get US Indices
    success, resp = test_endpoint(
        "Get US Market Indices",
        "GET",
        f"{BASE_URL}/api/markets/US/indices"
    )
    results.append(("Get US Market Indices", success))
    
    if success and resp:
        indices = resp.json()
        print(f"   📈 Found {len(indices)} US indices:")
        for idx in indices:
            print(f"      • {idx['symbol']}: {idx['name']}")
    
    # Test 5: Live Data
    print_header("3. REAL-TIME MARKET DATA")
    success, resp = test_endpoint(
        "S&P 500 Live Data",
        "GET",
        f"{BASE_URL}/api/markets/index/^GSPC/live"
    )
    results.append(("S&P 500 Live Data", success))
    
    if success and resp:
        data = resp.json()
        print(f"   💰 S&P 500: ${data['price']:.2f} ({data['change_percent']:+.2f}%)")
    
    # Test 6: Historical Data
    print_header("4. HISTORICAL DATA")
    success, resp = test_endpoint(
        "S&P 500 Historical (1 month, daily)",
        "GET",
        f"{BASE_URL}/api/markets/index/^GSPC/historical?period=1mo&interval=1d"
    )
    results.append(("S&P 500 Historical", success))
    
    if success and resp:
        data = resp.json()
        print(f"   📊 Got {len(data['data'])} data points for {data['period']} period")
        if data['data']:
            latest = data['data'][-1]
            print(f"   Latest: {latest['date'][:10]} - Close: ${latest['close']:.2f}")
    
    # Test 7: Technical Indicators
    print_header("5. TECHNICAL INDICATORS")
    success, resp = test_endpoint(
        "S&P 500 Indicators (RSI, MACD)",
        "GET",
        f"{BASE_URL}/api/markets/index/^GSPC/indicators?indicators=rsi,macd"
    )
    results.append(("S&P 500 Indicators", success))
    
    if success and resp:
        data = resp.json()
        if data.get('rsi'):
            latest_rsi = data['rsi'][-1]
            print(f"   📉 Latest RSI: {latest_rsi:.2f}")
        if data.get('macd'):
            latest_macd = data['macd']['macd'][-1]
            print(f"   📈 Latest MACD: {latest_macd:.4f}")
    
    # Test 8: NIFTY 50 (India)
    print_header("6. MULTI-MARKET VERIFICATION")
    success, resp = test_endpoint(
        "NIFTY 50 Live Data (India)",
        "GET",
        f"{BASE_URL}/api/markets/index/^NSEI/live"
    )
    results.append(("NIFTY 50 Live Data", success))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*70}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 3 backend is fully operational.")
    elif passed > 0:
        print(f"\n⚠️  Some tests failed. Check server logs for details.")
    else:
        print(f"\n❌ All tests failed. Is the backend server running?")
        print(f"   Run: uvicorn main:app --reload")
    
    print()


if __name__ == "__main__":
    main()
