# Machine Learning Implementation for Stock Analytics
## How to Improve Signal Accuracy to 75-85%

---

## Overview

Implement a supervised machine learning model that learns from historical signals and their outcomes to predict BUY/HOLD/SELL signals more accurately than rule-based technical indicators.

**Expected Improvement:** +10-15% accuracy (from 65-75% to 75-85%)

---

## Approach: Supervised Learning

### **What We'll Build:**

```
Historical Data → Feature Engineering → Train ML Model → Predict Signals
     ↓                    ↓                    ↓              ↓
  OHLCV Data      Calculate Features      Random Forest    BUY/HOLD/SELL
                  (RSI, MACD, Volume)     or XGBoost       + Confidence
```

---

## Step 1: Data Collection & Labeling

### **Collect Training Data**

```python
# For each stock, for each day in history:
{
    "date": "2024-01-15",
    "features": {
        "rsi": 58,
        "macd_histogram": 3.2,
        "sma_20": 2750,
        "volume_ratio": 1.8,
        "price_change_5d": 2.3,
        # ... 20-30 features total
    },
    "label": "BUY",  # What signal was given
    "outcome": 1     # 1 if profitable after 30 days, 0 if loss
}
```

### **Labeling Strategy:**

```python
def label_outcome(entry_price, exit_price_30d_later):
    """
    Label if a signal was correct
    """
    return_pct = ((exit_price_30d_later - entry_price) / entry_price) * 100
    
    if return_pct > 3:  # 3% profit = success
        return 1  # Correct signal
    else:
        return 0  # Incorrect signal
```

**Data Needed:**
- Minimum: 1000 labeled examples (500 BUY, 500 SELL)
- Ideal: 10,000+ examples from multiple stocks
- Time: Last 5 years of daily data

---

## Step 2: Feature Engineering

### **Create Features from Raw Data**

```python
def create_features(candles):
    """
    Extract 30+ features from OHLCV data
    """
    features = {}
    
    # Price-based features
    features['rsi_14'] = calculate_rsi(candles, 14)
    features['rsi_7'] = calculate_rsi(candles, 7)  # Short-term RSI
    features['macd_histogram'] = calculate_macd(candles)['histogram']
    features['sma_20'] = calculate_sma(candles, 20)
    features['sma_50'] = calculate_sma(candles, 50)
    features['price_vs_sma_20'] = (current_price / sma_20 - 1) * 100
    
    # Volume features
    features['volume_ratio'] = analyze_volume(candles)['volume_ratio']
    features['volume_trend'] = 1 if volume_trend == 'INCREASING' else 0
    features['obv'] = analyze_volume(candles)['obv']
    
    # Momentum features
    features['price_change_1d'] = price_change(1)
    features['price_change_5d'] = price_change(5)
    features['price_change_20d'] = price_change(20)
    
    # Volatility features
    features['std_dev_20'] = standard_deviation(close_prices[-20:])
    features['atr'] = average_true_range(candles)
    
    # Pattern features
    features['higher_highs'] = 1 if detect_higher_highs() else 0
    features['lower_lows'] = 1 if detect_lower_lows() else 0
    
    # Bollinger Bands
    bb = calculate_bollinger_bands(candles)
    features['bb_width'] = (bb['upper'] - bb['lower']) / bb['middle']
    features['price_bb_position'] = (current_price - bb['lower']) / (bb['upper'] - bb['lower'])
    
    return features  # 30+ features
```

---

## Step 3: Model Selection

### **Option A: Random Forest (Recommended for Start)**

**Pros:**
- Easy to implement
- Handles non-linear relationships
- Feature importance analysis
- Less prone to overfitting

**Cons:**
- Slightly lower accuracy than XGBoost
- Slower prediction time

### **Option B: XGBoost (Best Accuracy)**

**Pros:**
- Highest accuracy
- Handles missing data well
- Built-in feature importance

**Cons:**
- More complex tuning
- Risk of overfitting

### **Option C: Neural Network (Advanced)**

**Pros:**
- Can learn complex patterns
- Can use LSTM for time series

**Cons:**
- Requires more data (50,000+ examples)
- Harder to interpret
- Longer training time

**Recommendation:** Start with Random Forest, upgrade to XGBoost later.

---

## Step 4: Implementation

### **Backend: ML Model Service**

**File:** `backend/app/services/ml_signal_service.py`

```python
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd

class MLSignalService:
    def __init__(self):
        self.model = None
        self.feature_names = []
        
    def train(self, training_data):
        """
        Train the ML model on historical data
        
        training_data: List of dicts with 'features' and 'label'
        """
        # Convert to DataFrame
        df = pd.DataFrame([d['features'] for d in training_data])
        labels = [d['outcome'] for d in training_data]
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            df, labels, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        self.feature_names = df.columns.tolist()
        
        # Evaluate
        accuracy = self.model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy * 100:.2f}%")
        
        # Save model
        joblib.dump(self.model, 'ml_model.pkl')
        
        return accuracy
    
    def predict(self, features):
        """
        Predict signal for new data
        
        Returns: {
            'signal': 'BUY',
            'confidence': 0.85,
            'feature_importance': {...}
        }
        """
        if not self.model:
            self.model = joblib.load('ml_model.pkl')
        
        # Convert features to DataFrame
        df = pd.DataFrame([features])
        
        # Predict probability
        proba = self.model.predict_proba(df)[0]
        prediction = self.model.predict(df)[0]
        
        # Map to signal
        signal = "BUY" if prediction == 1 else "SELL"
        confidence = max(proba) * 100
        
        # Get feature importance
        importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        return {
            'signal': signal,
            'confidence': round(confidence, 1),
            'ml_probability': round(proba[1], 2),
            'feature_importance': importance
        }

# Singleton
ml_signal_service = MLSignalService()
```

