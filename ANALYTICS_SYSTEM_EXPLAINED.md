# Symbol Analytics System - Technical Documentation

## Overview

The Symbol Analytics Dashboard automatically analyzes stocks using technical indicators and generates actionable BUY/HOLD/SELL signals with AI-powered insights.

---

## How It Works: Step-by-Step

### 1. User Action
```
User selects a symbol (e.g., RELIANCE, Token: 2885) from the Charts page
```

### 2. API Request
```
Frontend → GET /api/angel-historical/analytics/2885?exchange=NSE
```

### 3. Data Collection
Backend fetches **last 200 days** of historical candle data:
```python
candles = [
    {
        "timestamp": "2024-12-01",
        "open": 2750.50,
        "high": 2780.00,
        "low": 2740.00,
        "close": 2775.00,
        "volume": 5000000
    },
    # ... 200 days of data
]
```

### 4. Technical Indicator Calculations

#### A. RSI (Relative Strength Index)
**Purpose:** Identify overbought/oversold conditions

```python
# Calculate RSI (14-period)
prices = [2750, 2760, 2755, 2780, ...]
gains = [10, 0, 25, ...]  # When price goes up
losses = [0, 5, 0, ...]   # When price goes down

avg_gain = sum(gains[-14:]) / 14
avg_loss = sum(losses[-14:]) / 14

rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
# Result: 58.5
```

**Interpretation:**
- **0-30**: Oversold → BUY signal
- **30-70**: Neutral
- **70-100**: Overbought → SELL signal

---

#### B. MACD (Moving Average Convergence Divergence)
**Purpose:** Detect trend momentum and reversals

```python
# Calculate EMAs
ema_12 = exponential_moving_average(prices, 12)  # Fast
ema_26 = exponential_moving_average(prices, 26)  # Slow

macd_line = ema_12 - ema_26
signal_line = exponential_moving_average([macd_line], 9)
histogram = macd_line - signal_line

# Result:
# {
#     "macd_line": 15.5,
#     "signal_line": 12.3,
#     "histogram": 3.2  # Positive = Bullish
# }
```

**Interpretation:**
- **Histogram > 0**: Bullish crossover → BUY
- **Histogram < 0**: Bearish crossover → SELL
- **Near 0**: Neutral

---

#### C. Moving Averages (SMA)
**Purpose:** Identify trend direction

```python
sma_20 = sum(prices[-20:]) / 20   # Short-term: 2750
sma_50 = sum(prices[-50:]) / 50   # Medium-term: 2680
sma_200 = sum(prices[-200:]) / 200 # Long-term: 2600

current_price = 2780
```

**Interpretation:**
- **Price > SMA_20 > SMA_50 > SMA_200**: Strong uptrend (Bullish)
- **Price < SMA_20 < SMA_50 < SMA_200**: Strong downtrend (Bearish)
- **Golden Cross**: SMA_50 crosses above SMA_200 (Very Bullish)
- **Death Cross**: SMA_50 crosses below SMA_200 (Very Bearish)

---

#### D. Support & Resistance
**Purpose:** Identify key price levels

```python
recent_candles = candles[-50:]  # Last 50 days

support = min(c['low'] for c in recent_candles)      # ₹2,720
resistance = max(c['high'] for c in recent_candles)  # ₹2,850
```

**Usage:**
- **Support**: Price level where buying pressure prevents further decline
- **Resistance**: Price level where selling pressure prevents further rise

---

### 5. Trend Detection Algorithm

```python
score = 0

# Price vs Moving Averages (+1 each)
if current_price > sma_20: score += 1
if current_price > sma_50: score += 1
if current_price > sma_200: score += 1

# SMA Alignment (+1 each)
if sma_20 > sma_50: score += 1
if sma_50 > sma_200: score += 1

# Determine Trend
if score >= 3:
    trend = "BULLISH"
    strength = "STRONG" if score >= 4 else "MODERATE"
elif score <= -3:
    trend = "BEARISH"
    strength = "STRONG" if score <= -4 else "MODERATE"
else:
    trend = "NEUTRAL"
    strength = "WEAK"
```

---

