"""
Database Migration Script for OAuth & 2FA Support
Adds new tables and columns without losing existing data
"""

import sqlite3
from datetime import datetime

def run_migration():
    # Connect to database
    conn = sqlite3.connect('git_alpha.db')
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    try:
        # 1. Add 2FA columns to users table
        print("Adding 2FA columns to users table...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0")
            print("  [+] Added two_factor_enabled column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("  [~] two_factor_enabled already exists")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN two_factor_secret TEXT")
            print("  [+] Added two_factor_secret column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("  [~] two_factor_secret already exists")
            else:
                raise
        
        # 2. Create sessions table
        print("\nCreating sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_jti TEXT UNIQUE NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("  [+] Created sessions table")
        
        # 3. Create oauth_accounts table
        print("\nCreating oauth_accounts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oauth_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                provider TEXT NOT NULL,
                provider_user_id TEXT NOT NULL,
                email TEXT,
                access_token TEXT,
                refresh_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("  [+] Created oauth_accounts table")
        
        # Commit changes
        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        print("\nNew tables created:")
        print("  - sessions (for session management)")
        print("  - oauth_accounts (for Google/GitHub login)")
        print("\nNew columns added to users:")
        print("  - two_factor_enabled")
        print("  - two_factor_secret")
        print("\n[SUCCESS] All existing data preserved!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
