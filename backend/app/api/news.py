"""
News Hub API Endpoints
Handles news fetching, filtering, bookmarks, and alerts
"""
from datetime import datetime
from typing import List, Optional
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..db import get_db
from ..models import User, NewsArticle, UserBookmark
from ..schemas import (
    NewsArticleOut,
    NewsArticleList,
    UserBookmarkCreate,
    UserBookmarkOut,
    NewsFetchRequest,
    # Phase 2 schemas
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    ClusteredArticlesResponse,
    ClusterInfo,
    TrendingTopicsResponse,
    TrendingTopic,
    # Phase 3 schemas
    NewsAlertsListResponse,
)

from ..services.news_service import NewsService
from ..services.rss_service import RSSService
from .auth import get_current_user

router = APIRouter(prefix="/api/news", tags=["News Hub"])

# Initialize services
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
news_service = NewsService(api_key=NEWS_API_KEY) if NEWS_API_KEY else None
rss_service = RSSService()


@router.get("/articles", response_model=NewsArticleList)
def get_news_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (positive/negative/neutral)"),
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get news articles with optional filters
    """
    offset = (page - 1) * page_size

    # Get articles from database
    if news_service:
        articles = news_service.get_articles(
            db=db,
            category=category,
            sentiment=sentiment,
            ticker=ticker,
            limit=page_size,
            offset=offset,
        )
    else:
        # Query database directly if news_service is not available
        from sqlalchemy import and_, desc
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
            query = query.filter(NewsArticle.related_tickers.contains(ticker))
        
        # Order by published date and apply pagination
        articles = query.order_by(desc(NewsArticle.published_at)).limit(page_size).offset(offset).all()

    # Get total count
    total = len(articles)

    return {
        "articles": articles,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

@router.post("/fetch", response_model=dict)
def fetch_news(
    request: NewsFetchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch new articles from NewsAPI or RSS feeds
    Requires authentication
    """
    fetched_count = 0

    # Fetch from NewsAPI if available
    if news_service and (request.category or request.query):
        if request.query:
            articles = news_service.search_articles(
                db=db,
                query=request.query,
                page_size=request.limit,
            )
        else:
            articles = news_service.fetch_top_headlines(
                db=db,
                category=request.category,
                page_size=request.limit,
            )
        fetched_count += len(articles)

    # Fetch from RSS feeds
    if not request.query:
        rss_count = rss_service.fetch_all_default_feeds(
            db=db,
            limit_per_feed=request.limit // 5,  # Distribute across feeds
        )
        fetched_count += rss_count

    return {
        "status": "success",
        "fetched": fetched_count,
        "message": f"Fetched {fetched_count} new articles",
    }


