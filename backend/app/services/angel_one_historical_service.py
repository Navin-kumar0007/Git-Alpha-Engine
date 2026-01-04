"""
Angel One Historical Data Service
Fetches and caches historical OHLCV candle data
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from smart_auth import SmartAuth
from app import models
import json


class AngelOneHistoricalService:
    """Service to fetch and cache historical candle data from Angel One"""
    
    _instance = None
    
    # Supported intervals
    INTERVALS = {
        "ONE_MINUTE": {"display": "1 Minute", "minutes": 1, "max_days": 30},
        "THREE_MINUTE": {"display": "3 Minutes", "minutes": 3, "max_days": 2000},
        "FIVE_MINUTE": {"display": "5 Minutes", "minutes": 5, "max_days": 2000},
        "TEN_MINUTE": {"display": "10 Minutes", "minutes": 10, "max_days": 2000},
        "FIFTEEN_MINUTE": {"display": "15 Minutes", "minutes": 15, "max_days": 2000},
        "THIRTY_MINUTE": {"display": "30 Minutes", "minutes": 30, "max_days": 2000},
        "ONE_HOUR": {"display": "1 Hour", "minutes": 60, "max_days": 2000},
        "ONE_DAY": {"display": "1 Day", "minutes": 1440, "max_days": 2000},
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.auth = SmartAuth()
            self.smart_api = None
            self.authenticated = False
            self.cache_duration = 3600  # 1 hour cache duration
            self.initialized = True
    
    def authenticate(self) -> bool:
        """Authenticate with Angel One API"""
        try:
            login_data = self.auth.login()
            if login_data['status']:
                self.smart_api = self.auth.get_instance()
                self.authenticated = True
                print("[Angel One Historical] Authentication successful")
                return True
            else:
                print(f"[Angel One Historical] Login failed: {login_data['message']}")
                return False
        except Exception as e:
            print(f"[Angel One Historical] Authentication error: {e}")
            return False
    
    def ensure_authenticated(self) -> bool:
        """Ensure we have valid authentication"""
        if not self.authenticated:
            return self.authenticate()
        return True
    
    def get_candles(
        self,
        db: Session,
        user_id: int,
        exchange: str,
        symboltoken: str,
        interval: str,
        from_date: str,
        to_date: str,
        trading_symbol: Optional[str] = None
    ) -> Dict:
        """
        Fetch historical candle data with intelligent caching
        
        Args:
            exchange: NSE, BSE, NFO, etc.
            symboltoken: Symbol token (e.g., "3045" for RELIANCE)
            interval: ONE_MINUTE, FIVE_MINUTE, etc.
            from_date: Start date (YYYY-MM-DD HH:MM)
            to_date: End date (YYYY-MM-DD HH:MM)
            trading_symbol: Optional trading symbol name
        
        Returns:
            Dict with success status and candle data
        """
        
        # Validate interval
        if interval not in self.INTERVALS:
            return {
                "success": False,
                "error": f"Invalid interval. Must be one of: {', '.join(self.INTERVALS.keys())}"
            }
        
        # Check cache first
        cached_data = self._get_cached_candles(db, symboltoken, interval, from_date, to_date)
        if cached_data:
            print(f"[Angel One Historical] Using cached candles for {symboltoken} ({interval})")
            return {
                "success": True,
                "data": cached_data,
                "cached": True
            }
        
        # Fetch from API
        if not self.ensure_authenticated():
            return {
                "success": False,
                "error": "Failed to authenticate with Angel One"
            }
        
        try:
            # Prepare parameters
            params = {
                "exchange": exchange,
                "symboltoken": symboltoken,
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date
            }
            
            print(f"[Angel One Historical] Fetching candles: {params}")
            
            # Call Angel One API
            response = self.smart_api.getCandleData(params)
            
            if not response or response.get('status') is False:
                error_msg = response.get('message', 'Failed to fetch candles') if response else 'No response from API'
                print(f"[Angel One Historical] API error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            # Extract candle data
            candles_raw = response.get('data', [])
            
            if not candles_raw:
                print(f"[Angel One Historical] No candle data returned")
                return {
                    "success": True,
                    "data": [],
                    "cached": False
                }
            
            # Process and cache candles
            candles = self._process_candles(candles_raw)
            self._cache_candles(db, user_id, exchange, symboltoken, interval, candles, trading_symbol)
            
            print(f"[Angel One Historical] Fetched and cached {len(candles)} candles")
            
            return {
                "success": True,
                "data": candles,
                "cached": False
            }
            
        except Exception as e:
            print(f"[Angel One Historical] Error fetching candles: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_candles(self, candles_raw: List) -> List[Dict]:
        """
        Process raw candle data from Angel One API
        
        Angel One returns data as: [timestamp, open, high, low, close, volume]
        """
        candles = []
        for candle in candles_raw:
            try:
                candles.append({
                    "timestamp": candle[0],  # ISO format timestamp
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": int(candle[5]) if len(candle) > 5 else 0
                })
            except (IndexError, ValueError) as e:
                print(f"[Angel One Historical] Error processing candle: {e}")
                continue
        
        return candles
    
    def _cache_candles(
        self,
        db: Session,
        user_id: int,
        exchange: str,
        symboltoken: str,
        interval: str,
        candles: List[Dict],
        trading_symbol: Optional[str] = None
    ):
        """Cache candles in database"""
        try:
            # Delete existing candles for this symbol/interval in the date range
            if candles:
                first_ts = datetime.fromisoformat(candles[0]['timestamp'].replace('Z', '+00:00'))
                last_ts = datetime.fromisoformat(candles[-1]['timestamp'].replace('Z', '+00:00'))
                
                db.query(models.AngelOneCandle).filter(
                    models.AngelOneCandle.user_id == user_id,
                    models.AngelOneCandle.symboltoken == symboltoken,
                    models.AngelOneCandle.interval == interval,
                    models.AngelOneCandle.timestamp >= first_ts,
                    models.AngelOneCandle.timestamp <= last_ts
                ).delete()
            
            # Insert new candles
            for candle in candles:
                candle_obj = models.AngelOneCandle(
                    user_id=user_id,
                    symboltoken=symboltoken,
                    exchange=exchange,
                    trading_symbol=trading_symbol,
                    timestamp=datetime.fromisoformat(candle['timestamp'].replace('Z', '+00:00')),
                    open_price=candle['open'],
                    high=candle['high'],
                    low=candle['low'],
                    close=candle['close'],
                    volume=candle['volume'],
                    interval=interval
                )
                db.add(candle_obj)
            
            db.commit()
            print(f"[Angel One Historical] Cached {len(candles)} candles")
            
        except Exception as e:
            db.rollback()
            print(f"[Angel One Historical] Error caching candles: {e}")
    
    def _get_cached_candles(
        self,
        db: Session,
        symboltoken: str,
        interval: str,
        from_date: str,
        to_date: str
    ) -> Optional[List[Dict]]:
        """Retrieve cached candles from database"""
        try:
            # Parse dates
            from_dt = datetime.strptime(from_date, "%Y-%m-%d %H:%M")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d %H:%M")
            
            # Check if cache is fresh (within cache_duration)
            cache_cutoff = datetime.utcnow() - timedelta(seconds=self.cache_duration)
            
            # Query cached candles
            candles = db.query(models.AngelOneCandle).filter(
                models.AngelOneCandle.symboltoken == symboltoken,
                models.AngelOneCandle.interval == interval,
                models.AngelOneCandle.timestamp >= from_dt,
                models.AngelOneCandle.timestamp <= to_dt,
                models.AngelOneCandle.fetched_at >= cache_cutoff
            ).order_by(models.AngelOneCandle.timestamp).all()
            
            if not candles:
                return None
            
            # Convert to dict format
            return [{
                "timestamp": c.timestamp.isoformat() + "Z",
                "open": c.open_price,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume
            } for c in candles]
            
        except Exception as e:
            print(f"[Angel One Historical] Error retrieving cached candles: {e}")
            return None
    
    def get_intervals(self) -> List[Dict]:
        """Get list of supported intervals"""
        return [
            {
                "value": key,
                "display": value["display"],
                "minutes": value["minutes"],
                "max_days": value["max_days"]
            }
            for key, value in self.INTERVALS.items()
        ]


# Global singleton instance
angel_one_historical_service = AngelOneHistoricalService()
