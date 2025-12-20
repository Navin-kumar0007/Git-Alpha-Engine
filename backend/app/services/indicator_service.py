"""Technical Indicators Service

Provides calculations for:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional


def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: List of closing prices
        period: RSI period (default: 14)
        
    Returns:
        List of RSI values (0-100)
    """
    if len(prices) < period + 1:
        return []
    
    prices_series = pd.Series(prices)
    delta = prices_series.diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.fillna(50).tolist()


def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict[str, List[float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: List of closing prices
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)
        
    Returns:
        Dictionary with 'macd', 'signal', and 'histogram' lists
    """
    if len(prices) < slow_period:
        return {"macd": [], "signal": [], "histogram": []}
    
    prices_series = pd.Series(prices)
    
    # Calculate EMAs
    ema_fast = prices_series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices_series.ewm(span=slow_period, adjust=False).mean()
    
    # MACD line
    macd_line = ema_fast - ema_slow
    
    # Signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Histogram
    histogram = macd_line - signal_line
    
    return {
        "macd": macd_line.tolist(),
        "signal": signal_line.tolist(),
        "histogram": histogram.tolist()
    }


def calculate_bollinger_bands(
    prices: List[float],
    period: int = 20,
    std_dev: int = 2
) -> Dict[str, List[float]]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: List of closing prices
        period: Moving average period (default: 20)
        std_dev: Number of standard deviations (default: 2)
        
    Returns:
        Dictionary with 'upper', 'middle', and 'lower' band lists
    """
    if len(prices) < period:
        return {"upper": [], "middle": [], "lower": []}
    
    prices_series = pd.Series(prices)
    
    # Middle band (SMA)
    middle_band = prices_series.rolling(window=period).mean()
    
    # Standard deviation
    std = prices_series.rolling(window=period).std()
    
    # Upper and lower bands
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return {
        "upper": upper_band.tolist(),
        "middle": middle_band.tolist(),
        "lower": lower_band.tolist()
    }


def calculate_sma(prices: List[float], period: int = 20) -> List[float]:
    """
    Calculate Simple Moving Average (SMA)
    
    Args:
        prices: List of closing prices
        period: Moving average period (default: 20)
        
    Returns:
        List of SMA values
    """
    if len(prices) < period:
        return []
    
    prices_series = pd.Series(prices)
    sma = prices_series.rolling(window=period).mean()
    
    return sma.tolist()


def calculate_ema(prices: List[float], period: int = 20) -> List[float]:
    """
    Calculate Exponential Moving Average (EMA)
    
    Args:
        prices: List of closing prices
        period: Moving average period (default: 20)
        
    Returns:
        List of EMA values
    """
    if len(prices) < period:
        return []
    
    prices_series = pd.Series(prices)
    ema = prices_series.ewm(span=period, adjust=False).mean()
    
    return ema.tolist()


def calculate_all_indicators(
    prices: List[float],
    indicators: List[str],
    params: Optional[Dict] = None
) -> Dict:
    """
    Calculate multiple indicators at once
    
    Args:
        prices: List of closing prices
        indicators: List of indicator names (rsi, macd, bb, sma, ema)
        params: Optional parameters for indicators
        
    Returns:
        Dictionary with indicator results
    """
    params = params or {}
    results = {}
    
    if "rsi" in indicators:
        results["rsi"] = calculate_rsi(
            prices,
            period=params.get("rsi_period", 14)
        )
    
    if "macd" in indicators:
        results["macd"] = calculate_macd(
            prices,
            fast_period=params.get("macd_fast", 12),
            slow_period=params.get("macd_slow", 26),
            signal_period=params.get("macd_signal", 9)
        )
    
    if "bb" in indicators or "bollinger_bands" in indicators:
        results["bollinger_bands"] = calculate_bollinger_bands(
            prices,
            period=params.get("bb_period", 20),
            std_dev=params.get("bb_std", 2)
        )
    
    if "sma" in indicators:
        results["sma"] = calculate_sma(
            prices,
            period=params.get("sma_period", 20)
        )
    
    if "ema" in indicators:
        results["ema"] = calculate_ema(
            prices,
            period=params.get("ema_period", 20)
        )
    
    return results
