"""
News Hub Service
Handles fetching, processing, and managing news articles from NewsAPI and RSS feeds
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import logging

from newsapi import NewsApiClient
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from ..models import NewsArticle, UserBookmark, NewsAlert
from .ai_engine import AIEngine

logger = logging.getLogger(__name__)


class NewsService:
    """Service for managing news articles and feeds"""

    def __init__(self, api_key: str):
        """Initialize NewsAPI client"""
        self.client = NewsApiClient(api_key=api_key)
        self.ai_engine = AIEngine()

    def fetch_top_headlines(
        self,
        db: Session,
        category: Optional[str] = None,
        country: str = "us",
        page_size: int = 20,
    ) -> List[NewsArticle]:
        """
        Fetch top headlines from NewsAPI and store in database

        Args:
            db: Database session
            category: News category (business, technology, etc.)
            country: Country code (us, in, etc.)
            page_size: Number of articles to fetch

        Returns:
            List of NewsArticle objects
        """
        try:
            # Fetch from NewsAPI
            response = self.client.get_top_headlines(
                category=category,
                country=country,
                page_size=page_size,
            )

            articles = []
            if response.get("status") == "ok":
                for article_data in response.get("articles", []):
                    # Check if article already exists
                    existing = (
                        db.query(NewsArticle)
                        .filter(NewsArticle.url == article_data.get("url"))
                        .first()
                    )

                    if not existing:
                        # Create new article
                        article = self._create_article_from_newsapi(
                            article_data, category
                        )
                        db.add(article)
                        articles.append(article)
                    else:
                        articles.append(existing)

                db.commit()
                logger.info(f"Fetched {len(articles)} new articles")

            return articles

        except Exception as e:
            logger.error(f"Error fetching headlines: {str(e)}")
            db.rollback()
            return []

    def search_articles(
        self,
        db: Session,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        sort_by: str = "publishedAt",
        page_size: int = 20,
    ) -> List[NewsArticle]:
        """
        Search for articles using NewsAPI

        Args:
            db: Database session
            query: Search query
            from_date: Start date for search
            to_date: End date for search
            sort_by: Sort field (publishedAt, relevancy, popularity)
            page_size: Number of results

        Returns:
            List of NewsArticle objects
        """
        try:
            # Default to last 7 days if no date specified
            if not from_date:
                from_date = datetime.now() - timedelta(days=7)

            # Fetch from NewsAPI
            response = self.client.get_everything(
                q=query,
                from_param=from_date.strftime("%Y-%m-%d") if from_date else None,
                to=to_date.strftime("%Y-%m-%d") if to_date else None,
                sort_by=sort_by,
                page_size=page_size,
            )

            articles = []
            if response.get("status") == "ok":
                for article_data in response.get("articles", []):
                    # Check if article already exists
                    existing = (
                        db.query(NewsArticle)
                        .filter(NewsArticle.url == article_data.get("url"))
                        .first()
                    )

                    if not existing:
                        article = self._create_article_from_newsapi(article_data)
                        db.add(article)
                        articles.append(article)
                    else:
                        articles.append(existing)

                db.commit()

            return articles

        except Exception as e:
            logger.error(f"Error searching articles: {str(e)}")
            db.rollback()
            return []

    def get_articles(
        self,
        db: Session,
        category: Optional[str] = None,
        sentiment: Optional[str] = None,
        ticker: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NewsArticle]:
        """
        Get articles from database with filters

        Args:
            db: Database session
            category: Filter by category
            sentiment: Filter by sentiment (positive, negative, neutral)
            ticker: Filter by related ticker symbol
            limit: Number of articles to return
            offset: Pagination offset

        Returns:
            List of NewsArticle objects
        """
        query = db.query(NewsArticle)

        # Apply filters
        if category:
            query = query.filter(NewsArticle.category == category)

        if sentiment:
            if sentiment == "positive":
                query = query.filter(NewsArticle.sentiment_score > 0.3)
            elif sentiment == "negative":
                query = query.filter(NewsArticle.sentiment_score < -0.3)
            elif sentiment == "neutral":
                query = query.filter(
                    and_(
                        NewsArticle.sentiment_score >= -0.3,
                        NewsArticle.sentiment_score <= 0.3,
                    )
                )

        if ticker:
            # Search in related_tickers JSON field
            query = query.filter(NewsArticle.related_tickers.contains(ticker))

        # Order by published date
        query = query.order_by(desc(NewsArticle.published_at))

        # Apply pagination
        articles = query.limit(limit).offset(offset).all()

        return articles

    def create_bookmark(
        self, db: Session, user_id: int, article_id: int, notes: Optional[str] = None
    ) -> UserBookmark:
        """Create a bookmark for an article"""
        bookmark = UserBookmark(
            user_id=user_id, article_id=article_id, notes=notes
        )
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        return bookmark

    def delete_bookmark(self, db: Session, bookmark_id: int, user_id: int) -> bool:
        """Delete a bookmark"""
        bookmark = (
            db.query(UserBookmark)
            .filter(
                and_(
                    UserBookmark.id == bookmark_id,
                    UserBookmark.user_id == user_id,
                )
            )
            .first()
        )

        if bookmark:
            db.delete(bookmark)
            db.commit()
            return True
        return False

    def get_user_bookmarks(
        self, db: Session, user_id: int, limit: int = 50
    ) -> List[UserBookmark]:
        """Get all bookmarks for a user"""
        return (
            db.query(UserBookmark)
            .filter(UserBookmark.user_id == user_id)
            .order_by(desc(UserBookmark.created_at))
            .limit(limit)
            .all()
        )

    def analyze_article_sentiment(self, db: Session, article_id: int) -> float:
        """
        Analyze article sentiment using AI engine

        Returns:
            Sentiment score from -1.0 (negative) to 1.0 (positive)
        """
        article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()

        if not article:
            return 0.0

        # Use AI engine to analyze sentiment
        text = f"{article.title} {article.description or ''} {article.content or ''}"
        sentiment_score = self.ai_engine.analyze_sentiment(text)

        # Update article
        article.sentiment_score = sentiment_score
        db.commit()

        return sentiment_score

    def generate_summary(self, db: Session, article_id: int) -> str:
        """
        Generate AI summary for an article

        Returns:
            Summary text
        """
        article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()

        if not article:
            return ""

        # Use AI engine to generate summary (returns tuple: summary, confidence)
        text = f"{article.title}\n\n{article.content or article.description or ''}"
        summary, confidence = self.ai_engine.generate_summary(text)

        # Update article
        article.summary = summary
        db.commit()

        return summary

    def extract_tickers(self, db: Session, article_id: int) -> List[str]:
        """
        Extract ticker symbols from article content

        Returns:
            List of ticker symbols
        """
        article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()

        if not article:
            return []

        # Use AI engine to extract tickers
        text = f"{article.title} {article.description or ''} {article.content or ''}"
        tickers = self.ai_engine.extract_tickers(text)

        # Update article
        article.related_tickers = json.dumps(tickers)
        db.commit()

        return tickers

    def _create_article_from_newsapi(
        self, article_data: Dict[str, Any], category: Optional[str] = None
    ) -> NewsArticle:
        """Create NewsArticle object from NewsAPI response"""
        # Parse published date
        published_at = article_data.get("publishedAt")
        if isinstance(published_at, str):
            published_at = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            )

        return NewsArticle(
            title=article_data.get("title", "")[:500],  # Limit to 500 chars
            description=article_data.get("description"),
            content=article_data.get("content"),
            url=article_data.get("url"),
            image_url=article_data.get("urlToImage"),
            source_name=article_data.get("source", {}).get("name"),
            source_id=article_data.get("source", {}).get("id"),
            author=article_data.get("author"),
            published_at=published_at or datetime.utcnow(),
            category=category,
        )

    def auto_analyze_article(self, db: Session, article: NewsArticle) -> Dict[str, Any]:
        """
        Auto-analyze article: sentiment, summary, tickers, impact score

        Args:
            db: Database session
            article: NewsArticle object

        Returns:
            Dictionary with analysis results
        """
        try:
            text = f"{article.title} {article.description or ''} {article.content or ''}"

            # Analyze sentiment
            sentiment_score = self.ai_engine.analyze_sentiment(text, article.source_name)
            article.sentiment_score = sentiment_score

            # Generate summary
            summary, confidence = self.ai_engine.generate_summary(
                f"{article.title}\n\n{article.content or article.description or ''}"
            )
            article.summary = summary

            # Extract tickers
            tickers = self.ai_engine.extract_tickers(text)
            article.related_tickers = json.dumps(tickers)

            # Calculate impact score
            impact_score = self.ai_engine.calculate_impact_score(
                sentiment_score, tickers, article.source_name
            )
            article.impact_score = impact_score

            db.commit()

            return {
                "sentiment_score": sentiment_score,
                "summary": summary,
                "tickers": tickers,
                "impact_score": impact_score
            }

        except Exception as e:
            logger.error(f"Error auto-analyzing article {article.id}: {str(e)}")
            return {}

    def analyze_articles_batch(
        self, db: Session, article_ids: List[int]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Batch analyze multiple articles

        Args:
            db: Database session
            article_ids: List of article IDs to analyze

        Returns:
            Dictionary mapping article_id to analysis results
        """
        results = {}

        for article_id in article_ids:
            article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
            
            if article:
                analysis = self.auto_analyze_article(db, article)
                results[article_id] = analysis

        logger.info(f"Batch analyzed {len(results)} articles")
        return results

    def get_clustered_articles(
        self, db: Session, num_clusters: int = 5, limit: int = 100
    ) -> Dict[int, Dict[str, Any]]:
        """
        Get articles grouped by similarity clusters

        Args:
            db: Database session
            num_clusters: Number of clusters to create
            limit: Maximum articles to cluster

        Returns:
            Dictionary of clusters with article lists
        """
        # Get recent articles
        articles = (
            db.query(NewsArticle)
            .order_by(desc(NewsArticle.published_at))
            .limit(limit)
            .all()
        )

        if not articles:
            return {}

        # Prepare article data for clustering
        article_data = [
            {
                "id": article.id,
                "title": article.title,
                "description": article.description or ""
            }
            for article in articles
        ]

        # Cluster articles
        clusters = self.ai_engine.cluster_articles(article_data, num_clusters)

        # Enrich clusters with article objects
        for cluster_id, cluster_info in clusters.items():
            article_ids = cluster_info["article_ids"]
            cluster_articles = [a for a in articles if a.id in article_ids]
            cluster_info["articles"] = cluster_articles

        return clusters

    def get_trending_topics(
        self, db: Session, days: int = 7, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trending topics from recent articles

        Args:
            db: Database session
            days: Number of days to look back
            limit: Number of top topics to return

        Returns:
            List of trending topics with metadata
        """
        # Get articles from last N days
        from_date = datetime.now() - timedelta(days=days)
        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.published_at >= from_date)
            .all()
        )

        if not articles:
            return []

        # Prepare article data
        article_data = [
            {
                "id": article.id,
                "title": article.title,
                "description": article.description or "",
                "published_at": article.published_at
            }
            for article in articles
        ]

        # Extract trending topics
        trending_topics = self.ai_engine.extract_trending_topics(article_data, limit)

        return trending_topics

    def update_impact_scores(self, db: Session, days: int = 7) -> int:
        """
        Recalculate impact scores for recent articles

        Args:
            db: Database session
            days: Number of days to look back

        Returns:
            Number of articles updated
        """
        from_date = datetime.now() - timedelta(days=days)
        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.published_at >= from_date)
            .all()
        )

        updated_count = 0
        for article in articles:
            try:
                # Parse tickers if stored as JSON
                tickers = []
                if article.related_tickers:
                    try:
                        tickers = json.loads(article.related_tickers)
                    except:
                        pass

                # Recalculate impact score
                impact_score = self.ai_engine.calculate_impact_score(
                    article.sentiment_score or 0.0,
                    tickers,
                    article.source_name
                )
                article.impact_score = impact_score
                updated_count += 1

            except Exception as e:
                logger.error(f"Error updating impact score for article {article.id}: {str(e)}")

        db.commit()
        logger.info(f"Updated impact scores for {updated_count} articles")
        return updated_count

    def get_portfolio_news(
        self, db: Session, user_id: int, days: int = 7, limit: int = 50
    ) -> List[NewsArticle]:
        """
        Get news articles relevant to user's portfolio holdings

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back
            limit: Maximum articles to return

        Returns:
            List of NewsArticle objects relevant to portfolio
        """
        from ..models import Portfolio
        
        # Get user's portfolio holdings
        portfolio_items = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        
        if not portfolio_items:
            return []

        # Extract asset IDs and map to tickers
        asset_ticker_map = {
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL',
            'cardano': 'ADA', 'polkadot': 'DOT', 'dogecoin': 'DOGE',
            'avalanche': 'AVAX', 'polygon': 'MATIC', 'chainlink': 'LINK',
            'ripple': 'XRP', 'binance': 'BNB', 'cosmos': 'ATOM'
        }

        # Get tickers for portfolio assets
        portfolio_tickers = []
        for item in portfolio_items:
            ticker = asset_ticker_map.get(item.asset_id.lower())
            if ticker:
                portfolio_tickers.append(ticker)

        if not portfolio_tickers:
            return []

        # Get recent articles mentioning portfolio tickers
        from_date = datetime.now() - timedelta(days=days)
        
        # Query articles that mention any of the portfolio tickers
        relevant_articles = []
        for article in (
            db.query(NewsArticle)
            .filter(NewsArticle.published_at >= from_date)
            .order_by(desc(NewsArticle.published_at))
            .all()
        ):
            if article.related_tickers:
                try:
                    article_tickers = json.loads(article.related_tickers)
                    # Check if any portfolio ticker is in article
                    if any(ticker in article_tickers for ticker in portfolio_tickers):
                        relevant_articles.append(article)
                        
                        if len(relevant_articles) >= limit:
                            break
                except:
                    pass

        logger.info(f"Found {len(relevant_articles)} articles for user {user_id}'s portfolio")
        return relevant_articles

    def create_portfolio_alerts(
        self, db: Session, user_id: int, threshold_impact: int = 7
    ) -> List[NewsAlert]:
        """
        Create news alerts for high-impact articles affecting user's portfolio

        Args:
            db: Database session
            user_id: User ID
            threshold_impact: Minimum impact score to trigger alert (default: 7)

        Returns:
            List of created NewsAlert objects
        """
        from ..models import Portfolio
        
        # Get portfolio news
        portfolio_articles = self.get_portfolio_news(db, user_id, days=1, limit=20)
        
        # Filter high-impact articles
        high_impact_articles = [
            article for article in portfolio_articles
            if article.impact_score and article.impact_score >= threshold_impact
        ]

        created_alerts = []
        for article in high_impact_articles:
            # Check if alert already exists
            existing_alert = (
                db.query(NewsAlert)
                .filter(
                    NewsAlert.user_id == user_id,
                    NewsAlert.article_id == article.id
                )
                .first()
            )

            if not existing_alert:
                # Determine which portfolio assets are affected
                affected_tickers = []
                if article.related_tickers:
                    try:
                        affected_tickers = json.loads(article.related_tickers)
                    except:
                        pass

                # Create alert
                alert = NewsAlert(
                    user_id=user_id,
                    article_id=article.id,
                    alert_type="portfolio_impact",
                    trigger_reason=f"High impact ({article.impact_score}/10) news about {', '.join(affected_tickers[:3])}"
                )
                db.add(alert)
                created_alerts.append(alert)

        db.commit()
        logger.info(f"Created {len(created_alerts)} portfolio alerts for user {user_id}")
        return created_alerts
