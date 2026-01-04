"""
Database migration to add Angel One Portfolio tables
Run this script to create the new tables for Angel One portfolio sync
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import engine, Base
from app.models import AngelOneHolding, AngelOnePosition, AngelOneFunds

def migrate():
    """Create Angel One portfolio tables"""
    print("Creating Angel One Portfolio tables...")
    
    try:
        # Create all tables (will only create missing ones)
        Base.metadata.create_all(bind=engine)
        print("✓ Successfully created tables:")
        print("  - angel_one_holdings")
        print("  - angel_one_positions")
        print("  - angel_one_funds")
        print("\nMigration complete!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate()
