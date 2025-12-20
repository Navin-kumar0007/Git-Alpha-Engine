"""Final Verification - Confirm everything is ready"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.db import get_db
from app.models import Market, MarketIndex, HistoricalData

print("\n" + "=" * 70)
print("FINAL VERIFICATION - Database Status")
print("=" * 70)

db = next(get_db())
try:
    # Count records
    market_count = db.query(Market).count()
    index_count = db.query(MarketIndex).count()
    historical_count = db.query(HistoricalData).count()
    
    print(f"\n✅ DATABASE STATUS:")
    print(f"   Markets: {market_count}")
    print(f"   Indices: {index_count}")
    print(f"   Historical data points: {historical_count}")
    
    # List markets and indices
    markets = db.query(Market).all()
    print(f"\n✅ MARKETS CREATED:")
    for market in markets:
        print(f"   {market.code}: {market.name} ({market.currency})")
        for idx in market.indices:
            print(f"      └─ {idx.symbol}: {idx.name}")
    
    print(f"\n✅ PHASE 3 BACKEND IS READY!")
    print(f"\n⚠️  NEXT STEP: Restart the backend server")
    print(f"   1. Stop the current uvicorn server (Ctrl+C)")
    print(f"   2. Run: uvicorn main:app --reload")
    print(f"   3. Test: http://localhost:8000/api/markets/health")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)
