"""Check which tables exist in both databases"""

import sqlite3

print("=" * 60)
print("Checking tables in both databases")
print("=" * 60)

# Check users.db
print("\n1. Tables in users.db:")
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
users_tables = [t[0] for t in cursor.fetchall()]
for table in users_tables:
    print(f"   - {table}")
conn.close()

# Check git_alpha.db
print("\n2. Tables in git_alpha.db:")
conn = sqlite3.connect('git_alpha.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
git_alpha_tables = [t[0] for t in cursor.fetchall()]
for table in git_alpha_tables:
    print(f"   - {table}")
conn.close()

# Check for market tables
market_tables = ['markets', 'market_indices', 'market_data', 'historical_data']
print(f"\n3. Market tables location:")
for table in market_tables:
    in_users = table in users_tables
    in_git_alpha = table in git_alpha_tables
    location = []
    if in_users:
        location.append("users.db")
    if in_git_alpha:
        location.append("git_alpha.db")
    
    if location:
        print(f"   ✓ {table}: {', '.join(location)}")
    else:
        print(f"   ✗ {table}: NOT FOUND")

print(f"\n4. Application uses: users.db (from db.py)")
print(f"   Market tables needed in: users.db")
