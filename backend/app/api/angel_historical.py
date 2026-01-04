"""
Angel One Historical Data API Endpoints
Provides REST API for fetching historical OHLCV candle data
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.auth import get_current_user
from app.models import User
from app.db import get_db
from app.services.angel_one_historical_service import angel_one_historical_service


router = APIRouter(prefix="/api/angel-historical", tags=["Angel One Historical"])


class CandleResponse(BaseModel):
    """Response model for candle data"""
    success: bool
    data: List[Dict]
    cached: bool = False
    error: Optional[str] = None


class IntervalInfo(BaseModel):
    """Interval metadata"""
    value: str
    display: str
    minutes: int
    max_days: int


@router.get("/candles", response_model=CandleResponse)
async def get_candles(
    exchange: str = Query(..., description="Exchange (NSE, BSE, NFO)"),
    symboltoken: str = Query(..., description="Symbol token"),
    interval: str = Query(..., description="Interval (ONE_MINUTE, ONE_DAY, etc.)"),
    from_date: str = Query(..., description="Start date (YYYY-MM-DD HH:MM)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD HH:MM)"),
    trading_symbol: Optional[str] = Query(None, description="Trading symbol name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch historical candle data for a symbol
    
    Example:
        /api/angel-historical/candles?exchange=NSE&symboltoken=3045&interval=ONE_DAY&from_date=2024-01-01 00:00&to_date=2024-12-31 23:59
    """
    try:
        result = angel_one_historical_service.get_candles(
            db=db,
            user_id=current_user.id,
            exchange=exchange,
            symboltoken=symboltoken,
            interval=interval,
            from_date=from_date,
            to_date=to_date,
            trading_symbol=trading_symbol
        )
        
        return CandleResponse(
            success=result['success'],
            data=result.get('data', []),
            cached=result.get('cached', False),
            error=result.get('error')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch candles: {str(e)}"
        )


@router.get("/intervals", response_model=List[IntervalInfo])
async def get_intervals(current_user: User = Depends(get_current_user)):
    """
    Get list of supported intervals with metadata
    
    Returns information about available timeframes and their limitations
    """
    return angel_one_historical_service.get_intervals()


@router.get("/quick-range/{range_type}")
async def get_quick_range(
    range_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get date range for common timeframes
    
    Args:
        range_type: 1D, 1W, 1M, 3M, 6M, 1Y, 5Y
    
    Returns:
        from_date and to_date in YYYY-MM-DD HH:MM format
    """
    now = datetime.now()
    
    ranges = {
        "1D": timedelta(days=1),
        "1W": timedelta(weeks=1),
        "1M": timedelta(days=30),
        "3M": timedelta(days=90),
        "6M": timedelta(days=180),
        "1Y": timedelta(days=365),
        "5Y": timedelta(days=1825),
    }
    
    if range_type not in ranges:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid range_type. Must be one of: {', '.join(ranges.keys())}"
        )
    
    from_date = now - ranges[range_type]
    
    return {
        "from_date": from_date.strftime("%Y-%m-%d %H:%M"),
        "to_date": now.strftime("%Y-%m-%d %H:%M"),
        "range_type": range_type
    }


@router.delete("/cache/{symboltoken}")
async def clear_cache(
    symboltoken: str,
    interval: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear cached candle data for a symbol
    
    Args:
        symboltoken: Symbol token to clear cache for
        interval: Optional specific interval to clear (clears all if not specified)
    """
    try:
        from app.models import AngelOneCandle
        
        query = db.query(AngelOneCandle).filter(
            AngelOneCandle.user_id == current_user.id,
            AngelOneCandle.symboltoken == symboltoken
        )
        
        if interval:
            query = query.filter(AngelOneCandle.interval == interval)
        
        deleted_count = query.delete()
        db.commit()
        
        return {
            "success": True,
            "message": f"Cleared {deleted_count} cached candles",
            "symboltoken": symboltoken,
            "interval": interval
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/analytics/{symboltoken}")
async def get_symbol_analytics(
    symboltoken: str,
    exchange: str = Query("NSE", description="Exchange (NSE, BSE, NFO)"),
    interval: str = Query("ONE_DAY", description="Interval for analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for a symbol including:
    - BUY/HOLD/SELL signal
    - Technical indicators (RSI, MACD, Moving Averages)
    - Trend analysis
    - Support/Resistance levels
    - Performance metrics
    
    Example:
        /api/angel-historical/analytics/3045?exchange=NSE&interval=ONE_DAY
    """
    try:
        from app.services.symbol_analytics_service import symbol_analytics_service
        
        # Fetch recent candles for analysis (last 200 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=200)
        
        result = angel_one_historical_service.get_candles(
            db=db,
            user_id=current_user.id,
            exchange=exchange,
            symboltoken=symboltoken,
            interval=interval,
            from_date=from_date.strftime("%Y-%m-%d %H:%M"),
            to_date=to_date.strftime("%Y-%m-%d %H:%M"),
            trading_symbol=None
        )
        
        if not result['success'] or not result.get('data'):
            return {
                "success": False,
                "error": "Failed to fetch historical data for analysis"
            }
        
        # Perform analytics
        analytics = symbol_analytics_service.analyze_symbol(result['data'])
        
        return {
            "success": True,
            "symboltoken": symboltoken,
            "exchange": exchange,
            "interval": interval,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics: {str(e)}"
        )
