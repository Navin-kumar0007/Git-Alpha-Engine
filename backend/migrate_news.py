"""
Database Migration Script for News Hub
Adds news_articles, user_bookmarks, and news_alerts tables
"""

import sqlite3
from datetime import datetime


def run_migration():
    # Connect to database
    conn = sqlite3.connect('git_alpha.db')
    cursor = conn.cursor()

    print("Starting News Hub database migration...")

    try:
        # 1. Create news_articles table
        print("\nCreating news_articles table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                url TEXT UNIQUE NOT NULL,
                image_url TEXT,
                source_name TEXT,
                source_id TEXT,
                author TEXT,
                published_at TIMESTAMP NOT NULL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                summary TEXT,
                sentiment_score REAL,
                impact_score INTEGER,
                category TEXT,
                related_tickers TEXT,
                tags TEXT
            )
        """)
        print("  [+] Created news_articles table")

        # Create index on URL for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_articles_url 
            ON news_articles(url)
        """)
        print("  [+] Created index on url")

        # Create index on published_at for sorting
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_articles_published_at 
            ON news_articles(published_at DESC)
        """)
        print("  [+] Created index on published_at")

        # 2. Create user_bookmarks table
        print("\nCreating user_bookmarks table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                article_id INTEGER NOT NULL,
                notes TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (article_id) REFERENCES news_articles(id),
                UNIQUE(user_id, article_id)
            )
        """)
        print("  [+] Created user_bookmarks table")

        # Create index on user_id
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_bookmarks_user_id 
            ON user_bookmarks(user_id)
        """)
        print("  [+] Created index on user_id")

        # 3. Create news_alerts table
        print("\nCreating news_alerts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                article_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                trigger_reason TEXT,
                is_read BOOLEAN DEFAULT 0,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (article_id) REFERENCES news_articles(id)
            )
        """)
        print("  [+] Created news_alerts table")

        # Create index on user_id and is_read
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_news_alerts_user_id 
            ON news_alerts(user_id, is_read)
        """)
        print("  [+] Created index on user_id and is_read")

        # Commit changes
        conn.commit()
        print("\n[SUCCESS] News Hub migration completed successfully!")
        print("\nNew tables created:")
        print("  - news_articles (stores fetched news)")
        print("  - user_bookmarks (user's saved articles)")
        print("  - news_alerts (news alerts for users)")
        print("\n[SUCCESS] Database is ready for News Hub!")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
