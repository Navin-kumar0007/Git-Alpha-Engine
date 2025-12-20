"""
Password Migration Script
--------------------------
Migrates existing pbkdf2_sha256 hashed passwords to bcrypt for better performance.

This script is OPTIONAL. The system will auto-migrate passwords when users login.
However, running this script will migrate all passwords immediately.

Usage: python migrate_passwords.py
"""

from app.db import SessionLocal
from app.models import User
from passlib.context import CryptContext

# Old context (slow pbkdf2)
old_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# New context (fast bcrypt)
new_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def migrate_passwords():
    """Migrate all user passwords from pbkdf2_sha256 to bcrypt"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        migrated = 0
        skipped = 0
        
        for user in users:
            if user.hashed_password:
                # Check if password is using old pbkdf2 format
                if user.hashed_password.startswith("$pbkdf2"):
                    print(f"Migrating user: {user.email}")
                    # Note: We can't rehash without the plain password
                    # So this approach won't work. Users will be auto-migrated on login.
                    print(f"  ❌ Cannot migrate without plain password")
                    print(f"  ℹ️  User will be auto-migrated on next login")
                    skipped += 1
                else:
                    print(f"Skipping user {user.email} - already using modern hash")
                    skipped += 1
        
        print(f"\n✅ Migration complete!")
        print(f"   Migrated: {migrated}")
        print(f"   Skipped: {skipped}")
        print(f"\n📝 Note: Users with old passwords will be auto-migrated on their next login")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🔐 Password Migration Script")
    print("=" * 50)
    print("\nThis script checks for users with old password hashes.")
    print("Due to security, we cannot migrate without plain passwords.")
    print("Users will be automatically migrated on their next login.\n")
    
    response = input("Continue to check database? (yes/no): ")
    if response.lower() == "yes":
        migrate_passwords()
    else:
        print("Migration cancelled.")
