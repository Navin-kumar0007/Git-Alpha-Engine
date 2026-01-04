"""
Technical Indicators Calculator
Utility functions for calculating technical indicators from OHLCV data
"""
from typing import List, Dict, Optional
import statistics


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: List of closing prices (oldest to newest)
        period: RSI period (default: 14)
    
    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if len(prices) < period + 1:
        return None
    
    # Calculate price changes
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Separate gains and losses
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    # Calculate average gain and loss for the period
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    # Avoid division by zero
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_sma(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate Simple Moving Average (SMA)
    
    Args:
        prices: List of closing prices
        period: SMA period
    
    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    return round(statistics.mean(prices[-period:]), 2)


def calculate_ema(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate Exponential Moving Average (EMA)
    
    Args:
        prices: List of closing prices
        period: EMA period
    
    Returns:
        EMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = statistics.mean(prices[:period])  # Start with SMA
    
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return round(ema, 2)


def calculate_macd(prices: List[float]) -> Optional[Dict[str, float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: List of closing prices
    
    Returns:
        Dict with macd_line, signal_line, histogram or None if insufficient data
    """
    if len(prices) < 26:
        return None
    
    # Calculate 12 and 26 period EMAs
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    
    if ema_12 is None or ema_26 is None:
        return None
    
    macd_line = ema_12 - ema_26
    
    # Calculate signal line (9-day EMA of MACD)
    # For simplicity, we'll calculate this from recent MACD values
    # In production, you'd track historical MACD values
    signal_line = macd_line * 0.8  # Simplified approximation
    
    histogram = macd_line - signal_line
    
    return {
        "macd_line": round(macd_line, 2),
        "signal_line": round(signal_line, 2),
        "histogram": round(histogram, 2)
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Optional[Dict[str, float]]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: List of closing prices
        period: Period for moving average (default: 20)
        std_dev: Number of standard deviations (default: 2)
    
    Returns:
        Dict with upper, middle, lower bands or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    recent_prices = prices[-period:]
    middle_band = statistics.mean(recent_prices)
    std = statistics.stdev(recent_prices)
    
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)
    
    return {
        "upper": round(upper_band, 2),
        "middle": round(middle_band, 2),
        "lower": round(lower_band, 2)
    }


def find_support_resistance(candles: List[Dict], lookback: int = 50) -> Dict[str, float]:
    """
    Find support and resistance levels from recent candles
    
    Args:
        candles: List of candle dicts with 'high' and 'low' keys
        lookback: Number of recent candles to analyze
    
    Returns:
        Dict with support and resistance levels
    """
    if len(candles) < 10:
        return {"support": 0, "resistance": 0}
    
    recent = candles[-lookback:] if len(candles) > lookback else candles
    
    # Support is the lowest low in the lookback period
    support = min(c['low'] for c in recent)
    
    # Resistance is the highest high in the lookback period
    resistance = max(c['high'] for c in recent)
    
    return {
        "support": round(support, 2),
        "resistance": round(resistance, 2)
    }


def calculate_performance_metrics(candles: List[Dict]) -> Dict[str, float]:
    """
    Calculate performance metrics (returns over different periods)
    
    Args:
        candles: List of candles (oldest to newest)
    
    Returns:
        Dict with various return percentages
    """
    if not candles or len(candles) < 2:
        return {}
    
    current_price = candles[-1]['close']
    metrics = {}
    
    # Helper function to calculate return
    def calc_return(days_ago: int, label: str):
        if len(candles) > days_ago:
            old_price = candles[-days_ago]['close']
            return_pct = ((current_price - old_price) / old_price) * 100
            metrics[label] = round(return_pct, 2)
    
    # Calculate returns for different periods
    calc_return(5, "week_return")      # ~1 week (5 trading days)
    calc_return(20, "month_return")    # ~1 month (20 trading days)
    calc_return(60, "quarter_return")  # ~3 months
    calc_return(120, "half_year_return")  # ~6 months
    calc_return(250, "year_return")    # ~1 year (250 trading days)
    
    # 52-week high/low
    if len(candles) >= 250:
        year_candles = candles[-250:]
        metrics["week_52_high"] = round(max(c['high'] for c in year_candles), 2)
        metrics["week_52_low"] = round(min(c['low'] for c in year_candles), 2)
    
    return metrics


def detect_trend(prices: List[float], sma_20: float, sma_50: float, sma_200: Optional[float]) -> Dict[str, str]:
    """
    Detect overall trend based on price and moving averages
    
    Args:
        prices: List of recent prices
        sma_20: 20-day SMA
        sma_50: 50-day SMA
        sma_200: 200-day SMA (optional)
    
    Returns:
        Dict with trend and strength
    """
    if not prices:
        return {"trend": "NEUTRAL", "strength": "WEAK"}
    
    current_price = prices[-1]
    score = 0
    
    # Price vs SMAs
    if current_price > sma_20:
        score += 1
    else:
        score -= 1
    
    if current_price > sma_50:
        score += 1
    else:
        score -= 1
    
    if sma_200 and current_price > sma_200:
        score += 1
    elif sma_200:
        score -= 1
    
    # SMA alignment
    if sma_20 > sma_50:
        score += 1
    else:
        score -= 1
    
    if sma_200 and sma_50 > sma_200:
        score += 1
    elif sma_200:
        score -= 1
    
    # Determine trend and strength
    if score >= 3:
        return {"trend": "BULLISH", "strength": "STRONG"}
    elif score >= 1:
        return {"trend": "BULLISH", "strength": "MODERATE"}
    elif score <= -3:
        return {"trend": "BEARISH", "strength": "STRONG"}
    elif score <= -1:
        return {"trend": "BEARISH", "strength": "MODERATE"}
    else:
        return {"trend": "NEUTRAL", "strength": "WEAK"}


def analyze_volume(candles: List[Dict], period: int = 20) -> Dict:
    """
    Analyze volume patterns and trends
    
    Args:
        candles: List of candle dicts with 'volume', 'close', 'open' keys
        period: Period for average volume calculation (default: 20)
    
    Returns:
        Dict with volume analysis including:
        - avg_volume: Average volume over period
        - current_volume: Most recent volume
        - volume_ratio: Current vs average ratio
        - trend: Volume trend (INCREASING/DECREASING/STABLE)
        - obv: On-Balance Volume
        - price_volume_correlation: Correlation score
    """
    if not candles or len(candles) < period:
        return {
            "avg_volume": 0,
            "current_volume": 0,
            "volume_ratio": 1.0,
            "trend": "STABLE",
            "obv": 0,
            "price_volume_correlation": "NEUTRAL"
        }
    
    # Extract volumes
    volumes = [c['volume'] for c in candles]
    current_volume = volumes[-1]
    
    # Calculate average volume
    avg_volume = statistics.mean(volumes[-period:]) if len(volumes) >= period else statistics.mean(volumes)
    
    # Volume ratio (current vs average)
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
    
    # Detect volume trend
    if len(volumes) >= 10:
        recent_avg = statistics.mean(volumes[-5:])
        older_avg = statistics.mean(volumes[-15:-5]) if len(volumes) >= 15 else avg_volume
        
        if recent_avg > older_avg * 1.2:
            volume_trend = "INCREASING"
        elif recent_avg < older_avg * 0.8:
            volume_trend = "DECREASING"
        else:
            volume_trend = "STABLE"
    else:
        volume_trend = "STABLE"
    
    # Calculate On-Balance Volume (OBV)
    obv = 0
    for i in range(1, len(candles)):
        if candles[i]['close'] > candles[i-1]['close']:
            obv += candles[i]['volume']
        elif candles[i]['close'] < candles[i-1]['close']:
            obv -= candles[i]['volume']
    
    # Price-Volume Correlation (simplified)
    correlation = analyze_price_volume_correlation(candles[-10:] if len(candles) >= 10 else candles)
    
    return {
        "avg_volume": round(avg_volume, 0),
        "current_volume": current_volume,
        "volume_ratio": round(volume_ratio, 2),
        "trend": volume_trend,
        "obv": obv,
        "price_volume_correlation": correlation
    }


def analyze_price_volume_correlation(candles: List[Dict]) -> str:
    """
    Analyze correlation between price and volume movements
    
    Args:
        candles: Recent candles (typically last 10)
    
    Returns:
        Correlation type: CONFIRMATORY/DIVERGENT/NEUTRAL
    """
    if len(candles) < 3:
        return "NEUTRAL"
    
    # Count price up/down days with high/low volume
    confirming = 0
    diverging = 0
    
    avg_vol = statistics.mean([c['volume'] for c in candles])
    
    for i in range(1, len(candles)):
        price_up = candles[i]['close'] > candles[i-1]['close']
        high_volume = candles[i]['volume'] > avg_vol
        
        if (price_up and high_volume) or (not price_up and not high_volume):
            confirming += 1
        elif (price_up and not high_volume) or (not price_up and high_volume):
            diverging += 1
    
    if confirming > diverging * 1.5:
        return "CONFIRMATORY"  # Price moves confirmed by volume
    elif diverging > confirming * 1.5:
        return "DIVERGENT"  # Warning: price moves without volume support
    else:
        return "NEUTRAL"


def get_volume_signal_adjustment(volume_data: Dict, price_trend: str) -> int:
    """
    Calculate signal score adjustment based on volume analysis
    
    Args:
        volume_data: Dict from analyze_volume()
        price_trend: "BULLISH", "BEARISH", or "NEUTRAL"
    
    Returns:
        Score adjustment (-2 to +2)
    """
    adjustment = 0
    
    # High volume ratio boosts signal confidence
    if volume_data['volume_ratio'] > 1.5:  # 50% above average
        adjustment += 1
    elif volume_data['volume_ratio'] > 2.0:  # 100% above average (breakout)
        adjustment += 2
    elif volume_data['volume_ratio'] < 0.7:  # Low volume weakens signal
        adjustment -= 1
    
    # Price-volume correlation
    if volume_data['price_volume_correlation'] == "CONFIRMATORY":
        if price_trend == "BULLISH":
            adjustment += 1  # Bullish move on high volume = strong
        elif price_trend == "BEARISH":
            adjustment -= 1  # Bearish move on high volume = strong sell
    elif volume_data['price_volume_correlation'] == "DIVERGENT":
        # Warning: price moving without volume support
        adjustment -= 1
    
    # OBV trending with price
    if volume_data['obv'] > 0 and price_trend == "BULLISH":
        adjustment += 1
    elif volume_data['obv'] < 0 and price_trend == "BEARISH":
        adjustment -= 1
    
    # Cap adjustment
    return max(-2, min(2, adjustment))
