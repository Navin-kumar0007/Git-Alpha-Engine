"""
ML Training Data Service
Generates synthetic training data for XGBoost model
"""
from typing import List, Dict
import random
from datetime import datetime, timedelta


class MLTrainingDataService:
    """Service for generating training data"""
    
    def generate_synthetic_data(self, num_samples: int = 5000) -> List[Dict]:
        """
        Generate synthetic training data based on indicator patterns
        
        Strategy: Create scenarios where traditional indicators
        would give a signal, then label based on multiple indicator agreement
        
        Args:
            num_samples: Number of training examples to generate
        
        Returns:
            List of {features: Dict, label: int} where:
            - label = 1: BUY signal (profitable)
            - label = 0: NOT BUY (HOLD or SELL)
        """
        training_data = []
        
        for _ in range(num_samples):
            # Generate random but realistic feature values
            features = self._generate_random_features()
            
            # Label based on feature combination (rule-based labeling)
            label = self._label_from_features(features)
            
            training_data.append({
                'features': features,
                'label': label
            })
        
        # Balance classes (50% BUY, 50% NOT BUY)
        buy_samples = [d for d in training_data if d['label'] == 1]
        not_buy_samples = [d for d in training_data if d['label'] == 0]
        
        # Ensure balanced dataset
        min_class_size = min(len(buy_samples), len(not_buy_samples))
        balanced_data = (
            buy_samples[:min_class_size] +
            not_buy_samples[:min_class_size]
        )
        
        random.shuffle(balanced_data)
        return balanced_data
    
    def _generate_random_features(self) -> Dict[str, float]:
        """Generate random but realistic feature values"""
        features = {}
        
        # Momentum (typically -10% to +10%)
        features['price_change_1d'] = random.uniform(-5, 5)
        features['price_change_5d'] = random.uniform(-8, 8)
        features['price_change_10d'] = random.uniform(-12, 12)
        features['price_change_20d'] = random.uniform(-15, 15)
        
        # RSI (0-100, usually 30-70)
        features['rsi_14'] = random.uniform(20, 80)
        features['rsi_7'] = random.uniform(20, 80)
        features['rsi_diff'] = features['rsi_14'] - features['rsi_7']
        
        # MACD
        features['macd_line'] = random.uniform(-20, 20)
        features['macd_signal'] = random.uniform(-20, 20)
        features['macd_histogram'] = features['macd_line'] - features['macd_signal']
        features['macd_positive'] = 1 if features['macd_histogram'] > 0 else 0
        
        # Moving Averages (simulated prices around 1000-3000)
        base_price = random.uniform(1000, 3000)
        features['sma_20'] = base_price * random.uniform(0.95, 1.05)
        features['sma_50'] = base_price * random.uniform(0.93, 1.07)
        features['sma_200'] = base_price * random.uniform(0.90, 1.10)
        
        current_price = base_price
        features['price_vs_sma20'] = ((current_price / features['sma_20']) - 1) * 100
        features['price_vs_sma50'] = ((current_price / features['sma_50']) - 1) * 100
        features['price_vs_sma200'] = ((current_price / features['sma_200']) - 1) * 100
        
        features['sma20_above_sma50'] = 1 if features['sma_20'] > features['sma_50'] else 0
        features['sma50_above_sma200'] = 1 if features['sma_50'] > features['sma_200'] else 0
        
        # Bollinger Bands
        features['bb_width'] = random.uniform(5, 30)
        features['bb_position'] = random.uniform(0, 100)
        features['bb_squeeze'] = 1 if features['bb_width'] < 10 else 0
        
        # Volume
        features['volume_ratio'] = random.uniform(0.5, 2.5)
        features['volume_trend_inc'] = random.choice([0, 1])
        features['volume_trend_dec'] = 1 - features['volume_trend_inc'] if random.random() < 0.5 else 0
        features['volume_confirmatory'] = random.choice([0, 1])
        features['volume_divergent'] = 1 - features['volume_confirmatory'] if random.random() < 0.3 else 0
        
        # Volatility
        features['volatility_20d'] = random.uniform(1, 5)
        features['hl_range'] = random.uniform(0.5, 4)
        
        # Trend
        trend_choice = random.choice(['bullish', 'bearish', 'neutral'])
        features['trend_bullish'] = 1 if trend_choice == 'bullish' else 0
        features['trend_bearish'] = 1 if trend_choice == 'bearish' else 0
        features['trend_strong'] = random.choice([0, 1])
        
        # Patterns
        features['higher_highs'] = random.choice([0, 1])
        features['lower_lows'] = random.choice([0, 1])
        
        return features
    
    def _label_from_features(self, features: Dict[str, float]) -> int:
        """
        Label example as BUY (1) or NOT BUY (0) based on feature combination
        
        Uses rule-based logic similar to traditional signal generation
        """
        score = 0
        
        # RSI scoring
        if features['rsi_14'] < 30:  # Oversold
            score += 2
        elif features['rsi_14'] > 70:  # Overbought
            score -= 2
        
        # MACD scoring
        if features['macd_histogram'] > 0:
            score += 2
        else:
            score -= 2
        
        # Moving average scoring
        if features['price_vs_sma20'] > 0 and features['sma20_above_sma50']:
            score += 2
        elif features['price_vs_sma20'] < 0 and not features['sma20_above_sma50']:
            score -= 2
        
        # Volume confirmation
        if features['volume_ratio'] > 1.5 and features['volume_confirmatory']:
            score += 1
        elif features['volume_ratio'] < 0.7 or features['volume_divergent']:
            score -= 1
        
        # Trend scoring
        if features['trend_bullish'] and features['trend_strong']:
            score += 1
        elif features['trend_bearish'] and features['trend_strong']:
            score -= 1
        
        # Pattern scoring
        if features['higher_highs']:
            score += 1
        if features['lower_lows']:
            score -= 1
        
        # Label: BUY if score >= 3, else NOT BUY
        return 1 if score >= 3 else 0


# Singleton instance
ml_training_data_service = MLTrainingDataService()
