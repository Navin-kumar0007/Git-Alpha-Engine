"""Markets API Router

Provides endpoints for multi-market data access:
- List markets and indices
- Real-time market data
- Historical OHLCV data
- Technical indicators
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..db import get_db
from ..models import Market, MarketIndex, HistoricalData
from ..schemas import (
    MarketOut,
    MarketDetailOut,
    IndexOut,
    LiveMarketData,
    HistoricalDataOut,
    HistoricalDataPoint,
    IndicatorData
)
from ..services.market_service import (
    get_cached_market_data,
    update_market_data,
    get_historical_data,
    get_market_indicators,
    seed_markets
)

router = APIRouter(prefix="/api/markets", tags=["Markets"])


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "markets",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/seed")
def seed_market_data(db: Session = Depends(get_db)):
    """Seed initial market and index data (Admin only)"""
    try:
        seed_markets(db)
        return {"status": "success", "message": "Markets and indices seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")


@router.get("/", response_model=List[MarketOut])
def get_all_markets(db: Session = Depends(get_db)):
    """Get all supported markets"""
    markets = db.query(Market).filter(Market.is_active == True).all()
    
    # Add indices count
    result = []
    for market in markets:
        market_dict = {
            "id": market.id,
            "code": market.code,
            "name": market.name,
            "currency": market.currency,
            "timezone": market.timezone,
            "is_active": market.is_active,
            "created_at": market.created_at,
            "indices_count": len(market.indices)
        }
        result.append(market_dict)
    
    return result


@router.get("/{market_code}", response_model=MarketDetailOut)
def get_market_detail(market_code: str, db: Session = Depends(get_db)):
    """Get specific market with its indices"""
    market = db.query(Market).filter(
        Market.code == market_code.upper(),
        Market.is_active == True
    ).first()
    
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    return {
        "market": market,
        "indices": market.indices
    }


@router.get("/{market_code}/indices", response_model=List[IndexOut])
def get_market_indices(market_code: str, db: Session = Depends(get_db)):
    """Get all indices for a market"""
    market = db.query(Market).filter(
        Market.code == market_code.upper()
    ).first()
    
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    indices = db.query(MarketIndex).filter(
        MarketIndex.market_id == market.id,
        MarketIndex.is_active == True
    ).all()
    
    return indices



@router.get("/index/{symbol}/live", response_model=LiveMarketData)
def get_live_data(
    symbol: str,
    force_refresh: bool = Query(False, description="Force refresh cache"),
    db: Session = Depends(get_db)
):
    """Get real-time market data for an index (cached for 5 minutes)"""
    # Find the index
    index = db.query(MarketIndex).filter(
        MarketIndex.symbol == symbol.upper()
    ).first()
    
    if not index:
        raise HTTPException(status_code=404, detail="Index not found")
    
    # Check cache unless force refresh
    if not force_refresh:
        cached = get_cached_market_data(db, index.id, cache_minutes=5)
        if cached:
            return LiveMarketData(
                symbol=index.symbol,
                name=index.name,
                price=cached.price,
                open=cached.open_price,
                high=cached.high,
                low=cached.low,
                volume=cached.volume,
                change_percent=cached.change_percent,
                timestamp=cached.timestamp
            )
    
    # Fetch fresh data
    market_data = update_market_data(db, index.id, index.symbol)
    
    if not market_data:
        raise HTTPException(status_code=503, detail="Failed to fetch market data")
    
    return LiveMarketData(
        symbol=index.symbol,
        name=index.name,
        price=market_data.price,
        open=market_data.open_price,
        high=market_data.high,
        low=market_data.low,
        volume=market_data.volume,
        change_percent=market_data.change_percent,
        timestamp=market_data.timestamp
    )


@router.get("/index/{symbol}/historical", response_model=HistoricalDataOut)
def get_historical(
    symbol: str,
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y"),
    interval: str = Query("1d", description="Interval: 1m, 5m, 15m, 1h, 1d, 1wk"),
    db: Session = Depends(get_db)
):
    """Get historical OHLCV data"""
    # Find the index
    index = db.query(MarketIndex).filter(
        MarketIndex.symbol == symbol.upper()
    ).first()
    
    if not index:
        raise HTTPException(status_code=404, detail="Index not found")
    
    # For daily data, try to use database first
    if interval == "1d":
        historical = db.query(HistoricalData).filter(
            HistoricalData.index_id == index.id
        ).order_by(HistoricalData.date.desc()).limit(
            365 if period == "1y" else 90 if period == "3mo" else 30
        ).all()
        
        if historical:
            data_points = [
                HistoricalDataPoint(
                    date=h.date.isoformat(),
                    open=h.open_price,
                    high=h.high,
                    low=h.low,
                    close=h.close,
                    volume=h.volume,
                    adj_close=h.adj_close
                )
                for h in reversed(historical)
            ]
            
            return HistoricalDataOut(
                symbol=index.symbol,
                name=index.name,
                period=period,
                interval=interval,
                data=data_points
            )
    
    # Fetch from Yahoo Finance
    hist_data = get_historical_data(index.symbol, period=period, interval=interval)
    
    if not hist_data:
        raise HTTPException(status_code=503, detail="Failed to fetch historical data")
    
    data_points = [HistoricalDataPoint(**point) for point in hist_data]
    
    return HistoricalDataOut(
        symbol=index.symbol,
        name=index.name,
        period=period,
        interval=interval,
        data=data_points
    )


@router.get("/index/{symbol}/indicators", response_model=IndicatorData)
def get_indicators(
    symbol: str,
    period: str = Query("3mo", description="Period for calculation"),
    indicators: str = Query("rsi,macd,bb,sma,ema", description="Comma-separated indicators"),
    db: Session = Depends(get_db)
):
    """Calculate technical indicators"""
    # Find the index
    index = db.query(MarketIndex).filter(
        MarketIndex.symbol == symbol.upper()
    ).first()
    
    if not index:
        raise HTTPException(status_code=404, detail="Index not found")
    
    # Parse indicators
    indicator_list = [i.strip() for i in indicators.split(",")]
    
    # Calculate indicators
    indicator_values = get_market_indicators(
        db,
        index.id,
        period=period,
        indicators=indicator_list
    )
    
    if not indicator_values:
        raise HTTPException(status_code=404, detail="No historical data available")
    
    return IndicatorData(
        symbol=index.symbol,
        period=period,
        **indicator_values
    )