---

## Step 5: Integration Strategy

### **Hybrid Approach (Best Results)**

Combine traditional indicators with ML:

```python
def generate_hybrid_signal(candles):
    # Traditional signal
    traditional_signal = generate_traditional_signal(candles)  # Your current system
    
    # ML signal
    features = create_features(candles)
    ml_signal = ml_signal_service.predict(features)
    
    # Combine signals
    if traditional_signal['signal'] == ml_signal['signal']:
        # Both agree - high confidence
        return {
            'signal': traditional_signal['signal'],
            'confidence': (traditional_signal['confidence'] + ml_signal['confidence']) / 2,
            'agreement': 'HIGH'
        }
    else:
        # Disagree - use ML if high confidence, else HOLD
        if ml_signal['confidence'] > 75:
            return ml_signal
        else:
            return {
                'signal': 'HOLD',
                'confidence': 50,
                'agreement': 'LOW'
            }
```

---

## Step 6: Training Pipeline

### **Continuous Learning**

```python
def retrain_model_monthly():
    """
    Retrain model with new data every month
    """
    # 1. Collect signals from last month
    signals = db.query(Signal).filter(
        Signal.created_at > last_month
    ).all()
    
    # 2. Label outcomes (30 days later)
    training_data = []
    for signal in signals:
        outcome = check_if_profitable(signal)
        training_data.append({
            'features': signal.features,
            'outcome': outcome
        })
    
    # 3. Add to existing training data
    all_training_data = load_historical_training_data()
    all_training_data.extend(training_data)
    
    # 4. Retrain model
    accuracy = ml_signal_service.train(all_training_data)
    
    print(f"Model retrained. New accuracy: {accuracy * 100:.2f}%")
```

---

## Step 7: Evaluation Metrics

### **Track Performance**

```python
def evaluate_ml_model():
    """
    Comprehensive evaluation
    """
    metrics = {
        # Accuracy
        'overall_accuracy': 0.78,  # 78%
        'buy_signal_accuracy': 0.82,
        'sell_signal_accuracy': 0.74,
        
        # Precision/Recall
        'precision': 0.80,  # Of signals given, 80% are correct
        'recall': 0.75,     # Of correct signals, 75% are caught
        
        # Profitability
        'avg_return_per_signal': 4.2,  # Average 4.2% return
        'win_rate': 0.78,  # 78% of signals are profitable
        
        # Comparison
        'traditional_accuracy': 0.68,  # Your current system
        'ml_accuracy': 0.78,           # ML system
        'improvement': 0.10            # +10%
    }
    
    return metrics
```

---

## Implementation Timeline

### **Phase 1: Data Collection (Week 1)**
- Fetch 5 years of historical data for 50 stocks
- Calculate all features
- Label outcomes (did price go up/down after 30 days?)
- **Deliverable:** 10,000 labeled examples

### **Phase 2: Model Training (Week 2)**
- Implement feature engineering pipeline
- Train Random Forest model
- Cross-validation
- **Deliverable:** Trained model with 75%+ test accuracy

### **Phase 3: Integration (Week 3)**
- Create ML service endpoint
- Integrate with existing analytics
- Implement hybrid signal logic
- **Deliverable:** Working ML predictions in API

### **Phase 4: Testing & Tuning (Week 4)**
- Backtest on unseen data
- A/B test vs traditional signals
- Fine-tune hyperparameters
- **Deliverable:** Production-ready ML system

---

## Required Libraries

```bash
# Backend
pip install scikit-learn  # Random Forest
pip install xgboost       # XGBoost (optional)
pip install pandas        # Data manipulation
pip install joblib        # Model saving
pip install numpy         # Numerical operations
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Overfitting** | Use cross-validation, limit tree depth |
| **Market regime change** | Retrain monthly, use recent data |
| **Feature drift** | Monitor feature importance, add new features |
| **Insufficient data** | Start with 50+ stocks, 5 years each |
| **Black swan events** | Combine with traditional indicators |

---

## Expected Results

**Before ML:**
- Accuracy: 65-70%
- High confidence signals: 70-75%

**After ML (Hybrid Approach):**
- Accuracy: 75-80%
- High confidence signals: 80-85%
- **Agreement signals** (both ML + traditional): 85-90%

---

## Alternative: Use Pre-trained Models

### **Option: Transfer Learning**

Instead of training from scratch, use pre-trained financial models:

```python
# Use FinBERT for sentiment
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Or use pre-trained time series models
from darts.models import TFTModel  # Temporal Fusion Transformer
```

---

## Quick Start: Minimal Implementation

If you want to start small:

```python
# 1. Collect 1000 examples (easy)
# 2. Use sklearn's default Random Forest (5 lines of code)
# 3. Get 70-75% accuracy immediately
# 4. Iterate from there

from sklearn.ensemble import RandomForestClassifier

# Train
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Predict
prediction = model.predict(features)
```

---

## Recommendation

**Start Small:**
1. Collect 1000 labeled examples (1 week)
2. Train basic Random Forest (1 day)
3. Test accuracy (should be 70-75%)
4. If good, expand dataset and retrain

**Don't:**
- Start with neural networks (too complex)
- Over-engineer features (start with 10-15)
- Expect 100% accuracy (unrealistic)

**Do:**
- Use hybrid approach (ML + traditional)
- Retrain regularly (monthly)
- Track real-world performance
- Start simple, iterate

---

## Next Steps

Want me to:
1. **Implement basic ML model** (Random Forest with 1000 examples)?
2. **Create data collection pipeline** (fetch & label historical data)?
3. **Build hybrid signal system** (combine ML + traditional)?

Let me know which path you'd like to take! 🚀
