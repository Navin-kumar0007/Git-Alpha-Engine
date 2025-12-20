"""
RSS Feed Service
Handles parsing and fetching news from RSS feeds
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

import feedparser
from dateutil import parser as date_parser
from sqlalchemy.orm import Session

from ..models import NewsArticle

logger = logging.getLogger(__name__)


class RSSService:
    """Service for parsing and managing RSS feeds"""

    # Popular financial/crypto RSS feeds
    DEFAULT_FEEDS = [
        {
            "url": "https://cointelegraph.com/rss",
            "category": "cryptocurrency",
            "name": "Cointelegraph",
        },
        {
            "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "category": "cryptocurrency",
            "name": "CoinDesk",
        },
        {
            "url": "https://feeds.bloomberg.com/markets/news.rss",
            "category": "business",
            "name": "Bloomberg Markets",
        },
        {
            "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "category": "business",
            "name": "CNBC Markets",
        },
        {
            "url": "https://finance.yahoo.com/news/rssindex",
            "category": "business",
            "name": "Yahoo Finance",
        },
    ]

    def __init__(self):
        """Initialize RSS service"""
        pass

    def fetch_feed(
        self, db: Session, feed_url: str, category: Optional[str] = None, limit: int = 20
    ) -> List[NewsArticle]:
        """
        Fetch and parse RSS feed

        Args:
            db: Database session
            feed_url: URL of RSS feed
            category: Category to assign to articles
            limit: Maximum number of articles to fetch

        Returns:
            List of NewsArticle objects
        """
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_url}")
                return []

            articles = []
            for entry in feed.entries[:limit]:
                # Check if article already exists
                url = entry.get("link", "")
                existing = (
                    db.query(NewsArticle)
                    .filter(NewsArticle.url == url)
                    .first()
                )

                if not existing and url:
                    article = self._create_article_from_rss(entry, category)
                    db.add(article)
                    articles.append(article)
                elif existing:
                    articles.append(existing)

            if articles:
                db.commit()
                logger.info(f"Fetched {len(articles)} new articles from {feed_url}")

            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {str(e)}")
            db.rollback()
            return []

    def fetch_all_default_feeds(self, db: Session, limit_per_feed: int = 10) -> int:
        """
        Fetch articles from all default RSS feeds

        Args:
            db: Database session
            limit_per_feed: Maximum articles per feed

        Returns:
            Total number of new articles fetched
        """
        total_articles = 0

        for feed_config in self.DEFAULT_FEEDS:
            articles = self.fetch_feed(
                db=db,
                feed_url=feed_config["url"],
                category=feed_config.get("category"),
                limit=limit_per_feed,
            )
            total_articles += len(articles)

        logger.info(f"Total new articles fetched from all feeds: {total_articles}")
        return total_articles

    def add_custom_feed(
        self, feed_url: str, category: Optional[str] = None, name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a custom RSS feed to the system

        Args:
            feed_url: URL of the RSS feed
            category: Category for articles from this feed
            name: Display name for the feed

        Returns:
            Feed configuration dictionary
        """
        feed_config = {
            "url": feed_url,
            "category": category or "general",
            "name": name or feed_url,
        }

        # Validate feed by parsing
        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                raise ValueError("Feed has no entries")

            return feed_config

        except Exception as e:
            logger.error(f"Invalid RSS feed {feed_url}: {str(e)}")
            raise ValueError(f"Invalid RSS feed: {str(e)}")

    def _create_article_from_rss(
        self, entry: Dict[str, Any], category: Optional[str] = None
    ) -> NewsArticle:
        """
        Create NewsArticle object from RSS feed entry

        Args:
            entry: RSS feed entry
            category: Article category

        Returns:
            NewsArticle object
        """
        # Parse published date
        published_at = None
        if "published" in entry:
            try:
                published_at = date_parser.parse(entry.published)
            except Exception:
                pass

        if not published_at and "updated" in entry:
            try:
                published_at = date_parser.parse(entry.updated)
            except Exception:
                pass

        if not published_at:
            published_at = datetime.utcnow()

        # Get description/summary
        description = entry.get("summary", entry.get("description", ""))

        # Get image URL
        image_url = None
        if "media_content" in entry and entry.media_content:
            image_url = entry.media_content[0].get("url")
        elif "media_thumbnail" in entry and entry.media_thumbnail:
            image_url = entry.media_thumbnail[0].get("url")

        # Get author
        author = entry.get("author", entry.get("dc_creator", None))

        # Get source name from feed title
        source_name = entry.get("source", {}).get("title", None)

        return NewsArticle(
            title=entry.get("title", "")[:500],
            description=description,
            content=entry.get("content", [{}])[0].get("value") if "content" in entry else None,
            url=entry.get("link", ""),
            image_url=image_url,
            source_name=source_name,
            author=author,
            published_at=published_at,
            category=category,
        )
