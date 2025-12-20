"""
Background Tasks Scheduler for News Hub
Periodic fetching of news from NewsAPI and RSS feeds
"""
import asyncio
import logging
from datetime import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.news_service import NewsService
from app.services.rss_service import RSSService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./git_alpha.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def fetch_news_task():
    """Background task to fetch news periodically"""
    logger.info("Starting news fetching task...")

    # Initialize services
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    news_service = NewsService(api_key=NEWS_API_KEY) if NEWS_API_KEY else None
    rss_service = RSSService()

    db = SessionLocal()

    try:
        # Fetch from RSS feeds (always available)
        logger.info("Fetching from RSS feeds...")
        rss_count = rss_service.fetch_all_default_feeds(db=db, limit_per_feed=10)
        logger.info(f"Fetched {rss_count} articles from RSS feeds")

        # Fetch from NewsAPI if available
        if news_service:
            logger.info("Fetching from NewsAPI...")

            # Fetch business news
            business_articles = news_service.fetch_top_headlines(
                db=db, category="business", page_size=20
            )

            # Fetch technology news
            tech_articles = news_service.fetch_top_headlines(
                db=db, category="technology", page_size=20
            )

            logger.info(
                f"Fetched {len(business_articles) + len(tech_articles)} articles from NewsAPI"
            )
        else:
            logger.warning("NewsAPI key not configured, skipping NewsAPI fetch")

        logger.info("News fetching task completed successfully")

    except Exception as e:
        logger.error(f"Error in news fetching task: {str(e)}")
    finally:
        db.close()


async def periodic_news_fetcher(interval_minutes: int = 60):
    """
    Run news fetching task periodically

    Args:
        interval_minutes: Interval between fetches in minutes
    """
    while True:
        try:
            logger.info(f"[{datetime.now()}] Running periodic news fetch...")
            await fetch_news_task()
            logger.info(f"Next fetch scheduled in {interval_minutes} minutes")
            await asyncio.sleep(interval_minutes * 60)
        except Exception as e:
            logger.error(f"Error in periodic news fetcher: {str(e)}")
            await asyncio.sleep(60)  # Retry after 1 minute on error


if __name__ == "__main__":
    # Run the periodic fetcher
    logger.info("Starting News Hub background task scheduler...")
    asyncio.run(periodic_news_fetcher(interval_minutes=60))
