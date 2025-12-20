"""Debug script to test database and imports"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    print("Testing imports...")
    from app.db import get_db, engine
    from app.models import Market, MarketIndex
    from app.schemas import MarketOut
    print("✓ Imports successful")
    
    print("\nTesting database connection...")
    from sqlalchemy.orm import Session
    db = next(get_db())
    
    print("\nQuerying markets...")
    markets = db.query(Market).all()
    print(f"✓ Found {len(markets)} markets")
    
    for market in markets:
        print(f"\n  Market: {market.name} ({market.code})")
        print(f"    Indices: {len(market.indices)}")
        
        # Test MarketOut schema
        market_dict = {
            "id": market.id,
            "code": market.code,
            "name": market.name,
            "currency": market.currency,
            "timezone": market.timezone,
            "is_active": market.is_active,
            "created_at": market.created_at,
            "indices_count": len(market.indices)
        }
        
        market_out = MarketOut(**market_dict)
        print(f"    Schema validated: {market_out.model_dump_json()[:100]}...")
    
    db.close()
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
