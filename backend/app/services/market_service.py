"""Market Data Service

Fetches real-time and historical market data using Yahoo Finance.
Implements caching to reduce API calls.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import Market, MarketIndex, MarketData, HistoricalData
from .indicator_service import calculate_all_indicators


# Market indices configuration
MARKET_INDICES = {
    "IN": [
        {"symbol": "^NSEI", "name": "NIFTY 50", "description": "India's premier stock market index"},
        {"symbol": "^BSESN", "name": "SENSEX", "description": "BSE Sensex 30 companies"},
        {"symbol": "^NSEBANK", "name": "BANK NIFTY", "description": "Banking sector index"}
    ],
    "US": [
        {"symbol": "^GSPC", "name": "S&P 500", "description": "500 largest US companies"},
        {"symbol": "^IXIC", "name": "NASDAQ", "description": "Technology-heavy composite"},
        {"symbol": "^DJI", "name": "DOW JONES", "description": "30 significant US stocks"}
    ],
    "UK": [
        {"symbol": "^FTSE", "name": "FTSE 100", "description": "100 largest UK companies"}
    ],
    "JP": [
        {"symbol": "^N225", "name": "NIKKEI 225", "description": "Tokyo Stock Exchange index"}
    ],
    "SG": [
        {"symbol": "^STI", "name": "STI", "description": "Singapore Straits Times Index"}
    ]
}

MARKETS_CONFIG = {
    "IN": {"name": "India", "currency": "INR", "timezone": "Asia/Kolkata"},
    "US": {"name": "United States", "currency": "USD", "timezone": "America/New_York"},
    "UK": {"name": "United Kingdom", "currency": "GBP", "timezone": "Europe/London"},
    "JP": {"name": "Japan", "currency": "JPY", "timezone": "Asia/Tokyo"},
    "SG": {"name": "Singapore", "currency": "SGD", "timezone": "Asia/Singapore"}
}


def get_live_market_data(symbol: str) -> Optional[Dict]:
    """
    Fetch real-time market data for a symbol
    
    Args:
        symbol: Yahoo Finance symbol (e.g., "^GSPC")
        
    Returns:
        Dictionary with current market data or None if failed
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price data
        hist = ticker.history(period="1d", interval="1m")
        
        if hist.empty:
            return None
        
        current = hist.iloc[-1]
        open_price = hist.iloc[0]['Open']
        
        change_percent = ((current['Close'] - open_price) / open_price) * 100
        
        return {
            "price": float(current['Close']),
            "open": float(open_price),
            "high": float(hist['High'].max()),
            "low": float(hist['Low'].min()),
            "volume": float(hist['Volume'].sum()),
            "change_percent": float(change_percent),
            "timestamp": datetime.now()
        }
    except Exception as e:
        print(f"Error fetching live data for {symbol}: {e}")
        return None


def get_historical_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
) -> Optional[List[Dict]]:
    """
    Fetch historical OHLCV data
    
    Args:
        symbol: Yahoo Finance symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
    Returns:
        List of historical data points or None if failed
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return None
        
        data = []
        for index, row in hist.iterrows():
            data.append({
                "date": index.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": float(row['Volume']),
                "adj_close": float(row.get('Close', row['Close']))
            })
        
        return data
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return None


def get_cached_market_data(db: Session, index_id: int, cache_minutes: int = 5) -> Optional[MarketData]:
    """
    Get cached market data if available and fresh
    
    Args:
        db: Database session
        index_id: Market index ID
        cache_minutes: Cache validity in minutes
        
    Returns:
        MarketData object or None
    """
    cache_time = datetime.now() - timedelta(minutes=cache_minutes)
    
    cached = db.query(MarketData).filter(
        MarketData.index_id == index_id,
        MarketData.timestamp >= cache_time
    ).order_by(desc(MarketData.timestamp)).first()
    
    return cached


def update_market_data(db: Session, index_id: int, symbol: str) -> Optional[MarketData]:
    """
    Fetch and update market data in database
    
    Args:
        db: Database session
        index_id: Market index ID
        symbol: Yahoo Finance symbol
        
    Returns:
        Updated MarketData object or None
    """
    live_data = get_live_market_data(symbol)
    
    if not live_data:
        return None
    
    market_data = MarketData(
        index_id=index_id,
        price=live_data["price"],
        open_price=live_data["open"],
        high=live_data["high"],
        low=live_data["low"],
        volume=live_data["volume"],
        change_percent=live_data["change_percent"],
        timestamp=live_data["timestamp"]
    )
    
    db.add(market_data)
    db.commit()
    db.refresh(market_data)
    
    return market_data


def store_historical_data(db: Session, index_id: int, symbol: str, period: str = "1y") -> int:
    """
    Fetch and store historical data in database
    
    Args:
        db: Database session
        index_id: Market index ID
        symbol: Yahoo Finance symbol
        period: Time period to fetch
        
    Returns:
        Number of records stored
    """
    hist_data = get_historical_data(symbol, period=period, interval="1d")
    
    if not hist_data:
        return 0
    
    # Delete existing data for this index
    db.query(HistoricalData).filter(HistoricalData.index_id == index_id).delete()
    
    # Store new data
    count = 0
    for point in hist_data:
        historical = HistoricalData(
            index_id=index_id,
            date=datetime.fromisoformat(point["date"]),
            open_price=point["open"],
            high=point["high"],
            low=point["low"],
            close=point["close"],
            volume=point["volume"],
            adj_close=point["adj_close"]
        )
        db.add(historical)
        count += 1
    
    db.commit()
    return count


def seed_markets(db: Session) -> None:
    """
    Seed initial market and index data
    
    Args:
        db: Database session
    """
    for code, config in MARKETS_CONFIG.items():
        # Check if market exists
        market = db.query(Market).filter(Market.code == code).first()
        
        if not market:
            market = Market(
                code=code,
                name=config["name"],
                currency=config["currency"],
                timezone=config["timezone"]
            )
            db.add(market)
            db.commit()
            db.refresh(market)
            print(f"Created market: {market.name}")
        
        # Seed indices for this market
        for idx_config in MARKET_INDICES.get(code, []):
            index = db.query(MarketIndex).filter(
                MarketIndex.symbol == idx_config["symbol"]
            ).first()
            
            if not index:
                index = MarketIndex(
                    market_id=market.id,
                    symbol=idx_config["symbol"],
                    name=idx_config["name"],
                    description=idx_config["description"]
                )
                db.add(index)
                db.commit()
                db.refresh(index)
                print(f"Created index: {index.name} ({index.symbol})")
                
                # Fetch initial historical data
                count = store_historical_data(db, index.id, index.symbol, period="1y")
                print(f"  Stored {count} historical data points")


def get_market_indicators(
    db: Session,
    index_id: int,
    period: str = "3mo",
    indicators: List[str] = None
) -> Dict:
    """
    Calculate technical indicators for a market index
    
    Args:
        db: Database session
        index_id: Market index ID
        period: Time period for calculation
        indicators: List of indicator names
        
    Returns:
        Dictionary with indicator values
    """
    if indicators is None:
        indicators = ["rsi", "macd", "bb", "sma", "ema"]
    
    # Get historical data
    historical = db.query(HistoricalData).filter(
        HistoricalData.index_id == index_id
    ).order_by(HistoricalData.date).all()
    
    if not historical:
        return {}
    
    # Extract closing prices
    prices = [h.close for h in historical]
    
    # Calculate indicators
    return calculate_all_indicators(prices, indicators)
