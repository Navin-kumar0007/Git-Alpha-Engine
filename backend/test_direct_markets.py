"""Direct test of markets API functions"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    print("Testing market API functions directly...")
    from app.db import get_db
    from app.api.markets import get_all_markets, get_market_detail, health_check
    
    print("\n1. Testing health_check...")
    result = health_check()
    print(f"✓ Health check: {result}")
    
    print("\n2. Testing get_all_markets...")
    db = next(get_db())
    result = get_all_markets(db)
    print(f"✓ Got {len(result)} markets")
    for market in result:
        print(f"   - {market}")
    
    print("\n3. Testing get_market_detail for US...")
    result = get_market_detail("US", db)
    print(f"✓ Market detail: {result}")
    
    db.close()
    print("\n✓ All direct tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
