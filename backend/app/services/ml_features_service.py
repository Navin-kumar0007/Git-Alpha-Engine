"""
ML Feature Engineering Service
Extracts 30+ features from candle data for XGBoost model
"""
from typing import List, Dict
import statistics
from app.utils.technical_indicators import (
    calculate_rsi,
    calculate_sma,
    calculate_ema,
    calculate_macd,
    calculate_bollinger_bands,
    analyze_volume,
    detect_trend
)


class MLFeaturesService:
    """Service for extracting ML features from candle data"""
    
    def extract_features(self, candles: List[Dict]) -> Dict[str, float]:
        """
        Extract 30+ features from OHLCV candle data
        
        Args:
            candles: List of candle dicts (oldest to newest)
        
        Returns:
            Dict of feature_name -> feature_value
        """
        if not candles or len(candles) < 20:
            return {}
        
        features = {}
        
        # Extract price and volume data
        close_prices = [c['close'] for c in candles]
        high_prices = [c['high'] for c in candles]
        low_prices = [c['low'] for c in candles]
        volumes = [c['volume'] for c in candles]
        current_price = close_prices[-1]
        
        # === Price Momentum Features ===
        features['price_change_1d'] = self._calc_return(close_prices, 1)
        features['price_change_5d'] = self._calc_return(close_prices, 5)
        features['price_change_10d'] = self._calc_return(close_prices, 10)
        features['price_change_20d'] = self._calc_return(close_prices, 20)
        
        # === RSI Features ===
        rsi_14 = calculate_rsi(close_prices, 14)
        rsi_7 = calculate_rsi(close_prices, 7)
        features['rsi_14'] = rsi_14 if rsi_14 else 50
        features['rsi_7'] = rsi_7 if rsi_7 else 50
        features['rsi_diff'] = (rsi_14 - rsi_7) if (rsi_14 and rsi_7) else 0
        
        # === MACD Features ===
        macd = calculate_macd(close_prices)
        if macd:
            features['macd_line'] = macd['macd_line']
            features['macd_signal'] = macd['signal_line']
            features['macd_histogram'] = macd['histogram']
            features['macd_positive'] = 1 if macd['histogram'] > 0 else 0
        else:
            features['macd_line'] = 0
            features['macd_signal'] = 0
            features['macd_histogram'] = 0
            features['macd_positive'] = 0
        
        # === Moving Average Features ===
        sma_20 = calculate_sma(close_prices, 20)
        sma_50 = calculate_sma(close_prices, 50)
        sma_200 = calculate_sma(close_prices, 200)
        
        features['sma_20'] = sma_20 if sma_20 else current_price
        features['sma_50'] = sma_50 if sma_50 else current_price
        features['sma_200'] = sma_200 if sma_200 else current_price
        
        # Price vs SMA positions (percentage)
        features['price_vs_sma20'] = ((current_price / features['sma_20']) - 1) * 100
        features['price_vs_sma50'] = ((current_price / features['sma_50']) - 1) * 100
        features['price_vs_sma200'] = ((current_price / features['sma_200']) - 1) * 100
        
        # SMA alignment (golden cross / death cross indicators)
        features['sma20_above_sma50'] = 1 if features['sma_20'] > features['sma_50'] else 0
        features['sma50_above_sma200'] = 1 if features['sma_50'] > features['sma_200'] else 0
        
        # === Bollinger Bands Features ===
        bb = calculate_bollinger_bands(close_prices)
        if bb:
            features['bb_width'] = ((bb['upper'] - bb['lower']) / bb['middle']) * 100
            features['bb_position'] = ((current_price - bb['lower']) / (bb['upper'] - bb['lower'])) * 100
            features['bb_squeeze'] = 1 if features['bb_width'] < 10 else 0
        else:
            features['bb_width'] = 20
            features['bb_position'] = 50
            features['bb_squeeze'] = 0
        
        # === Volume Features ===
        vol_data = analyze_volume(candles)
        features['volume_ratio'] = vol_data['volume_ratio']
        features['volume_trend_inc'] = 1 if vol_data['trend'] == 'INCREASING' else 0
        features['volume_trend_dec'] = 1 if vol_data['trend'] == 'DECREASING' else 0
        features['volume_confirmatory'] = 1 if vol_data['price_volume_correlation'] == 'CONFIRMATORY' else 0
        features['volume_divergent'] = 1 if vol_data['price_volume_correlation'] == 'DIVERGENT' else 0
        
        # === Volatility Features ===
        if len(close_prices) >= 20:
            features['volatility_20d'] = statistics.stdev(close_prices[-20:]) / statistics.mean(close_prices[-20:]) * 100
        else:
            features['volatility_20d'] = 0
        
        # High-Low range
        features['hl_range'] = ((high_prices[-1] - low_prices[-1]) / close_prices[-1]) * 100
        
        # === Trend Features ===
        trend_data = detect_trend(close_prices, features['sma_20'], features['sma_50'], features['sma_200'])
        features['trend_bullish'] = 1 if trend_data['trend'] == 'BULLISH' else 0
        features['trend_bearish'] = 1 if trend_data['trend'] == 'BEARISH' else 0
        features['trend_strong'] = 1 if trend_data['strength'] == 'STRONG' else 0
        
        # === Pattern Features ===
        features['higher_highs'] = 1 if self._detect_higher_highs(high_prices[-10:]) else 0
        features['lower_lows'] = 1 if self._detect_lower_lows(low_prices[-10:]) else 0
        
        return features
    
    def _calc_return(self, prices: List[float], days_ago: int) -> float:
        """Calculate percentage return from N days ago"""
        if len(prices) <= days_ago:
            return 0.0
        return ((prices[-1] - prices[-days_ago]) / prices[-days_ago]) * 100
    
    def _detect_higher_highs(self, highs: List[float]) -> bool:
        """Detect if making higher highs (uptrend pattern)"""
        if len(highs) < 3:
            return False
        return highs[-1] > highs[-2] and highs[-2] > highs[-3]
    
    def _detect_lower_lows(self, lows: List[float]) -> bool:
        """Detect if making lower lows (downtrend pattern)"""
        if len(lows) < 3:
            return False
        return lows[-1] < lows[-2] and lows[-2] < lows[-3]
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names for model training"""
        return [
            # Momentum
            'price_change_1d', 'price_change_5d', 'price_change_10d', 'price_change_20d',
            # RSI
            'rsi_14', 'rsi_7', 'rsi_diff',
            # MACD
            'macd_line', 'macd_signal', 'macd_histogram', 'macd_positive',
            # Moving Averages
            'sma_20', 'sma_50', 'sma_200',
            'price_vs_sma20', 'price_vs_sma50', 'price_vs_sma200',
            'sma20_above_sma50', 'sma50_above_sma200',
            # Bollinger Bands
            'bb_width', 'bb_position', 'bb_squeeze',
            # Volume
            'volume_ratio', 'volume_trend_inc', 'volume_trend_dec',
            'volume_confirmatory', 'volume_divergent',
            # Volatility
            'volatility_20d', 'hl_range',
            # Trend
            'trend_bullish', 'trend_bearish', 'trend_strong',
            # Patterns
            'higher_highs', 'lower_lows'
        ]


# Singleton instance
ml_features_service = MLFeaturesService()
