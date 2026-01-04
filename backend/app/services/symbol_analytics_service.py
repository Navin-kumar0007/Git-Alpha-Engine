"""
Symbol Analytics Service
Analyzes stock symbols and generates trading signals and insights
"""
from typing import List, Dict, Optional
from app.utils.technical_indicators import (
    calculate_rsi,
    calculate_sma,
    calculate_macd,
    calculate_bollinger_bands,
    find_support_resistance,
    calculate_performance_metrics,
    detect_trend,
    analyze_volume,
    get_volume_signal_adjustment
)


class SymbolAnalyticsService:
    """Service for analyzing stock symbols and generating insights"""
    
    def __init__(self):
        self.ml_enabled = True  # Enable/disable ML predictions
        try:
            from app.services.ml_features_service import ml_features_service
            from app.services.ml_model_service import ml_model_service
            self.ml_features = ml_features_service
            self.ml_model = ml_model_service
            # Try to load model
            self.ml_model.load_model()
        except Exception as e:
            print(f"ML model not available: {e}")
            self.ml_enabled = False
    
    def analyze_symbol(self, candles: List[Dict]) -> Dict:
        """
        Analyze a symbol's historical data and generate insights
        
        Args:
            candles: List of OHLCV candle dicts (oldest to newest)
        
        Returns:
            Dict with comprehensive analytics including:
            - signal (BUY/HOLD/SELL)
            - trend (BULLISH/BEARISH/NEUTRAL)
            - indicators (RSI, MACD, SMAs)
            - levels (support/resistance)
            - performance metrics
            - confidence score
        """
        if not candles or len(candles) < 20:
            return {
                "error": "Insufficient data for analysis",
                "min_required": 20,
                "received": len(candles) if candles else 0
            }
        
        # Extract closing prices
        close_prices = [c['close'] for c in candles]
        current_price = close_prices[-1]
        
        # Calculate technical indicators
        rsi = calculate_rsi(close_prices)
        macd = calculate_macd(close_prices)
        sma_20 = calculate_sma(close_prices, 20)
        sma_50 = calculate_sma(close_prices, 50)
        sma_200 = calculate_sma(close_prices, 200)
        bollinger = calculate_bollinger_bands(close_prices)
        
        # Find support/resistance
        levels = find_support_resistance(candles)
        
        # Calculate performance
        performance = calculate_performance_metrics(candles)
        
        # Detect trend
        trend_data = detect_trend(close_prices, sma_20 or current_price, sma_50 or current_price, sma_200)
        
        # Analyze volume
        volume_data = analyze_volume(candles)
        
        # Generate ML prediction (if available)
        ml_prediction = None
        if self.ml_enabled:
            try:
                features = self.ml_features.extract_features(candles)
                ml_prediction = self.ml_model.predict(features)
            except Exception as e:
                print(f"ML prediction failed: {e}")
                ml_prediction = None
        
        # Generate trading signal (with volume adjustment)
        signal_data = self._generate_signal(
            current_price=current_price,
            rsi=rsi,
            macd=macd,
            sma_20=sma_20,
            sma_50=sma_50,
            sma_200=sma_200,
            bollinger=bollinger,
            trend=trend_data['trend'],
            volume_data=volume_data,
            ml_prediction=ml_prediction
        )
        
        # Compile analytics
        analytics = {
            "signal": signal_data['signal'],
            "confidence": signal_data['confidence'],
            "trend": trend_data['trend'],
            "strength": trend_data['strength'],
            "current_price": round(current_price, 2),
            "indicators": {
                "rsi": rsi,
                "rsi_interpretation": self._interpret_rsi(rsi) if rsi else "N/A",
                "macd": macd,
                "macd_signal": self._interpret_macd(macd) if macd else "N/A",
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "bollinger_bands": bollinger
            },
            "volume": volume_data,
            "levels": levels,
            "performance": performance,
            "summary": self._generate_summary(signal_data['signal'], trend_data, rsi, volume_data),
            "ml_prediction": ml_prediction,
            "signal_source": signal_data.get('source', 'TRADITIONAL')
        }
        
        return analytics
    
    def _generate_signal(
        self,
        current_price: float,
        rsi: Optional[float],
        macd: Optional[Dict],
        sma_20: Optional[float],
        sma_50: Optional[float],
        sma_200: Optional[float],
        bollinger: Optional[Dict],
        trend: str,
        volume_data: Optional[Dict] = None,
        ml_prediction: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Generate BUY/HOLD/SELL signal based on multiple indicators
        
        Returns:
            Dict with signal and confidence score
        """
        score = 0
        max_score = 0
        
        # RSI scoring (weight: 2)
        if rsi:
            max_score += 2
            if rsi < 30:  # Oversold
                score += 2
            elif rsi > 70:  # Overbought
                score -= 2
            elif 40 <= rsi <= 60:  # Neutral zone
                score += 0
        
        # MACD scoring (weight: 2)
        if macd:
            max_score += 2
            if macd['histogram'] > 0:  # Bullish
                score += 2
            else:  # Bearish
                score -= 2
        
        # Moving average scoring (weight: 3)
        if sma_20 and sma_50:
            max_score += 3
            if current_price > sma_20 > sma_50:  # Strong uptrend
                score += 3
            elif current_price < sma_20 < sma_50:  # Strong downtrend
                score -= 3
            elif current_price > sma_20:  # Mild uptrend
                score += 1
            elif current_price < sma_20:  # Mild downtrend
                score -= 1
        
        # 200-day SMA scoring (weight: 1)
        if sma_200:
            max_score += 1
            if current_price > sma_200:
                score += 1
            else:
                score -= 1
        
        # Bollinger Bands scoring (weight: 1)
        if bollinger:
            max_score += 1
            if current_price < bollinger['lower']:  # Oversold
                score += 1
            elif current_price > bollinger['upper']:  # Overbought
                score -= 1
        
        # Volume scoring (weight: 2) - NEW!
        if volume_data:
            max_score += 2
            volume_adjustment = get_volume_signal_adjustment(volume_data, trend)
            score += volume_adjustment
        
        # Normalize score to percentage confidence
        if max_score > 0:
            confidence = abs(score) / max_score * 100
        else:
            confidence = 50
        
        # Generate signal
        if score >= 3:
            signal = "BUY"
        elif score <= -3:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        # Apply ML hybrid logic if available
        source = "TRADITIONAL"
        if ml_prediction and ml_prediction.get('signal'):
            ml_signal = ml_prediction['signal']
            ml_confidence = ml_prediction['confidence']
            
            # Hybrid strategy
            if signal == ml_signal:
                # Both agree - boost confidence
                confidence = min(95, (confidence + ml_confidence) / 2 + 10)
                source = "HYBRID_AGREEMENT"
            elif ml_confidence > 80:
                # ML is very confident, trust it
                signal = ml_signal
                confidence = ml_confidence
                source = "ML_HIGH_CONFIDENCE"
            # else: keep traditional signal
        
        return {
            "signal": signal,
            "confidence": round(confidence, 0),
            "score": score,
            "max_score": max_score,
            "source": source
        }
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value"""
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        elif 45 <= rsi <= 55:
            return "Neutral"
        elif rsi > 55:
            return "Slightly Overbought"
        else:
            return "Slightly Oversold"
    
    def _interpret_macd(self, macd: Dict) -> str:
        """Interpret MACD values"""
        if macd['histogram'] > 0:
            return "Bullish Crossover"
        elif macd['histogram'] < 0:
            return "Bearish Crossover"
        else:
            return "Neutral"
    
    def _generate_summary(self, signal: str, trend_data: Dict, rsi: Optional[float], volume_data: Optional[Dict] = None) -> str:
        """Generate a human-readable summary"""
        trend = trend_data['trend']
        strength = trend_data['strength']
        
        rsi_text = ""
        if rsi:
            if rsi > 70:
                rsi_text = ", but showing overbought conditions"
            elif rsi < 30:
                rsi_text = ", showing oversold conditions"
        
        # Add volume context
        volume_text = ""
        if volume_data:
            if volume_data['volume_ratio'] > 1.5:
                volume_text = " High volume confirms the move."
            elif volume_data['volume_ratio'] < 0.7:
                volume_text = " Low volume suggests caution."
            elif volume_data['price_volume_correlation'] == "DIVERGENT":
                volume_text = " Volume not confirming price action."
        
        summaries = {
            "BUY": {
                "BULLISH": f"Strong buy signal detected. Stock is in a {strength.lower()} bullish trend{rsi_text}.{volume_text} Good entry opportunity.",
                "BEARISH": f"Buy signal detected despite bearish trend. Potential reversal forming{rsi_text}.{volume_text} Exercise caution.",
                "NEUTRAL": f"Buy signal detected. Stock showing bullish momentum{rsi_text}.{volume_text} Monitor for trend confirmation."
            },
            "SELL": {
                "BULLISH": f"Sell signal detected despite bullish trend. Consider profit booking{rsi_text}.{volume_text} Watch for reversal signs.",
                "BEARISH": f"Strong sell signal. Stock in {strength.lower()} bearish trend{rsi_text}.{volume_text} Exit recommended.",
                "NEUTRAL": f"Sell signal detected. Bearish momentum developing{rsi_text}.{volume_text} Consider reducing positions."
            },
            "HOLD": {
                "BULLISH": f"Hold recommended. Stock in {strength.lower()} bullish trend{rsi_text}.{volume_text} Wait for better entry.",
                "BEARISH": f"Hold position. Stock in {strength.lower()} bearish trend{rsi_text}.{volume_text} Avoid fresh buying.",
                "NEUTRAL": f"Neutral stance. No clear trend{rsi_text}.{volume_text} Wait for clearer signals before action."
            }
        }
        
        return summaries.get(signal, {}).get(trend, "Insufficient data for summary.")


# Singleton instance
symbol_analytics_service = SymbolAnalyticsService()
