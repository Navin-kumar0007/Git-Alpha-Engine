import os
os.environ.setdefault('DATABASE_URL', 'sqlite:///./git_alpha.db')

from dotenv import load_dotenv
load_dotenv()

from app.db import SessionLocal
from app.models import NewsArticle

db = SessionLocal()

try:
    # Delete all articles with example.com URLs (the dummy ones)
    print("Checking for dummy articles...")
    dummy_articles = db.query(NewsArticle).filter(NewsArticle.url.like('%example.com%')).all()
    print(f"Found {len(dummy_articles)} dummy articles")
    
    for article in dummy_articles:
        print(f"  Deleting: {article.title}")
    
    deleted = db.query(NewsArticle).filter(NewsArticle.url.like('%example.com%')).delete(synchronize_session=False)
    db.commit()
    
    print(f"\n[SUCCESS] Deleted {deleted} dummy articles from git_alpha.db!")
    
    total = db.query(NewsArticle).count()
    print(f"Remaining: {total} real news articles\n")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