### 6. Signal Generation (BUY/HOLD/SELL)

```python
signal_score = 0
max_score = 0

# 1. RSI Scoring (Weight: 2 points)
max_score += 2
if rsi < 30:           # Oversold
    signal_score += 2
elif rsi > 70:         # Overbought
    signal_score -= 2

# 2. MACD Scoring (Weight: 2 points)
max_score += 2
if macd['histogram'] > 0:  # Bullish crossover
    signal_score += 2
else:                      # Bearish crossover
    signal_score -= 2

# 3. Moving Average Scoring (Weight: 3 points)
max_score += 3
if price > sma_20 > sma_50 > sma_200:  # Strong uptrend
    signal_score += 3
elif price < sma_20 < sma_50 < sma_200:  # Strong downtrend
    signal_score -= 3

# 4. 200-day SMA (Weight: 1 point)
max_score += 1
if price > sma_200:
    signal_score += 1
else:
    signal_score -= 1

# 5. Bollinger Bands (Weight: 1 point)
max_score += 1
if price < bollinger_lower:  # Price below lower band
    signal_score += 1
elif price > bollinger_upper:  # Price above upper band
    signal_score -= 1

# Generate Signal
if signal_score >= 3:
    signal = "BUY"
elif signal_score <= -3:
    signal = "SELL"
else:
    signal = "HOLD"

# Calculate Confidence
confidence = (abs(signal_score) / max_score) * 100
# Result: 78% confidence
```

---

### 7. Performance Metrics

```python
current_price = candles[-1]['close']  # ₹2,780

# Calculate returns for different periods
week_return = ((current_price - candles[-5]['close']) / candles[-5]['close']) * 100
month_return = ((current_price - candles[-20]['close']) / candles[-20]['close']) * 100
quarter_return = ((current_price - candles[-60]['close']) / candles[-60]['close']) * 100
year_return = ((current_price - candles[-250]['close']) / candles[-250]['close']) * 100

# Results:
# week_return: +2.96%
# month_return: +5.70%
# quarter_return: +8.50%
# year_return: +18.20%
```

---

### 8. Generate Human-Readable Summary

```python
def generate_summary(signal, trend, strength, rsi):
    if signal == "BUY" and trend == "BULLISH":
        summary = f"Strong buy signal detected. Stock is in a {strength.lower()} "
        summary += f"bullish trend"
        if rsi < 30:
            summary += ", showing oversold conditions"
        summary += ". Good entry opportunity."
    
    return summary

# Result:
# "Strong buy signal detected. Stock is in a strong bullish trend. Good entry opportunity."
```

---

### 9. Complete Response

```json
{
  "success": true,
  "symboltoken": "2885",
  "exchange": "NSE",
  "analytics": {
    "signal": "BUY",
    "confidence": 78,
    "trend": "BULLISH",
    "strength": "STRONG",
    "current_price": 2780,
    "indicators": {
      "rsi": 58,
      "rsi_interpretation": "Neutral",
      "macd": {
        "macd_line": 15.5,
        "signal_line": 12.3,
        "histogram": 3.2
      },
      "macd_signal": "Bullish Crossover",
      "sma_20": 2750,
      "sma_50": 2680,
      "sma_200": 2600
    },
    "levels": {
      "support": 2720,
      "resistance": 2850
    },
    "performance": {
      "week_return": 2.96,
      "month_return": 5.70,
      "quarter_return": 8.50,
      "year_return": 18.20
    },
    "summary": "Strong buy signal detected. Stock is in a strong bullish trend. Good entry opportunity."
  }
}
```

---

### 10. Frontend Display

The frontend renders this data as:

