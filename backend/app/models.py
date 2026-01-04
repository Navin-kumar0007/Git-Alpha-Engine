from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 2FA/MFA fields
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)  # Encrypted TOTP secret

    # Relationships
    watchlist = relationship(
        "Watchlist",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    preferences = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    alerts = relationship(
        "Alert",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    portfolio_items = relationship(
        "Portfolio",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    oauth_accounts = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(String, nullable=False)
    target_price = Column(Float, nullable=True)
    direction = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    sentiment = Column(String, default="neutral")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    theme = Column(String, default="system")            # light/dark/system
    default_tab = Column(String, default="Dashboard")   # Dashboard/Signals/Watchlist
    risk_profile = Column(String, default="balanced")   # conservative/balanced/aggressive

    user = relationship("User", back_populates="preferences")


# ========================================
# Portfolio Management Models
# ========================================

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(String, nullable=False)  # e.g., "bitcoin", "ethereum"
    
    # Holdings
    amount = Column(Float, nullable=False, default=0.0)  # Amount of asset held
    avg_entry_price = Column(Float, nullable=False)  # Average entry price
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="portfolio_items")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(String, nullable=False)  # "buy" or "sell"
    amount = Column(Float, nullable=False)  # Quantity
    price = Column(Float, nullable=False)  # Price at transaction
    total_value = Column(Float, nullable=False)  # amount * price
    
    # Optional
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    portfolio = relationship("Portfolio", back_populates="transactions")


# ========================================
# Multi-Market Models
# ========================================

class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)  # e.g., "IN", "US", "UK"
    name = Column(String, nullable=False)  # e.g., "India", "United States"
    currency = Column(String, nullable=False)  # e.g., "INR", "USD"
    timezone = Column(String, nullable=False)  # e.g., "Asia/Kolkata"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    indices = relationship("MarketIndex", back_populates="market", cascade="all, delete-orphan")


class MarketIndex(Base):
    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    symbol = Column(String, unique=True, nullable=False)  # Yahoo Finance symbol
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    market = relationship("Market", back_populates="indices")
    market_data = relationship("MarketData", back_populates="index", cascade="all, delete-orphan")
    historical_data = relationship("HistoricalData", back_populates="index", cascade="all, delete-orphan")


class MarketData(Base):
    """Real-time market data with caching"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    index_id = Column(Integer, ForeignKey("market_indices.id"), nullable=False)
    price = Column(Float, nullable=False)
    open_price = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship
    index = relationship("MarketIndex", back_populates="market_data")


class HistoricalData(Base):
    """OHLCV historical data for charting"""
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True)
    index_id = Column(Integer, ForeignKey("market_indices.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=True)

    # Relationship
    index = relationship("MarketIndex", back_populates="historical_data")


# ========================================
# Authentication & Security Models
# ========================================

class Session(Base):
    """Track active user sessions for security and management"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_jti = Column(String, unique=True, nullable=False)  # JWT ID for token tracking
    device_info = Column(String, nullable=True)  # Browser/device information
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationship
    user = relationship("User", back_populates="sessions")


class OAuthAccount(Base):
    """Link OAuth provider accounts to users"""
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # "google" or "github"
    provider_user_id = Column(String, nullable=False)  # OAuth provider's user ID
    email = Column(String, nullable=True)
    access_token = Column(String, nullable=True)  # Encrypted
    refresh_token = Column(String, nullable=True)  # Encrypted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="oauth_accounts")


# ========================================
# News & Research Hub Models
# ========================================

class NewsArticle(Base):
    """News articles aggregated from NewsAPI and RSS feeds"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    
    # Article content
    title = Column(String(500), nullable=False)
    description = Column(String, nullable=True)
    content = Column(String, nullable=True)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    image_url = Column(String(1000), nullable=True)
    
    # Source information
    source_name = Column(String(100), nullable=True)
    source_id = Column(String(100), nullable=True)
    author = Column(String(200), nullable=True)
    
    # Timestamps
    published_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # AI-generated fields
    summary = Column(String, nullable=True)  # AI-generated summary
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    impact_score = Column(Integer, nullable=True)  # 1-10 scale
    
    # Categorization
    category = Column(String(50), nullable=True)  # business, technology, etc.
    related_tickers = Column(String, nullable=True)  # JSON array as string: '["AAPL","MSFT"]'
    tags = Column(String, nullable=True)  # JSON array as string: '["tech","ai"]'
    
    # Relationships
    bookmarks = relationship("UserBookmark", back_populates="article", cascade="all, delete-orphan")
    alerts = relationship("NewsAlert", back_populates="article", cascade="all, delete-orphan")


class UserBookmark(Base):
    """User's saved articles / reading list"""
    __tablename__ = "user_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)
    
    # User notes
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # User's custom tags JSON array
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    article = relationship("NewsArticle", back_populates="bookmarks")


class NewsAlert(Base):
    """News alerts triggered for users"""
    __tablename__ = "news_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)
    
    # Alert metadata
    alert_type = Column(String(50), nullable=False)  # portfolio_impact, keyword, ticker
    trigger_reason = Column(String, nullable=True)  # Why this alert was triggered
    
    # Status
    is_read = Column(Boolean, default=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    article = relationship("NewsArticle", back_populates="alerts")


# ========================================
# Angel One - Live Market Data Models
# ========================================

class PriceAlert(Base):
    """User-defined price alerts for live market data"""
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Target
    token = Column(String, nullable=False)  # Angel One token (e.g., "26000" for NIFTY)
    symbol_name = Column(String, nullable=False)  # Human-readable name (e.g., "NIFTY 50")
    
    # Alert condition
    alert_type = Column(String, nullable=False)  # "above", "below", "percentage_change"
    target_price = Column(Float, nullable=True)  # For above/below alerts
    percentage = Column(Float, nullable=True)  # For percentage change alerts
    
    # Status
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User")


class TradingSignal(Base):
    """AI-generated trading signals based on live data"""
    __tablename__ = "trading_signals"

    id = Column(Integer, primary_key=True, index=True)
    
    # Target
    token = Column(String, nullable=False)
    symbol_name = Column(String, nullable=False)
    
    # Signal details
    signal_type = Column(String, nullable=False)  # "buy", "sell", "hold"
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    reasoning = Column(String, nullable=True)  # AI-generated explanation
    
    # Technical indicators (JSON stored as string)
    indicators = Column(String, nullable=True)  # e.g., '{"RSI": 65, "MACD": "bullish"}'
    
    # Price context
    price_at_signal = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class MarketDataSnapshot(Base):
    """Periodic snapshots of market data for analysis"""
    __tablename__ = "market_data_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    
    # Target
    token = Column(String, nullable=False, index=True)
    symbol_name = Column(String, nullable=False)
    
    # Price data (stored in rupees)
    last_traded_price = Column(Float, nullable=False)
    open_price = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    
    # Metadata
    exchange_type = Column(Integer, nullable=False)  # 1=NSE, 2=BSE, etc
    subscription_mode = Column(Integer, nullable=False)  # 1=LTP, 3=Full
    
    # Timestamp
    exchange_timestamp = Column(DateTime, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow, index=True)


# ========================================
# Angel One - Portfolio Sync Models
# ========================================

class AngelOneHolding(Base):
    """Cache of Angel One holdings (Demat holdings)"""
    __tablename__ = "angel_one_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Angel One data
    trading_symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    isin = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)
    ltp = Column(Float, nullable=False)  # Last traded price
    pnl = Column(Float, nullable=False)  # Profit/Loss
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User")


class AngelOnePosition(Base):
    """Cache of Angel One positions (Intraday/Delivery)"""
    __tablename__ = "angel_one_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Position data
    trading_symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    product_type = Column(String, nullable=False)  # INTRADAY, DELIVERY, etc.
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)
    ltp = Column(Float, nullable=False)
    pnl = Column(Float, nullable=False)
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User")


class AngelOneFunds(Base):
    """Cache of Angel One funds/margins"""
    __tablename__ = "angel_one_funds"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Fund data
    available_cash = Column(Float, nullable=False, default=0.0)
    used_margin = Column(Float, nullable=False, default=0.0)
    available_margin = Column(Float, nullable=False, default=0.0)
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User")


# ========================================
# Angel One - Historical Data Models
# ========================================

class AngelOneCandle(Base):
    """Historical OHLCV candle data from Angel One"""
    __tablename__ = "angel_one_candles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Symbol info
    symboltoken = Column(String, nullable=False, index=True)
    exchange = Column(String, nullable=False)  # NSE, BSE, NFO
    trading_symbol = Column(String, nullable=True)
    
    # Candle data (OHLCV)
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
    # Metadata
    interval = Column(String, nullable=False)  # ONE_MINUTE, FIVE_MINUTE, etc.
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User")
    
    # Composite index for fast lookups
    __table_args__ = (
        Index('ix_candles_lookup', 'symboltoken', 'interval', 'timestamp'),
    )

