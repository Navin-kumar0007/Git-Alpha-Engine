from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr

# ---------- AUTH / USER ----------

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    name: constr(min_length=2, max_length=50)
    password: constr(min_length=6)


class UserLogin(UserBase):
    password: constr(min_length=1)
    remember_me: bool = False
    totp_code: Optional[str] = None  # 6-digit 2FA code


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    created_at: datetime
    two_factor_enabled: bool = False  # Show 2FA status
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- 2FA / MFA ----------

class TwoFactorSetup(BaseModel):
    """Response for 2FA setup containing secret and QR code"""
    secret: str
    qr_code_url: str  # Data URL for QR code image
    backup_codes: Optional[List[str]] = None


class TwoFactorVerify(BaseModel):
    """Request to verify 2FA code"""
    code: constr(min_length=6, max_length=6)


class TwoFactorStatusOut(BaseModel):
    """2FA status for a user"""
    enabled: bool
    setup_required: bool = False


# ---------- SESSION MANAGEMENT ----------

class SessionOut(BaseModel):
    """Active session information"""
    id: int
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_active: datetime
    expires_at: datetime
    is_current: bool = False  # Set by API when listing sessions
    
    class Config:
        from_attributes = True


class SessionListOut(BaseModel):
    """List of active sessions"""
    current_session_id: int
    sessions: List[SessionOut]


# ---------- OAUTH ----------

class OAuthAccountOut(BaseModel):
    """Connected OAuth account"""
    id: int
    provider: str
    email: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ---------- PASSWORD STRENGTH ----------

class PasswordStrengthCheck(BaseModel):
    """Request to check password strength"""
    password: str


class PasswordStrengthOut(BaseModel):
    """Password strength analysis"""
    score: int  # 0-4 (0=very weak, 4=very strong)
    strength_text: str  # "Very Weak", "Weak", "Fair", "Strong", "Very Strong"
    feedback: List[str]  # Suggestions for improvement
    has_length: bool = False
    has_uppercase: bool = False
    has_lowercase: bool = False
    has_numbers: bool = False
    has_special: bool = False


# ---------- PREFERENCES ----------

class PreferenceBase(BaseModel):
    theme: str = "system"
    default_tab: str = "Dashboard"
    risk_profile: str = "balanced"


class PreferenceUpdate(PreferenceBase):
    pass


class PreferenceOut(PreferenceBase):
    id: int

    class Config:
        from_attributes = True


# ---------- WATCHLIST ----------

class WatchlistItemBase(BaseModel):
    asset_id: str
    user_id: Optional[int] = None
    target_price: Optional[float] = None
    direction: Optional[str] = None  # "above" / "below"


class WatchlistCreate(WatchlistItemBase):
    pass