```
┌─────────────────────────────────┐
│ 📊 Signal                       │
├─────────────────────────────────┤
│        BUY ✅                   │
│     78% confidence              │
│                                 │
│ 📈 BULLISH (STRONG)            │
│                                 │
│ Strong buy signal detected.     │
│ Stock is in a strong bullish    │
│ trend. Good entry opportunity.  │
├─────────────────────────────────┤
│ Technical Indicators            │
├─────────────────────────────────┤
│ RSI: 58 (Neutral)              │
│ [========|=======]              │
│                                 │
│ MACD: +3.2                      │
│ Bullish Crossover               │
│                                 │
│ SMA(20):  ₹2,750               │
│ SMA(50):  ₹2,680               │
│ SMA(200): ₹2,600               │
├─────────────────────────────────┤
│ Key Levels                      │
├─────────────────────────────────┤
│ ↓ Support:    ₹2,720           │
│ ↑ Resistance: ₹2,850           │
├─────────────────────────────────┤
│ Performance                     │
├─────────────────────────────────┤
│ 1 Week:    +2.96%              │
│ 1 Month:   +5.70%              │
│ 3 Months:  +8.50%              │
│ 1 Year:    +18.20%             │
└─────────────────────────────────┘
```

---

## Why This System Works

### Multi-Indicator Approach
- Uses **5 different indicators** to avoid false signals
- Each indicator votes BUY/HOLD/SELL
- Final signal is based on consensus

### Confidence Scoring
- Shows how strongly indicators agree
- **High confidence (>70%)**: Strong signal
- **Low confidence (<50%)**: Weak signal, use caution

### Contextual Analysis
- Considers trend direction
- Evaluates momentum
- Accounts for overbought/oversold conditions

### Performance Validation
- Historical returns show if stock is actually performing
- Helps validate the signal

---

## Example Scenarios

### Scenario 1: Strong Buy
```
RSI: 28 (Oversold) → +2 points
MACD: Bullish crossover → +2 points
Price > all SMAs → +3 points
Total: +7 points → BUY with 88% confidence
```

### Scenario 2: Hold (Conflicting Signals)
```
RSI: 72 (Overbought) → -2 points
MACD: Bullish → +2 points
Price > SMA_20 but < SMA_50 → +1 point
Total: +1 point → HOLD with 40% confidence
```

### Scenario 3: Strong Sell
```
RSI: 78 (Overbought) → -2 points
MACD: Bearish crossover → -2 points
Price < all SMAs → -3 points
Total: -7 points → SELL with 85% confidence
```

---

## Technical Stack

### Backend (`/backend/app`)
```
utils/technical_indicators.py
├── calculate_rsi()
├── calculate_macd()
├── calculate_sma()
├── find_support_resistance()
└── detect_trend()

services/symbol_analytics_service.py
├── analyze_symbol()
├── _generate_signal()
└── _generate_summary()

api/angel_historical.py
└── GET /analytics/{symboltoken}
```

### Frontend (`/frontend/src/components`)
```
SymbolAnalytics.jsx
├── Fetches analytics from API
├── Displays signal badge
├── Shows indicators
├── Renders performance metrics
└── Updates on symbol change
```

---

## Limitations & Disclaimers

1. **Not Financial Advice**: Signals are algorithmic, not professional advice
2. **Past Performance**: Historical returns don't guarantee future results
3. **Market Conditions**: Works best in trending markets, less reliable in choppy/sideways markets
4. **Data Dependency**: Requires minimum 200 days of data for accuracy
5. **Lagging Indicators**: Based on historical data, not predictive

---

## Future Enhancements

- **Pattern Recognition**: Detect candlestick patterns (Doji, Hammer, etc.)
- **Volume Analysis**: Incorporate volume trends
- **Sector Comparison**: Compare against sector performance
- **Machine Learning**: Train ML model on historical signals
- **Backtesting**: Show historical accuracy of signals
- **Custom Alerts**: Notify users when signals change

---

## Quick Reference

| Indicator | Purpose | Buy Signal | Sell Signal |
|-----------|---------|------------|-------------|
| RSI | Overbought/Oversold | < 30 | > 70 |
| MACD | Momentum | Histogram > 0 | Histogram < 0 |
| SMA | Trend | Price > SMAs | Price < SMAs |
| Support | Floor | Price near support | - |
| Resistance | Ceiling | - | Price near resistance |

**Signal Confidence:**
- **70-100%**: High confidence - Strong signal
- **50-70%**: Medium confidence - Moderate signal
- **0-50%**: Low confidence - Weak signal, use caution

---

**Created:** 2026-01-03  
**Version:** 1.0  
**Status:** Production
