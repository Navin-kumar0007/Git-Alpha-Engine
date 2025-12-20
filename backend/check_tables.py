import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]

print(f"\nAll tables in users.db:")
for table in tables:
    print(f"  - {table}")

market_tables = [t for t in tables if 'market' in t.lower()]
print(f"\nMarket-related tables: {market_tables}")

conn.close()