class WatchlistItemOut(WatchlistItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- ASSETS ----------

class AssetHistory(BaseModel):
    day: str
    price: float
    commits: int


class Asset(BaseModel):
    id: str
    name: str
    symbol: str
    price: float
    change24h: float
    alphaScore: int
    repo: str
    velocity: int
    sentiment: str
    keywords: List[str]
    description: str
    history: List[AssetHistory]


# ---------- PORTFOLIO ----------

class TransactionBase(BaseModel):
    transaction_type: str  # "buy" or "sell"
    amount: float
    price: float
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    asset_id: str


class TransactionOut(TransactionBase):
    id: int
    portfolio_id: int
    total_value: float
    timestamp: datetime

    class Config:
        from_attributes = True


class PortfolioItemBase(BaseModel):
    asset_id: str
    amount: float
    avg_entry_price: float


class PortfolioItemOut(PortfolioItemBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Complete portfolio summary with analytics"""
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percentage: float
    holdings: List[dict]  # Detailed holdings
    top_performers: List[dict]
    worst_performers: List[dict]


# ---------- MARKETS ----------

class MarketBase(BaseModel):
    code: str
    name: str
    currency: str
    timezone: str


class MarketOut(MarketBase):
    id: int
    is_active: bool
    created_at: datetime
    indices_count: Optional[int] = 0

    class Config:
        from_attributes = True


class IndexBase(BaseModel):
    symbol: str
    name: str
    description: Optional[str] = None


class IndexOut(IndexBase):
    id: int
    market_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LiveMarketData(BaseModel):
    symbol: str
    name: str
    price: float
    open: float
    high: float
    low: float
    volume: float
    change_percent: float
    timestamp: datetime


class HistoricalDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    adj_close: Optional[float] = None


class HistoricalDataOut(BaseModel):
    symbol: str
    name: str
    period: str
    interval: str
    data: List[HistoricalDataPoint]


class IndicatorData(BaseModel):
    symbol: str
    period: str
    rsi: Optional[List[float]] = None
    macd: Optional[dict] = None  # {macd: [], signal: [], histogram: []}
    bollinger_bands: Optional[dict] = None  # {upper: [], middle: [], lower: []}
    sma: Optional[List[float]] = None
    ema: Optional[List[float]] = None


class MarketDetailOut(BaseModel):
    market: MarketOut
    indices: List[IndexOut]


# ---------- NEWS HUB ----------

class NewsArticleBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source_name: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None


class NewsArticleOut(NewsArticleBase):
    id: int
    published_at: datetime
    fetched_at: datetime
    summary: Optional[str] = None
    sentiment_score: Optional[float] = None
    impact_score: Optional[int] = None
    related_tickers: Optional[str] = None
    tags: Optional[str] = None

    class Config:
        from_attributes = True


class NewsArticleList(BaseModel):
    """Paginated list of news articles"""
    articles: List[NewsArticleOut]
    total: int
    page: int
    page_size: int


class UserBookmarkCreate(BaseModel):
    article_id: int
    notes: Optional[str] = None
    tags: Optional[str] = None


class UserBookmarkOut(BaseModel):
    id: int
    user_id: int
    article_id: int
    notes: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime
    article: Optional[NewsArticleOut] = None

    class Config:
        from_attributes = True


class NewsAlertCreate(BaseModel):
    article_id: int
    alert_type: str
    trigger_reason: Optional[str] = None


class NewsAlertOut(BaseModel):
    id: int
    user_id: int
    article_id: int
    alert_type: str
    trigger_reason: Optional[str] = None
    is_read: bool
    triggered_at: datetime
    article: Optional[NewsArticleOut] = None

    class Config:
        from_attributes = True


class NewsFetchRequest(BaseModel):
    """Request to fetch news from sources"""
    category: Optional[str] = None
    query: Optional[str] = None
    limit: int = 20


class NewsFilters(BaseModel):
    """Filters for news queries"""
    category: Optional[str] = None
    sentiment: Optional[str] = None  # positive, negative, neutral
    ticker: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


# ---------- PHASE 2: AI FEATURES ----------

class BatchAnalyzeRequest(BaseModel):
    """Request for batch article analysis"""
    article_ids: List[int]


class ArticleAnalytics(BaseModel):
    """Analytics result for a single article"""
    article_id: int
    sentiment_score: Optional[float] = None
    summary: Optional[str] = None
    tickers: List[str] = []
    impact_score: Optional[int] = None


class BatchAnalyzeResponse(BaseModel):
    """Response with analytics for multiple articles"""
    results: dict  # Maps article_id to ArticleAnalytics
    analyzed_count: int


class ClusterInfo(BaseModel):
    """Information about an article cluster"""
    cluster_id: int
    label: str
    size: int
    article_ids: List[int]
    articles: Optional[List[NewsArticleOut]] = None


class ClusteredArticlesResponse(BaseModel):
    """Articles grouped by clusters"""
    clusters: List[ClusterInfo]
    total_articles: int
    num_clusters: int


class TrendingTopic(BaseModel):
    """Trending topic with metadata"""
    topic: str
    score: float
    article_count: int


class TrendingTopicsResponse(BaseModel):
    """List of trending topics"""
    topics: List[TrendingTopic]
    period_days: int
    total_articles: int


# ---------- PHASE 3: PORTFOLIO INTEGRATION ----------

class PortfolioNewsResponse(BaseModel):
    """News filtered by user's portfolio"""
    articles: List[NewsArticleOut]
    portfolio_tickers: List[str]
    total_articles: int


class AlertCreateResponse(BaseModel):
    """Response when creating portfolio alerts"""
    created_alerts: int
    alert_ids: List[int]
    message: str


class NewsAlertsListResponse(BaseModel):
    """Response for listing user alerts"""
    alerts: List[NewsAlertOut]
    total: int
    unread_count: int