@router.post("/bookmarks", response_model=UserBookmarkOut)
def create_bookmark(
    bookmark: UserBookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a bookmark for an article"""
    # Verify article exists
    article = db.query(NewsArticle).filter(NewsArticle.id == bookmark.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check if bookmark already exists
    existing = (
        db.query(UserBookmark)
        .filter(
            UserBookmark.user_id == current_user.id,
            UserBookmark.article_id == bookmark.article_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Article already bookmarked")

    # Create bookmark
    new_bookmark = news_service.create_bookmark(
        db=db,
        user_id=current_user.id,
        article_id=bookmark.article_id,
        notes=bookmark.notes,
    ) if news_service else None

    if not new_bookmark:
        raise HTTPException(status_code=500, detail="Failed to create bookmark")

    return new_bookmark


@router.get("/bookmarks", response_model=List[UserBookmarkOut])
def get_bookmarks(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all bookmarks for current user"""
    bookmarks = news_service.get_user_bookmarks(
        db=db,
        user_id=current_user.id,
        limit=limit,
    ) if news_service else []

    # Load article data for each bookmark
    for bookmark in bookmarks:
        bookmark.article = db.query(NewsArticle).filter(NewsArticle.id == bookmark.article_id).first()

    return bookmarks


@router.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a bookmark"""
    success = news_service.delete_bookmark(
        db=db,
        bookmark_id=bookmark_id,
        user_id=current_user.id,
    ) if news_service else False

    if not success:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    return {"status": "success", "message": "Bookmark deleted"}


@router.post("/articles/{article_id}/analyze")
def analyze_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze article sentiment and extract tickers
    Requires authentication
    """
    if not news_service:
        raise HTTPException(status_code=503, detail="News service not available")

    article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Analyze sentiment
    sentiment_score = news_service.analyze_article_sentiment(db=db, article_id=article_id)

    # Generate summary
    summary = news_service.generate_summary(db=db, article_id=article_id)

    # Extract tickers
    tickers = news_service.extract_tickers(db=db, article_id=article_id)

    return {
        "status": "success",
        "sentiment_score": sentiment_score,
        "summary": summary,
        "tickers": tickers,
    }


# ========== PHASE 2: AI FEATURES ==========

@router.post("/articles/analyze-batch", response_model=BatchAnalyzeResponse)
def batch_analyze_articles(
    request: BatchAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Batch analyze multiple articles
    Requires authentication
    """
    if not news_service:
        raise HTTPException(status_code=503, detail="News service not available")

    # Analyze articles in batch
    results = news_service.analyze_articles_batch(db=db, article_ids=request.article_ids)

    return {
        "results": results,
        "analyzed_count": len(results)
    }


@router.get("/articles/clustered", response_model=ClusteredArticlesResponse)
def get_clustered_articles(
    num_clusters: int = Query(5, ge=2, le=10, description="Number of clusters"),
    limit: int = Query(100, ge=10, le=200, description="Max articles to cluster"),
    db: Session = Depends(get_db),
):
    """
    Get articles grouped by similarity clusters
    """
    if not news_service:
        raise HTTPException(status_code=503, detail="News service not available")

    # Get clustered articles
    clusters_dict = news_service.get_clustered_articles(
        db=db,
        num_clusters=num_clusters,
        limit=limit
    )

    # Convert to response format
    clusters_list = []
    total_articles = 0

    for cluster_id, cluster_info in clusters_dict.items():
        # Remove articles from cluster_info for serialization
        cluster_articles = cluster_info.pop("articles", [])
        
        cluster = ClusterInfo(
            cluster_id=cluster_id,
            label=cluster_info["label"],
            size=cluster_info["size"],
            article_ids=cluster_info["article_ids"],
            articles=cluster_articles  # These will be serialized
        )
        clusters_list.append(cluster)
        total_articles += cluster_info["size"]

    return {
        "clusters": clusters_list,
        "total_articles": total_articles,
        "num_clusters": len(clusters_list)
    }


@router.get("/articles/trending", response_model=TrendingTopicsResponse)
def get_trending_topics(
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    limit: int = Query(10, ge=5, le=20, description="Number of topics"),
    db: Session = Depends(get_db),
):
    """
    Get trending topics from recent articles
    """
    if not news_service:
        # Return empty response if news service not available
        return {
            "topics": [],
            "period_days": days,
            "total_articles": 0
        }

    # Get trending topics (returns empty list if no articles)
    topics = news_service.get_trending_topics(db=db, days=days, limit=limit) or []

    # Count total articles
    from datetime import datetime, timedelta
    from_date = datetime.now() - timedelta(days=days)
    total_articles = db.query(NewsArticle).filter(
        NewsArticle.published_at >= from_date
    ).count()

    return {
        "topics": topics,
        "period_days": days,
        "total_articles": total_articles
    }


@router.post("/articles/update-scores")
def update_impact_scores(
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger impact score updates for recent articles
    Requires authentication
    """
    if not news_service:
        raise HTTPException(status_code=503, detail="News service not available")

    # Update impact scores
    updated_count = news_service.update_impact_scores(db=db, days=days)

    return {
        "status": "success",
        "updated_count": updated_count,
        "message": f"Updated impact scores for {updated_count} articles"
    }


@router.get("/articles/{article_id}", response_model=NewsArticleOut)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
):
    """Get a single article by ID"""
    article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article


# ========== PHASE 3: PORTFOLIO INTEGRATION ==========

@router.get("/portfolio/news", response_model=dict)
def get_portfolio_news(
    days: int = Query(7, ge=1, le=30, description="Days to look back"),
    limit: int = Query(50, ge=1, le=100, description="Max articles"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get news articles relevant to user's portfolio holdings
    Requires authentication
    """
    if not news_service:
        raise HTTPException(status_code=503, detail="News service not available")

    # Get portfolio-filtered news
    articles = news_service.get_portfolio_news(
        db=db,
        user_id=current_user.id,
        days=days,
        limit=limit
    )

    # Get portfolio tickers for response
    from ..models import Portfolio
    portfolio_items = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
    
    asset_ticker_map = {
        'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL',
        'cardano': 'ADA', 'polkadot': 'DOT', 'dogecoin': 'DOGE',
        'avalanche': 'AVAX', 'polygon': 'MATIC', 'chainlink': 'LINK',
        'ripple': 'XRP', 'binance': 'BNB', 'cosmos': 'ATOM'
    }
    
    portfolio_tickers = [
        asset_ticker_map.get(item.asset_id.lower())
        for item in portfolio_items
        if asset_ticker_map.get(item.asset_id.lower())
    ]

    return {
        "articles": articles,
        "portfolio_tickers": portfolio_tickers,
        "total_articles": len(articles)
    }


@router.post("/portfolio/alerts")
def create_portfolio_alerts(
    threshold: int = Query(7, ge=1, le=10, description="Minimum impact score"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create alerts for high-impact news affecting portfolio
    Requires authentication
    """
    if not news_service:
        raise HTTPException(status_code=503, detail="News service not available")

    # Create portfolio alerts
    alerts = news_service.create_portfolio_alerts(
        db=db,
        user_id=current_user.id,
        threshold_impact=threshold
    )

    return {
        "created_alerts": len(alerts),
        "alert_ids": [alert.id for alert in alerts],
        "message": f"Created {len(alerts)} portfolio alerts"
    }


@router.get("/alerts", response_model=NewsAlertsListResponse)
def get_user_alerts(
    unread_only: bool = Query(False, description="Show only unread alerts"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get news alerts for current user
    Requires authentication
    """
    from ..models import NewsAlert
    
    query = db.query(NewsAlert).filter(NewsAlert.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(NewsAlert.is_read == False)
    
    alerts = query.order_by(desc(NewsAlert.triggered_at)).limit(limit).all()
    
    # Load article data
    for alert in alerts:
        alert.article = db.query(NewsArticle).filter(NewsArticle.id == alert.article_id).first()
    
    return {
        "alerts": alerts,
        "total": len(alerts),
        "unread_count": sum(1 for a in alerts if not a.is_read)
    }


@router.put("/alerts/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark an alert as read
    Requires authentication
    """
    from ..models import NewsAlert
    
    alert = db.query(NewsAlert).filter(
        NewsAlert.id == alert_id,
        NewsAlert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    db.commit()
    
    return {"status": "success", "message": "Alert marked as read"}
