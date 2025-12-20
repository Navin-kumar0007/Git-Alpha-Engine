"""Database Migration for Multi-Market Support

This script:
1. Creates new tables for markets, indices, and market data
2. Seeds initial market and index data
3. Fetches initial historical data for all indices
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.db import engine, get_db, Base
from app.models import Market, MarketIndex, MarketData, HistoricalData
from app.services.market_service import seed_markets

def main():
    """Run migration"""
    print("=" * 60)
    print("Multi-Market Database Migration")
    print("=" * 60)
    
    # Create all tables
    print("\n[1/2] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")
    
    # Seed data
    print("\n[2/2] Seeding market data...")
    print("This will fetch historical data and may take a few minutes...")
    
    db = next(get_db())
    try:
        seed_markets(db)
        print("\n✓ Market data seeded successfully")
    except Exception as e:
        print(f"\n✗ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
    
    # Show summary
    db = next(get_db())
    try:
        market_count = db.query(Market).count()
        index_count = db.query(MarketIndex).count()
        historical_count = db.query(HistoricalData).count()
        
        print(f"\nSummary:")
        print(f"  Markets: {market_count}")
        print(f"  Indices: {index_count}")
        print(f"  Historical data points: {historical_count}")
        print()
    finally:
        db.close()


if __name__ == "__main__":
    main()
