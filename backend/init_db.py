"""
Initialize the database by creating all tables
"""
from app.db import engine, Base
from app import models

def init_database():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("📊 Tables created:")
        for table in Base.metadata.tables.keys():
            print(f"   - {table}")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise

if __name__ == "__main__":
    init_database()
