"""
Fetch MORE news articles from additional categories
"""
import sys
import os

os.environ.setdefault('DATABASE_URL', 'sqlite:///./git_alpha.db')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.db import SessionLocal
from app.services.news_service import NewsService
from app.services.rss_service import RSSService

def fetch_more_news():
    """Fetch additional news from more categories"""
    db = SessionLocal()
    
    try:
        NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
        news_service = NewsService(api_key=NEWS_API_KEY) if NEWS_API_KEY else None
        rss_service = RSSService()
        
        total_new = 0
        
        # Fetch from MORE NewsAPI categories
        if news_service:
            print("[*] Fetching MORE news from NewsAPI...")
            
            # Additional categories
            categories = ["science", "health", "entertainment"]
            for category in categories:
                print(f"  -> Fetching {category} news...")
                articles = news_service.fetch_top_headlines(
                    db=db,
                    category=category,
                    page_size=20
                )
                print(f"     [OK] Fetched {len(articles)} {category} articles")
                total_new += len(articles)
        
        # Fetch MORE from RSS (increase limit)
        print("\n[*] Fetching MORE from RSS feeds...")
        rss_count = rss_service.fetch_all_default_feeds(
            db=db,
            limit_per_feed=20  # Increased from 10
        )
        print(f"  [OK] Fetched {rss_count} more articles from RSS")
        total_new += rss_count
        
        # Get final total
        from app.models import NewsArticle
        total_articles = db.query(NewsArticle).count()
        
        print(f"\n[SUCCESS] Fetched {total_new} additional articles!")
        print(f"Total articles in database: {total_articles}")
        print("\nRefresh your News Hub!")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("FETCHING MORE NEWS")
    print("=" * 60)
    print()
    fetch_more_news()
