"""
News Database Population Script
Fetches news articles from NewsAPI and RSS feeds to populate the News Hub
"""
import sys
import os

# Force using the correct database from .env
os.environ.setdefault('DATABASE_URL', 'sqlite:///./git_alpha.db')

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

from app.db import SessionLocal
from app.services.news_service import NewsService
from app.services.rss_service import RSSService

def populate_news():
    """Fetch and populate news articles"""
    db = SessionLocal()
    
    try:
        # Initialize services
        NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
        news_service = NewsService(api_key=NEWS_API_KEY) if NEWS_API_KEY else None
        rss_service = RSSService()
        
        total_articles = 0
        
        # Fetch from NewsAPI if available
        if news_service:
            print("[*] Fetching from NewsAPI...")
            
            categories = ["technology", "business"]
            for category in categories:
                print(f"  -> Fetching {category} news...")
                articles = news_service.fetch_top_headlines(
                    db=db,
                    category=category,
                    page_size=20
                )
                print(f"     [OK] Fetched {len(articles)} {category} articles")
                total_articles += len(articles)
        else:
            print("[!] NewsAPI key not found - skipping NewsAPI")
        
        # Fetch from RSS feeds
        print("\n[*] Fetching from RSS feeds...")
        rss_count = rss_service.fetch_all_default_feeds(
            db=db,
            limit_per_feed=10
        )
        print(f"  [OK] Fetched {rss_count} articles from RSS feeds")
        total_articles += rss_count
        
        print(f"\n[SUCCESS] Populated {total_articles} total articles!")
        print("\nTip: Refresh your News Hub to see the articles!")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("NEWS HUB POPULATION SCRIPT")
    print("=" * 60)
    print()
    
    populate_news()
