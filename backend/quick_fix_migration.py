"""Quick Fix Migration - Run this to create tables and seed data"""

import sys
import os
from pathlib import Path

# Set environment and path
os.chdir(str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "=" * 70)
print("MULTI-MARKET DATABASE MIGRATION - QUICK FIX")
print("=" * 70)

try:
    print("\n[Step 1/4] Importing modules...")
    from app.db import engine, get_db, Base
    from app.models import Market, MarketIndex, MarketData, HistoricalData
    from app.services.market_service import seed_markets
    print("✓ Imports successful")
    
    print(f"\n[Step 2/4] Database location: {engine.url}")
    
    print("\n[Step 3/4] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    print("\n[Step 4/4] Seeding market data...")
    print("   (This may take 2-3 minutes...)")
    
    db = next(get_db())
    try:
        seed_markets(db)
        print("✓ Data seeded successfully")
    except Exception as e:
        print(f"✗ Seeding error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
    
    # Verify
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    db = next(get_db())
    try:
        market_count = db.query(Market).count()
        index_count = db.query(MarketIndex).count()
        historical_count = db.query(HistoricalData).count()
        
        print(f"\n✓ Markets: {market_count}")
        print(f"✓ Indices: {index_count}")
        print(f"✓ Historical data points: {historical_count}")
        
        if market_count > 0:
            print("\nMarkets created:")
            markets = db.query(Market).all()
            for m in markets:
                print(f"  - {m.name} ({m.code}): {len(m.indices)} indices")
        
    finally:
        db.close()
    
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    
except Exception as e:
    print(f"\n✗ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
